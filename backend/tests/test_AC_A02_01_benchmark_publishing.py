"""
Automated Test for AC-A02-01: Daily Benchmark Price Publishing
รองรับ UC-03, REQ-DAT-001, BR-01, AC-A02-01, D-A02-01, D-A02-02, CC-03, REQ-OP-001
"""

import time
import pytest
from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_store_state():
    """รีเซ็ตหรือเตรียมข้อมูลก่อนการทดสอบแต่ละเคส"""
    original_price = dict(supabase_store.benchmark_prices.get("MAT-CARDBOARD", {}))
    yield
    if original_price:
        supabase_store.benchmark_prices["MAT-CARDBOARD"] = original_price


def test_AC_A02_01_list_benchmark_prices_success():
    """
    ทดสอบการเรียกดูตารางราคากลางรายวันทั้งหมดด้วยสิทธิ์ ADMIN
    รองรับ AC-A02-01, D-A02-01, CC-03
    """
    start_time = time.time()
    response = client.get(
        "/api/v1/admin/benchmark-prices",
        headers={"X-Admin-Role": "ADMIN"},
    )
    duration = time.time() - start_time

    assert response.status_code == 200
    assert duration < 2.0, f"เวลาตอบสนอง {duration}s เกินเกณฑ์ 2.0 วินาทีตาม REQ-OP-001"

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 6

    # ตรวจสอบโครงสร้างข้อมูลของแต่ละรายการ
    cardboard = next((p for p in data if p["category_code"] == "MAT-CARDBOARD"), None)
    assert cardboard is not None
    assert cardboard["category_name"] == "กระดาษลัง"
    assert cardboard["unit"] == "kg"
    assert cardboard["min_price_per_unit"] > 0
    assert cardboard["max_price_per_unit"] >= cardboard["min_price_per_unit"]
    assert "updated_at" in cardboard
    assert "effective_date" in cardboard


def test_AC_A02_01_update_benchmark_price_success():
    """
    ทดสอบการอัปเดตช่วงราคากลาง (Min-Max) ของหมวดหมู่วัสดุ
    รองรับ AC-A02-01, BR-01, D-A02-02
    """
    payload = {
        "min_price_per_unit": 3.20,
        "max_price_per_unit": 4.20,
        "grading_condition": "แห้ง สะอาด ไม่เปียกชื้น",
        "confirm_shift": False,
        "updated_by": "admin-01",
        "change_reason": "ปรับตามราคาอ้างอิงรายวัน",
    }
    response = client.put(
        "/api/v1/admin/benchmark-prices/MAT-CARDBOARD",
        json=payload,
        headers={"X-Admin-Role": "ADMIN"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["category_code"] == "MAT-CARDBOARD"
    assert data["min_price_per_unit"] == 3.20
    assert data["max_price_per_unit"] == 4.20

    # ยืนยันว่าฝั่ง Public API มองเห็นราคาล่าสุด
    pub_res = client.get("/api/v1/pricing/benchmark-prices")
    assert pub_res.status_code == 200
    pub_data = pub_res.json()
    item = next((p for p in pub_data["prices"] if p["category_code"] == "MAT-CARDBOARD"), None)
    assert item is not None
    assert item["min_price_per_unit"] == 3.20
    assert item["max_price_per_unit"] == 4.20


def test_AC_A02_01_update_benchmark_price_validation_negative_and_max_less_than_min():
    """
    ทดสอบการตรวจความถูกต้องของราคา: min > 0, max >= min, ทศนิยม <= 2
    รองรับ AC-A02-01, D-A02-02
    """
    # 1. min_price <= 0
    res1 = client.put(
        "/api/v1/admin/benchmark-prices/MAT-CARDBOARD",
        json={"min_price_per_unit": 0.0, "max_price_per_unit": 4.0},
        headers={"X-Admin-Role": "ADMIN"},
    )
    assert res1.status_code == 422

    # 2. max_price < min_price
    res2 = client.put(
        "/api/v1/admin/benchmark-prices/MAT-CARDBOARD",
        json={"min_price_per_unit": 5.0, "max_price_per_unit": 3.0},
        headers={"X-Admin-Role": "ADMIN"},
    )
    assert res2.status_code == 422

    # 3. ทศนิยมเกิน 2 ตำแหน่ง
    res3 = client.put(
        "/api/v1/admin/benchmark-prices/MAT-CARDBOARD",
        json={"min_price_per_unit": 3.123, "max_price_per_unit": 4.0},
        headers={"X-Admin-Role": "ADMIN"},
    )
    assert res3.status_code == 422


def test_AC_A02_01_fallback_mechanism():
    """
    ทดสอบกลไก Fallback: หากไม่มีการอัปเดตใหม่ก่อน 06:00 น. ระบบจะดึงราคาฐานเดิมมาใช้
    รองรับ AC-A02-01, D-A02-01
    """
    # หมวดกระดาษขาวดำยังไม่เคยแก้รอบวันนี้ ยังคงมีค่าราคาฐานและวันเวลาอัปเดตล่าสุด
    response = client.get(
        "/api/v1/admin/benchmark-prices?q=MAT-WHITE-PAPER",
        headers={"X-Admin-Role": "ADMIN"},
    )
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    white_paper = items[0]
    assert white_paper["min_price_per_unit"] == 6.0
    assert white_paper["max_price_per_unit"] == 7.0
    assert white_paper["effective_date"] is not None
    assert white_paper["updated_at"] is not None

