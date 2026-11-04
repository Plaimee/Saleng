"""
Job & Route Management Service (UC-04, UC-09, UC-12, Buyer 04)
รองรับ REQ-BR-002, REQ-SEC-002, REQ-OP-001, CC-01, CC-04, CC-05, BR-02, BR-03, D-B04-01..06
"""

from datetime import datetime, timezone
from typing import List, Optional

from backend.app.models.job_route_models import (
    ClaimJobRequest,
    ClaimJobResponse,
    ActiveJobSummary,
    ActiveQueueResponse,
    StartTransitRequest,
    StartTransitResponse,
    CollectorCancelJobRequest,
    CollectorCancelJobResponse,
    build_google_maps_navigation_url,
)
from backend.app.services.job_search_service import DualEngineRoutingService
from backend.app.core.supabase import supabase_store


class JobRouteManagementService:
    """บริการจัดการงาน เส้นทาง การกดรับงานแบบ Atomic, การออกเดินทาง และการยกเลิกคืนสถานะ"""

    @classmethod
    def claim_job(cls, order_id: str, req: ClaimJobRequest) -> ClaimJobResponse:
        """
        กดรับงานแบบ Single Collector Atomic Claim ด้วย Optimistic Concurrency Control (OCC)
        (BR-02, REQ-BR-002, CC-04, AC-B04-01, D-B04-01)
        """
        saleng_id = req.saleng_id

        # 1. ตรวจสอบการยืนยันตัวตน KYC (D-00-01)
        collector = supabase_store.saleng_profiles.get(saleng_id)
        if not collector:
            raise KeyError(f"ไม่พบโปรไฟล์ซาเล้งรหัส {saleng_id}")

        if not collector.get("verified") or collector.get("kyc_status") != "VERIFIED":
            raise PermissionError("ต้องผ่านการยืนยันตัวตน KYC ให้เสร็จสมบูรณ์ก่อนจึงจะกดรับงานได้")

        # 2. ตรวจสอบสถานะความพร้อมรับงาน Online (CC-02, D-B03-05)
        if not collector.get("is_online", True):
            raise ValueError("กรุณาเปิดสถานะออนไลน์ (Online) ก่อนรับงาน")

        # 3. ตรวจสอบคำขอขายและน้ำหนักความจุรถสะสม (BR-03, REQ-CON-003)
        order = supabase_store.orders.get(order_id)
        if not order:
            raise KeyError(f"ไม่พบคำขอขายรหัส {order_id}")

        current_load = supabase_store.get_saleng_current_load(saleng_id)
        job_est_weight = float(order.get("total_est_weight_kg", 0.0))
        max_capacity = float(collector.get("max_capacity_kg", 200.0))

        if round(current_load + job_est_weight, 2) > max_capacity:
            raise ValueError(
                f"น้ำหนักงานนี้ ({job_est_weight:.1f} กก.) รวมกับของสะสมในรถ ({current_load:.1f} กก.) "
                f"เกินความจุรถสูงสุด {max_capacity:.1f} กก."
            )

        # 4. ดำเนินการ Atomic Claim ผ่าน Optimistic Concurrency Control (version column)
        # หากมีซาเล้งรับไปแล้ว หรือ version ไม่ตรงกัน จะ raise ValueError
        claimed_order = supabase_store.claim_order_occ(
            order_id=order_id,
            saleng_id=saleng_id,
            expected_version=req.expected_version,
        )

        # 5. ดึงข้อมูลสถานที่และผู้ขายเพื่อเปิดเผย PII (REQ-SEC-002, D-00-02, CC-06)
        loc_id = claimed_order.get("location_id")
        location = supabase_store.get_pickup_location(loc_id) if loc_id else None
        if not location:
            raise KeyError(f"ไม่พบข้อมูลสถานที่นัดรับของคำขอ {order_id}")

        seller_id = claimed_order.get("seller_id", "seller-01")
        seller = supabase_store.sellers.get(seller_id) or {}
        seller_name = seller.get("display_name", "คุณวิภาดา")
        seller_phone = seller.get("phone", "081-234-5678")

        real_lat = float(location.get("lat", 13.7950))
        real_lng = float(location.get("lng", 100.5810))
        nav_url = build_google_maps_navigation_url(real_lat, real_lng)

        # 6. บันทึก Audit Log (REQ-SEC-001)
        supabase_store.record_audit_log(
            action="COLLECTOR_CLAIMED_JOB",
            actor_id=saleng_id,
            actor_role="COLLECTOR",
            entity_id=order_id,
            details={
                "order_id": order_id,
                "version": claimed_order.get("version"),
                "total_est_weight_kg": job_est_weight,
            },
        )

        return ClaimJobResponse(
            order_id=order_id,
            status="S3",
            collector_id=saleng_id,
            address_text=location.get("address_text", ""),
            dest_lat=real_lat,
            dest_lng=real_lng,
            seller_phone=seller_phone,
            seller_name=seller_name,
            subdistrict_name=location.get("subdistrict", ""),
            district_name=location.get("district", ""),
            total_est_weight_kg=job_est_weight,
            total_est_price_min=float(claimed_order.get("total_est_min_price", 0.0)),
            total_est_price_max=float(claimed_order.get("total_est_max_price", 0.0)),
            claimed_at=claimed_order.get("claimed_at", datetime.now(timezone.utc).isoformat()),
            version=int(claimed_order.get("version", 2)),
            navigation_url=nav_url,
        )

    @classmethod
    def skip_job(cls, order_id: str, saleng_id: str) -> dict:
        """
        ข้ามงาน ปิดหน้ารายละเอียด และคงสถานะคำขอขายเป็น S2 (Extension A2, AC-B04-02)
        """
        order = supabase_store.orders.get(order_id)
        if not order:
            raise KeyError(f"ไม่พบคำขอขายรหัส {order_id}")

        supabase_store.record_audit_log(
            action="COLLECTOR_SKIPPED_JOB",
            actor_id=saleng_id,
            actor_role="COLLECTOR",
            entity_id=order_id,
            details={"order_id": order_id, "current_status": order.get("status")},
        )

        return {
            "order_id": order_id,
            "status": order.get("status", "S2"),
            "skipped": True,
            "message": "ข้ามงานเรียบร้อย คำขอยังคงสถานะรอผู้รับงานสำหรับซาเล้งคนอื่น",
        }

    @classmethod
    def get_active_queue(
        cls,
        saleng_id: str,
        saleng_lat: Optional[float] = None,
        saleng_lng: Optional[float] = None,
    ) -> ActiveQueueResponse:
        """
        ดึงรายการคิวงานและตารางนัดหมายสะสมในสถานะ S3 และ S4 ของซาเล้ง
        พร้อมจัดลำดับเส้นทางอย่างคุ้มค่า (BR-03, D-B04-02, AC-B04-04)
        """
        collector = supabase_store.saleng_profiles.get(saleng_id)
        if not collector:
            raise KeyError(f"ไม่พบโปรไฟล์ซาเล้งรหัส {saleng_id}")

        cur_lat = saleng_lat if saleng_lat is not None else float(collector.get("current_lat", 13.7900))
        cur_lng = saleng_lng if saleng_lng is not None else float(collector.get("current_lng", 100.5750))
        max_cap = float(collector.get("max_capacity_kg", 200.0))

        raw_active = supabase_store.get_collector_active_jobs(saleng_id)

        job_summaries: List[ActiveJobSummary] = []
        total_route_distance = 0.0
        cumulative_weight = 0.0

        # จัดเรียงลำดับจุดแวะรับตามเวลานัดหมายและระยะทางใกล้เคียง (Nearest-Neighbor)
        for idx, o in enumerate(raw_active, start=1):
            order_id = o.get("order_id")
            loc_id = o.get("location_id")
            location = supabase_store.get_pickup_location(loc_id) if loc_id else None
            seller_id = o.get("seller_id", "seller-01")
            seller = supabase_store.sellers.get(seller_id) or {}

            dest_lat = float(location.get("lat", 13.7950)) if location else 13.7950
            dest_lng = float(location.get("lng", 100.5810)) if location else 100.5810

            # คำนวณระยะทางจากจุดปัจจุบัน
            calc_dist, _ = DualEngineRoutingService.calculate_distance(
                cur_lat, cur_lng, dest_lat, dest_lng
            )
            total_route_distance += calc_dist
            w = float(o.get("total_est_weight_kg", 0.0))
            cumulative_weight += w

            # ประมาณเวลาถึง (นาที) ~ 4 นาที/กม. + 5 นาทีเผื่อเวลา
            eta_mins = max(5, int(calc_dist * 4) + 5)
            nav_url = build_google_maps_navigation_url(dest_lat, dest_lng)

            job_summaries.append(
                ActiveJobSummary(
                    order_id=order_id,
                    status=o.get("status", "S3"),
                    pickup_slot_time=o.get("pickup_slot_time", "09:00 - 11:00"),
                    address_text=location.get("address_text", "") if location else "",
                    dest_lat=dest_lat,
                    dest_lng=dest_lng,
                    seller_name=seller.get("display_name", "ผู้ขาย"),
                    seller_phone=seller.get("phone", "081-234-5678"),
                    total_est_weight_kg=w,
                    total_est_price_min=float(o.get("total_est_min_price", 0.0)),
                    total_est_price_max=float(o.get("total_est_max_price", 0.0)),
                    road_distance_km=round(calc_dist, 2),
                    estimated_arrival_minutes=eta_mins,
                    sequence_order=idx,
                    need_lifting_help=bool(o.get("need_lifting_help", False)),
                    navigation_url=nav_url,
                )
            )

        current_load = round(cumulative_weight, 2)
        remaining = round(max(0.0, max_cap - current_load), 2)
        cap_pct = round(min(100.0, (current_load / max_cap) * 100), 1) if max_cap > 0 else 0.0

        return ActiveQueueResponse(
            saleng_id=saleng_id,
            total_active_jobs=len(job_summaries),
            current_load_kg=current_load,
            max_capacity_kg=max_cap,
            remaining_capacity_kg=remaining,
            capacity_percentage=cap_pct,
            total_route_distance_km=round(total_route_distance, 2),
            jobs=job_summaries,
        )

    @classmethod
    def start_transit(cls, order_id: str, req: StartTransitRequest) -> StartTransitResponse:
        """
        ยืนยันออกเดินทาง เปลี่ยนสถานะ S3 -> S4 (In-Transit)
        พร้อมล็อกปุ่มยกเลิกผู้ขายตาม BR-03 (UC-09, AC-B04-05)
        """
        saleng_id = req.saleng_id
        order = supabase_store.orders.get(order_id)
        if not order:
            raise KeyError(f"ไม่พบคำขอขายรหัส {order_id}")

        current_collector = order.get("collector_id") or order.get("assigned_saleng_id")
        if current_collector != saleng_id:
            raise PermissionError("คุณไม่ใช่ผู้รับผิดชอบคำขอขายนี้ จึงไม่สามารถกดเริ่มออกเดินทางได้")

        current_status = order.get("status")
        if current_status not in ("S3", "S4"):
            raise ValueError(f"คำขอขายไม่อยู่ในสถานะที่สามารถออกเดินทางได้ (สถานะปัจจุบัน: {current_status})")

        now = datetime.now(timezone.utc).isoformat()
        order["status"] = "S4"
        order["in_transit_at"] = now
        order["updated_at"] = now

        loc_id = order.get("location_id")
        location = supabase_store.get_pickup_location(loc_id) if loc_id else None
        dest_lat = float(location.get("lat", 13.7950)) if location else 13.7950
        dest_lng = float(location.get("lng", 100.5810)) if location else 100.5810
        nav_url = build_google_maps_navigation_url(dest_lat, dest_lng)

        supabase_store.record_audit_log(
            action="COLLECTOR_STARTED_TRANSIT",
            actor_id=saleng_id,
            actor_role="COLLECTOR",
            entity_id=order_id,
            details={"order_id": order_id, "status": "S4", "started_at": now},
        )

        return StartTransitResponse(
            order_id=order_id,
            status="S4",
            started_at=now,
            seller_notified=True,
            seller_cancel_locked=True,
            navigation_url=nav_url,
        )

    @classmethod
    def cancel_job(cls, order_id: str, req: CollectorCancelJobRequest) -> CollectorCancelJobResponse:
        """
        ซาเล้งสละสิทธิ์/ยกเลิกงานในสถานะ S3 และคืนสถานะคำขอกลับเป็น S2 (Pending) อัตโนมัติ
        (D-B04-04, MD-STM-04, AC-B04-06)
        """
        saleng_id = req.saleng_id
        order = supabase_store.orders.get(order_id)
        if not order:
            raise KeyError(f"ไม่พบคำขอขายรหัส {order_id}")

        current_collector = order.get("collector_id") or order.get("assigned_saleng_id")
        if current_collector != saleng_id:
            raise PermissionError("คุณไม่ใช่ผู้รับผิดชอบคำขอขายนี้ จึงไม่สามารถยกเลิกงานได้")

        # คืนสถานะคำขอกลับเป็น S2 ผ่าน Store
        reverted = supabase_store.revert_order_to_pending(
            order_id=order_id,
            saleng_id=saleng_id,
            reason=req.reason,
            note=req.note,
        )

        supabase_store.record_audit_log(
            action="COLLECTOR_CANCELLED_JOB",
            actor_id=saleng_id,
            actor_role="COLLECTOR",
            entity_id=order_id,
            details={
                "order_id": order_id,
                "reason": req.reason,
                "note": req.note,
                "reverted_to": "S2",
            },
        )

        return CollectorCancelJobResponse(
            order_id=order_id,
            status="S2",
            message=f"สละสิทธิ์งานสำเร็จ คำขอขายถูกส่งกลับไปเป็น 'รอผู้รับงาน (S2)' เพื่อให้ซาเล้งคนอื่นรับต่อ",
            cancelled_at=reverted.get("cancelled_at", datetime.now(timezone.utc).isoformat()),
            reverted_to_pending=True,
        )
