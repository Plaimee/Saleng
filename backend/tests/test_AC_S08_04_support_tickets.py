"""
Automated Backend Tests สำหรับ AC-S08-04: Customer Support Ticket & Hotline
รองรับ UC-08, UC-13, REQ-SEC-002, REQ-SEC-001, AC-S08-04, P-04, P-05, Q-04
"""

from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


def test_submit_support_ticket_success_and_masking():
    """
    AC-S08-04 / REQ-SEC-002 / REQ-SEC-001:
    1. ผู้ขายส่ง Support Ticket สำเร็จ
    2. ได้รับรหัสตั๋ว TCK-YYYYMMDD-XXXX
    3. เบอร์โทรศัพท์ถูกปกปิดเป็น 08X-XXX-XXXX (PDPA Masking)
    4. บันทึก Audit Log SELLER_SUBMIT_SUPPORT_TICKET
    """
    seller_id = "SELLER-TICKET-01"
    payload = {
        "category": "WEIGHING",
        "subject": "สอบถามเรื่องรูปตาชั่งไม่ชัด",
        "description": "ซาเล้งมาชั่งของหน้าบ้านแต่รูปถ่ายหน้าตาชั่งมัวมาก มองตัวเลขไม่เห็น",
        "contact_phone": "0819998877",
    }

    response = client.post(f"/api/v1/sellers/{seller_id}/support-tickets", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert data["seller_id"] == seller_id
    assert data["category"] == "WEIGHING"
    assert data["subject"] == "สอบถามเรื่องรูปตาชั่งไม่ชัด"
    assert data["ticket_no"].startswith("TCK-")

    # REQ-SEC-002: ตรวจสอบ PII Masking
    assert data["contact_phone_masked"] == "08X-XXX-8877"
    assert "0819998877" not in response.text

    # ตรวจสอบ Audit Log (REQ-SEC-001, AC-S08-05)
    logs = [
        l for l in supabase_store.audit_logs
        if l["action"] == "SELLER_SUBMIT_SUPPORT_TICKET" and l["entity_id"] == data["ticket_no"]
    ]
    assert len(logs) >= 1
    assert logs[-1]["details"]["category"] == "WEIGHING"


def test_get_contact_info():
    """
    AC-S08-04: ตรวจสอบข้อมูลติดต่อสายด่วน Call Center และ LINE Official
    """
    response = client.get("/api/v1/help/contact-info")
    assert response.status_code == 200
    info = response.json()

    assert info["call_center_phone"] == "02-123-4567"
    assert "08:00 - 18:00" in info["operating_hours"]
    assert info["line_official"] == "@saleng-help"

