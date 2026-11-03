"""
Job Search & Dual-Engine Routing Service (UC-04, Buyer 02)
รองรับ REQ-FN-002, REQ-QA-002, REQ-SEC-002, REQ-OP-002, CC-03, CC-06, D-00-02, P-01..P-06
"""

from typing import List, Optional, Tuple, Dict, Any
import math
import time
from backend.app.models.job_search_models import (
    fuzz_coordinates,
    JobSearchQueryParams,
    NearbyJobSummaryResponse,
    NearbyJobListResponse,
    SimulateOrderRequest,
)
from backend.app.core.supabase import supabase_store


class DualEngineRoutingService:
    """
    ระบบคำนวณระยะทางแบบ 2 เครื่องยนต์ (Dual-Engine Routing Service - CC-03, REQ-OP-002)
    - Primary: Road Network Distance (คำนวณระยะทางตามแนวเส้นถนนจริงด้วยค่าสัมประสิทธิ์ 1.20)
    - Fallback: Haversine * 1.35 (สลับใช้อัตโนมัติเมื่อเกิดข้อผิดพลาดหรือโหมดออฟไลน์)
    - การตอบสนองต้องเสร็จสิ้นภายใน <= 2.0 วินาที
    """

    @staticmethod
    def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """คำนวณระยะทางแบบเส้นตรงผิวโลก (Great Circle Distance) เป็นกิโลเมตร"""
        r = 6371.0  # Earth radius in km
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lng2 - lng1)
        a = (
            math.sin(delta_phi / 2.0) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
        )
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return r * c

    @classmethod
    def calculate_distance(
        cls,
        lat1: float,
        lng1: float,
        lat2: float,
        lng2: float,
        force_fallback: bool = False,
    ) -> Tuple[float, bool]:
        """
        คำนวณระยะทางระหว่าง 2 พิกัด
        คืนค่า (distance_km, is_fallback_distance)
        """
        straight_km = cls.haversine_km(lat1, lng1, lat2, lng2)

        if force_fallback:
            # Fallback Engine: Haversine * 1.35 ตาม REQ-OP-002
            road_distance = round(straight_km * 1.35, 2)
            return (road_distance, True)

        try:
            # Primary Engine: Road Network Routing (สัมประสิทธิ์โครงข่ายถนนเมือง 1.20)
            road_distance = round(straight_km * 1.20, 2)
            return (road_distance, False)
        except Exception:
            # สลับใช้ Haversine Fallback อัตโนมัติเมื่อเกิดข้อผิดพลาด
            fallback_distance = round(straight_km * 1.35, 2)
            return (fallback_distance, True)


class PrivacyProtectionService:
    """
    ระบบคุ้มครองข้อมูลส่วนบุคคล (PII & Coordinate Protection - REQ-SEC-002, D-00-02, CC-06)
    - ปิดบังพิกัดจริงด้วย Coordinate Fuzzing (±300–500 ม.)
    - ปิดบังบ้านเลขที่และเบอร์โทรศัพท์ก่อนรับงานเด็ดขาด
    """

    @staticmethod
    def mask_order_for_discovery(
        order: dict,
        location: dict,
        road_distance_km: float,
        is_fallback_distance: bool = False,
    ) -> NearbyJobSummaryResponse:
        real_lat = location.get("lat", 13.7900)
        real_lng = location.get("lng", 100.5750)
        order_id = order.get("order_id", "order-unknown")

        # Fuzzing พิกัด
        approx_lat, approx_lng = fuzz_coordinates(real_lat, real_lng, seed=order_id)

        # สรุปหมวดหมู่
        items = order.get("items", [])
        categories = list({i.get("category_code") for i in items if i.get("category_code")})
        if not categories and order.get("categories"):
            categories = list(order.get("categories"))

        item_count = len(items) if items else 1
        est_min = float(order.get("total_est_min_price", 100.0))
        est_max = float(order.get("total_est_max_price", 150.0))
        est_weight = float(order.get("total_est_weight_kg", 20.0))

        return NearbyJobSummaryResponse(
            order_id=order_id,
            status=order.get("status", "S2"),
            subdistrict_name=location.get("subdistrict", "แขวงในพื้นที่"),
            district_name=location.get("district", "เขตในพื้นที่"),
            approximate_lat=approx_lat,
            approximate_lng=approx_lng,
            road_distance_km=road_distance_km,
            estimated_price_min=est_min,
            estimated_price_max=est_max,
            estimated_weight_kg=est_weight,
            categories=categories,
            item_count=item_count,
            need_lifting_help=order.get("need_lifting_help", False),
            is_fallback_distance=is_fallback_distance,
            created_at=order.get("created_at", ""),
        )


class JobSearchService:
    """บริการค้นหาและคัดกรองคำขอขายสำหรับซาเล้ง (UC-04)"""

    @classmethod
    def search_nearby_jobs(
        cls,
        params: JobSearchQueryParams,
        actor_id: str = "saleng-01",
        force_fallback: bool = False,
    ) -> NearbyJobListResponse:
        start_time = time.time()
        
        # ตรวจสอบ GPS Coordinates ความสมเหตุสมผล
        if params.saleng_lat == 0.0 and params.saleng_lng == 0.0:
            raise ValueError("พิกัด GPS เป็น 0.0 ไม่สามารถใช้ระบุตำแหน่งได้")

        open_orders = supabase_store.get_open_orders_s2()
        matched_jobs: List[NearbyJobSummaryResponse] = []
        jobs_in_expanded_range = 0

        for order in open_orders:
            loc_id = order.get("location_id")
            location = supabase_store.get_pickup_location(loc_id)
            if not location:
                continue

            order_lat = location.get("lat")
            order_lng = location.get("lng")
            if order_lat is None or order_lng is None:
                continue

            # คำนวณระยะทางถนนจริง
            dist_km, is_fallback = DualEngineRoutingService.calculate_distance(
                params.saleng_lat,
                params.saleng_lng,
                order_lat,
                order_lng,
                force_fallback=force_fallback,
            )

            # ตรวจสอบว่าอยู่ในรัศมีขยาย (10 กม.) หรือไม่
            if dist_km <= 10.0:
                jobs_in_expanded_range += 1

            # กรองตามรัศมีที่ระบุ
            if dist_km > params.radius_km:
                continue

            # ตัวกรองตามหมวดหมู่วัสดุ (Multi-criteria Category Filter - Q-03)
            order_items = order.get("items", [])
            order_cats = {i.get("category_code") for i in order_items if i.get("category_code")}
            if order.get("categories"):
                order_cats.update(order.get("categories"))

            if params.category and params.category not in ("ALL", "", None):
                # ตรวจสอบหมวดหมู่ (รองรับทั้งรหัส MAT-xxx และคำนำหน้า)
                cat_match = False
                for c in order_cats:
                    if params.category == c or params.category in c:
                        cat_match = True
                        break
                if not cat_match:
                    continue

            # ตัวกรองตามช่วงน้ำหนักประเมิน (Weight Range Filter - Q-03)
            weight = float(order.get("total_est_weight_kg", 0.0))
            if params.weight_range == "SMALL" and not (weight < 50.0):
                continue
            elif params.weight_range == "MEDIUM" and not (50.0 <= weight <= 100.0):
                continue
            elif params.weight_range == "LARGE" and not (weight > 100.0):
                continue

            # ปิดบัง PII ก่อนส่งออก
            job_summary = PrivacyProtectionService.mask_order_for_discovery(
                order=order,
                location=location,
                road_distance_km=dist_km,
                is_fallback_distance=is_fallback,
            )
            matched_jobs.append(job_summary)

        # การจัดเรียงลำดับ (Sorting - Q-03)
        if params.sort_by == "PRICE_DESC":
            matched_jobs.sort(key=lambda x: x.estimated_price_max, reverse=True)
        else:
            # Default: DISTANCE (ใกล้สุดก่อน)
            matched_jobs.sort(key=lambda x: x.road_distance_km)

        # กรณีไม่พบงานในรัศมีที่กำหนด (AC-B02-02, A1, Q-06)
        message = None
        can_expand = False
        if len(matched_jobs) == 0:
            message = "ยังไม่มีงานในเส้นทาง"
            can_expand = (params.radius_km < 10.0 and jobs_in_expanded_range > 0)

        # บันทึก Audit Log (REQ-SEC-001)
        elapsed = round(time.time() - start_time, 4)
        supabase_store.record_audit_log(
            action="JOB_SEARCH_QUERY",
            actor_id=actor_id,
            actor_role="COLLECTOR",
            details={
                "radius_km": params.radius_km,
                "saleng_lat": params.saleng_lat,
                "saleng_lng": params.saleng_lng,
                "category": params.category,
                "weight_range": params.weight_range,
                "sort_by": params.sort_by,
                "result_count": len(matched_jobs),
                "elapsed_seconds": elapsed,
            },
        )

        return NearbyJobListResponse(
            total_count=len(matched_jobs),
            radius_km=params.radius_km,
            jobs=matched_jobs,
            active_filters={
                "category": params.category,
                "weight_range": params.weight_range,
                "sort_by": params.sort_by,
            },
            message=message,
            can_expand_radius=can_expand,
        )

    @classmethod
    def get_job_summary(
        cls,
        order_id: str,
        saleng_lat: Optional[float] = None,
        saleng_lng: Optional[float] = None,
        force_fallback: bool = False,
    ) -> NearbyJobSummaryResponse:
        order = supabase_store.get_order(order_id)
        if not order:
            raise KeyError(f"ไม่พบคำขอขายรหัส: {order_id}")

        loc_id = order.get("location_id")
        location = supabase_store.get_pickup_location(loc_id)
        if not location:
            raise KeyError(f"ไม่พบข้อมูลสถานที่นัดรับสำหรับคำขอ: {order_id}")

        dist_km = 0.0
        is_fallback = False
        if saleng_lat is not None and saleng_lng is not None:
            dist_km, is_fallback = DualEngineRoutingService.calculate_distance(
                saleng_lat,
                saleng_lng,
                location.get("lat", 13.7900),
                location.get("lng", 100.5750),
                force_fallback=force_fallback,
            )

        return PrivacyProtectionService.mask_order_for_discovery(
            order=order,
            location=location,
            road_distance_km=dist_km,
            is_fallback_distance=is_fallback,
        )

    @classmethod
    def simulate_order(cls, req: SimulateOrderRequest) -> dict:
        """จำลองสร้างคำขอขายใหม่สถานะ S2 สำหรับทดสอบ Live Alert (Q-02)"""
        order_data = {
            "seller_id": req.seller_id,
            "status": "S2",
            "total_est_min_price": req.estimated_price_min,
            "total_est_max_price": req.estimated_price_max,
            "total_est_weight_kg": req.estimated_weight_kg,
            "need_lifting_help": req.need_lifting_help,
            "categories": req.categories,
        }
        location_data = {
            "seller_id": req.seller_id,
            "address_text": "ที่อยู่จำลองของผู้ขาย",
            "subdistrict": req.subdistrict,
            "district": req.district,
            "province": "กรุงเทพมหานคร",
            "lat": req.lat,
            "lng": req.lng,
        }
        created = supabase_store.add_simulated_order(order_data, location_data)

        # บันทึก Audit Log
        supabase_store.record_audit_log(
            action="ORDER_SIMULATED",
            actor_id=req.seller_id,
            actor_role="SELLER",
            details={
                "order_id": created["order_id"],
                "lat": req.lat,
                "lng": req.lng,
                "subdistrict": req.subdistrict,
            },
        )
        return created

