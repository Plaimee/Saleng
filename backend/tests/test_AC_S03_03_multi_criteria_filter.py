"""
Backend API Tests สำหรับ AC-S03-03: Multi-Criteria Filter & Bulky Vehicle Match
รองรับ UC-03, REQ-FN-001, CC-03, Card 03, AC-S03-03, P-03, Q-03
"""

from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


def test_AC_S03_03_filter_by_vehicle_type():
    """ทดสอบการกรองตามประเภทยานพาหนะ เช่น รถกระบะ (PICKUP_TRUCK)"""
    response = client.get("/api/v1/buyer-search/collectors?vehicle_type=PICKUP_TRUCK")
    assert response.status_code == 200
    collectors = response.json()["collectors"]
    assert len(collectors) >= 1
    for c in collectors:
        assert c["vehicle_type"] == "PICKUP_TRUCK"


def test_AC_S03_03_filter_by_min_rating():
    """ทดสอบการกรองตามคะแนนรีวิวขั้นต่ำ เช่น 4.85 ดาวขึ้นไป"""
    response = client.get("/api/v1/buyer-search/collectors?min_rating=4.85")
    assert response.status_code == 200
    collectors = response.json()["collectors"]
    for c in collectors:
        assert c["rating"] >= 4.85


def test_AC_S03_03_bulky_items_auto_detection():
    """
    ทดสอบว่าหากคำขอมีของชิ้นใหญ่ (ตู้เย็น/เครื่องซักผ้า ตาม Card 03)
    ระบบตรวจจับอัตโนมัติและแสดงป้ายเตือนแนะนำรถกระบะ
    """
    order_id = "order-with-fridge"
    supabase_store.orders[order_id] = {
        "order_id": order_id,
        "seller_id": "seller-01",
        "status": "S1",
    }
    # เพิ่มรายการของชิ้นใหญ่ลงในคำขอ
    supabase_store.items["item-fridge"] = {
        "item_id": "item-fridge",
        "order_id": order_id,
        "category_code": "BULKY-APPLIANCE",
        "sub_category": "ตู้เย็น",
        "quantity": 1,
    }

    response = client.get(f"/api/v1/buyer-search/collectors?order_id={order_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["has_bulky_items"] is True
    assert "ของชิ้นใหญ่" in data["bulky_warning_message"]

