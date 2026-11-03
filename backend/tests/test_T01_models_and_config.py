"""
Test Suite for T-01: Config, Supabase Client & Data Models
รองรับ REQ-DAT-001, REQ-FN-001, REQ-FN-006, CC-04, D-01, D-02, D-04
"""

import pytest
from pydantic import ValidationError
from backend.app.core.config import settings
from backend.app.core.supabase import supabase_store
from backend.app.models.pricing_models import (
    BenchmarkPrice,
    WasteItemEstimateInput,
    CalculationEstimateResponse,
    OrderSubmissionInput,
)


def test_T01_config_values():
    """ตรวจสอบค่าคอนฟิกตาม D-01, D-03, D-04"""
    assert settings.THRESHOLD_MIN_ESTIMATED_BAHT == 500.0
    assert settings.THRESHOLD_MIN_BAGS == 2
    assert settings.THRESHOLD_BUILDING_KG == 20.0
    assert settings.BENCHMARK_PRICE_REFRESH_TIME == "06:00"
    assert settings.PRICE_CALCULATION_TIMEOUT_MS == 3000


def test_T01_supabase_store_seed_and_crud():
    """ตรวจสอบการทำงานของ SupabaseStore ตาม CC-04, REQ-DAT-001"""
    prices = supabase_store.get_benchmark_prices()
    assert len(prices) >= 5
    cardboard = supabase_store.get_price_by_category("MAT-CARDBOARD")
    assert cardboard is not None
    assert cardboard["category_name"] == "กระดาษลัง"
    assert cardboard["min_price_per_unit"] == 3.0
    assert cardboard["max_price_per_unit"] == 4.0

    # ตรวจสอบขวดแก้ว/พลาสติกแบบกระสอบ (D-02, AC-S04-05)
    glass_bag = supabase_store.get_price_by_category("MAT-GLASS-BOTTLE-BAG")
    assert glass_bag is not None
    assert glass_bag["unit"] == "bag"
    assert glass_bag["min_price_per_unit"] == 40.0
    assert glass_bag["max_price_per_unit"] == 60.0


def test_T01_benchmark_price_validation():
    """ตรวจสอบ Model Validation ของ BenchmarkPrice ตาม BR-01"""
    valid_price = BenchmarkPrice(
        id="11111111-1111-1111-1111-111111111111",
        category_code="MAT-CARDBOARD",
        category_name="กระดาษลัง",
        unit="kg",
        min_price_per_unit=3.0,
        max_price_per_unit=4.0,
        updated_at="2026-11-03T06:00:00Z"
    )
    assert valid_price.min_price_per_unit == 3.0

    # กรณี max < min ต้องเกิด ValidationError
    with pytest.raises(ValidationError):
        BenchmarkPrice(
            id="11111111-1111-1111-1111-111111111111",
            category_code="MAT-CARDBOARD",
            category_name="กระดาษลัง",
            unit="kg",
            min_price_per_unit=5.0,
            max_price_per_unit=3.0,
            updated_at="2026-11-03T06:00:00Z"
        )


def test_T01_waste_item_estimate_input_validation():
    """ตรวจสอบการบล็อกปริมาณ <= 0 ตาม AC-S04-04"""
    # ปริมาณปกติ
    item = WasteItemEstimateInput(
        category_code="MAT-CARDBOARD",
        unit="kg",
        quantity=10.0
    )
    assert item.quantity == 10.0

    # ปริมาณ = 0 (ต้อง error ข้อความ "กรุณากรอกปริมาณมากกว่า 0")
    with pytest.raises(ValidationError) as exc_info:
        WasteItemEstimateInput(
            category_code="MAT-CARDBOARD",
            unit="kg",
            quantity=0.0
        )
    assert "กรุณากรอกปริมาณมากกว่า 0" in str(exc_info.value)

    # ปริมาณติดลบ
    with pytest.raises(ValidationError) as exc_info:
        WasteItemEstimateInput(
            category_code="MAT-CARDBOARD",
            unit="kg",
            quantity=-5.0
        )
    assert "กรุณากรอกปริมาณมากกว่า 0" in str(exc_info.value)

