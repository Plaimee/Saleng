"""
Acceptance Tests for AC-B05-04: Pre-Claim Privacy Guard in Status S2
(Task T-05: REQ-SEC-002, CC-06, D-B05-01)
"""

import pytest
from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_s2_test_environment():
    """เตรียมคำขอขายในสถานะ S2 (รอผู้รับงาน / Direct Request)"""
    order_id = "order-s2-pdpa"
    supabase_store.orders[order_id] = {
        "order_id": order_id,
        "seller_id": "seller-pdpa-01",
        "collector_id": None,
        "assigned_saleng_id": None,
        "status": "S2",
        "version": 1,
    }

    supabase_store.sellers["seller-pdpa-01"] = {
        "seller_id": "seller-pdpa-01",
        "display_name": "คุณวิภาดา",
        "phone": "081-999-0000",
    }

    orig_profile = dict(supabase_store.saleng_profiles.get("saleng-01", {}))
    supabase_store.saleng_profiles["saleng-01"].update({
        "verified": True,
        "kyc_status": "VERIFIED",
        "is_online": True,
    })

    yield

    supabase_store.orders.pop(order_id, None)
    supabase_store.sellers.pop("seller-pdpa-01", None)
    if orig_profile:
        supabase_store.saleng_profiles["saleng-01"] = orig_profile


def test_AC_B05_04_pre_claim_masks_phone():
    """
    AC-B05-04: ในสถานะ S2 ห้องแชตจะ Mask เบอร์โทรศัพท์ของผู้ขายเป็น None และ phone_masked=True (REQ-SEC-002, CC-06)
    """
    order_id = "order-s2-pdpa"
    resp = client.get(f"/api/v1/collectors/chat/{order_id}/messages?saleng_id=saleng-01")
    assert resp.status_code == 200
    data = resp.json()

    assert data["order_status"] == "S2"
    assert data["seller_info"]["display_name"] == "คุณวิภาดา"
    assert data["seller_info"]["phone"] is None
    assert data["seller_info"]["phone_masked"] is True


def test_AC_B05_04_pre_claim_call_blocked():
    """
    AC-B05-04: ในสถานะ S2 ไม่อนุญาตให้โทรหาผู้ขาย (บล็อกด้วย HTTP 403)
    """
    order_id = "order-s2-pdpa"
    payload = {
        "saleng_id": "saleng-01",
        "dialed_phone": "081-999-0000",
    }
    resp = client.post(f"/api/v1/collectors/chat/{order_id}/call-log", json=payload)
    assert resp.status_code == 403
    assert "ยังไม่ได้รับงาน" in resp.json()["detail"]


def test_AC_B05_04_pre_claim_chat_allowed_for_inquiry():
    """
    AC-B05-04: ในสถานะ S2 ซาเล้งสามารถพิมพ์แชตสอบถามรายละเอียดก่อนรับงานได้ (D-B05-01)
    """
    order_id = "order-s2-pdpa"
    payload = {
        "saleng_id": "saleng-01",
        "message_text": "บ้านอยู่ซอยไหนครับ พอดีกำลังดูเส้นทาง",
        "is_quick_reply": False,
    }
    resp = client.post(f"/api/v1/collectors/chat/{order_id}/messages", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "success"
    assert data["message"]["message_text"] == payload["message_text"]
