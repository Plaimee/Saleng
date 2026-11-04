"""
Acceptance Tests for AC-B03-02: Dual-Engine Routing Fallback & Timeout Handling
(Task T-03: UC-04, CC-03, REQ-OP-002, AC-04-10, E3, D-B03-02)
"""

import time
from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app

client = TestClient(app)


def test_AC_B03_02_dual_engine_routing_fallback_performance():
    """
    Given: บริการแผนที่ภายนอก (Maps API) ล้มเหลวหรือช้าเกิน 1.5 วินาที (จำลองด้วย force_fallback=True)
    When: ซาเล้งเปิดดูรายละเอียดคำขอขาย
    Then: ระบบสลับไปใช้สูตรสำรอง Haversine * 1.35 อัตโนมัติทันที
    And: เวลาตอบสนองต้องเสร็จสิ้นภายใน <= 2.0 วินาที (REQ-OP-002, CC-03)
    And: ข้อมูลส่งกลับมี Flag is_fallback_distance = True และค่าน้ำมันถูกคำนวณจากระยะทางสำรอง
    """
    start_time = time.time()
    resp = client.get(
        "/api/v1/collectors/jobs/order-s2-01/evaluate",
        params={
            "saleng_id": "saleng-01",
            "saleng_lat": 13.7900,
            "saleng_lng": 100.5750,
            "force_fallback": True,
        },
    )
    elapsed = time.time() - start_time

    assert resp.status_code == 200, f"Got {resp.status_code}: {resp.text}"
    # REQ-OP-002: การตอบสนองโหมดสำรองต้อง <= 2.0 วินาที
    assert elapsed <= 2.0, f"Fallback evaluation time {elapsed:.3f}s exceeded 2.0s SLO threshold"

    data = resp.json()
    assert data["order_id"] == "order-s2-01"
    assert data["is_fallback_distance"] is True
    assert data["road_distance_km"] > 0

    # ค่าน้ำมันต้องคำนวณจากระยะทางสำรอง
    expected_fuel = round(data["road_distance_km"] * data["fuel_rate_per_km"], 2)
    assert data["estimated_fuel_cost"] == expected_fuel

