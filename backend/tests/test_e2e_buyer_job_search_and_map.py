"""
Integration E2E Test Suite for Buyer Job Search & Map View Lifecycle
(UC-04: ค้นหาและแสดงงานรับซื้อตามพิกัด, REQ-FN-002, REQ-QA-002, REQ-SEC-002, REQ-OP-002, CC-01..06, D-00-01, D-00-02, P-01..P-06)
"""

import time
import math
from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


def haversine_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    r = 6371000.0
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


def test_e2e_buyer_job_search_and_map_complete_lifecycle():
    """
    ทดสอบครบวงจรระบบค้นหาและแสดงงานรับซื้อของซาเล้ง (UC-04):
    1. ซาเล้งส่งพิกัด GPS ค้นหางานในรัศมี 5.0 กม. -> ตอบกลับภายใน <= 3.0s (REQ-QA-002)
    2. ทดสอบการขยายรัศมีเป็น 10.0 กม. เพื่อค้นพบงานระยะไกล (order-s2-04) (AC-B02-02)
    3. ตรวจสอบการป้องกันข้อมูลส่วนบุคคล PII & Coordinate Fuzzing (D-00-02, CC-06)
    4. ทดสอบตัวกรองหมวดหมู่, ช่วงน้ำหนัก และการจัดเรียงลำดับ (AC-B02-05)
    5. จำลองคำขอขายใหม่ในพื้นที่ และตรวจสอบการตรวจจับงานใหม่สำหรับ Live Alert (Q-02)
    6. ทดสอบระบบสำรอง Dual-Engine Routing Fallback (CC-03, REQ-OP-002)
    7. ตรวจสอบบันทึก Audit Log ครบถ้วน (REQ-SEC-001)
    """
    saleng_lat = 13.7900
    saleng_lng = 100.5750

    # -------------------------------------------------------------------------
    # 1. ซาเล้งส่งพิกัด GPS ค้นหางานรัศมี 5.0 กม.
    # -------------------------------------------------------------------------
    start_time = time.time()
    resp_5km = client.get(
        "/api/v1/collectors/jobs/nearby",
        params={
            "saleng_lat": saleng_lat,
            "saleng_lng": saleng_lng,
            "radius_km": 5.0,
        },
    )
    elapsed_5km = time.time() - start_time

    assert resp_5km.status_code == 200
    assert elapsed_5km <= 3.0, f"Response time {elapsed_5km}s exceeded 3.0s threshold"

    data_5km = resp_5km.json()
    assert data_5km["radius_km"] == 5.0
    jobs_5km = data_5km["jobs"]
    assert len(jobs_5km) >= 3

    job_ids_5km = [j["order_id"] for j in jobs_5km]
    assert "order-s2-01" in job_ids_5km
    assert "order-s2-02" in job_ids_5km
    assert "order-s2-03" in job_ids_5km
    assert "order-s2-04" not in job_ids_5km

    # -------------------------------------------------------------------------
    # 2. ทดสอบการขยายรัศมีเป็น 10.0 กม.
    # -------------------------------------------------------------------------
    resp_10km = client.get(
        "/api/v1/collectors/jobs/nearby",
        params={
            "saleng_lat": saleng_lat,
            "saleng_lng": saleng_lng,
            "radius_km": 10.0,
        },
    )
    assert resp_10km.status_code == 200
    data_10km = resp_10km.json()
    job_ids_10km = [j["order_id"] for j in data_10km["jobs"]]
    assert "order-s2-04" in job_ids_10km

    # -------------------------------------------------------------------------
    # 3. ตรวจสอบการป้องกันข้อมูลส่วนบุคคล PII & Coordinate Fuzzing (D-00-02, CC-06)
    # -------------------------------------------------------------------------
    for job in jobs_5km:
        assert "address_text" not in job
        assert "phone" not in job
        assert "seller_phone" not in job

        order_db = supabase_store.get_order(job["order_id"])
        loc_db = supabase_store.get_pickup_location(order_db["location_id"])
        offset_m = haversine_m(loc_db["lat"], loc_db["lng"], job["approximate_lat"], job["approximate_lng"])
        assert 295.0 <= offset_m <= 505.0

    # ตรวจสอบ API Job Summary
    resp_sum = client.get(
        "/api/v1/collectors/jobs/order-s2-01/summary",
        params={"saleng_lat": saleng_lat, "saleng_lng": saleng_lng},
    )
    assert resp_sum.status_code == 200
    sum_data = resp_sum.json()
    assert "address_text" not in sum_data
    assert sum_data["subdistrict_name"] == "แขวงสามเสนนอก"
    assert sum_data["district_name"] == "เขตห้วยขวาง"

    # -------------------------------------------------------------------------
    # 4. ทดสอบตัวกรองและจัดเรียงลำดับ (AC-B02-05)
    # -------------------------------------------------------------------------
    # กรองเฉพาะหมวดหมู่ขวดพลาสติก PET
    resp_filter_cat = client.get(
        "/api/v1/collectors/jobs/nearby",
        params={
            "saleng_lat": saleng_lat,
            "saleng_lng": saleng_lng,
            "radius_km": 5.0,
            "category": "MAT-PET-BOTTLE",
        },
    )
    assert resp_filter_cat.status_code == 200
    pet_jobs = resp_filter_cat.json()["jobs"]
    assert len(pet_jobs) >= 1
    assert all("MAT-PET-BOTTLE" in j["categories"] for j in pet_jobs)

    # จัดเรียงตามราคาสูงสุด
    resp_sort_price = client.get(
        "/api/v1/collectors/jobs/nearby",
        params={
            "saleng_lat": saleng_lat,
            "saleng_lng": saleng_lng,
            "radius_km": 5.0,
            "sort_by": "PRICE_DESC",
        },
    )
    assert resp_sort_price.status_code == 200
    priced_jobs = resp_sort_price.json()["jobs"]
    assert priced_jobs[0]["estimated_price_max"] >= priced_jobs[-1]["estimated_price_max"]

    # -------------------------------------------------------------------------
    # 5. จำลองคำขอขายใหม่ในพื้นที่ (Live Alert Testing - Q-02)
    # -------------------------------------------------------------------------
    sim_resp = client.post(
        "/api/v1/collectors/jobs/simulate-new-order",
        json={
            "seller_id": "seller-e2e-sim",
            "lat": 13.7915,
            "lng": 100.5755,
            "subdistrict": "แขวงสามเสนนอก",
            "district": "เขตห้วยขวาง",
            "categories": ["MAT-ALU-CAN"],
            "estimated_weight_kg": 50.0,
            "estimated_price_min": 500.0,
            "estimated_price_max": 750.0,
            "need_lifting_help": False,
        },
    )
    assert sim_resp.status_code == 201
    sim_order_id = sim_resp.json()["order"]["order_id"]

    # ค้นหาอีกรอบต้องพบงานจำลองนี้
    resp_after_sim = client.get(
        "/api/v1/collectors/jobs/nearby",
        params={"saleng_lat": saleng_lat, "saleng_lng": saleng_lng, "radius_km": 5.0},
    )
    assert resp_after_sim.status_code == 200
    assert sim_order_id in [j["order_id"] for j in resp_after_sim.json()["jobs"]]

    # -------------------------------------------------------------------------
    # 6. ทดสอบระบบสำรอง Dual-Engine Routing Fallback (CC-03, REQ-OP-002)
    # -------------------------------------------------------------------------
    start_fallback = time.time()
    resp_fallback = client.get(
        "/api/v1/collectors/jobs/nearby",
        params={
            "saleng_lat": saleng_lat,
            "saleng_lng": saleng_lng,
            "radius_km": 5.0,
            "force_fallback": True,
        },
    )
    elapsed_fallback = time.time() - start_fallback

    assert resp_fallback.status_code == 200
    assert elapsed_fallback <= 2.0, "Fallback routing exceeded 2.0s SLO threshold"
    fallback_jobs = resp_fallback.json()["jobs"]
    for j in fallback_jobs:
        assert j["is_fallback_distance"] is True

    # -------------------------------------------------------------------------
    # 7. ตรวจสอบประวัติ Audit Log (REQ-SEC-001)
    # -------------------------------------------------------------------------
    search_logs = supabase_store.get_audit_logs("JOB_SEARCH_QUERY")
    assert len(search_logs) >= 5
    sim_logs = supabase_store.get_audit_logs("ORDER_SIMULATED")
    assert len(sim_logs) >= 1

