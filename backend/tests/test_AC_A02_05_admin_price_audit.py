"""
Automated Test for AC-A02-05: Admin RBAC, 50% Shift Warning & Audit Trail
รองรับ REQ-SEC-001, CC-03, CC-05, D-A02-02, D-A02-06, AC-A02-05
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_store_state():
    orig_white = dict(supabase_store.benchmark_prices.get("MAT-WHITE-PAPER", {}))
    yield
    if orig_white:
        supabase_store.benchmark_prices["MAT-WHITE-PAPER"] = orig_white


def test_AC_A02_05_rbac_blocks_non_admin():
    """
    ทดสอบการปฏิเสธคำขอที่ไม่มีสิทธิ์แอดมินด้วย HTTP 403 Forbidden
    รองรับ AC-A02-05, CC-03, D-A02-06
    """
    # 1. ไม่มี Header X-Admin-Role
    res1 = client.get("/api/v1/admin/benchmark-prices")
    assert res1.status_code == 403

    # 2. X-Admin-Role เป็น SELLER
    res2 = client.put(
        "/api/v1/admin/benchmark-prices/MAT-CARDBOARD",
        json={"min_price_per_unit": 3.0, "max_price_per_unit": 4.0},
        headers={"X-Admin-Role": "SELLER"},
    )
    assert res2.status_code == 403

    # 3. X-Admin-Role เป็น COLLECTOR
    res3 = client.post(
        "/api/v1/admin/benchmark-prices/batch-update",
        json={"items": []},
        headers={"X-Admin-Role": "COLLECTOR"},
    )
    assert res3.status_code == 403

    # 4. เรียก Grading API ด้วยบทบาทอื่น
    res4 = client.get(
        "/api/v1/admin/benchmark-prices/grading/MAT-CARDBOARD",
        headers={"X-Admin-Role": "GUEST"},
    )
    assert res4.status_code == 403


def test_AC_A02_05_price_shift_exceeds_50_percent_requires_confirmation():
    """
    ทดสอบการแจ้งเตือนและบังคับยืนยัน confirm_shift เมื่อราคาเปลี่ยนเกิน ±50%
    รองรับ AC-A02-05, D-A02-02
    """
    # ราคาเดิม MAT-WHITE-PAPER คือ 6.0 - 7.0 (mid = 6.5)
    # หากปรับราคาเป็น 12.0 - 14.0 (mid = 13.0, shift = 100% > 50%)
    excessive_payload = {
        "min_price_per_unit": 12.0,
        "max_price_per_unit": 14.0,
        "confirm_shift": False,
        "updated_by": "admin-01",
    }
    res_blocked = client.put(
        "/api/v1/admin/benchmark-prices/MAT-WHITE-PAPER",
        json=excessive_payload,
        headers={"X-Admin-Role": "ADMIN"},
    )
    assert res_blocked.status_code == 400
    err_body = res_blocked.json()
    assert "PRICE_SHIFT_EXCEEDS_50_PERCENT" in str(err_body)

    # เมื่อส่ง confirm_shift = True ระบบต้องยอมให้อัปเดตและมี warning แจ้งเตือน
    confirmed_payload = {
        "min_price_per_unit": 12.0,
        "max_price_per_unit": 14.0,
        "confirm_shift": True,
        "updated_by": "admin-01",
        "change_reason": "ยืนยันการขึ้นราคาตามตลาดโลก",
    }
    res_confirmed = client.put(
        "/api/v1/admin/benchmark-prices/MAT-WHITE-PAPER",
        json=confirmed_payload,
        headers={"X-Admin-Role": "ADMIN"},
    )
    assert res_confirmed.status_code == 200
    data = res_confirmed.json()
    assert data["success"] is True
    assert data["warning"] is not None
    assert "ได้รับการยืนยันแล้ว" in data["warning"]


def test_AC_A02_05_audit_logs_recorded():
    """
    ทดสอบการบันทึก Audit Logs แบบ Append-only
    รองรับ AC-A02-05, REQ-SEC-001
    """
    audits_price = [a for a in supabase_store.audit_logs if a["action"] == "ADMIN_UPDATED_BENCHMARK_PRICE"]
    assert len(audits_price) >= 1
    last = audits_price[-1]
    assert last["actor_id"] == "admin-01"
    assert last["details"]["actor_role"] == "ADMIN"
    assert "old_min_price" in last["details"]
    assert "new_min_price" in last["details"]
