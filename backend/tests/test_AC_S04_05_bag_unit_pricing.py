"""
Automated Test for AC-S04-05: Bag Unit & Flat-Rate Handling
รองรับ AC-S04-05, P-02, D-02
"""

from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app

client = TestClient(app)


def test_AC_S04_05_glass_bottle_bag_pricing():
    """
    AC-S04-05 & D-02: รองรับการเลือกหน่วยเป็น 'กระสอบ' สำหรับขวดแก้ว
    ขวดแก้วกระสอบละ 40–60 บาท
    เมื่อเลือก 2 กระสอบ -> ช่วงราคาต้องเป็น 80–120 บาท
    """
    payload = {
        "items": [
            {
                "category_code": "MAT-GLASS-BOTTLE",
                "unit": "bag",
                "quantity": 2.0
            }
        ]
    }
    response = client.post("/api/v1/pricing/calculate-estimate", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert len(data["items"]) == 1
    item = data["items"][0]
    assert item["unit"] == "bag"
    assert item["quantity"] == 2.0
    assert item["unit_min_price"] == 40.0
    assert item["unit_max_price"] == 60.0
    assert item["est_min_price"] == 80.0
    assert item["est_max_price"] == 120.0
    assert data["total_est_min_price"] == 80.0
    assert data["total_est_max_price"] == 120.0


def test_AC_S04_05_plastic_bottle_bag_pricing():
    """
    AC-S04-05 & D-02: รองรับการเลือกหน่วยเป็น 'กระสอบ' สำหรับขวดพลาสติก
    ขวดพลาสติกกระสอบละ 30–50 บาท
    เมื่อเลือก 3 กระสอบ -> ช่วงราคาต้องเป็น 90–150 บาท
    """
    payload = {
        "items": [
            {
                "category_code": "MAT-PLASTIC-BOTTLE",
                "unit": "bag",
                "quantity": 3.0
            }
        ]
    }
    response = client.post("/api/v1/pricing/calculate-estimate", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert len(data["items"]) == 1
    item = data["items"][0]
    assert item["unit"] == "bag"
    assert item["quantity"] == 3.0
    assert item["unit_min_price"] == 30.0
    assert item["unit_max_price"] == 50.0
    assert item["est_min_price"] == 90.0
    assert item["est_max_price"] == 150.0


def test_AC_S04_05_mixed_kg_and_bag_basket():
    """
    ทดสอบการรวมรายการแบบผสม: กก. + กระสอบ
    - กระดาษลัง 10 กก. (3–4 บ./กก. -> 30–40 บาท)
    - ขวดแก้ว 2 กระสอบ (40–60 บ./กระสอบ -> 80–120 บาท)
    ยอดรวมทั้งตะกร้า: 110–160 บาท
    """
    payload = {
        "items": [
            {
                "category_code": "MAT-CARDBOARD",
                "unit": "kg",
                "quantity": 10.0
            },
            {
                "category_code": "MAT-GLASS-BOTTLE",
                "unit": "bag",
                "quantity": 2.0
            }
        ]
    }
    response = client.post("/api/v1/pricing/calculate-estimate", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert len(data["items"]) == 2
    assert data["total_est_min_price"] == 110.0
    assert data["total_est_max_price"] == 160.0

