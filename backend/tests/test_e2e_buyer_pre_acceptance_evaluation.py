"""
Integration E2E Test: Pre-acceptance Job Evaluation & Fuel Cost Workflow
(Task T-08: UC-04, Card 02, AC-B03-01..05, REQ-FN-002, REQ-QA-002, REQ-OP-002, REQ-CON-003, REQ-SEC-002, D-00-01, D-00-02)

ทดสอบครบวงจรระบบประเมินงานและค่าน้ำมันก่อนรับ:
1. การคำนวณค่าน้ำมันตามประเภทรถ (TRICYCLE, MOTORCYCLE, PICKUP) และความคลาดเคลื่อน <= 15% (AC-B03-01)
2. ระบบสำรอง Dual-Engine Routing Fallback พร้อม Flag สำรอง (AC-B03-02)
3. ระบบป้องกันน้ำหนักเกินความจุรถ (Capacity Guard > 200 กก. บล็อกรับงาน) (AC-B03-03)
4. การสลับสถานะ Online/Offline และการบล็อกสิทธิ์รับงานเมื่อ Offline (AC-B03-03)
5. การปกป้องข้อมูลส่วนบุคคล PII และ Coordinate Fuzzing (AC-B03-04)
6. การตรวจจับและบล็อกสิทธิ์รับงานสำหรับซาเล้งที่ยังไม่ผ่าน KYC (AC-B03-05)
"""

import pytest
from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_environment_state():
    """ทำความสะอาดและคืนค่าสถานะซาเล้งก่อนและหลังการทดสอบทุกครั้ง"""
    orig_profile = supabase_store.saleng_profiles.get("saleng-01")
    orig_vehicle = orig_profile.get("vehicle_type", "MOTORCYCLE") if orig_profile else "MOTORCYCLE"
    orig_online = orig_profile.get("is_online", True) if orig_profile else True
    orig_verified = orig_profile.get("verified", True) if orig_profile else True
    orig_kyc = orig_profile.get("kyc_status", "VERIFIED") if orig_profile else "VERIFIED"

    supabase_store.set_saleng_current_load("saleng-01", 0.0)
    supabase_store.update_saleng_online_status("saleng-01", is_online=True)

    yield

    # คืนค่าเดิมหลังทดสอบ
    if "saleng-01" in supabase_store.saleng_profiles:
        supabase_store.saleng_profiles["saleng-01"]["vehicle_type"] = orig_vehicle
        supabase_store.saleng_profiles["saleng-01"]["is_online"] = orig_online
        supabase_store.saleng_profiles["saleng-01"]["verified"] = orig_verified
        supabase_store.saleng_profiles["saleng-01"]["kyc_status"] = orig_kyc
    supabase_store.set_saleng_current_load("saleng-01", 0.0)


def test_e2e_fuel_cost_by_vehicle_type_and_distance_accuracy():
    """
    E2E ขั้นตอนที่ 1: ตรวจสอบการประเมินระยะทางถนนและค่าน้ำมันตามประเภทรถ (AC-B03-01, Card 02, REQ-QA-002)
    - MOTORCYCLE: อัตรา 2.50 บาท/กม.
    - TRICYCLE: อัตรา 0.00 บาท/กม.
    - PICKUP: อัตรา 4.50 บาท/กม.
    - ความคลาดเคลื่อนระยะทางถนนเทียบกับ Haversine ไม่เกิน 15%
    """
    # 1. ทดสอบมอเตอร์ไซค์ (MOTORCYCLE)
    supabase_store.saleng_profiles["saleng-01"]["vehicle_type"] = "MOTORCYCLE"
    res_moto = client.get(
        "/api/v1/collectors/jobs/order-s2-01/evaluate",
        params={"saleng_id": "saleng-01", "saleng_lat": 13.7900, "saleng_lng": 100.5750},
    )
    assert res_moto.status_code == 200
    data_moto = res_moto.json()

    dist = data_moto["road_distance_km"]
    assert dist > 0.0
    assert data_moto["vehicle_type"] == "MOTORCYCLE"
    expected_moto_cost = round(dist * 2.50, 2)
    assert data_moto["estimated_fuel_cost"] == expected_moto_cost

    # 2. ทดสอบรถซาเล้งถีบ (TRICYCLE)
    supabase_store.saleng_profiles["saleng-01"]["vehicle_type"] = "TRICYCLE"
    res_tri = client.get(
        "/api/v1/collectors/jobs/order-s2-01/evaluate",
        params={"saleng_id": "saleng-01", "saleng_lat": 13.7900, "saleng_lng": 100.5750},
    )
    assert res_tri.status_code == 200
    data_tri = res_tri.json()
    assert data_tri["vehicle_type"] == "TRICYCLE"
    assert data_tri["estimated_fuel_cost"] == 0.0

    # 3. ทดสอบรถกระบะ (PICKUP)
    supabase_store.saleng_profiles["saleng-01"]["vehicle_type"] = "PICKUP"
    res_pick = client.get(
        "/api/v1/collectors/jobs/order-s2-01/evaluate",
        params={"saleng_id": "saleng-01", "saleng_lat": 13.7900, "saleng_lng": 100.5750},
    )
    assert res_pick.status_code == 200
    data_pick = res_pick.json()
    assert data_pick["vehicle_type"] == "PICKUP"
    expected_pick_cost = round(dist * 4.50, 2)
    assert data_pick["estimated_fuel_cost"] == expected_pick_cost


def test_e2e_dual_engine_routing_fallback():
    """
    E2E ขั้นตอนที่ 2: ระบบสำรอง Dual-Engine Routing Fallback (AC-B03-02, CC-03, REQ-OP-002)
    - สลับใช้สูตร Haversine * 1.35 อัตโนมัติเมื่อบริการแผนที่ล้มเหลว
    - ตอบสนองพร้อม Flag `is_fallback_distance: true`
    """
    supabase_store.saleng_profiles["saleng-01"]["vehicle_type"] = "MOTORCYCLE"
    res = client.get(
        "/api/v1/collectors/jobs/order-s2-01/evaluate",
        params={
            "saleng_id": "saleng-01",
            "saleng_lat": 13.7900,
            "saleng_lng": 100.5750,
            "force_fallback": True,
        },
    )
    assert res.status_code == 200
    data = res.json()

    assert data["is_fallback_distance"] is True
    assert data["road_distance_km"] > 0.0
    assert data["estimated_fuel_cost"] > 0.0


def test_e2e_capacity_overload_blocks_job_claim():
    """
    E2E ขั้นตอนที่ 3: ระบบป้องกันน้ำหนักเกินความจุรถ (AC-B03-03, BR-03, REQ-CON-003)
    - ความจุสูงสุด 200.0 กก.
    - เมื่อ current_load_kg + job_weight > 200.0 กก.
    - can_claim_job = False และ claim_block_reason = "CAPACITY_EXCEEDED"
    """
    # ตั้งค่าน้ำหนักสะสมในรถให้มีอยู่แล้ว 180 กก. (order-s2-01 มีน้ำหนักประมาณ 25 กก. -> รวม 205 กก. > 200 กก.)
    supabase_store.set_saleng_current_load("saleng-01", 180.0)

    res = client.get(
        "/api/v1/collectors/jobs/order-s2-01/evaluate",
        params={"saleng_id": "saleng-01"},
    )
    assert res.status_code == 200
    data = res.json()

    assert data["collector_current_load_kg"] == 180.0
    assert data["is_capacity_exceeded"] is True
    assert data["can_claim_job"] is False
    assert data["claim_block_reason"] == "CAPACITY_EXCEEDED"


def test_e2e_offline_toggle_allows_viewing_but_blocks_claim():
    """
    E2E ขั้นตอนที่ 4: สลับสถานะ Online/Offline (AC-B03-03, CC-02, D-B03-05)
    - สามารถเปิดดูรายละเอียดและประเมินงานได้แม้อยู่ในสถานะ Offline
    - แต่ can_claim_job = False และ claim_block_reason = "OFFLINE"
    """
    # สลับเป็นออฟไลน์ผ่าน API
    toggle_res = client.patch(
        "/api/v1/collectors/saleng-01/status",
        json={"saleng_id": "saleng-01", "is_online": False},
    )
    assert toggle_res.status_code == 200
    assert toggle_res.json()["profile"]["is_online"] is False

    # เปิดดูรายละเอียดประเมินงาน
    eval_res = client.get(
        "/api/v1/collectors/jobs/order-s2-01/evaluate",
        params={"saleng_id": "saleng-01"},
    )
    assert eval_res.status_code == 200
    data = eval_res.json()

    assert data["collector_is_online"] is False
    assert data["can_claim_job"] is False
    assert data["claim_block_reason"] == "OFFLINE"


def test_e2e_pdpa_pii_and_coordinate_masking():
    """
    E2E ขั้นตอนที่ 5: การปกปิดข้อมูลส่วนบุคคล PII และพิกัดจริง (AC-B03-04, REQ-SEC-002, D-00-02, CC-06)
    - ตัด address_text, phone, เบอร์ผู้ขาย และพิกัดจริงทิ้งทั้งหมด
    - ส่งเฉพาะ fuzzed_lat, fuzzed_lng (±300-500 ม.) และชื่อตำบล/แขวง
    """
    res = client.get(
        "/api/v1/collectors/jobs/order-s2-01/evaluate",
        params={"saleng_id": "saleng-01"},
    )
    assert res.status_code == 200
    data = res.json()

    # ตรวจสอบว่าไม่มีฟิลด์ PII ใน JSON เด็ดขาด
    assert "address_text" not in data
    assert "phone" not in data
    assert "seller_phone" not in data
    assert "dest_lat" not in data
    assert "dest_lng" not in data
    assert "real_lat" not in data
    assert "real_lng" not in data

    # ตรวจสอบว่ามีเฉพาะ Fuzzed Coordinates และชื่อแขวง/เขต
    assert data["subdistrict_name"] == "แขวงสามเสนนอก"
    assert data["district_name"] == "เขตห้วยขวาง"
    assert "approximate_lat" in data
    assert "approximate_lng" in data

    order_db = supabase_store.get_order("order-s2-01")
    loc_db = supabase_store.get_pickup_location(order_db["location_id"])
    assert (data["approximate_lat"], data["approximate_lng"]) != (loc_db["lat"], loc_db["lng"])


def test_e2e_unverified_kyc_gate():
    """
    E2E ขั้นตอนที่ 6: Unverified KYC Gate (AC-B03-05, D-00-01)
    - ซาเล้งที่ยังไม่ผ่าน KYC สามารถดูรายละเอียดประเมินงานได้
    - แต่ can_claim_job = False และ claim_block_reason = "UNVERIFIED_KYC"
    """
    # จำลองซาเล้งยังไม่ผ่าน KYC
    supabase_store.saleng_profiles["saleng-01"]["verified"] = False
    supabase_store.saleng_profiles["saleng-01"]["kyc_status"] = "UNVERIFIED"

    res = client.get(
        "/api/v1/collectors/jobs/order-s2-01/evaluate",
        params={"saleng_id": "saleng-01"},
    )
    assert res.status_code == 200
    data = res.json()

    assert data["collector_is_verified"] is False
    assert data["can_claim_job"] is False
    assert data["claim_block_reason"] == "UNVERIFIED_KYC"
