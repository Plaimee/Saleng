"""
Unit tests สำหรับ T-01: Notifications & Help Models & Supabase Store
รองรับ UC-08, UC-13, REQ-SEC-002, CC-04, P-01..P-04
"""

import pytest
from datetime import datetime, timezone, timedelta
from pydantic import ValidationError
from backend.app.models.notification_help_models import (
    NotificationItem,
    NotificationListResponse,
    SortingGuideItem,
    FaqItem,
    SupportTicketCreateRequest,
    SupportTicketResponse,
)
from backend.app.core.supabase import supabase_store


def test_support_ticket_create_request_validation():
    """ตรวจสอบการตรวจสอบข้อมูลคำร้องขอความช่วยเหลือ (AC-S08-04)"""
    # กรณีถูกต้อง
    valid_req = SupportTicketCreateRequest(
        category="BOOKING",
        subject="สอบถามการนัดหมาย",
        description="ต้องการเปลี่ยนเวลานัดหมายกับซาเล้งในช่วงบ่าย",
        contact_phone="0812345678",
    )
    assert valid_req.category == "BOOKING"
    assert valid_req.subject == "สอบถามการนัดหมาย"

    # กรณี subject สั้นเกินไป (< 3 chars)
    with pytest.raises(ValidationError):
        SupportTicketCreateRequest(
            category="BOOKING",
            subject="ab",
            description="ต้องการเปลี่ยนเวลานัดหมายกับซาเล้งในช่วงบ่าย",
            contact_phone="0812345678",
        )

    # กรณี description สั้นเกินไป (< 10 chars)
    with pytest.raises(ValidationError):
        SupportTicketCreateRequest(
            category="BOOKING",
            subject="สอบถามการนัดหมาย",
            description="สั้นไป",
            contact_phone="0812345678",
        )


def test_supabase_store_notification_lifecycle():
    """ตรวจสอบการสร้างและทำเครื่องหมายอ่านแล้วของการแจ้งเตือน (P-01, Q-01)"""
    seller_id = "SELLER-NOTIF-TEST-01"

    # สร้างการแจ้งเตือน
    notif = supabase_store.create_notification({
        "seller_id": seller_id,
        "type": "ORDER_STATUS_UPDATE",
        "title": "ซาเล้งรับงานแล้ว",
        "message": "นายสมคิดตอบรับคำขอนัดหมายของคุณแล้ว",
        "is_read": False,
    })
    assert notif["id"] is not None
    assert notif["is_read"] is False

    # ตรวจสอบรายการแจ้งเตือน
    notifs = supabase_store.get_seller_notifications(seller_id)
    assert len(notifs) >= 1

    # ทำเครื่องหมายอ่านแล้ว
    updated = supabase_store.mark_notification_as_read(notif["id"])
    assert updated["is_read"] is True


def test_draft_reminder_generation_for_stale_orders():
    """ตรวจสอบการสร้าง Draft Reminder อัตโนมัติสำหรับคำขอ S1 ที่ค้างเกิน 3 วัน (AC-S08-01, Q-01)"""
    seller_id = "SELLER-STALE-DRAFT"
    order_id = "ORDER-S1-STALE"

    # คำขอ S1 สร้างเมื่อ 4 วันที่แล้ว
    four_days_ago = (datetime.now(timezone.utc) - timedelta(days=4)).isoformat()
    supabase_store.orders[order_id] = {
        "order_id": order_id,
        "seller_id": seller_id,
        "status": "S1",
        "created_at": four_days_ago,
    }

    # สร้างการแจ้งเตือนของค้าง
    supabase_store.generate_draft_reminders_for_seller(seller_id)

    # ต้องพบ Notification ประเภท DRAFT_REMINDER
    notifs = supabase_store.get_seller_notifications(seller_id)
    draft_reminders = [n for n in notifs if n.get("type") == "DRAFT_REMINDER"]
    assert len(draft_reminders) == 1
    assert "รายการของเก่าค้างในฉบับร่าง" in draft_reminders[0]["title"]
    assert draft_reminders[0]["order_id"] == order_id

