"""
Unit Tests for Task T-01: Communication Data Models and Supabase Store Extensions
รองรับ UC-08, REQ-UX-001, REQ-SEC-001, CC-04, D-B05-01, D-B05-03, D-B05-04
"""

import pytest
from pydantic import ValidationError
from backend.app.models.communication_models import (
    ChatMessage,
    SendChatMessageRequest,
    ChatMessageResponse,
    SellerContactInfo,
    ChatRoomResponse,
    LogCallRequest,
    LogCallResponse,
    QuickReplyItem,
    QuickRepliesResponse,
    DEFAULT_QUICK_REPLIES,
)
from backend.app.core.supabase import supabase_store


def test_chat_message_schema_validation():
    """ตรวจสอบความถูกต้องของ ChatMessage schema"""
    msg = ChatMessage(
        message_id="msg-100",
        order_id="order-001",
        sender_id="saleng-01",
        sender_role="COLLECTOR",
        message_text="กำลังเดินทางไปครับ",
        is_quick_reply=True,
        sent_at="2026-11-04T10:00:00Z",
    )
    assert msg.message_id == "msg-100"
    assert msg.sender_role == "COLLECTOR"
    assert msg.is_quick_reply is True

    # ทดสอบกรณี message_text ว่างเปล่า หรือเกิน 500 ตัวอักษร
    with pytest.raises(ValidationError):
        ChatMessage(
            message_id="msg-101",
            order_id="order-001",
            sender_id="saleng-01",
            sender_role="COLLECTOR",
            message_text="",
            sent_at="2026-11-04T10:00:00Z",
        )

    with pytest.raises(ValidationError):
        ChatMessage(
            message_id="msg-102",
            order_id="order-001",
            sender_id="saleng-01",
            sender_role="COLLECTOR",
            message_text="x" * 501,
            sent_at="2026-11-04T10:00:00Z",
        )


def test_send_chat_message_request_and_response():
    """ตรวจสอบคำขอและผลตอบกลับการส่งข้อความ"""
    req = SendChatMessageRequest(
        saleng_id="saleng-01",
        message_text="สวัสดีครับ",
        is_quick_reply=False,
    )
    assert req.saleng_id == "saleng-01"
    assert req.message_text == "สวัสดีครับ"

    chat_msg = ChatMessage(
        message_id="msg-200",
        order_id="order-002",
        sender_id=req.saleng_id,
        sender_role="COLLECTOR",
        message_text=req.message_text,
        is_quick_reply=req.is_quick_reply,
        sent_at="2026-11-04T10:05:00Z",
    )
    resp = ChatMessageResponse(status="success", message=chat_msg)
    assert resp.status == "success"
    assert resp.message.message_id == "msg-200"


def test_seller_contact_info_and_chatroom_response():
    """ตรวจสอบโมเดลข้อมูลติดต่อผู้ขายและการตอบกลับห้องแชต"""
    seller_info = SellerContactInfo(
        seller_id="seller-01",
        display_name="คุณวิภาดา",
        phone=None,
        phone_masked=True,
        subdistrict="แขวงสามเสนนอก",
    )
    assert seller_info.phone is None
    assert seller_info.phone_masked is True

    room = ChatRoomResponse(
        order_id="order-003",
        order_status="S2",
        is_read_only=False,
        read_only_reason=None,
        seller_info=seller_info,
        messages=[],
    )
    assert room.order_status == "S2"
    assert room.is_read_only is False
    assert len(room.messages) == 0


def test_quick_replies_defaults():
    """ตรวจสอบค่าเริ่มต้นของ Quick Replies 4 ข้อความมาตรฐาน (D-B05-03)"""
    assert len(DEFAULT_QUICK_REPLIES) == 4
    qr_ids = [q.id for q in DEFAULT_QUICK_REPLIES]
    assert qr_ids == ["qr-01", "qr-02", "qr-03", "qr-04"]
    assert DEFAULT_QUICK_REPLIES[0].text == "กำลังเดินทางไปครับ"
    assert DEFAULT_QUICK_REPLIES[0].emoji == "🚚"


def test_supabase_store_chat_and_audit_methods():
    """ทดสอบเมธอดของ SupabaseStore ที่เพิ่มขึ้นมาสำหรับระบบสื่อสาร"""
    test_order_id = "order-comm-test-01"
    
    # 1. ส่งข้อความแชต 2 ข้อความ
    msg1 = supabase_store.send_chat_message(
        order_id=test_order_id,
        sender_id="saleng-01",
        sender_role="COLLECTOR",
        message_text="กำลังเดินทางไปครับ",
        is_quick_reply=True,
    )
    assert msg1["order_id"] == test_order_id
    assert msg1["is_quick_reply"] is True

    msg2 = supabase_store.send_chat_message(
        order_id=test_order_id,
        sender_id="seller-01",
        sender_role="SELLER",
        message_text="รับทราบค่ะ รออยู่ที่บ้าน",
        is_quick_reply=False,
    )
    assert msg2["sender_role"] == "SELLER"

    # 2. ดึงข้อความแชตทั้งหมดของ order
    history = supabase_store.get_order_chat_messages(test_order_id)
    assert len(history) == 2
    assert history[0]["message_text"] == "กำลังเดินทางไปครับ"
    assert history[1]["message_text"] == "รับทราบค่ะ รออยู่ที่บ้าน"

    # 3. บันทึก audit log
    audit_entry = supabase_store.log_communication_audit(
        order_id=test_order_id,
        saleng_id="saleng-01",
        action="COLLECTOR_INITIATED_CALL",
        details={"dialed_phone": "081-234-5678"},
    )
    assert audit_entry["action"] == "COLLECTOR_INITIATED_CALL"
    assert audit_entry["order_id"] == test_order_id
    assert audit_entry["entity_id"] == test_order_id
    assert audit_entry["actor_id"] == "saleng-01"

    # ล้างข้อมูลทดสอบออกจาก store เพื่อป้องกันผลข้างเคียง
    supabase_store.chat_messages = [
        m for m in supabase_store.chat_messages if m.get("order_id") != test_order_id
    ]
    supabase_store.audit_logs = [
        l for l in supabase_store.audit_logs if l.get("entity_id") != test_order_id
    ]
