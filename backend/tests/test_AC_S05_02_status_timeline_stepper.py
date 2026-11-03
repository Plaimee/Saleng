"""
Backend API Tests สำหรับ AC-S05-02: Real-Time 9-State Timeline Stepper
รองรับ UC-04, MD-STM-04, REQ-FN-003, AC-S05-02, P-02
"""

from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


def test_AC_S05_02_status_timeline_stepper_progression():
    """
    ทดสอบการดึงข้อมูลสถานะและการอัปเดตขั้นตอน Stepper 5 ขั้นตอนหลัก:
    - S1/S2: Step 1 (ส่งคำขอ)
    - S3: Step 2 (มีผู้รับงานแล้ว)
    - S4: Step 3 (กำลังเดินทาง)
    - S5: Step 4 (ถึงหน้าบ้าน)
    - S6/S7: Step 5 (ชำระเงิน/ปิดงาน)
    """
    order_id = "order-stepper-test"
    supabase_store.orders[order_id] = {
        "order_id": order_id,
        "seller_id": "seller-01",
        "status": "S2",
    }

    # 1. สถานะ S2: Step 1
    res_s2 = client.get(f"/api/v1/booking-tracking/orders/{order_id}/status")
    assert res_s2.status_code == 200
    assert res_s2.json()["status"] == "S2"
    assert res_s2.json()["stepper_step"] == 1

    # 2. จำลองสถานะเป็น S3 (รับงานแล้ว): Step 2
    client.patch(
        f"/api/v1/booking-tracking/orders/{order_id}/simulate-status",
        json={"target_status": "S3", "saleng_id": "saleng-01"},
    )
    res_s3 = client.get(f"/api/v1/booking-tracking/orders/{order_id}/status")
    assert res_s3.json()["status"] == "S3"
    assert res_s3.json()["stepper_step"] == 2
    assert res_s3.json()["assigned_saleng"]["saleng_id"] == "saleng-01"

    # 3. จำลองสถานะเป็น S4 (กำลังเดินทาง): Step 3
    client.patch(
        f"/api/v1/booking-tracking/orders/{order_id}/simulate-status",
        json={"target_status": "S4"},
    )
    res_s4 = client.get(f"/api/v1/booking-tracking/orders/{order_id}/status")
    assert res_s4.json()["status"] == "S4"
    assert res_s4.json()["stepper_step"] == 3

    # 4. จำลองสถานะเป็น S5 (ถึงหน้างาน): Step 4
    client.patch(
        f"/api/v1/booking-tracking/orders/{order_id}/simulate-status",
        json={"target_status": "S5"},
    )
    res_s5 = client.get(f"/api/v1/booking-tracking/orders/{order_id}/status")
    assert res_s5.json()["status"] == "S5"
    assert res_s5.json()["stepper_step"] == 4

