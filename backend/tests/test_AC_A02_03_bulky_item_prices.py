"""
Automated Test for AC-A02-03: Bulky Waste Lump-sum Price Management & Batch Update
รองรับ UC-05, REQ-FN-003, AC-A02-03, D-A02-04, REQ-DAT-001, CC-03
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_bulky_state():
    orig_fridge = dict(supabase_store.benchmark_prices.get("BULKY-FRIDGE", {}))
    orig_tv = dict(supabase_store.benchmark_prices.get("BULKY-TV", {}))
    orig_washer = dict(supabase_store.benchmark_prices.get("BULKY-WASHING-MACHINE", {}))
    orig_ac = dict(supabase_store.benchmark_prices.get("BULKY-AIR-CONDITIONER", {}))
    yield
    if orig_fridge:
        supabase_store.benchmark_prices["BULKY-FRIDGE"] = orig_fridge
    if orig_tv:
        supabase_store.benchmark_prices["BULKY-TV"] = orig_tv
    if orig_washer:
        supabase_store.benchmark_prices["BULKY-WASHING-MACHINE"] = orig_washer
    if orig_ac:
        supabase_store.benchmark_prices["BULKY-AIR-CONDITIONER"] = orig_ac


def test_AC_A02_03_bulky_item_prices_retrieval():
    """
    ทดสอบการดึงรายการราคาขยะชิ้นใหญ่เหมาจ่าย (หน่วย PIECE)
    รองรับ AC-A02-03, UC-05, REQ-FN-003, D-A02-04
    - ตู้เย็น (200–300 บาท)
    - เครื่องซักผ้า (150–250 บาท)
    - แอร์/เครื่องปรับอากาศ (300–500 บาท)
    - โทรทัศน์/จอภาพ (50–150 บาท)
    - เฟอร์นิเจอร์/เตียง/เบาะ (10–100 บาท)
    """
    response = client.get(
        "/api/v1/admin/benchmark-prices?unit=piece",
        headers={"X-Admin-Role": "ADMIN"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 5

    items_map = {item["category_code"]: item for item in data}
    assert "BULKY-FRIDGE" in items_map
    assert "BULKY-WASHING-MACHINE" in items_map
    assert "BULKY-AIR-CONDITIONER" in items_map
    assert "BULKY-TV" in items_map
    assert "BULKY-FURNITURE" in items_map

    # ตรวจสอบหน่วยเป็น piece ทุกรายการ
    for code, item in items_map.items():
        assert item["unit"] == "piece"
        assert item["min_price_per_unit"] > 0
        assert item["max_price_per_unit"] >= item["min_price_per_unit"]


def test_AC_A02_03_update_bulky_item_price_single():
    """
    ทดสอบการอัปเดตราคาขยะชิ้นใหญ่รายการเดี่ยว (ตู้เย็น)
    """
    payload = {
        "min_price_per_unit": 220.0,
        "max_price_per_unit": 320.0,
        "grading_condition": "คอมเพรสเซอร์ทำงานปกติ สภาพดี",
        "confirm_shift": False,
        "updated_by": "admin-01",
        "change_reason": "ปรับราคาตามต้นทุนอะไหล่ตลาด",
    }
    response = client.put(
        "/api/v1/admin/benchmark-prices/BULKY-FRIDGE",
        json=payload,
        headers={"X-Admin-Role": "ADMIN"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["category_code"] == "BULKY-FRIDGE"
    assert data["min_price_per_unit"] == 220.0
    assert data["max_price_per_unit"] == 320.0


def test_AC_A02_03_batch_update_prices_success():
    """
    ทดสอบการอัปเดตราคากลางแบบกลุ่มประจำวัน (Batch Update)
    รองรับ AC-A02-03, REQ-DAT-001, D-A02-01..04
    """
    payload = {
        "items": [
            {
                "category_code": "BULKY-TV",
                "min_price_per_unit": 60.0,
                "max_price_per_unit": 160.0,
                "grading_condition": "จอสมบูรณ์ เปิดติด",
                "confirm_shift": False,
            },
            {
                "category_code": "BULKY-WASHING-MACHINE",
                "min_price_per_unit": 160.0,
                "max_price_per_unit": 260.0,
                "grading_condition": "ถังซักสภาพดี มอเตอร์ครบ",
                "confirm_shift": False,
            },
            {
                "category_code": "BULKY-AIR-CONDITIONER",
                "min_price_per_unit": 320.0,
                "max_price_per_unit": 520.0,
                "grading_condition": "คอยล์ทองแดงไม่รั่ว",
                "confirm_shift": False,
            },
        ],
        "effective_date": "2026-11-05",
        "updated_by": "admin-01",
        "change_reason": "ปรับราคาเหมาจ่ายขยะชิ้นใหญ่รอบวันที่ 5 พ.ย.",
    }
    response = client.post(
        "/api/v1/admin/benchmark-prices/batch-update",
        json=payload,
        headers={"X-Admin-Role": "ADMIN"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["updated_count"] == 3

    # ตรวจสอบว่าใน Store อัปเดตจริง
    tv = supabase_store.benchmark_prices["BULKY-TV"]
    assert tv["min_price_per_unit"] == 60.0
    assert tv["max_price_per_unit"] == 160.0
    assert tv["effective_date"] == "2026-11-05"

    # ตรวจสอบประวัติราคา
    history = supabase_store.get_benchmark_price_history("BULKY-TV")
    assert len(history) >= 1
    assert history[-1]["new_min_price"] == 60.0


def test_AC_A02_03_batch_update_unknown_category_fails():
    """
    ทดสอบกรณี Batch Update มีหมวดหมู่ที่ไม่พบในระบบ (404 Not Found)
    """
    payload = {
        "items": [
            {
                "category_code": "UNKNOWN-CAT-999",
                "min_price_per_unit": 100.0,
                "max_price_per_unit": 200.0,
                "confirm_shift": False,
            }
        ],
        "updated_by": "admin-01",
    }
    response = client.post(
        "/api/v1/admin/benchmark-prices/batch-update",
        json=payload,
        headers={"X-Admin-Role": "ADMIN"},
    )
    assert response.status_code == 404
