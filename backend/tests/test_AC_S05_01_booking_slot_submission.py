"""
Backend API Tests สำหรับ AC-S05-01: Booking Slot Selection & Order Submission
รองรับ UC-04, REQ-FN-003, AC-S05-01, P-01, Q-01
"""

from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


def test_AC_S05_01_booking_slot_immediate():
    """ทดสอบการเลือกเวลานัดหมายแบบเรียกทันที (IMMEDIATE) และเปลี่ยนสถานะเป็น S2"""
    order_id = "order-book-immediate"
    supabase_store.orders[order_id] = {
        "order_id": order_id,
        "seller_id": "seller-01",
        "status": "S1",
    }

    payload = {
        "booking_type": "IMMEDIATE",
        "notes": "พร้อมส่งมอบทันทีครับ",
    }
    response = client.post(
        f"/api/v1/booking-tracking/orders/{order_id}/book?seller_id=seller-01",
        json=payload,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "S2"
    assert data["booking_type"] == "IMMEDIATE"
    assert "เรียกทันที" in data["scheduled_time_display"]

    # ตรวจสอบ Audit Log
    logs = [
        l for l in supabase_store.audit_logs
        if l.get("action") == "ORDER_SUBMITTED" and l.get("entity_id") == order_id
    ]
    assert len(logs) >= 1


def test_AC_S05_01_booking_slot_scheduled():
    """ทดสอบการนัดหมายล่วงหน้า (SCHEDULED) ระบุวันและช่วงเวลา"""
    order_id = "order-book-scheduled"
    supabase_store.orders[order_id] = {
        "order_id": order_id,
        "seller_id": "seller-01",
        "status": "S1",
    }

    payload = {
        "booking_type": "SCHEDULED",
        "scheduled_date": "2026-11-15",
        "scheduled_slot": "AFTERNOON_13_16",
        "notes": "อยู่บ้านช่วงบ่าย",
    }
    response = client.post(
        f"/api/v1/booking-tracking/orders/{order_id}/book?seller_id=seller-01",
        json=payload,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "S2"
    assert data["booking_type"] == "SCHEDULED"
    assert "2026-11-15" in data["scheduled_time_display"]
    assert "13:00 – 16:00" in data["scheduled_time_display"]

