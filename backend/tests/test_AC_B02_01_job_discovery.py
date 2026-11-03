"""
Acceptance Tests for AC-B02-01: Job Discovery in 5.0 km Radius within 3.0s
(Task T-02: UC-04, REQ-FN-002, REQ-QA-002, CC-03, P-01)
"""

import time
import pytest
from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.services.job_search_service import DualEngineRoutingService

client = TestClient(app)


def test_AC_B02_01_job_discovery_radius_and_performance():
    """
    Given: ซาเล้งเปิด GPS ที่พิกัด 13.7900, 100.5750 และมีคำขอขายสถานะ S2 ในและนอกรัศมี 5.0 กม.
    When: ซาเล้งค้นหางานใกล้เคียงด้วยรัศมี 5.0 กม.
    Then: ระบบแสดงเฉพาะงานที่อยู่ในรัศมีถนน <= 5.0 กม. เท่านั้น ครบถ้วน 100%
    And: เวลาตอบสนองต้องไม่เกิน 3.0 วินาที (REQ-QA-002)
    """
    saleng_lat = 13.7900
    saleng_lng = 100.5750

    start_time = time.time()
    response = client.get(
        "/api/v1/collectors/jobs/nearby",
        params={
            "saleng_lat": saleng_lat,
            "saleng_lng": saleng_lng,
            "radius_km": 5.0,
        },
    )
    elapsed = time.time() - start_time

    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    # REQ-QA-002: การตอบสนอง <= 3.0 วินาที
    assert elapsed <= 3.0, f"Response time {elapsed:.3f}s exceeded 3.0s SLO threshold"

    data = response.json()
    assert "jobs" in data
    assert data["radius_km"] == 5.0
    jobs = data["jobs"]

    # ต้องพบคำขอขายในรัศมี 5.0 กม. (order-s2-01, order-s2-02, order-s2-03)
    assert len(jobs) >= 3, f"Expected at least 3 jobs within 5km, got {len(jobs)}"

    returned_ids = [j["order_id"] for j in jobs]
    assert "order-s2-01" in returned_ids
    assert "order-s2-02" in returned_ids
    assert "order-s2-03" in returned_ids
    # order-s2-04 อยู่ที่ 7.5 กม. ต้องไม่อยู่ในผลลัพธ์รัศมี 5.0 กม.
    assert "order-s2-04" not in returned_ids

    # ตรวจสอบฟิลด์ข้อมูลที่แสดงบนการ์ดงาน
    for job in jobs:
        assert job["road_distance_km"] <= 5.0
        assert job["status"] == "S2"
        assert len(job["subdistrict_name"]) > 0
        assert len(job["district_name"]) > 0
        assert job["estimated_price_min"] > 0
        assert job["estimated_price_max"] >= job["estimated_price_min"]
        assert len(job["categories"]) > 0
        assert job["approximate_lat"] != 0.0
        assert job["approximate_lng"] != 0.0


def test_AC_B02_01_dual_engine_routing_fallback():
    """
    ทดสอบระบบสำรอง Dual-Engine Routing Fallback (CC-03, REQ-OP-002)
    เมื่อเปิด force_fallback ระบบจะใช้ Haversine * 1.35 อัตโนมัติและส่ง flag is_fallback_distance=True
    """
    saleng_lat = 13.7900
    saleng_lng = 100.5750

    start_time = time.time()
    response = client.get(
        "/api/v1/collectors/jobs/nearby",
        params={
            "saleng_lat": saleng_lat,
            "saleng_lng": saleng_lng,
            "radius_km": 5.0,
            "force_fallback": True,
        },
    )
    elapsed = time.time() - start_time

    assert response.status_code == 200
    assert elapsed <= 2.0, f"Fallback response time {elapsed:.3f}s exceeded 2.0s"

    data = response.json()
    jobs = data["jobs"]
    assert len(jobs) >= 3
    for job in jobs:
        assert job["is_fallback_distance"] is True

    # ตรวจสอบการคำนวณของ DualEngineRoutingService โดยตรง
    dist, is_fallback = DualEngineRoutingService.calculate_distance(
        13.7900, 100.5750, 13.7930, 100.5780, force_fallback=True
    )
    assert is_fallback is True
    assert dist > 0.0

