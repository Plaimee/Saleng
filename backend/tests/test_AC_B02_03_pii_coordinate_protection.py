"""
Acceptance Tests for AC-B02-03: PDPA PII & Coordinate Protection
(Task T-04: UC-04, REQ-SEC-002, D-00-02, CC-06, Q-01)
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


def test_AC_B02_03_pii_and_exact_coordinate_masking_in_nearby_api():
    """
    Given: คำขอขายยังอยู่ในสถานะ S2 (ยังไม่มีซาเล้งรับงาน)
    When: ซาเล้งเรียก GET /api/v1/collectors/jobs/nearby
    Then: ใน Payload จะต้องไม่มี address_text, บ้านเลขที่, เบอร์โทรศัพท์, หรือพิกัดจริงของผู้ขาย
    And: พิกัดบนแผนที่ต้องเป็น Fuzzed Coordinates (เบี่ยงเบนสุ่ม 300–500 ม.)
    And: ระบุพื้นที่เฉพาะระดับแขวง/ตำบล และเขต/อำเภอ
    """
    resp = client.get(
        "/api/v1/collectors/jobs/nearby",
        params={"saleng_lat": 13.7900, "saleng_lng": 100.5750, "radius_km": 5.0},
    )
    assert resp.status_code == 200
    data = resp.json()
    jobs = data["jobs"]

    for job in jobs:
        order_id = job["order_id"]
        # ตรวจสอบว่าไม่มีฟิลด์ PII ใด ๆ หลุดออกมาใน response
        assert "address_text" not in job
        assert "house_number" not in job
        assert "phone" not in job
        assert "seller_phone" not in job
        assert "real_lat" not in job
        assert "real_lng" not in job

        # ตรวจสอบชื่อพื้นที่ระดับตำบล/อำเภอ
        assert job["subdistrict_name"].startswith("แขวง") or job["subdistrict_name"].startswith("ตำบล")
        assert job["district_name"].startswith("เขต") or job["district_name"].startswith("อำเภอ")

        # ตรวจสอบการ Fuzzing พิกัดเทียบกับพิกัดจริงในฐานข้อมูล
        order_db = supabase_store.get_order(order_id)
        assert order_db is not None
        loc_db = supabase_store.get_pickup_location(order_db["location_id"])
        assert loc_db is not None

        real_lat = loc_db["lat"]
        real_lng = loc_db["lng"]
        fuzzed_lat = job["approximate_lat"]
        fuzzed_lng = job["approximate_lng"]

        # พิกัดต้องไม่ตรงกับพิกัดจริง
        assert (fuzzed_lat, fuzzed_lng) != (real_lat, real_lng)

        # ระยะห่างต้องอยู่ในช่วง 300 ถึง 500 เมตร (ยอมรับ tolerance เล็กน้อยจากการปัดเศษ)
        distance_m = haversine_m(real_lat, real_lng, fuzzed_lat, fuzzed_lng)
        assert 295.0 <= distance_m <= 505.0, (
            f"Fuzzed coordinate offset {distance_m:.1f}m for {order_id} is out of 300-500m bounds"
        )


def test_AC_B02_03_pii_masking_in_job_summary_api():
    """
    Given: คำขอขาย order-s2-01 อยู่ในสถานะ S2
    When: ซาเล้งเรียกดูสรุปคำขอ GET /api/v1/collectors/jobs/order-s2-01/summary
    Then: ข้อมูลสรุปต้องไม่มี PII (บ้านเลขที่, เบอร์โทร) และพิกัดต้องผ่าน Fuzzing
    """
    resp = client.get(
        "/api/v1/collectors/jobs/order-s2-01/summary",
        params={"saleng_lat": 13.7900, "saleng_lng": 100.5750},
    )
    assert resp.status_code == 200
    summary = resp.json()

    assert summary["order_id"] == "order-s2-01"
    assert "address_text" not in summary
    assert "phone" not in summary
    assert summary["subdistrict_name"] == "แขวงสามเสนนอก"
    assert summary["district_name"] == "เขตห้วยขวาง"
    assert summary["approximate_lat"] != 13.7930
    assert summary["approximate_lng"] != 100.5780

