"""
Automated Backend Tests สำหรับ AC-S08-01: In-App Notifications & Draft Reminders
รองรับ UC-08, AC-S08-01, P-01, P-05, REQ-SEC-001, Q-01
"""

from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


def test_notifications_and_draft_reminder():
    """
    AC-S08-01 / Q-01:
    1. ตรวจสอบการสร้าง Draft Reminder อัตโนมัติสำหรับคำขอ S1 > 3 วัน
    2. ตรวจสอบการดึงรายการแจ้งเตือน และจำนวน unread_count
    3. ตรวจสอบการทำเครื่องหมายว่าอ่านแล้วรายข้อ
    4. ตรวจสอบการทำเครื่องหมายว่าอ่านแล้วทั้งหมด พร้อม Audit Log (REQ-SEC-001, AC-S08-05)
    """
    seller_id = "SELLER-NOTIF-AC01"
    order_id = "ORDER-DRAFT-3DAYS"

    # คำขอ S1 ค้างเกิน 3 วัน (สร้างเมื่อ 4 วันก่อน)
    four_days_ago = (datetime.now(timezone.utc) - timedelta(days=4)).isoformat()
    supabase_store.orders[order_id] = {
        "order_id": order_id,
        "seller_id": seller_id,
        "status": "S1",
        "created_at": four_days_ago,
    }

    # เพิ่มการแจ้งเตือนสถานะคำขอปกติ
    supabase_store.create_notification({
        "seller_id": seller_id,
        "type": "ORDER_STATUS_UPDATE",
        "title": "ซาเล้งใกล้ถึงหน้าบ้านแล้ว",
        "message": "นายสมคิดกำลังเดินทางถึงจุดนัดหมายของคุณ",
        "is_read": False,
    })

    # ดึงการแจ้งเตือนผ่าน API
    response = client.get(f"/api/v1/sellers/{seller_id}/notifications")
    assert response.status_code == 200
    data = response.json()

    assert data["seller_id"] == seller_id
    assert data["unread_count"] >= 2  # ต้องมีทั้ง Draft Reminder และ Status Update

    # ตรวจสอบว่ามี Draft Reminder
    notifs = data["notifications"]
    draft_reminder = next(n for n in notifs if n["type"] == "DRAFT_REMINDER")
    assert "รายการของเก่าค้างในฉบับร่าง" in draft_reminder["title"]
    assert draft_reminder["order_id"] == order_id

    # ทำเครื่องหมายว่าอ่านแล้วรายข้อ (PATCH)
    notif_id = draft_reminder["id"]
    patch_resp = client.patch(f"/api/v1/notifications/{notif_id}/read")
    assert patch_resp.status_code == 200
    assert patch_resp.json()["is_read"] is True

    # ดึงอีกครั้ง unread_count ต้องลดลง 1
    resp_after = client.get(f"/api/v1/sellers/{seller_id}/notifications").json()
    assert resp_after["unread_count"] == data["unread_count"] - 1

    # ทำเครื่องหมายอ่านแล้วทั้งหมด (POST mark-all-read)
    clear_resp = client.post(f"/api/v1/sellers/{seller_id}/notifications/mark-all-read")
    assert clear_resp.status_code == 200
    assert clear_resp.json()["cleared_count"] >= 1

    # ดึงอีกครั้ง unread_count ต้องเป็น 0
    resp_cleared = client.get(f"/api/v1/sellers/{seller_id}/notifications").json()
    assert resp_cleared["unread_count"] == 0

    # ตรวจสอบ Audit Log (REQ-SEC-001, AC-S08-05)
    logs = [
        l for l in supabase_store.audit_logs
        if l["action"] == "SELLER_CLEAR_NOTIFICATIONS" and l["entity_id"] == seller_id
    ]
    assert len(logs) >= 1

