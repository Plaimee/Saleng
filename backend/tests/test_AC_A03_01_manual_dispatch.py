"""
Test Suite for AC-A03-01: Stalled Pending Orders Queue & Manual Dispatch Fallback
รองรับ UC-13, D-A03-02, D-A03-03, D-00-01, REQ-OP-001, CC-03, CC-06
"""

import time
import pytest
from datetime import datetime, timezone, timedelta
from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)
ADMIN_HEADER = {"X-Admin-Role": "ADMIN"}


@pytest.fixture(autouse=True)
def setup_teardown_dispatch_data():
    """เตรียมข้อมูลและคืนค่าเดิมหลังทดสอบ"""
    created_orders = []
    created_disputes = []
    yield {"orders": created_orders, "disputes": created_disputes}
    for oid in created_orders:
        supabase_store.orders.pop(oid, None)
        supabase_store.items.pop(f"item-{oid}", None)
        supabase_store.pickup_locations.pop(f"loc-{oid}", None)


def test_AC_A03_01_list_stalled_orders(setup_teardown_dispatch_data):
    """
    AC-A03-01: แอดมินเรียกดูคิวคำขอนัดหมาย S2 ที่ตกค้างเกิน 30 นาที
    - ต้องคำนวณ waiting_minutes ถูกต้อง
    - ต้องแสดงตำบล/แขวง และซ่อนพิกัดละเอียดตาม CC-06
    - เวลาตอบสนองต้องน้อยกว่า 2.0 วินาที (REQ-OP-001)
    """
    # สร้าง Order ตกค้าง 50 นาที
    order_id = "test-order-stalled-50min"
    setup_teardown_dispatch_data["orders"].append(order_id)
    now = datetime.now(timezone.utc)
    t_50min_ago = (now - timedelta(minutes=50)).isoformat()

    supabase_store.pickup_locations[f"loc-{order_id}"] = {
        "location_id": f"loc-{order_id}",
        "seller_id": "seller-01",
        "subdistrict": "แขวงสามเสนนอก",
        "district": "เขตห้วยขวาง",
        "province": "กรุงเทพมหานคร",
        "lat": 13.7900,
        "lng": 100.5750,
    }
    supabase_store.orders[order_id] = {
        "order_id": order_id,
        "seller_id": "seller-01",
        "location_id": f"loc-{order_id}",
        "status": "S2",
        "total_est_min_price": 250.0,
        "total_est_max_price": 380.0,
        "total_est_weight_kg": 35.0,
        "search_radius_km": 5.0,
        "created_at": t_50min_ago,
        "version": 1,
    }

    start_t = time.time()
    resp = client.get("/api/v1/admin/dispatch/stalled-orders?min_wait_minutes=30", headers=ADMIN_HEADER)
    latency = time.time() - start_t

    assert latency < 2.0, f"Latency {latency}s exceeds 2.0s SLO (REQ-OP-001)"
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    item = next((o for o in data if o["order_id"] == order_id), None)
    assert item is not None
    assert item["status"] == "S2"
    assert item["waiting_minutes"] >= 49.0
    assert item["subdistrict"] == "แขวงสามเสนนอก"
    assert item["district"] == "เขตห้วยขวาง"


def test_AC_A03_01_manual_direct_assign(setup_teardown_dispatch_data):
    """
    AC-A03-01: แอดมินมอบหมายงานตรง (Direct Assign) ให้ซาเล้งออนไลน์ที่ผ่าน KYC
    - คำขอเปลี่ยนสถานะจาก S2 เป็น S3 (Assigned)
    - กำกับ is_manual_dispatched = True และ dispatched_by = admin_id
    """
    order_id = "test-order-direct-assign"
    setup_teardown_dispatch_data["orders"].append(order_id)
    now = datetime.now(timezone.utc)
    t_35min_ago = (now - timedelta(minutes=35)).isoformat()

    supabase_store.orders[order_id] = {
        "order_id": order_id,
        "seller_id": "seller-01",
        "status": "S2",
        "total_est_min_price": 180.0,
        "total_est_max_price": 260.0,
        "created_at": t_35min_ago,
        "version": 1,
    }

    payload = {
        "order_id": order_id,
        "saleng_id": "saleng-01",
        "admin_id": "admin-01",
        "notes": "มอบหมายงานตรงผ่านศูนย์ควบคุม",
    }
    resp = client.post("/api/v1/admin/dispatch/assign", json=payload, headers=ADMIN_HEADER)
    assert resp.status_code == 200
    res_data = resp.json()
    assert res_data["success"] is True
    assert res_data["order_id"] == order_id
    assert res_data["status"] == "S3"
    assert res_data["assigned_saleng_id"] == "saleng-01"

    # ตรวจสอบใน Store
    stored_order = supabase_store.orders[order_id]
    assert stored_order["status"] == "S3"
    assert stored_order["assigned_saleng_id"] == "saleng-01"
    assert stored_order["is_manual_dispatched"] is True
    assert stored_order["dispatched_by"] == "admin-01"


def test_AC_A03_01_direct_assign_precondition_unverified_saleng(setup_teardown_dispatch_data):
    """
    AC-A03-01 / D-00-01: มอบหมายงานให้ซาเล้งที่ไม่ผ่าน KYC ต้องถูกปฏิเสธ (400 Bad Request)
    """
    order_id = "test-order-unverified-assign"
    setup_teardown_dispatch_data["orders"].append(order_id)
    now = datetime.now(timezone.utc).isoformat()

    supabase_store.orders[order_id] = {
        "order_id": order_id,
        "seller_id": "seller-01",
        "status": "S2",
        "created_at": now,
        "version": 1,
    }

    # สร้าง ซาเล้งชั่วคราวที่ไม่ผ่าน KYC
    unverified_id = "saleng-unverified-test"
    supabase_store.saleng_profiles[unverified_id] = {
        "saleng_id": unverified_id,
        "display_name": "ซาเล้งรอ KYC",
        "verified": False,
        "is_online": True,
    }

    try:
        payload = {
            "order_id": order_id,
            "saleng_id": unverified_id,
        }
        resp = client.post("/api/v1/admin/dispatch/assign", json=payload, headers=ADMIN_HEADER)
        assert resp.status_code == 400
        assert "ยังไม่ผ่านการยืนยันตัวตน KYC" in resp.json()["detail"]
    finally:
        supabase_store.saleng_profiles.pop(unverified_id, None)


def test_AC_A03_01_expand_search_radius(setup_teardown_dispatch_data):
    """
    AC-A03-01: แอดมินกดขยายรัศมีการค้นหาเป็น 10.0 กม.
    - รัศมีในออเดอร์เปลี่ยนเป็น 10.0 กม.
    - บันทึก Audit Log ADMIN_EXPAND_DISPATCH_RADIUS
    """
    order_id = "test-order-expand-radius"
    setup_teardown_dispatch_data["orders"].append(order_id)
    now = datetime.now(timezone.utc).isoformat()

    supabase_store.orders[order_id] = {
        "order_id": order_id,
        "seller_id": "seller-01",
        "status": "S2",
        "search_radius_km": 5.0,
        "created_at": now,
        "version": 1,
    }

    payload = {
        "order_id": order_id,
        "new_radius_km": 10.0,
        "admin_id": "admin-01",
    }
    resp = client.post("/api/v1/admin/dispatch/expand-radius", json=payload, headers=ADMIN_HEADER)
    assert resp.status_code == 200
    res_data = resp.json()
    assert res_data["success"] is True
    assert res_data["new_radius_km"] == 10.0

    stored = supabase_store.orders[order_id]
    assert stored["search_radius_km"] == 10.0

    # ตรวจสอบ Audit Log
    audit = next((a for a in supabase_store.audit_logs if a.get("action") == "ADMIN_EXPAND_DISPATCH_RADIUS" and a.get("entity_id") == order_id), None)
    assert audit is not None
    assert audit["details"]["new_radius_km"] == 10.0

