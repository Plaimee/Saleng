"""
ชุดทดสอบ AC-A01-03: User Penalty Enforcement for Saleng & Seller (UC-11, REQ-SEC-001, D-A01-03, D-A01-04)
"""

import pytest
from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_penalty_data():
    """เตรียมข้อมูลผู้ใช้และกู้คืนสถานะหลังทดสอบ"""
    orig_saleng = {k: dict(v) for k, v in supabase_store.saleng_profiles.items()}
    orig_sellers = {k: dict(v) for k, v in supabase_store.sellers.items()}
    orig_audit = list(supabase_store.audit_logs)

    # รับประกันว่ามีผู้ใช้พร้อมทดสอบ
    supabase_store.saleng_profiles["saleng-01"]["account_status"] = "ACTIVE"
    supabase_store.sellers["seller-01"] = {
        "seller_id": "seller-01",
        "phone": "081-234-5678",
        "display_name": "คุณวิภาดา",
        "account_status": "ACTIVE",
        "penalty_reason": None,
        "penalized_at": None,
        "penalized_by": None,
    }

    yield

    supabase_store.saleng_profiles = orig_saleng
    supabase_store.sellers = orig_sellers
    supabase_store.audit_logs = orig_audit


def test_AC_A01_03_list_all_users_with_status():
    """
    ทดสอบ AC-A01-03: แอดมินสามารถดึงรายชื่อผู้ใช้ทั้งซาเล้งและผู้ขาย พร้อมสถานะบัญชีและเบอร์ Masking
    """
    response = client.get(
        "/api/v1/admin/users",
        headers={"X-Admin-Role": "ADMIN", "X-Admin-Id": "admin-01"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2

    # ตรวจสอบว่ามีทั้งบทบาท COLLECTOR และ SELLER
    roles = {u["role"] for u in data}
    assert "COLLECTOR" in roles
    assert "SELLER" in roles

    # ตรวจสอบว่าเบอร์โทรศัพท์ถูก Mask เป็น 08X-XXX-XXXX ตาม REQ-SEC-002, CC-06
    for u in data:
        assert "account_status" in u
        assert "phone_masked" in u
        assert "X-XXX-" in u["phone_masked"]


def test_AC_A01_03_suspend_saleng_user():
    """
    ทดสอบ AC-A01-03: สั่งระงับสิทธิ์ชั่วคราวซาเล้งกรณีโกงตาชั่ง -> account_status = SUSPENDED_TEMPORARY + Audit Log
    """
    response = client.post(
        "/api/v1/admin/users/penalty",
        json={
            "user_id": "saleng-01",
            "role": "COLLECTOR",
            "action": "SUSPEND_TEMPORARY",
            "penalty_reason": "ลูกค้าร้องเรียนเรื่องตาชั่งดิจิทัลไม่ตรงตามจริง",
            "duration_days": 14,
        },
        headers={"X-Admin-Role": "ADMIN", "X-Admin-Id": "admin-01"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["account_status"] == "SUSPENDED_TEMPORARY"
    assert data["user_id"] == "saleng-01"

    # ตรวจสอบใน store
    profile = supabase_store.get_saleng_profile("saleng-01")
    assert profile["account_status"] == "SUSPENDED_TEMPORARY"
    assert "ตาชั่งดิจิทัลไม่ตรง" in profile["penalty_reason"]

    # ตรวจสอบ Audit Log
    log = next(
        (l for l in supabase_store.audit_logs if l.get("action") == "ADMIN_PENALIZED_USER" and l.get("entity_id") == "saleng-01"),
        None
    )
    assert log is not None
    assert log["details"]["action"] == "SUSPEND_TEMPORARY"


def test_AC_A01_03_ban_seller_user():
    """
    ทดสอบ AC-A01-03: สั่งแบนถาวรผู้ขายกรณีเบี้ยวนัดหมาย No-show ซ้ำซาก -> account_status = BANNED + Audit Log
    """
    response = client.post(
        "/api/v1/admin/users/penalty",
        json={
            "user_id": "seller-01",
            "role": "SELLER",
            "action": "BAN",
            "penalty_reason": "เบี้ยวนัดหมายซ้ำซากเกิน 5 ครั้ง (No-show)",
        },
        headers={"X-Admin-Role": "ADMIN", "X-Admin-Id": "admin-01"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["account_status"] == "BANNED"
    assert data["user_id"] == "seller-01"

    # ตรวจสอบใน store
    seller = supabase_store.sellers["seller-01"]
    assert seller["account_status"] == "BANNED"
    assert "เบี้ยวนัดหมายซ้ำซาก" in seller["penalty_reason"]


def test_AC_A01_03_penalize_non_existent_user_returns_404():
    """
    ทดสอบ AC-A01-03: สั่งลงโทษผู้ใช้ที่ไม่มีตัวตน ต้องได้ 404 Not Found
    """
    response = client.post(
        "/api/v1/admin/users/penalty",
        json={
            "user_id": "unknown-user-999",
            "role": "COLLECTOR",
            "action": "BAN",
            "penalty_reason": "ข้อมูลทดสอบ",
        },
        headers={"X-Admin-Role": "ADMIN", "X-Admin-Id": "admin-01"},
    )
    assert response.status_code == 404
