"""
Automated Test for AC-S04-03: Minimum Threshold Guard & Alternative Options
รองรับ REQ-FN-001, REQ-FN-006, REQ-SEC-001, AC-S04-03, P-03, D-01, D-03
"""

from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)

DUMMY_SELLER_ID = "22222222-2222-2222-2222-222222222222"
DUMMY_LOCATION_ID = "33333333-3333-3333-3333-333333333333"


def test_AC_S04_03_pass_case_min_price_over_500():
    """
    AC-S04-03 Pass Case 1: มูลค่าประเมินขั้นต่ำ (min_price) >= 500 บาท
    กระดาษลัง 180 กก. (3–4 บ./กก. -> min_price = 540 บาท)
    ระบบอนุญาตให้ส่งคำขอนัดหมายเดี่ยวได้ทันที (HTTP 201, Status S2)
    """
    payload = {
        "seller_id": DUMMY_SELLER_ID,
        "pickup_location_id": DUMMY_LOCATION_ID,
        "submission_type": "DIRECT",
        "items": [
            {
                "category_code": "MAT-CARDBOARD",
                "unit": "kg",
                "quantity": 180.0
            }
        ]
    }
    response = client.post("/api/v1/orders/validate-and-submit", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["status"] == "S2"
    assert data["total_est_min_price"] == 540.0
    assert data["is_route_drop_in"] is False
    assert data["is_building_group_drop"] is False
    assert "order_id" in data


def test_AC_S04_03_pass_case_bottles_over_2_bags():
    """
    AC-S04-03 Pass Case 2: ขวดพลาสติก >= 2 กระสอบ (แม้ min_price < 500 บาท เช่น 2 กระสอบ = 60-100 บาท)
    ระบบอนุญาตให้ส่งคำขอนัดหมายเดี่ยวได้ทันทีตามเกณฑ์ (HTTP 201, Status S2)
    """
    payload = {
        "seller_id": DUMMY_SELLER_ID,
        "pickup_location_id": DUMMY_LOCATION_ID,
        "submission_type": "DIRECT",
        "items": [
            {
                "category_code": "MAT-PLASTIC-BOTTLE",
                "unit": "bag",
                "quantity": 2.0
            }
        ]
    }
    response = client.post("/api/v1/orders/validate-and-submit", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["status"] == "S2"
    assert data["total_est_min_price"] == 60.0  # 30 * 2 = 60
    assert data["is_route_drop_in"] is False


def test_AC_S04_03_blocked_under_500_baht_and_offer_alternatives():
    """
    AC-S04-03 Fail/Block Case: มูลค่าประเมิน < 500 บาท (เช่น กระดาษลัง 100 กก. -> 300–400 บาท)
    และไม่มีขวดแก้ว/พลาสติก 2 กระสอบ
    ระบบต้องบล็อกคำขอนัดหมายเดี่ยว (HTTP 400) และเสนอทางเลือก 'ฝากรวมจุดรับทางผ่าน' หรือ 'จุดรับรวมอาคาร'
    """
    payload = {
        "seller_id": DUMMY_SELLER_ID,
        "pickup_location_id": DUMMY_LOCATION_ID,
        "submission_type": "DIRECT",
        "items": [
            {
                "category_code": "MAT-CARDBOARD",
                "unit": "kg",
                "quantity": 100.0
            }
        ]
    }
    response = client.post("/api/v1/orders/validate-and-submit", json=payload)
    assert response.status_code == 400

    data = response.json()
    assert data["error"] == "MINIMUM_THRESHOLD_NOT_MET"
    assert data["total_est_min_price"] == 300.0
    assert "ROUTE_DROP_IN" in data["allowed_alternatives"]
    assert "BUILDING_GROUP" in data["allowed_alternatives"]


def test_AC_S04_03_alternative_route_drop_in():
    """
    AC-S04-03 Alt Case 1 (UC-08, REQ-FN-001, D-03):
    เมื่อไม่ถึงเกณฑ์ขั้นต่ำ (เช่น กระดาษลัง 100 กก. = 300 บาท) และผู้ขายเลือก 'ฝากรวมกับจุดรับทางผ่าน'
    ระบบส่งคำขอเข้าสู่สถานะ S2 ทันทีพร้อมติด Flag is_route_drop_in = True
    """
    payload = {
        "seller_id": DUMMY_SELLER_ID,
        "pickup_location_id": DUMMY_LOCATION_ID,
        "submission_type": "ROUTE_DROP_IN",
        "items": [
            {
                "category_code": "MAT-CARDBOARD",
                "unit": "kg",
                "quantity": 100.0
            }
        ]
    }
    response = client.post("/api/v1/orders/validate-and-submit", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["status"] == "S2"
    assert data["is_route_drop_in"] is True
    assert data["is_building_group_drop"] is False
    assert "ฝากรวมจุดรับทางผ่าน" in data["message"]


def test_AC_S04_03_alternative_building_group_drop():
    """
    AC-S04-03 Alt Case 2 (REQ-FN-006, D-03):
    เมื่อไม่ถึงเกณฑ์ขั้นต่ำ และผู้ขายเลือก 'จุดรับรวมประจำอาคาร/หอพัก'
    ระบบบันทึก is_building_group_drop = True และสร้างคำขอเข้าสู่สถานะ S2
    """
    payload = {
        "seller_id": DUMMY_SELLER_ID,
        "pickup_location_id": DUMMY_LOCATION_ID,
        "submission_type": "BUILDING_GROUP",
        "building_id": "44444444-4444-4444-4444-444444444444",
        "items": [
            {
                "category_code": "MAT-WHITE-PAPER",
                "unit": "kg",
                "quantity": 10.0
            }
        ]
    }
    response = client.post("/api/v1/orders/validate-and-submit", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["status"] == "S2"
    assert data["is_building_group_drop"] is True
    assert data["is_route_drop_in"] is False
    assert "จุดรับรวมประจำอาคาร" in data["message"]

    # ตรวจสอบว่ามีบันทึก Audit Log ลงฐานข้อมูลตาม REQ-SEC-001
    audit_logs = [log for log in supabase_store.audit_logs if log["action"] == "ORDER_CREATED_AND_SUBMITTED"]
    assert len(audit_logs) >= 1
    latest = audit_logs[-1]
    assert latest["details"]["status"] == "S2"

