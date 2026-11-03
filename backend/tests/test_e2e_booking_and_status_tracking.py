"""
E2E Integration Test สำหรับระบบนัดหมายและติดตามสถานะ (Booking & Status Tracking Lifecycle)
รองรับ UC-04, MD-STM-04, BR-03, REQ-FN-003, REQ-SEC-001, AC-S05-01..05, P-01..P-06
"""

from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


def test_e2e_booking_and_status_tracking_lifecycle():
    """
    ทดสอบวงจรชีวิตของระบบนัดหมายและติดตามสถานะแบบครบวงจร:
    1. สร้างคำขอฉบับร่าง S1
    2. นัดหมายล่วงหน้า (SCHEDULED) -> คำขอเปลี่ยนเป็น S2
    3. จำลองซาเล้งรับงาน (S3) -> ตรวจสอบว่ายังกดยกเลิกได้ (can_cancel = True)
    4. จำลองซาเล้งออกเดินทาง (S4 In-Transit) -> ตรวจสอบระยะทาง, ETA, และปุ่มยกเลิกถูกล็อก (can_cancel = False)
    5. พยายามกดยกเลิกในสถานะ S4 -> ต้องถูกบล็อกด้วย HTTP 400 ตามกฎ BR-03
    6. จำลองซาเล้งถึงหน้างาน (S5) -> สถานะอัปเดตเป็นถึงจุดนัดหมาย
    7. ตรวจสอบ Audit Log ครบทุกขั้นตอน
    """
    seller_id = "seller-e2e-booking"
    order_id = "order-e2e-booking-05"

    # ขั้นตอนที่ 1: เตรียมคำขอฉบับร่าง S1
    supabase_store.orders[order_id] = {
        "order_id": order_id,
        "seller_id": seller_id,
        "status": "S1",
    }

    # ขั้นตอนที่ 2: นัดหมายล่วงหน้า
    book_res = client.post(
        f"/api/v1/booking-tracking/orders/{order_id}/book?seller_id={seller_id}",
        json={
            "booking_type": "SCHEDULED",
            "scheduled_date": "2026-11-20",
            "scheduled_slot": "MORNING_09_12",
            "notes": "บ้านอยู่สุดซอยรัชดา 18",
        },
    )
    assert book_res.status_code == 200
    book_data = book_res.json()
    assert book_data["status"] == "S2"
    assert book_data["can_cancel"] is True
    assert "2026-11-20" in book_data["scheduled_time_display"]

    # ขั้นตอนที่ 3: ซาเล้งรับงาน (S3)
    client.patch(
        f"/api/v1/booking-tracking/orders/{order_id}/simulate-status",
        json={"target_status": "S3", "saleng_id": "saleng-01"},
    )
    status_s3 = client.get(f"/api/v1/booking-tracking/orders/{order_id}/status").json()
    assert status_s3["status"] == "S3"
    assert status_s3["stepper_step"] == 2
    assert status_s3["can_cancel"] is True
    assert status_s3["assigned_saleng"]["saleng_id"] == "saleng-01"

    # ขั้นตอนที่ 4: ซาเล้งออกเดินทาง (S4)
    client.patch(
        f"/api/v1/booking-tracking/orders/{order_id}/simulate-status",
        json={"target_status": "S4"},
    )
    status_s4 = client.get(f"/api/v1/booking-tracking/orders/{order_id}/status").json()
    assert status_s4["status"] == "S4"
    assert status_s4["stepper_step"] == 3
    assert status_s4["can_cancel"] is False  # BR-03 ล็อกปุ่มยกเลิก
    assert status_s4["eta_minutes"] is not None
    assert status_s4["distance_km"] == 1.4

    # ขั้นตอนที่ 5: พยายามยกเลิกขณะ S4 -> ต้องโดนบล็อก HTTP 400
    cancel_attempt = client.post(
        f"/api/v1/booking-tracking/orders/{order_id}/cancel?seller_id={seller_id}",
        json={"reason": "พยายามยกเลิกตอนรถวิ่ง"},
    )
    assert cancel_attempt.status_code == 400
    assert "BR-03" in cancel_attempt.json()["detail"]

    # ขั้นตอนที่ 6: ซาเล้งถึงหน้างาน (S5)
    client.patch(
        f"/api/v1/booking-tracking/orders/{order_id}/simulate-status",
        json={"target_status": "S5"},
    )
    status_s5 = client.get(f"/api/v1/booking-tracking/orders/{order_id}/status").json()
    assert status_s5["status"] == "S5"
    assert status_s5["stepper_step"] == 4

    # ขั้นตอนที่ 7: ตรวจสอบ Audit Log
    logs = [
        l for l in supabase_store.audit_logs if l.get("entity_id") == order_id
    ]
    assert len(logs) >= 3  # ORDER_SUBMITTED, STATUS_SIMULATED (S3, S4, S5)

