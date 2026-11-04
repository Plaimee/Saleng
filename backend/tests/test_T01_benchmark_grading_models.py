"""
Unit Tests for Benchmark Price & Quality Grading Data Models & Supabase Store
รองรับ T-01, REQ-DAT-001, REQ-FN-003, BR-01, D-A02-01..06, CC-04
"""

import pytest
from pydantic import ValidationError
from backend.app.models.benchmark_price_grading_models import (
    BenchmarkPriceAdminItem,
    UpdateBenchmarkPriceRequest,
    BatchUpdateItem,
    BatchUpdateBenchmarkPricesRequest,
    QualityGradingRuleItem,
    UpdateGradingRulesRequest,
    PriceHistoryLogItem,
)
from backend.app.core.supabase import SupabaseStore


def test_update_benchmark_price_validation_success():
    """ตรวจสอบการสร้าง UpdateBenchmarkPriceRequest ที่ถูกต้อง"""
    req = UpdateBenchmarkPriceRequest(
        min_price_per_unit=3.5,
        max_price_per_unit=4.5,
        grading_condition="แห้ง สะอาด ไม่เปียกน้ำ",
        confirm_shift=False,
    )
    assert req.min_price_per_unit == 3.5
    assert req.max_price_per_unit == 4.5
    assert req.grading_condition == "แห้ง สะอาด ไม่เปียกน้ำ"


def test_update_benchmark_price_validation_negative_or_zero():
    """ตรวจสอบว่าราคาต้องมากกว่า 0 (min_price > 0) ตาม D-A02-02"""
    with pytest.raises(ValidationError) as exc:
        UpdateBenchmarkPriceRequest(
            min_price_per_unit=0.0,
            max_price_per_unit=5.0,
        )
    assert "ราคาต่อหน่วยต้องมากกว่า 0" in str(exc.value)

    with pytest.raises(ValidationError) as exc:
        UpdateBenchmarkPriceRequest(
            min_price_per_unit=-1.0,
            max_price_per_unit=5.0,
        )
    assert "ราคาต่อหน่วยต้องมากกว่า 0" in str(exc.value)


def test_update_benchmark_price_validation_max_less_than_min():
    """ตรวจสอบว่า max_price ต้อง >= min_price ตาม D-A02-02"""
    with pytest.raises(ValidationError) as exc:
        UpdateBenchmarkPriceRequest(
            min_price_per_unit=5.0,
            max_price_per_unit=4.0,
        )
    assert "ราคาสูงสุดต้องมากกว่าหรือเท่ากับราคาต่ำสุด" in str(exc.value)


def test_update_benchmark_price_validation_precision():
    """ตรวจสอบว่าทศนิยมต้องไม่เกิน 2 ตำแหน่ง ตาม D-A02-02"""
    with pytest.raises(ValidationError) as exc:
        UpdateBenchmarkPriceRequest(
            min_price_per_unit=3.125,
            max_price_per_unit=4.0,
        )
    assert "ทศนิยมไม่เกิน 2 ตำแหน่ง" in str(exc.value)


def test_quality_grading_rule_deduction_validation():
    """ตรวจสอบว่า % หักสิ่งปนเปื้อนต้องอยู่ระหว่าง 0 ถึง 100% ตาม D-A02-03"""
    rule = QualityGradingRuleItem(
        category_code="MAT-CARDBOARD",
        grade_level="GRADE_B",
        grade_name="เกรด B (ปนเปื้อนเล็กน้อย)",
        description="มีความชื้นเล็กน้อย",
        contamination_deduction_percent=5.0,
        price_target="MID",
    )
    assert rule.contamination_deduction_percent == 5.0

    with pytest.raises(ValidationError):
        QualityGradingRuleItem(
            category_code="MAT-CARDBOARD",
            grade_level="GRADE_C",
            grade_name="เกรด C",
            description="ผิดพลาด",
            contamination_deduction_percent=105.0,
        )


def test_supabase_store_benchmark_prices_admin_list_and_filter():
    """ทดสอบเมธอด get_all_benchmark_prices_admin และการกรองตามหน่วยหรือค้นหา"""
    store = SupabaseStore()
    all_prices = store.get_all_benchmark_prices_admin()
    assert len(all_prices) >= 11

    # กรองเฉพาะหน่วย kg
    kg_prices = store.get_all_benchmark_prices_admin(unit="kg")
    assert all(p["unit"] == "kg" for p in kg_prices)

    # กรองเฉพาะหน่วย piece (ขยะชิ้นใหญ่)
    piece_prices = store.get_all_benchmark_prices_admin(unit="piece")
    assert len(piece_prices) >= 5
    assert any(p["category_code"] == "BULKY-FRIDGE" for p in piece_prices)

    # ค้นหาด้วยคำค้น
    fridge = store.get_all_benchmark_prices_admin(q="ตู้เย็น")
    assert len(fridge) == 1
    assert fridge[0]["category_code"] == "BULKY-FRIDGE"


def test_supabase_store_update_benchmark_price_and_audit():
    """ทดสอบการอัปเดตราคากลาง การบันทึกประวัติ และ Audit Log"""
    store = SupabaseStore()
    updated = store.update_benchmark_price(
        category_code="MAT-CARDBOARD",
        min_price=3.5,
        max_price=4.5,
        grading_condition="แห้งสนิท ลังใหม่",
        updated_by="admin-test",
        change_reason="ปรับตามราคาตลาดลานรับซื้อ",
    )
    assert updated["min_price_per_unit"] == 3.5
    assert updated["max_price_per_unit"] == 4.5
    assert updated["grading_condition"] == "แห้งสนิท ลังใหม่"

    # ตรวจสอบประวัติราคา
    history = store.get_benchmark_price_history("MAT-CARDBOARD")
    assert len(history) >= 1
    assert history[-1]["old_min_price"] == 3.0
    assert history[-1]["new_min_price"] == 3.5

    # ตรวจสอบ Audit Log
    recent_audits = [a for a in store.audit_logs if a["action"] == "ADMIN_UPDATED_BENCHMARK_PRICE"]
    assert len(recent_audits) >= 1
    assert recent_audits[-1]["entity_id"] == "MAT-CARDBOARD"
    assert recent_audits[-1]["actor_id"] == "admin-test"


def test_supabase_store_grading_rules_crud():
    """ทดสอบการดึงและอัปเดตเกณฑ์คุณภาพ 3 ระดับ"""
    store = SupabaseStore()
    rules = store.get_quality_grading_rules("MAT-CARDBOARD")
    assert len(rules) == 3
    assert rules[0]["grade_level"] == "GRADE_A"
    assert rules[0]["contamination_deduction_percent"] == 0.0
    assert rules[1]["grade_level"] == "GRADE_B"
    assert rules[1]["contamination_deduction_percent"] == 5.0
    assert rules[2]["grade_level"] == "GRADE_C"
    assert rules[2]["contamination_deduction_percent"] == 10.0

    # ปรับปรุงเกณฑ์
    rules[1]["description"] = "มีลวดเย็บกระดาษเล็กน้อย"
    updated_rules = store.update_quality_grading_rules("MAT-CARDBOARD", rules, updated_by="admin-test")
    assert updated_rules[1]["description"] == "มีลวดเย็บกระดาษเล็กน้อย"

    # ตรวจสอบ Audit Log
    recent_audits = [a for a in store.audit_logs if a["action"] == "ADMIN_UPDATED_GRADING_RULES"]
    assert len(recent_audits) >= 1
    assert recent_audits[-1]["entity_id"] == "MAT-CARDBOARD"

