"""
Unit Tests for Buyer Job Evaluation Models, Fuel Calculation & Store Extensions
(Task T-01: UC-04, Card 02, REQ-FN-002, REQ-CON-003, D-B03-01)
"""

from backend.app.models.job_evaluation_models import (
    calculate_fuel_cost,
    FUEL_RATE_MAP,
    EvaluatedItemSummary,
    JobEvaluationResponse,
    CollectorStatusToggleRequest,
    CollectorCapacityResponse,
)
from backend.app.core.supabase import supabase_store


def test_T01_calculate_fuel_cost_by_vehicle_type():
    """
    ทดสอบสูตรคำนวณค่าน้ำมันตามประเภทยานพาหนะ (Card 02, D-B03-01):
    - TRICYCLE (ซาเล้งปั่น): 0.00 บาท
    - MOTORCYCLE (ซาเล้งพ่วงข้าง): 2.50 บาท/กม.
    - PICKUP (รถกระบะ): 4.50 บาท/กม.
    - DEFAULT: 2.50 บาท/กม.
    """
    dist_km = 4.0

    cost_tri = calculate_fuel_cost(dist_km, "TRICYCLE")
    assert cost_tri == 0.0, f"Expected 0.0 for TRICYCLE, got {cost_tri}"

    cost_moto = calculate_fuel_cost(dist_km, "MOTORCYCLE")
    assert cost_moto == 10.0, f"Expected 10.0 for MOTORCYCLE (4km * 2.5), got {cost_moto}"

    cost_pickup = calculate_fuel_cost(dist_km, "PICKUP")
    assert cost_pickup == 18.0, f"Expected 18.0 for PICKUP (4km * 4.5), got {cost_pickup}"

    cost_default = calculate_fuel_cost(dist_km, None)
    assert cost_default == 10.0, f"Expected 10.0 for default, got {cost_default}"


def test_T01_job_evaluation_response_schema_validation():
    """ตรวจสอบความถูกต้องของ Schema JobEvaluationResponse และการซ่อน PII (REQ-SEC-002, D-00-02)"""
    resp = JobEvaluationResponse(
        order_id="order-s2-01",
        status="S2",
        subdistrict_name="แขวงสามเสนนอก",
        district_name="เขตห้วยขวาง",
        approximate_lat=13.7950,
        approximate_lng=100.5810,
        road_distance_km=2.4,
        is_fallback_distance=False,
        vehicle_type="MOTORCYCLE",
        fuel_rate_per_km=2.50,
        estimated_fuel_cost=6.0,
        total_est_min_price=150.0,
        total_est_max_price=220.0,
        total_est_weight_kg=25.0,
        need_lifting_help=False,
        items=[
            EvaluatedItemSummary(
                item_id="item-01",
                category_code="MAT-CARDBOARD",
                category_name="กระดาษลัง",
                category_group="GENERAL_WEIGHT",
                est_weight_kg=20.0,
                est_min_price=80.0,
                est_max_price=100.0,
            )
        ],
        collector_current_load_kg=50.0,
        collector_max_capacity_kg=200.0,
        projected_total_load_kg=75.0,
        is_capacity_exceeded=False,
        remaining_capacity_kg=125.0,
        can_claim_job=True,
        collector_is_online=True,
        collector_is_verified=True,
        created_at="2026-11-04T03:00:00Z",
    )

    data = resp.model_dump()
    assert "address_text" not in data, "address_text must be stripped from evaluation"
    assert "phone" not in data, "phone must be stripped from evaluation"
    assert "seller_phone" not in data
    assert data["estimated_fuel_cost"] == 6.0
    assert data["is_capacity_exceeded"] is False
    assert data["remaining_capacity_kg"] == 125.0


def test_T01_supabase_store_load_and_status_helpers():
    """ตรวจสอบ Helper Methods ใน SupabaseStore สำหรับความจุรถและสถานะ Online (BR-03, CC-02)"""
    saleng_id = "saleng-01"

    # 1. ทดสอบการดึงและตั้งค่า current load
    supabase_store.set_saleng_current_load(saleng_id, 45.0)
    current_load = supabase_store.get_saleng_current_load(saleng_id)
    assert current_load == 45.0

    # 2. ทดสอบการสลับสถานะ Online/Offline
    updated = supabase_store.update_saleng_online_status(
        saleng_id=saleng_id,
        is_online=False,
        current_lat=13.7910,
        current_lng=100.5760,
    )
    assert updated is not None
    assert updated["is_online"] is False
    assert updated["current_lat"] == 13.7910

    # สลับกลับเป็น True เพื่อไม่กระทบการทดสอบอื่น
    supabase_store.update_saleng_online_status(saleng_id, True)

    # 3. ทดสอบการดึงข้อมูลเพื่อประเมินงาน
    eval_order = supabase_store.get_order_evaluation_data("order-s2-01")
    assert eval_order is not None
    assert eval_order["order_id"] == "order-s2-01"
    assert "items" in eval_order
    assert "location" in eval_order

