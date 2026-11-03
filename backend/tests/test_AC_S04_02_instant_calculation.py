"""
Automated Test for AC-S04-02: Instant Min-Max Calculation & Multi-Item Basket
รองรับ Card 01, BR-01, AC-S04-02, P-01, D-06
"""

from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app

client = TestClient(app)


def test_AC_S04_02_single_item_instant_calculation():
    """
    AC-S04-02: เมื่อเลือกประเภท 'กระดาษลัง' (3–4 บาท/กก.) และกรอกปริมาณ '10 กิโลกรัม'
    ระบบแสดงช่วงราคาประเมิน '30–40 บาท' ภายใน <= 3 วินาที พร้อมข้อความ 'ราคาจริงขึ้นกับสภาพของหน้างาน'
    """
    payload = {
        "items": [
            {
                "category_code": "MAT-CARDBOARD",
                "unit": "kg",
                "quantity": 10.0
            }
        ]
    }
    response = client.post("/api/v1/pricing/calculate-estimate", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert len(data["items"]) == 1
    item = data["items"][0]
    assert item["category_code"] == "MAT-CARDBOARD"
    assert item["category_name"] == "กระดาษลัง"
    assert item["quantity"] == 10.0
    assert item["unit"] == "kg"
    assert item["est_min_price"] == 30.0
    assert item["est_max_price"] == 40.0

    # ตรวจสอบยอดรวมของตะกร้า
    assert data["total_est_min_price"] == 30.0
    assert data["total_est_max_price"] == 40.0

    # ตรวจสอบข้อความกำกับตาม BR-01
    assert data["disclaimer"] == "ราคาจริงขึ้นกับสภาพของหน้างาน"

    # ตรวจสอบเกณฑ์เวลาคำนวณ (<= 3 วินาที หรือ <= 3000 ms)
    assert data["calculation_time_ms"] <= 3000.0


def test_AC_S04_02_multi_item_basket_calculation():
    """
    AC-S04-02 & D-06: ทดสอบตะกร้าหลายรายการ (Multi-Item Basket)
    รายการ 1: กระดาษลัง 10 กก. (3–4 บาท/กก. -> 30–40 บาท)
    รายการ 2: กระดาษขาวดำ 5 กก. (6–7 บาท/กก. -> 30–35 บาท)
    ยอดรวม: 60–75 บาท
    """
    payload = {
        "items": [
            {
                "category_code": "MAT-CARDBOARD",
                "unit": "kg",
                "quantity": 10.0
            },
            {
                "category_code": "MAT-WHITE-PAPER",
                "unit": "kg",
                "quantity": 5.0
            }
        ]
    }
    response = client.post("/api/v1/pricing/calculate-estimate", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert len(data["items"]) == 2

    cardboard = data["items"][0]
    assert cardboard["est_min_price"] == 30.0
    assert cardboard["est_max_price"] == 40.0

    white_paper = data["items"][1]
    assert white_paper["est_min_price"] == 30.0
    assert white_paper["est_max_price"] == 35.0

    # ยอดรวมทั้งตะกร้าต้องเป็น 60 - 75 บาท
    assert data["total_est_min_price"] == 60.0
    assert data["total_est_max_price"] == 75.0
    assert data["disclaimer"] == "ราคาจริงขึ้นกับสภาพของหน้างาน"

