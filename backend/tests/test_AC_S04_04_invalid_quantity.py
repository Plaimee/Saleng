"""
Automated Test for AC-S04-04: Invalid Quantity Guard
รองรับ Card 01 Exception Case, AC-S04-04, P-06
"""

from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app

client = TestClient(app)


def test_AC_S04_04_zero_quantity_guard():
    """
    AC-S04-04: หากกรอกปริมาณเป็น 0 ระบบต้องบล็อกการคำนวณและแจ้งเตือน 'กรุณากรอกปริมาณมากกว่า 0'
    """
    payload = {
        "items": [
            {
                "category_code": "MAT-CARDBOARD",
                "unit": "kg",
                "quantity": 0.0
            }
        ]
    }
    response = client.post("/api/v1/pricing/calculate-estimate", json=payload)
    assert response.status_code == 422

    error_detail = response.json()["detail"]
    # ตรวจสอบข้อความ error
    error_messages = [err.get("msg", "") for err in error_detail]
    assert any("กรุณากรอกปริมาณมากกว่า 0" in msg for msg in error_messages)


def test_AC_S04_04_negative_quantity_guard():
    """
    AC-S04-04: หากกรอกปริมาณเป็นค่าติดลบ ระบบต้องบล็อกการคำนวณและแจ้งเตือน 'กรุณากรอกปริมาณมากกว่า 0'
    """
    payload = {
        "items": [
            {
                "category_code": "MAT-CARDBOARD",
                "unit": "kg",
                "quantity": -10.5
            }
        ]
    }
    response = client.post("/api/v1/pricing/calculate-estimate", json=payload)
    assert response.status_code == 422

    error_detail = response.json()["detail"]
    error_messages = [err.get("msg", "") for err in error_detail]
    assert any("กรุณากรอกปริมาณมากกว่า 0" in msg for msg in error_messages)


def test_AC_S04_04_empty_items_guard():
    """
    ตรวจกรณีส่งรายการว่างเปล่า
    """
    payload = {"items": []}
    response = client.post("/api/v1/pricing/calculate-estimate", json=payload)
    assert response.status_code == 422

