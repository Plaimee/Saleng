"""
Acceptance Tests for AC-B05-01: In-App Direct Chat Messaging
(Task T-02: UC-08, REQ-UX-001, D-B05-01, D-B05-04)
"""

import pytest
from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_chat_test_environment():
    """เตรียมข้อมูลคำขอขายและโปรไฟล์ซาเล้งสำหรับการทดสอบระบบแชต"""
    order_id = "order-chat-ac01"
    supabase_store.orders[order_id] = {
        "order_id": order_id,
        "seller_id": "seller-01",
        "collector_id": "saleng-01",
        "assigned_saleng_id": "saleng-01",
        "status": "S3",
        "location_id": "loc-01",
        "total_est_weight_kg": 25.0,
        "version": 2,
    }

    orig_profile = dict(supabase_store.saleng_profiles.get("saleng-01", {}))
    supabase_store.saleng_profiles["saleng-01"].update({
        "verified": True,
        "kyc_status": "VERIFIED",
        "is_online": True,
    })

    # ล้างประวัติแชตของคำขอนี้
    supabase_store.chat_messages = [
        m for m in supabase_store.chat_messages if m.get("order_id") != order_id
    ]

    yield

    supabase_store.orders.pop(order_id, None)
    if orig_profile:
        supabase_store.saleng_profiles["saleng-01"] = orig_profile
    supabase_store.chat_messages = [
        m for m in supabase_store.chat_messages if m.get("order_id") != order_id
    ]


def test_AC_B05_01_send_and_retrieve_chat_messages():
    """
    AC-B05-01: ซาเล้งสามารถเปิดห้องแชต ส่งข้อความอิสระ และดูประวัติข้อความตามลำดับเวลาได้
    """
    order_id = "order-chat-ac01"

    # 1. ส่งข้อความแรกจากซาเล้ง
    payload1 = {
        "saleng_id": "saleng-01",
        "message_text": "สวัสดีครับพี่ กำลังจะเข้าไปรับของนะครับ",
        "is_quick_reply": False,
    }
    resp1 = client.post(f"/api/v1/collectors/chat/{order_id}/messages", json=payload1)
    assert resp1.status_code == 201
    data1 = resp1.json()
    assert data1["status"] == "success"
    assert data1["message"]["message_text"] == payload1["message_text"]
    assert data1["message"]["sender_role"] == "COLLECTOR"
    assert data1["message"]["is_quick_reply"] is False

    # 2. จำลองข้อความตอบกลับจากผู้ขาย
    supabase_store.send_chat_message(
        order_id=order_id,
        sender_id="seller-01",
        sender_role="SELLER",
        message_text="รับทราบค่ะ ของกองไว้หน้าประตูรั้วแล้ว",
        is_quick_reply=False,
    )

    # 3. ดึงประวัติห้องแชต
    room_resp = client.get(f"/api/v1/collectors/chat/{order_id}/messages?saleng_id=saleng-01")
    assert room_resp.status_code == 200
    room_data = room_resp.json()

    assert room_data["order_id"] == order_id
    assert room_data["order_status"] == "S3"
    assert room_data["is_read_only"] is False
    assert room_data["seller_info"]["display_name"] == "คุณวิภาดา"
    assert room_data["seller_info"]["phone"] == "081-234-5678"
    assert len(room_data["messages"]) == 2
    assert room_data["messages"][0]["sender_role"] == "COLLECTOR"
    assert room_data["messages"][1]["sender_role"] == "SELLER"


def test_AC_B05_01_empty_message_validation():
    """
    AC-B05-01: ส่งข้อความว่างเปล่าต้องตอบกลับ HTTP 400 Bad Request
    """
    order_id = "order-chat-ac01"
    payload = {
        "saleng_id": "saleng-01",
        "message_text": "   ",
        "is_quick_reply": False,
    }
    resp = client.post(f"/api/v1/collectors/chat/{order_id}/messages", json=payload)
    assert resp.status_code == 400
    assert "ข้อความแชตต้องไม่เป็นค่าว่าง" in resp.json()["detail"]


def test_AC_B05_01_non_existent_order():
    """
    AC-B05-01: เข้าห้องแชตของคำขอขายที่ไม่มีอยู่จริงต้องตอบกลับ HTTP 404
    """
    resp = client.get("/api/v1/collectors/chat/non-existent-order/messages?saleng_id=saleng-01")
    assert resp.status_code == 404
