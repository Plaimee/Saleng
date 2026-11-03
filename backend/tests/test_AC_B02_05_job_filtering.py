"""
Acceptance Tests for AC-B02-05: Multi-Criteria Job Filtering & Simulation
(Task T-05: UC-04, REQ-FN-002, P-03, Q-02, Q-03)
"""

from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app

client = TestClient(app)


def test_AC_B02_05_category_filter():
    """
    ทดสอบตัวกรองหมวดหมู่วัสดุ:
    - เมื่อกรอง category=BULKY-APPLIANCE ต้องได้เฉพาะคำขอที่มีเครื่องใช้ไฟฟ้า/ของชิ้นใหญ่ (order-s2-03)
    - เมื่อกรอง category=MAT-PET-BOTTLE ต้องได้ order-s2-02
    """
    lat, lng = 13.7900, 100.5750

    # 1. กรอง BULKY-APPLIANCE
    resp_bulky = client.get(
        "/api/v1/collectors/jobs/nearby",
        params={"saleng_lat": lat, "saleng_lng": lng, "radius_km": 5.0, "category": "BULKY-APPLIANCE"},
    )
    assert resp_bulky.status_code == 200
    jobs_bulky = resp_bulky.json()["jobs"]
    assert len(jobs_bulky) >= 1
    for job in jobs_bulky:
        assert any("BULKY" in c for c in job["categories"])

    # 2. กรอง MAT-PET-BOTTLE
    resp_pet = client.get(
        "/api/v1/collectors/jobs/nearby",
        params={"saleng_lat": lat, "saleng_lng": lng, "radius_km": 5.0, "category": "MAT-PET-BOTTLE"},
    )
    assert resp_pet.status_code == 200
    jobs_pet = resp_pet.json()["jobs"]
    assert len(jobs_pet) >= 1
    for job in jobs_pet:
        assert any("PET" in c for c in job["categories"])


def test_AC_B02_05_weight_range_filter():
    """
    ทดสอบตัวกรองช่วงน้ำหนักประเมิน 4 ช่วง (ALL, SMALL, MEDIUM, LARGE):
    - SMALL (< 50 กก.): order-s2-01 (25 กก.)
    - MEDIUM (50–100 กก.): order-s2-02 (60 กก.)
    - LARGE (> 100 กก.): order-s2-03 (120 กก.)
    """
    lat, lng = 13.7900, 100.5750

    # SMALL
    resp_small = client.get(
        "/api/v1/collectors/jobs/nearby",
        params={"saleng_lat": lat, "saleng_lng": lng, "radius_km": 5.0, "weight_range": "SMALL"},
    )
    assert resp_small.status_code == 200
    for job in resp_small.json()["jobs"]:
        assert job["estimated_weight_kg"] < 50.0

    # MEDIUM
    resp_med = client.get(
        "/api/v1/collectors/jobs/nearby",
        params={"saleng_lat": lat, "saleng_lng": lng, "radius_km": 5.0, "weight_range": "MEDIUM"},
    )
    assert resp_med.status_code == 200
    for job in resp_med.json()["jobs"]:
        assert 50.0 <= job["estimated_weight_kg"] <= 100.0

    # LARGE
    resp_large = client.get(
        "/api/v1/collectors/jobs/nearby",
        params={"saleng_lat": lat, "saleng_lng": lng, "radius_km": 5.0, "weight_range": "LARGE"},
    )
    assert resp_large.status_code == 200
    for job in resp_large.json()["jobs"]:
        assert job["estimated_weight_kg"] > 100.0


def test_AC_B02_05_sorting_distance_and_price():
    """
    ทดสอบการจัดเรียงลำดับ:
    - DISTANCE: เรียงจากใกล้ไปไกล (road_distance_km น้อยไปมาก)
    - PRICE_DESC: เรียงจากราคาสูงสุดไปต่ำสุด (estimated_price_max มากไปน้อย)
    """
    lat, lng = 13.7900, 100.5750

    # 1. เรียงตามระยะทางใกล้สุด (DISTANCE)
    resp_dist = client.get(
        "/api/v1/collectors/jobs/nearby",
        params={"saleng_lat": lat, "saleng_lng": lng, "radius_km": 5.0, "sort_by": "DISTANCE"},
    )
    assert resp_dist.status_code == 200
    jobs_dist = resp_dist.json()["jobs"]
    assert len(jobs_dist) >= 2
    for i in range(len(jobs_dist) - 1):
        assert jobs_dist[i]["road_distance_km"] <= jobs_dist[i + 1]["road_distance_km"]

    # 2. เรียงตามราคาประเมินสูงสุด (PRICE_DESC)
    resp_price = client.get(
        "/api/v1/collectors/jobs/nearby",
        params={"saleng_lat": lat, "saleng_lng": lng, "radius_km": 5.0, "sort_by": "PRICE_DESC"},
    )
    assert resp_price.status_code == 200
    jobs_price = resp_price.json()["jobs"]
    assert len(jobs_price) >= 2
    for i in range(len(jobs_price) - 1):
        assert jobs_price[i]["estimated_price_max"] >= jobs_price[i + 1]["estimated_price_max"]


def test_AC_B02_05_simulate_new_order_and_discovery():
    """
    ทดสอบการจำลองคำขอขายใหม่ในพื้นที่ (POST /api/v1/collectors/jobs/simulate-new-order)
    และสามารถค้นหาพบในรอบถัดไป (สำหรับรองรับ Live Alert & Polling ตาม Q-02)
    """
    lat, lng = 13.7910, 100.5760  # ห่างจากสุทธิสาร ~ 0.15 กม.

    sim_payload = {
        "seller_id": "seller-live-sim",
        "lat": lat,
        "lng": lng,
        "subdistrict": "แขวงสามเสนนอก",
        "district": "เขตห้วยขวาง",
        "categories": ["MAT-ALU-CAN"],
        "estimated_weight_kg": 40.0,
        "estimated_price_min": 400.0,
        "estimated_price_max": 600.0,
        "need_lifting_help": False,
    }

    create_resp = client.post("/api/v1/collectors/jobs/simulate-new-order", json=sim_payload)
    assert create_resp.status_code == 201
    created_data = create_resp.json()
    assert created_data["success"] is True
    order_id = created_data["order"]["order_id"]

    # ค้นหาคำขอใหม่ที่เพิ่งจำลอง
    search_resp = client.get(
        "/api/v1/collectors/jobs/nearby",
        params={"saleng_lat": 13.7900, "saleng_lng": 100.5750, "radius_km": 5.0},
    )
    assert search_resp.status_code == 200
    found_ids = [j["order_id"] for j in search_resp.json()["jobs"]]
    assert order_id in found_ids

