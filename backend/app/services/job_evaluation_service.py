"""
Job Evaluation & Fuel Cost Service (UC-04, Buyer 03, Card 02)
รองรับ REQ-FN-002, REQ-QA-002, REQ-OP-002, REQ-CON-003, REQ-SEC-002, BR-03, D-B03-01..06
"""

from typing import Optional, List
from backend.app.models.job_evaluation_models import (
    calculate_fuel_cost,
    FUEL_RATE_MAP,
    EvaluatedItemSummary,
    JobEvaluationResponse,
    CollectorStatusToggleRequest,
    CollectorCapacityResponse,
)
from backend.app.models.job_search_models import fuzz_coordinates
from backend.app.services.job_search_service import DualEngineRoutingService
from backend.app.core.supabase import supabase_store


class JobEvaluationService:
    """บริการประเมินคำขอขาย คำนวณค่าน้ำมัน ตรวจสอบความจุรถ และการสลับสถานะ Online/Offline (Card 02, UC-04)"""

    @classmethod
    def evaluate_job(
        cls,
        order_id: str,
        saleng_id: str = "saleng-01",
        saleng_lat: Optional[float] = None,
        saleng_lng: Optional[float] = None,
        force_fallback: bool = False,
    ) -> JobEvaluationResponse:
        # 1. ดึงข้อมูลคำขอขาย
        order = supabase_store.get_order_evaluation_data(order_id)
        if not order:
            raise KeyError(f"ไม่พบคำขอขายรหัส: {order_id}")

        location = order.get("location")
        if not location:
            raise KeyError(f"ไม่พบข้อมูลสถานที่นัดรับสำหรับคำขอ: {order_id}")

        # 2. ดึงข้อมูลโปรไฟล์ซาเล้ง
        collector = supabase_store.saleng_profiles.get(saleng_id)
        if not collector:
            # Fallback profile หากไม่พบ
            collector = {
                "saleng_id": saleng_id,
                "current_lat": 13.7900,
                "current_lng": 100.5750,
                "vehicle_type": "MOTORCYCLE",
                "max_capacity_kg": 200.0,
                "is_online": True,
                "verified": True,
                "kyc_status": "VERIFIED",
            }

        calc_lat = saleng_lat if saleng_lat is not None else collector.get("current_lat", 13.7900)
        calc_lng = saleng_lng if saleng_lng is not None else collector.get("current_lng", 100.5750)

        # 3. คำนวณระยะทางถนนจริงด้วย Dual-Engine Routing (CC-03, REQ-OP-002)
        real_dest_lat = location.get("lat", 13.7930)
        real_dest_lng = location.get("lng", 100.5780)

        dist_km, is_fallback = DualEngineRoutingService.calculate_distance(
            calc_lat,
            calc_lng,
            real_dest_lat,
            real_dest_lng,
            force_fallback=force_fallback,
        )

        # 4. คำนวณค่าน้ำมันโดยประมาณตามประเภทยานพาหนะ (Card 02, D-B03-01)
        vehicle_type = collector.get("vehicle_type", "MOTORCYCLE").upper()
        fuel_rate = FUEL_RATE_MAP.get(vehicle_type, FUEL_RATE_MAP["DEFAULT"])
        estimated_fuel_cost = calculate_fuel_cost(dist_km, vehicle_type)

        # 5. ตรวจสอบความจุรถสะสม (BR-03, REQ-CON-003, D-B03-03, D-B03-04)
        current_load_kg = supabase_store.get_saleng_current_load(saleng_id)
        max_capacity_kg = float(collector.get("max_capacity_kg", 200.0))
        job_est_weight_kg = float(order.get("total_est_weight_kg", 20.0))
        projected_total_load_kg = round(current_load_kg + job_est_weight_kg, 2)
        remaining_capacity_kg = round(max(0.0, max_capacity_kg - current_load_kg), 2)
        is_capacity_exceeded = projected_total_load_kg > max_capacity_kg

        # 6. ตรวจสอบสิทธิ์และเงื่อนไขการรับงาน (Can Claim Guard)
        is_online = bool(collector.get("is_online", True))
        is_verified = bool(collector.get("verified", False) and collector.get("kyc_status") == "VERIFIED")

        can_claim = True
        block_reason = None
        if not is_verified:
            can_claim = False
            block_reason = "UNVERIFIED_KYC"
        elif not is_online:
            can_claim = False
            block_reason = "OFFLINE"
        elif is_capacity_exceeded:
            can_claim = False
            block_reason = "CAPACITY_EXCEEDED"

        # 7. คุ้มครองข้อมูลส่วนบุคคล (PII & Coordinate Fuzzing - REQ-SEC-002, D-00-02, CC-06)
        approx_lat, approx_lng = fuzz_coordinates(real_dest_lat, real_dest_lng, seed=order_id)

        # แปลงรายการสิ่งของ
        items_summary: List[EvaluatedItemSummary] = []
        raw_items = order.get("items", [])
        for item in raw_items:
            items_summary.append(
                EvaluatedItemSummary(
                    item_id=item.get("item_id", ""),
                    category_code=item.get("category_code", "MAT-CARDBOARD"),
                    category_name=item.get("name", "ของเก่าทั่วไป"),
                    category_group=item.get("category_group", "GENERAL_WEIGHT"),
                    est_weight_kg=float(item.get("est_weight_kg", 0.0)),
                    est_min_price=float(item.get("est_min_price", 0.0)),
                    est_max_price=float(item.get("est_max_price", 0.0)),
                    sub_category=item.get("sub_category"),
                    photo_urls=item.get("photo_urls", []) or [],
                )
            )

        # 8. บันทึกประวัติ Audit Log (REQ-SEC-001)
        supabase_store.record_audit_log(
            action="JOB_EVALUATION_VIEWED",
            actor_id=saleng_id,
            actor_role="COLLECTOR",
            details={
                "order_id": order_id,
                "road_distance_km": dist_km,
                "estimated_fuel_cost": estimated_fuel_cost,
                "projected_total_load_kg": projected_total_load_kg,
                "is_capacity_exceeded": is_capacity_exceeded,
                "can_claim_job": can_claim,
            },
        )

        return JobEvaluationResponse(
            order_id=order_id,
            status=order.get("status", "S2"),
            subdistrict_name=location.get("subdistrict", "แขวงในพื้นที่"),
            district_name=location.get("district", "เขตในพื้นที่"),
            approximate_lat=approx_lat,
            approximate_lng=approx_lng,
            road_distance_km=dist_km,
            is_fallback_distance=is_fallback,
            vehicle_type=vehicle_type,
            fuel_rate_per_km=fuel_rate,
            estimated_fuel_cost=estimated_fuel_cost,
            total_est_min_price=float(order.get("total_est_min_price", 100.0)),
            total_est_max_price=float(order.get("total_est_max_price", 150.0)),
            total_est_weight_kg=job_est_weight_kg,
            need_lifting_help=bool(order.get("need_lifting_help", False)),
            items=items_summary,
            collector_current_load_kg=current_load_kg,
            collector_max_capacity_kg=max_capacity_kg,
            projected_total_load_kg=projected_total_load_kg,
            is_capacity_exceeded=is_capacity_exceeded,
            remaining_capacity_kg=remaining_capacity_kg,
            can_claim_job=can_claim,
            claim_block_reason=block_reason,
            collector_is_online=is_online,
            collector_is_verified=is_verified,
            created_at=order.get("created_at", ""),
        )

    @classmethod
    def toggle_online_status(cls, req: CollectorStatusToggleRequest) -> dict:
        """สลับสถานะความพร้อมรับงาน Online / Offline (CC-02, D-B03-05)"""
        profile = supabase_store.update_saleng_online_status(
            saleng_id=req.saleng_id,
            is_online=req.is_online,
            current_lat=req.current_lat,
            current_lng=req.current_lng,
        )
        if not profile:
            raise KeyError(f"ไม่พบข้อมูลซาเล้งรหัส: {req.saleng_id}")

        supabase_store.record_audit_log(
            action="STATUS_TOGGLED",
            actor_id=req.saleng_id,
            actor_role="COLLECTOR",
            details={"is_online": req.is_online, "current_lat": req.current_lat, "current_lng": req.current_lng},
        )
        return profile

    @classmethod
    def get_collector_capacity(cls, saleng_id: str) -> CollectorCapacityResponse:
        """ดึงข้อมูลความจุรถและน้ำหนักสะสมของซาเล้ง (BR-03, REQ-CON-003)"""
        collector = supabase_store.saleng_profiles.get(saleng_id)
        if not collector:
            raise KeyError(f"ไม่พบข้อมูลซาเล้งรหัส: {saleng_id}")

        current_load = supabase_store.get_saleng_current_load(saleng_id)
        max_cap = float(collector.get("max_capacity_kg", 200.0))
        remaining = round(max(0.0, max_cap - current_load), 2)
        load_pct = round((current_load / max_cap) * 100.0, 1) if max_cap > 0 else 0.0

        return CollectorCapacityResponse(
            saleng_id=saleng_id,
            current_load_kg=current_load,
            max_capacity_kg=max_cap,
            remaining_capacity_kg=remaining,
            vehicle_type=collector.get("vehicle_type", "MOTORCYCLE"),
            load_percentage=load_pct,
        )

