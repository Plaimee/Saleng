"""
End-to-End Integration Test สำหรับ Seller Feature 08: การแจ้งเตือนและการช่วยเหลือ (Notifications & Help Center)
รองรับ Use Case UC-08, UC-13, REQ-OP-001, REQ-SEC-001, REQ-SEC-002, AC-S08-01..05, P-01..P-06, Q-01..05
"""

from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


def test_e2e_notifications_and_help_lifecycle():
    """
    ทดสอบครบวงจรระบบแจ้งเตือนและศูนย์ช่วยเหลือ (End-to-End):
    1. จำลองคำขอค้างในสถานะ S1 นานกว่า 3 วัน (4 วันก่อน)
    2. ผู้ขายเปิดดูศูนย์แจ้งเตือน -> ระบบสร้าง Draft Reminder อัตโนมัติ (AC-S08-01, Q-01)
    3. ผู้ขายอ่านการแจ้งเตือนรายข้อ -> unread_count ลดลง (AC-S08-01)
    4. ผู้ขายกด "อ่านทั้งหมด" -> unread_count เป็น 0 พร้อมบันทึก Audit Log (AC-S08-01, AC-S08-05, REQ-SEC-001)
    5. ผู้ขายเปิดคู่มือคัดแยกขยะ 4 ชนิด -> ข้อมูลครบถ้วน พร้อมคำแนะนำเพิ่มมูลค่า (AC-S08-02, REQ-OP-001, Q-02)
    6. ผู้ขายเปิดอ่านคำถามพบบ่อย 3 หมวด พร้อมทดสอบค้นหาด้วยคำสำคัญ (AC-S08-03, Q-03)
    7. ผู้ขายส่งคำร้องขอความช่วยเหลือ -> ได้รับเลข Ticket รหัส TCK-, เบอร์โทรถูก Mask PII (AC-S08-04, REQ-SEC-002, Q-04)
    8. ผู้ขายดึงข้อมูลช่องทางติดต่อเร่งด่วน -> พบเบอร์ฮอตไลน์และ LINE Official (AC-S08-04, Q-04)
    9. ตรวจสอบ Audit Log ของทุกธุรกรรมครบถ้วนตามข้อกำหนด (AC-S08-05, REQ-SEC-001)
    """
    seller_id = "SELLER-E2E-S08"
    order_id = "ORDER-E2E-DRAFT-STALE"

    # -------------------------------------------------------------------------
    # 1. จัดเตรียมคำขอ S1 ค้าง 4 วัน และการแจ้งเตือนสถานะคำขอ
    # -------------------------------------------------------------------------
    four_days_ago = (datetime.now(timezone.utc) - timedelta(days=4)).isoformat()
    supabase_store.orders[order_id] = {
        "order_id": order_id,
        "seller_id": seller_id,
        "status": "S1",
        "created_at": four_days_ago,
    }

    supabase_store.create_notification({
        "seller_id": seller_id,
        "type": "ORDER_STATUS_UPDATE",
        "title": "ซาเล้งกำลังเดินทางมายังจุดนัดหมาย",
        "message": "นายสมคิด กำลังนำรถซาเล้งเข้ามารับของเก่าตามเวลานัด",
        "is_read": False,
        "order_id": order_id,
    })

    # -------------------------------------------------------------------------
    # 2. ผู้ขายเปิดดูศูนย์แจ้งเตือน (AC-S08-01, Q-01)
    # -------------------------------------------------------------------------
    res_notif = client.get(f"/api/v1/sellers/{seller_id}/notifications")
    assert res_notif.status_code == 200
    notif_data = res_notif.json()
    assert notif_data["seller_id"] == seller_id
    assert notif_data["unread_count"] >= 2

    # ตรวจสอบว่ามี DRAFT_REMINDER ที่สร้างขึ้นอัตโนมัติ
    reminder = next((n for n in notif_data["notifications"] if n["type"] == "DRAFT_REMINDER"), None)
    assert reminder is not None
    assert reminder["order_id"] == order_id
    assert "รายการของเก่าค้างในฉบับร่าง" in reminder["title"]
    assert reminder["is_read"] is False

    # -------------------------------------------------------------------------
    # 3. ผู้ขายอ่านการแจ้งเตือนรายข้อ (AC-S08-01)
    # -------------------------------------------------------------------------
    res_mark_single = client.patch(f"/api/v1/notifications/{reminder['id']}/read")
    assert res_mark_single.status_code == 200
    single_data = res_mark_single.json()
    assert single_data["is_read"] is True

    # ดึงซ้ำเพื่อตรวจสอบ unread_count ลดลง 1
    res_after_single = client.get(f"/api/v1/sellers/{seller_id}/notifications").json()
    assert res_after_single["unread_count"] == notif_data["unread_count"] - 1

    # -------------------------------------------------------------------------
    # 4. ผู้ขายกด "อ่านทั้งหมด" (AC-S08-01, AC-S08-05, REQ-SEC-001)
    # -------------------------------------------------------------------------
    res_mark_all = client.post(f"/api/v1/sellers/{seller_id}/notifications/mark-all-read")
    assert res_mark_all.status_code == 200
    all_read_data = res_mark_all.json()
    assert all_read_data["cleared_count"] >= 1

    # ดึงซ้ำเพื่อตรวจสอบ unread_count เป็น 0
    res_cleared = client.get(f"/api/v1/sellers/{seller_id}/notifications").json()
    assert res_cleared["unread_count"] == 0

    # ตรวจสอบ Audit Log การล้างสถานะการแจ้งเตือน
    notif_logs = [
        log for log in supabase_store.audit_logs
        if log.get("action") == "SELLER_CLEAR_NOTIFICATIONS" and log.get("entity_id") == seller_id
    ]
    assert len(notif_logs) >= 1
    assert notif_logs[-1]["details"]["cleared_count"] >= 1

    # -------------------------------------------------------------------------
    # 5. ผู้ขายเปิดคู่มือคัดแยกขยะ 4 ชนิด (AC-S08-02, REQ-OP-001, Q-02)
    # -------------------------------------------------------------------------
    res_guides = client.get("/api/v1/help/sorting-guides")
    assert res_guides.status_code == 200
    guides_data = res_guides.json()
    assert len(guides_data["guides"]) == 4

    categories = [g["category_code"] for g in guides_data["guides"]]
    assert "MAT-CARDBOARD" in categories
    assert "MAT-WHITE-PAPER" in categories
    assert "MAT-GLASS-BOTTLE" in categories
    assert "MAT-PLASTIC-PET" in categories

    cardboard_guide = next(g for g in guides_data["guides"] if g["category_code"] == "MAT-CARDBOARD")
    assert len(cardboard_guide["value_add_tips"]) > 0
    assert cardboard_guide["price_impact_description"] != ""
    assert len(cardboard_guide["precautions"]) > 0

    # -------------------------------------------------------------------------
    # 6. ผู้ขายเปิดอ่านคำถามพบบ่อย 3 หมวด และค้นหาด้วยคำสำคัญ (AC-S08-03, Q-03)
    # -------------------------------------------------------------------------
    res_faqs = client.get("/api/v1/help/faqs")
    assert res_faqs.status_code == 200
    faqs_data = res_faqs.json()
    assert faqs_data["total_faqs"] >= 8

    faq_categories = set(c["category_id"] for c in faqs_data["categories"])
    assert "MINIMUM_AND_BOOKING" in faq_categories
    assert "WEIGHING_AND_PRICING" in faq_categories
    assert "PAYMENT_AND_RECEIPT" in faq_categories

    # ค้นหาด้วยคำสำคัญ "500 บาท"
    res_faqs_search = client.get("/api/v1/help/faqs?query=500 บาท")
    assert res_faqs_search.status_code == 200
    search_data = res_faqs_search.json()
    assert search_data["total_faqs"] >= 1
    all_faqs = [f for c in search_data["categories"] for f in c["faqs"]]
    assert any("500 บาท" in f["question"] or "500 บาท" in f["answer"] for f in all_faqs)

    # -------------------------------------------------------------------------
    # 7. ผู้ขายส่งคำร้องขอความช่วยเหลือ (AC-S08-04, REQ-SEC-002, Q-04)
    # -------------------------------------------------------------------------
    ticket_payload = {
        "category": "PAYMENT",
        "subject": "ยอดเงินโอนไม่ตรงกับใบเสร็จดิจิทัล",
        "description": "ยอดเงินโอนเข้า PromptPay ขาดไป 50 บาท รบกวนเจ้าหน้าที่ตรวจสอบ",
        "contact_phone": "0891234567",
    }
    res_ticket = client.post(f"/api/v1/sellers/{seller_id}/support-tickets", json=ticket_payload)
    assert res_ticket.status_code == 201
    ticket_data = res_ticket.json()

    assert ticket_data["ticket_no"].startswith("TCK-")
    assert ticket_data["contact_phone_masked"] == "08X-XXX-4567"  # PDPA masking (REQ-SEC-002)
    assert "0891234567" not in res_ticket.text
    assert ticket_data["status"] == "OPEN"

    # -------------------------------------------------------------------------
    # 8. ผู้ขายดึงข้อมูลช่องทางติดต่อเร่งด่วน (AC-S08-04, Q-04)
    # -------------------------------------------------------------------------
    res_contact = client.get("/api/v1/help/contact-info")
    assert res_contact.status_code == 200
    contact_data = res_contact.json()
    assert contact_data["call_center_phone"] == "02-123-4567"
    assert "08:00 - 18:00" in contact_data["operating_hours"]
    assert contact_data["line_official"] == "@saleng-help"

    # -------------------------------------------------------------------------
    # 9. ตรวจสอบ Audit Log ตาม AC-S08-05 และ REQ-SEC-001
    # -------------------------------------------------------------------------
    ticket_logs = [
        log for log in supabase_store.audit_logs
        if log.get("action") == "SELLER_SUBMIT_SUPPORT_TICKET" and log.get("entity_id") == ticket_data["ticket_no"]
    ]
    assert len(ticket_logs) >= 1
    latest_ticket_log = ticket_logs[-1]
    assert latest_ticket_log["actor_id"] == seller_id
    assert latest_ticket_log["details"]["category"] == "PAYMENT"
    assert latest_ticket_log["details"]["contact_phone_masked"] == "08X-XXX-4567"
