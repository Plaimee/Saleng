"""
ชุดทดสอบ AC-A01-04: Reactivate & Penalty Revocation (UC-11, REQ-SEC-001)
"""

import pytest
from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_reactivate_data():
    """เตรียมข้อมูลผู้ใช้ที่ติดสถานะระงับสิทธิ์ และกู้คืนสถานะหลังทดสอบ"""
    orig_saleng = {k: dict(v) for k, v in supabase_store.saleng_profiles.items()}
    orig_sellers = {k: dict(v) for k, v in supabase_store.sellers.items()}
    orig_audit = list(supabase_store.audit_logs)

    # กำหนดให้ saleng-02 ติดโทษระงับสิทธิ์ชั่วคราว
    supabase_store.saleng_profiles["saleng-02"]["account_status"] = "SUSPENDED_TEMPORARY"
    supabase_store.saleng_profiles["saleng-02"]["penalty_reason"] = "รอการไต่สวนข้อพิพาท"

    # กำหนดให้ seller-02 ติดโทษแบน
    supabase_store.sellers["seller-02"] = {
        "seller_id": "seller-02",
        "phone": "0898765432",
        "display_name": "วิชัย รีไซเคิลบ้าน",
        "account_status": "BANNED",
        "penalty_reason": "แจ้งข้อมูลเท็จ",
    }

    yield

    supabase_store.saleng_profiles = orig_saleng
    supabase_store.sellers = orig_sellers
    supabase_store.audit_logs = orig_audit


def test_AC_A01_04_reactivate_saleng_user():
    """
    ทดสอบ AC-A01-04: แอดมินสั่งปลดระงับสิทธิ์ซาเล้ง -> account_status = ACTIVE, ล้าง penalty_reason และมี Audit Log
    """
    response = client.post(
        "/api/v1/admin/users/reactivate",
        json={
            "user_id": "saleng-02",
            "role": "COLLECTOR",
            "reason": "พ้นโทษแบน 14 วัน และผ่านการอบรมกฎระเบียบแล้ว",
        },
        headers={"X-Admin-Role": "ADMIN", "X-Admin-Id": "admin-01"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["account_status"] == "ACTIVE"
    assert data["user_id"] == "saleng-02"

    # ตรวจสอบใน store
    profile = supabase_store.get_saleng_profile("saleng-02")
    assert profile["account_status"] == "ACTIVE"
    assert profile["penalty_reason"] is None

    # ตรวจสอบ Audit Log (REQ-SEC-001)
    log = next(
        (l for l in supabase_store.audit_logs if l.get("action") == "ADMIN_UNSUSPENDED_USER" and l.get("entity_id") == "saleng-02"),
        None
    )
    assert log is not None
    assert log["actor_role"] == "ADMIN"
    assert log["details"]["account_status"] == "ACTIVE"


def test_AC_A01_04_reactivate_seller_user():
    """
    ทดสอบ AC-A01-04: แอดมินสั่งปลดแบนผู้ขาย -> account_status = ACTIVE
    """
    response = client.post(
        "/api/v1/admin/users/reactivate",
        json={
            "user_id": "seller-02",
            "role": "SELLER",
            "reason": "เจรจาไกล่เกลี่ยข้อพิพาทสำเร็จ",
        },
        headers={"X-Admin-Role": "ADMIN", "X-Admin-Id": "admin-01"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["account_status"] == "ACTIVE"

    # ตรวจสอบใน store
    seller = supabase_store.sellers["seller-02"]
    assert seller["account_status"] == "ACTIVE"
    assert seller["penalty_reason"] is None

