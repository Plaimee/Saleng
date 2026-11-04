"""
Acceptance Tests for AC-B03-01: Distance & Fuel Cost Estimation
(Task T-02: UC-04, Card 02, REQ-FN-002, REQ-QA-002, AC-04-11, D-B03-01)
"""

import time
from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


def test_AC_B03_01_evaluate_job_fuel_cost_motorcycle():
    """
    Given: ซาเล้งขับรถซาเล้งมอเตอร์ไซค์พ่วงข้าง (MOTORCYCLE: อัตรา 2.50 บาท/กม.)
    When: เปิดดูรายละเอียดคำขอขาย order-s2-01
    Then: ระบบแสดงระยะทางถนนจริงและค่าน้ำมันโดยประมาณถูกต้อง (road_distance_km * 2.50)
    And: เวลาตอบสนองต้องไม่เกิน 3.0 วินาที (REQ-QA-002)
    """
    # กำหนดให้ saleng-01 ใช้รถ MOTORCYCLE
    saleng_id = "saleng-01"
    profile = supabase_store.saleng_profiles.get(saleng_id)
    assert profile is not None
    original_vtype = profile.get("vehicle_type")
    profile["vehicle_type"] = "MOTORCYCLE"

    try:
        start_time = time.time()
        resp = client.get(
            f"/api/v1/collectors/jobs/order-s2-01/evaluate",
            params={"saleng_id": saleng_id, "saleng_lat": 13.7900, "saleng_lng": 100.5750},
        )
        elapsed = time.time() - start_time

        assert resp.status_code == 200, f"Got {resp.status_code}: {resp.text}"
        assert elapsed <= 3.0, f"Evaluation response time {elapsed:.3f}s exceeded 3.0s threshold"

        data = resp.json()
        assert data["order_id"] == "order-s2-01"
        assert data["vehicle_type"] == "MOTORCYCLE"
        assert data["fuel_rate_per_km"] == 2.50

        # ค่าน้ำมันต้องตรงตามสูตร round(dist * 2.50, 2)
        dist = data["road_distance_km"]
        expected_fuel = round(dist * 2.50, 2)
        assert data["estimated_fuel_cost"] == expected_fuel
        assert data["estimated_fuel_cost"] > 0

        # ตรวจสอบรายการสิ่งของและรูปถ่าย
        assert len(data["items"]) >= 1
        assert data["total_est_weight_kg"] > 0
        assert data["subdistrict_name"] == "แขวงสามเสนนอก"
    finally:
        profile["vehicle_type"] = original_vtype


def test_AC_B03_01_evaluate_job_fuel_cost_tricycle_and_pickup():
    """
    ทดสอบการคำนวณค่าน้ำมันสำหรับรถซาเล้งปั่น (TRICYCLE = 0 บ.) และรถกระบะ (PICKUP = 4.50 บ./กม.) (D-B03-01)
    """
    saleng_id = "saleng-01"
    profile = supabase_store.saleng_profiles.get(saleng_id)
    assert profile is not None
    original_vtype = profile.get("vehicle_type")

    try:
        # 1. ทดสอบ TRICYCLE (รถปั่น ค่าน้ำมันต้องเป็น 0)
        profile["vehicle_type"] = "TRICYCLE"
        resp_tri = client.get(
            f"/api/v1/collectors/jobs/order-s2-01/evaluate",
            params={"saleng_id": saleng_id, "saleng_lat": 13.7900, "saleng_lng": 100.5750},
        )
        assert resp_tri.status_code == 200
        data_tri = resp_tri.json()
        assert data_tri["vehicle_type"] == "TRICYCLE"
        assert data_tri["fuel_rate_per_km"] == 0.00
        assert data_tri["estimated_fuel_cost"] == 0.00

        # 2. ทดสอบ PICKUP (รถกระบะ อัตรา 4.50 บาท/กม.)
        profile["vehicle_type"] = "PICKUP"
        resp_pick = client.get(
            f"/api/v1/collectors/jobs/order-s2-01/evaluate",
            params={"saleng_id": saleng_id, "saleng_lat": 13.7900, "saleng_lng": 100.5750},
        )
        assert resp_pick.status_code == 200
        data_pick = resp_pick.json()
        assert data_pick["vehicle_type"] == "PICKUP"
        assert data_pick["fuel_rate_per_km"] == 4.50
        dist_pick = data_pick["road_distance_km"]
        assert data_pick["estimated_fuel_cost"] == round(dist_pick * 4.50, 2)
    finally:
        profile["vehicle_type"] = original_vtype

