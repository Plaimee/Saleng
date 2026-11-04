"""
Acceptance Tests for AC-B04-03: Address Unmasking & GPS Navigation Launch
(Task T-03: UC-04, UC-09, REQ-SEC-002, D-00-02, CC-06, D-B04-03)
"""

import pytest
from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_order_state():
    orig_order = supabase_store.orders.get("order-s2-02")
    orig_status = orig_order.get("status") if orig_order else "S2"
    orig_collector = orig_order.get("collector_id") if orig_order else None
    orig_assigned = orig_order.get("assigned_saleng_id") if orig_order else None
    orig_version = orig_order.get("version") if orig_order else 1

    if "order-s2-02" in supabase_store.orders:
        supabase_store.orders["order-s2-02"]["status"] = "S2"
        supabase_store.orders["order-s2-02"]["collector_id"] = None
        supabase_store.orders["order-s2-02"]["assigned_saleng_id"] = None
        supabase_store.orders["order-s2-02"]["version"] = 1

    yield

    if "order-s2-02" in supabase_store.orders:
        supabase_store.orders["order-s2-02"]["status"] = orig_status
        supabase_store.orders["order-s2-02"]["collector_id"] = orig_collector
        supabase_store.orders["order-s2-02"]["assigned_saleng_id"] = orig_assigned
        supabase_store.orders["order-s2-02"]["version"] = orig_version


def test_AC_B04_03_address_unmasking_and_navigation_url():
    """
    Given: คำขอขาย order-s2-02
    When: ซาเล้ง saleng-01 กดรับงานสำเร็จเข้าสู่สถานะ S3
    Then: ระบบเปิดเผยบ้านเลขที่จริง "88 ซอยรัชดาภิเษก 32", พิกัดจริง 13.8010, 100.5720 และเบอร์โทรผู้ขาย (REQ-SEC-002, D-00-02)
    And: ระบบสร้าง navigation_url ไปยัง Google Maps ตาม D-B04-03
    """
    res = client.post(
        "/api/v1/collectors/jobs/order-s2-02/claim",
        json={"saleng_id": "saleng-01", "expected_version": 1},
    )
    assert res.status_code == 200
    data = res.json()

    assert data["order_id"] == "order-s2-02"
    assert data["status"] == "S3"
    assert data["collector_id"] == "saleng-01"

    # ตรวจสอบว่าที่อยู่จริงและพิกัดจริงเปิดเผยอย่างถูกต้อง
    assert "88 ซอยรัชดาภิเษก 32" in data["address_text"]
    assert data["dest_lat"] == 13.8010
    assert data["dest_lng"] == 100.5720
    assert data["seller_phone"] != ""

    # ตรวจสอบลิงก์ Google Maps Navigation
    expected_nav_prefix = "https://www.google.com/maps/dir/?api=1&destination=13.801000,100.572000"
    assert data["navigation_url"].startswith(expected_nav_prefix)
    assert "travelmode=driving" in data["navigation_url"]

