"""
Acceptance Tests for AC-B03-04 & AC-B03-05: PDPA PII Masking & KYC Gate in Evaluation
(Task T-05: UC-04, REQ-SEC-002, D-00-01, D-00-02, CC-06, AC-B03-04, AC-B03-05)
"""

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


def test_AC_B03_04_pii_and_coordinate_masking_in_evaluation():
    """
    Given: คำขอขายยังอยู่ในสถานะ S2 (ยังไม่มีผู้รับงาน)
    When: ซาเล้งเปิดดูรายละเอียดคำขอขาย (GET /api/v1/collectors/jobs/{order_id}/evaluate)
    Then: ใน Payload ต้องไม่มีบ้านเลขที่ เบอร์โทรศัพท์เต็ม หรือพิกัดจริงของผู้ขายเด็ดขาด (REQ-SEC-002, D-00-02)
    And: พิกัดต้องเป็น Fuzzed Coordinates (เบี่ยงเบนสุ่ม 300–500 ม.)
    And: ระบุพื้นที่เฉพาะระดับตำบล/แขวง และอำเภอ/เขต
    """
    resp = client.get("/api/v1/collectors/jobs/order-s2-01/evaluate?saleng_id=saleng-01")
    assert resp.status_code == 200
    data = resp.json()

    # 1. ตรวจสอบว่าไม่มีฟิลด์ PII หลุดออกมา
    assert "address_text" not in data
    assert "house_number" not in data
    assert "phone" not in data
    assert "seller_phone" not in data
    assert "real_lat" not in data
    assert "real_lng" not in data

    # 2. ตรวจสอบชื่อพื้นที่
    assert data["subdistrict_name"] == "แขวงสามเสนนอก"
    assert data["district_name"] == "เขตห้วยขวาง"

    # 3. ตรวจสอบระยะห่างการ Fuzzing พิกัด
    order_db = supabase_store.get_order("order-s2-01")
    loc_db = supabase_store.get_pickup_location(order_db["location_id"])
    real_lat = loc_db["lat"]
    real_lng = loc_db["lng"]
    approx_lat = data["approximate_lat"]
    approx_lng = data["approximate_lng"]

    assert (approx_lat, approx_lng) != (real_lat, real_lng)
    dist_m = haversine_m(real_lat, real_lng, approx_lat, approx_lng)
    assert 295.0 <= dist_m <= 505.0, f"Offset {dist_m:.1f}m is out of 300-500m bounds"


def test_AC_B03_05_unverified_collector_kyc_gate_blocked():
    """
    Given: ซาเล้งยังไม่ผ่านการอนุมัติ KYC (verified = False หรือ kyc_status != 'VERIFIED') (D-00-01)
    When: ซาเล้งเปิดดูรายละเอียดคำขอขาย
    Then: ระบบอนุญาตให้ดูรายละเอียด ขนาด รูปถ่าย และค่าน้ำมันได้
    And: แต่ can_claim_job = False และ claim_block_reason = 'UNVERIFIED_KYC'
    """
    saleng_unverified = "saleng-unverified-test"
    supabase_store.saleng_profiles[saleng_unverified] = {
        "saleng_id": saleng_unverified,
        "display_name": "ซาเล้งรอตรวจ KYC",
        "verified": False,
        "kyc_status": "PENDING_REVIEW",
        "vehicle_type": "MOTORCYCLE",
        "max_capacity_kg": 200.0,
        "is_online": True,
        "current_lat": 13.7900,
        "current_lng": 100.5750,
    }

    try:
        resp = client.get(f"/api/v1/collectors/jobs/order-s2-01/evaluate?saleng_id={saleng_unverified}")
        assert resp.status_code == 200
        data = resp.json()

        # ดูรายละเอียดและค่าน้ำมันได้
        assert data["order_id"] == "order-s2-01"
        assert data["estimated_fuel_cost"] > 0
        assert len(data["items"]) >= 1

        # แต่ล็อกปุ่มรับงาน
        assert data["collector_is_verified"] is False
        assert data["can_claim_job"] is False
        assert data["claim_block_reason"] == "UNVERIFIED_KYC"
    finally:
        if saleng_unverified in supabase_store.saleng_profiles:
            del supabase_store.saleng_profiles[saleng_unverified]

