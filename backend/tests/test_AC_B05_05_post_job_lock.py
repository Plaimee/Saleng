"""
Acceptance Tests for AC-B05-05: Post-Transaction Privacy Guard in S7/S8
(Task T-05: MD-STM-04, REQ-SEC-002, D-B05-05)
"""

import pytest
from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_s7_s8_environment():
    """เตรียมคำขอขายในสถานะ S7 (Completed) และ S8 (Cancelled)"""
    order_s7 = "order-s7-completed"
    order_s8 = "order-s8-cancelled"

    supabase_store.orders[order_s7] = {
        "order_id": order_s7,
        "seller_id": "seller-01",
        "collector_id": "saleng-01",
        "assigned_saleng_id": "saleng-01",
        "status": "S7",
        "version": 5,
    }

    supabase_store.orders[order_s8] = {
        "order_id": order_s8,
        "seller_id": "seller-01",
        "collector_id": "saleng-01",
        "assigned_saleng_id": "saleng-01",
        "status": "S8",
        "version": 4,
    }

    orig_profile = dict(supabase_store.saleng_profiles.get("saleng-01", {}))
    supabase_store.saleng_profiles["saleng-01"].update({
        "verified": True,
        "kyc_status": "VERIFIED",
        "is_online": True,
    })

    yield

    supabase_store.orders.pop(order_s7, None)
    supabase_store.orders.pop(order_s8, None)
    if orig_profile:
        supabase_store.saleng_profiles["saleng-01"] = orig_profile


def test_AC_B05_05_s7_completed_room_is_read_only():
    """
    AC-B05-05: เมื่อคำขอขายเปลี่ยนเป็น S7 (Completed) ห้องแชตล็อกเป็น Read-only และซ่อนเบอร์โทรศัพท์
    """
    order_id = "order-s7-completed"
    resp = client.get(f"/api/v1/collectors/chat/{order_id}/messages?saleng_id=saleng-01")
    assert resp.status_code == 200
    data = resp.json()

    assert data["order_status"] == "S7"
    assert data["is_read_only"] is True
    assert "PDPA" in data["read_only_reason"]
    assert data["seller_info"]["phone"] is None
    assert data["seller_info"]["phone_masked"] is True


def test_AC_B05_05_s7_sending_message_blocked():
    """
    AC-B05-05: ส่งข้อความใหม่ในห้องแชตที่จบงานแล้ว (S7) ต้องถูกปฏิเสธด้วย HTTP 403 Forbidden
    """
    order_id = "order-s7-completed"
    payload = {
        "saleng_id": "saleng-01",
        "message_text": "ลืมของไว้ครับ ขอเข้าไปเอา",
        "is_quick_reply": False,
    }
    resp = client.post(f"/api/v1/collectors/chat/{order_id}/messages", json=payload)
    assert resp.status_code == 403
    assert "Read-only" in resp.json()["detail"] or "PDPA" in resp.json()["detail"]


def test_AC_B05_05_s8_cancelled_blocks_call():
    """
    AC-B05-05: คำขอขายที่ยกเลิก (S8) บล็อกการโทรหาผู้ขายด้วย HTTP 403 Forbidden
    """
    order_id = "order-s8-cancelled"
    payload = {
        "saleng_id": "saleng-01",
        "dialed_phone": "081-234-5678",
    }
    resp = client.post(f"/api/v1/collectors/chat/{order_id}/call-log", json=payload)
    assert resp.status_code == 403
    assert "PDPA" in resp.json()["detail"]
