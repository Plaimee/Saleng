"""
Acceptance Tests for AC-B05-02: Quick Replies Preset Bar
(Task T-03: REQ-UX-001, CC-01, D-B05-03, D-B05-04)
"""

import pytest
from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_quick_reply_environment():
    """เตรียมคำขอขายสำหรับการทดสอบ Quick Replies"""
    order_id = "order-qr-01"
    supabase_store.orders[order_id] = {
        "order_id": order_id,
        "seller_id": "seller-01",
        "collector_id": "saleng-01",
        "assigned_saleng_id": "saleng-01",
        "status": "S4",
        "location_id": "loc-01",
        "version": 3,
    }

    orig_profile = dict(supabase_store.saleng_profiles.get("saleng-01", {}))
    supabase_store.saleng_profiles["saleng-01"].update({
        "verified": True,
        "kyc_status": "VERIFIED",
        "is_online": True,
    })

    yield

    supabase_store.orders.pop(order_id, None)
    if orig_profile:
        supabase_store.saleng_profiles["saleng-01"] = orig_profile
    supabase_store.chat_messages = [
        m for m in supabase_store.chat_messages if m.get("order_id") != order_id
    ]


def test_AC_B05_02_get_standard_quick_replies():
    """
    AC-B05-02: ดึงรายการข้อความด่วนสำเร็จรูป 4 ข้อความมาตรฐานครบถ้วน (D-B05-03)
    """
    resp = client.get("/api/v1/collectors/chat/quick-replies")
    assert resp.status_code == 200
    data = resp.json()
    assert "quick_replies" in data
    items = data["quick_replies"]
    assert len(items) == 4

    expected = [
        {"id": "qr-01", "text": "กำลังเดินทางไปครับ", "emoji": "🚚"},
        {"id": "qr-02", "text": "ถึงหน้าบ้านแล้วครับ", "emoji": "📍"},
        {"id": "qr-03", "text": "ช่วยออกมารับหน่อยครับ", "emoji": "🚪"},
        {"id": "qr-04", "text": "ขอเลื่อนเวลาประมาณ 15 นาทีครับ", "emoji": "⏰"},
    ]

    for exp in expected:
        matched = [i for i in items if i["id"] == exp["id"]]
        assert len(matched) == 1
        assert matched[0]["text"] == exp["text"]
        assert matched[0]["emoji"] == exp["emoji"]


def test_AC_B05_02_send_quick_reply_message():
    """
    AC-B05-02: ส่งข้อความด่วนสำเร็จรูป flag is_quick_reply=True และบันทึก Audit Log ถูกต้อง
    """
    order_id = "order-qr-01"
    payload = {
        "saleng_id": "saleng-01",
        "message_text": "ถึงหน้าบ้านแล้วครับ",
        "is_quick_reply": True,
    }

    resp = client.post(f"/api/v1/collectors/chat/{order_id}/messages", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["message"]["message_text"] == "ถึงหน้าบ้านแล้วครับ"
    assert data["message"]["is_quick_reply"] is True

    # ตรวจสอบการบันทึก Audit Log
    latest_audit = supabase_store.audit_logs[-1]
    assert latest_audit["action"] == "COLLECTOR_SENT_MESSAGE"
    assert latest_audit["actor_id"] == "saleng-01"
    assert latest_audit["details"]["is_quick_reply"] is True
