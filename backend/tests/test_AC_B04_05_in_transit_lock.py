"""
Acceptance Tests for AC-B04-05: In-Transit Status Transition & Seller Cancel Lock
(Task T-05: UC-09, BR-03, AC-B04-05, D-B04-03)
"""

import pytest
from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_order_state():
    orig_status = supabase_store.orders["order-s2-01"].get("status")
    orig_collector = supabase_store.orders["order-s2-01"].get("collector_id")
    orig_assigned = supabase_store.orders["order-s2-01"].get("assigned_saleng_id")

    supabase_store.orders["order-s2-01"]["status"] = "S3"
    supabase_store.orders["order-s2-01"]["collector_id"] = "saleng-01"
    supabase_store.orders["order-s2-01"]["assigned_saleng_id"] = "saleng-01"

    yield

    supabase_store.orders["order-s2-01"]["status"] = orig_status
    supabase_store.orders["order-s2-01"]["collector_id"] = orig_collector
    supabase_store.orders["order-s2-01"]["assigned_saleng_id"] = orig_assigned


def test_AC_B04_05_start_transit_transitions_to_s4_and_locks_seller_cancel():
    """
    Given: คำขอขาย order-s2-01 อยู่ในสถานะ S3: มีผู้รับงานแล้ว (saleng-01)
    When: ซาเล้ง saleng-01 กดปุ่ม "เริ่มออกเดินทาง" (POST /start-transit)
    Then: สถานะคำขอเปลี่ยนเป็น S4: กำลังเดินทาง (In-Transit)
    And: ระบบล็อกปุ่มยกเลิกฝั่งผู้ขายทันทีตามกฎ BR-03 (seller_cancel_locked = True)
    And: ส่งคืน navigation_url ไปยัง Google Maps
    """
    res = client.post(
        "/api/v1/collectors/jobs/order-s2-01/start-transit",
        json={"saleng_id": "saleng-01", "current_lat": 13.7900, "current_lng": 100.5750},
    )
    assert res.status_code == 200
    data = res.json()

    assert data["order_id"] == "order-s2-01"
    assert data["status"] == "S4"
    assert data["seller_notified"] is True
    assert data["seller_cancel_locked"] is True
    assert "https://www.google.com/maps/dir/?api=1" in data["navigation_url"]

    # ตรวจสอบใน Store ว่าสถานะเป็น S4
    order_db = supabase_store.orders.get("order-s2-01")
    assert order_db["status"] == "S4"
    assert "in_transit_at" in order_db


def test_AC_B04_05_unauthorized_collector_cannot_start_transit():
    """ซาเล้งคนอื่นที่ไม่ใช่ผู้รับผิดชอบงาน ไม่สามารถกดเริ่มออกเดินทางได้"""
    res = client.post(
        "/api/v1/collectors/jobs/order-s2-01/start-transit",
        json={"saleng_id": "saleng-99"},
    )
    assert res.status_code == 403

