"""
Backend API Tests สำหรับ AC-S05-04: In-Transit ETA & Distance Display
รองรับ UC-04, CC-02, CC-03, AC-S05-04, P-04, Q-03
"""

from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


def test_AC_S05_04_in_transit_eta_and_distance_display():
    """
    ทดสอบว่าในสถานะ S4 (In-Transit) หน้าจอต้องได้รับข้อมูลระยะทาง (กม.)
    และเวลาประเมินถึงหน้างาน (ETA นาที) พร้อมโปรไฟล์ของซาเล้ง
    """
    order_id = "order-eta-test"
    supabase_store.orders[order_id] = {
        "order_id": order_id,
        "seller_id": "seller-01",
        "status": "S4",
        "assigned_saleng_id": "saleng-01",
        "in_transit_distance_km": 1.5,
    }

    response = client.get(f"/api/v1/booking-tracking/orders/{order_id}/status")
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "S4"
    assert data["distance_km"] == 1.5
    assert data["eta_minutes"] is not None
    assert data["eta_minutes"] > 0
    assert data["can_cancel"] is False

    # ตรวจสอบว่ามีข้อมูลโปรไฟล์ซาเล้งที่กำลังเดินทาง
    saleng = data["assigned_saleng"]
    assert saleng is not None
    assert saleng["saleng_id"] == "saleng-01"
    assert saleng["verified"] is True
    assert saleng["phone"] == "081-234-5678"

