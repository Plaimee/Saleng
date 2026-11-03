"""
Unit Tests for Buyer Job Search Models, Coordinate Fuzzing & Supabase Store Extension
(Task T-01: UC-04, MD-DOM-04, REQ-SEC-002, D-00-02, P-01)
"""

import math
import pytest
from pydantic import ValidationError
from backend.app.models.job_search_models import (
    fuzz_coordinates,
    JobSearchQueryParams,
    NearbyJobSummaryResponse,
    NearbyJobListResponse,
    SimulateOrderRequest,
)
from backend.app.core.supabase import supabase_store


def haversine_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """คำนวณระยะห่างทางภูมิศาสตร์เป็นเมตร"""
    r = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lng2 - lng1)
    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r * c


def test_T01_fuzz_coordinates_offset_bounds():
    """ตรวจสอบว่าการ Fuzzing พิกัดสร้างระยะคลาดเคลื่อนสุ่มระหว่าง 300 ถึง 500 เมตร (REQ-SEC-002, D-00-02)"""
    lat, lng = 13.7930, 100.5780
    seeds = ["order-01", "order-02", "order-xyz", "sample-seed-test-123"]

    for seed in seeds:
        fuzzed_lat, fuzzed_lng = fuzz_coordinates(lat, lng, seed=seed)
        dist = haversine_m(lat, lng, fuzzed_lat, fuzzed_lng)
        # ตรวจสอบว่าระยะห่างอยู่ในช่วง 295 ถึง 505 เมตร (รวม rounding tolerance)
        assert 295.0 <= dist <= 505.0, f"Distance {dist}m not in 300-500m for seed {seed}"
        assert (fuzzed_lat, fuzzed_lng) != (lat, lng)


def test_T01_fuzz_coordinates_determinism():
    """ตรวจสอบว่าการ Fuzzing ให้ผลคงที่เมื่อใช้ seed เดียวกัน (Deterministic Fuzzing)"""
    lat, lng = 13.7930, 100.5780
    seed = "order-fixed-seed-test"

    res1 = fuzz_coordinates(lat, lng, seed=seed)
    res2 = fuzz_coordinates(lat, lng, seed=seed)
    assert res1 == res2, "Same seed must produce exactly identical fuzzed coordinates"

    res_diff = fuzz_coordinates(lat, lng, seed="different-seed")
    assert res1 != res_diff, "Different seeds should produce different coordinates"


def test_T01_job_search_query_params_validation():
    """ตรวจสอบการตรวจสอบความถูกต้องของพารามิเตอร์การค้นหา (JobSearchQueryParams)"""
    valid = JobSearchQueryParams(
        saleng_lat=13.7900,
        saleng_lng=100.5750,
        radius_km=5.0,
        category="MAT-CARDBOARD",
        weight_range="MEDIUM",
        sort_by="DISTANCE",
    )
    assert valid.saleng_lat == 13.7900
    assert valid.radius_km == 5.0

    # พิกัด Lat นอกช่วง -90 ถึง 90
    with pytest.raises(ValidationError):
        JobSearchQueryParams(saleng_lat=95.0, saleng_lng=100.0)

    # พิกัด Lng นอกช่วง -180 ถึง 180
    with pytest.raises(ValidationError):
        JobSearchQueryParams(saleng_lat=13.0, saleng_lng=190.0)


def test_T01_nearby_job_summary_privacy_protection():
    """ตรวจสอบว่า Response Schema ไม่มี address_text หรือเบอร์โทรศัพท์ (REQ-SEC-002, CC-06)"""
    summary = NearbyJobSummaryResponse(
        order_id="order-s2-01",
        status="S2",
        subdistrict_name="แขวงสามเสนนอก",
        district_name="เขตห้วยขวาง",
        approximate_lat=13.7950,
        approximate_lng=100.5810,
        road_distance_km=0.85,
        estimated_price_min=150.0,
        estimated_price_max=220.0,
        estimated_weight_kg=25.0,
        categories=["MAT-CARDBOARD", "MAT-ALU-CAN"],
        item_count=2,
        need_lifting_help=False,
        is_fallback_distance=False,
        created_at="2026-11-04T02:30:00Z",
    )

    data = summary.model_dump()
    assert "address_text" not in data, "address_text must be stripped from response"
    assert "phone" not in data, "phone must be stripped from response"
    assert "seller_phone" not in data, "seller_phone must be stripped from response"
    assert data["order_id"] == "order-s2-01"
    assert data["approximate_lat"] == 13.7950


def test_T01_supabase_store_open_orders_s2():
    """ตรวจสอบการดึงและสร้างคำขอขายสถานะ S2 จาก SupabaseStore (UC-04, P-01)"""
    open_orders = supabase_store.get_open_orders_s2()
    assert len(open_orders) >= 4, f"Expected at least 4 seeded S2 orders, found {len(open_orders)}"

    seeded_s2_ids = {"order-s2-01", "order-s2-02", "order-s2-03", "order-s2-04"}
    seeded_orders = [o for o in open_orders if o.get("order_id") in seeded_s2_ids]
    assert len(seeded_orders) == 4, f"Expected 4 seeded orders, found {len(seeded_orders)}"

    for order in seeded_orders:
        assert order.get("status") in ("S2", "PENDING")
        assert order.get("assigned_saleng_id") is None
        assert "items" in order
        assert len(order["items"]) >= 1

    # ทดสอบการเพิ่มคำขอขายจำลอง
    sim_order = supabase_store.add_simulated_order(
        order_data={
            "seller_id": "seller-sim-test",
            "total_est_min_price": 200.0,
            "total_est_max_price": 280.0,
            "total_est_weight_kg": 35.0,
            "categories": ["MAT-CARDBOARD"],
        },
        location_data={
            "seller_id": "seller-sim-test",
            "address_text": "999 ซอยวิภาวดี 20",
            "subdistrict": "แขวงจอมพล",
            "district": "เขตจตุจักร",
            "lat": 13.8050,
            "lng": 100.5600,
        },
    )
    assert sim_order["order_id"] is not None
    assert sim_order["status"] == "S2"

    # ตรวจสอบ Audit Log
    log = supabase_store.record_audit_log(
        action="JOB_SEARCH_QUERY",
        actor_id="saleng-01",
        actor_role="COLLECTOR",
        details={"radius_km": 5.0, "saleng_lat": 13.7900, "saleng_lng": 100.5750},
    )
    assert log["log_id"] is not None
    assert log["action"] == "JOB_SEARCH_QUERY"
