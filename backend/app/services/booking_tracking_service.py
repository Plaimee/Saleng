"""
Booking & Status Tracking Service: นัดหมาย ติดตาม 9 สถานะ และบังคับใช้กฎเหล็กการยกเลิก BR-03
รองรับ UC-04, MD-STM-04, BR-03, REQ-FN-003, REQ-SEC-001, REQ-SEC-002, CC-02, CC-03, AC-S05-01..05, P-01..P-06
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from backend.app.core.supabase import supabase_store
from backend.app.models.booking_tracking_models import (
    BookingSlotRequest,
    OrderCancellationRequest,
    OrderTrackingResponse,
    SimulateStatusRequest,
)


class BookingTrackingService:
    STATUS_LABELS = {
        "S1": "ฉบับร่าง (กำลังเตรียมคำขอ)",
        "S2": "รอผู้รับซื้อ (กระจายคำขอสู่เส้นทาง)",
        "S3": "มีผู้รับงานแล้ว (ซาเล้งยืนยันรับงาน)",
        "S4": "กำลังเดินทาง (ซาเล้งกำลังเดินทางมาหาคุณ)",
        "S5": "ถึงจุดนัดหมายและชั่งของหน้างาน",
        "S6": "รอยืนยันชำระเงิน",
        "S7": "สำเร็จ / ปิดงานเรียบร้อย",
        "S8": "ยกเลิกคำขอแล้ว",
        "S9": "ระงับชั่วคราว / ข้อพิพาท",
    }

    STEP_MAPPING = {
        "S1": 1,
        "S2": 1,
        "S3": 2,
        "S4": 3,
        "S5": 4,
        "S6": 5,
        "S7": 5,
        "S8": 0,
        "S9": 0,
    }

    SLOT_LABELS = {
        "MORNING_09_12": "ช่วงเช้า (09:00 – 12:00 น.)",
        "AFTERNOON_13_16": "ช่วงบ่าย (13:00 – 16:00 น.)",
        "EVENING_16_18": "ช่วงเย็น (16:00 – 18:00 น.)",
    }

    @staticmethod
    def book_order_slot(
        order_id: str, req: BookingSlotRequest, seller_id: str = "seller-01"
    ) -> OrderTrackingResponse:
        """
        เลือกช่วงเวลานัดหมายและยืนยันส่งคำขอ S1 -> S2 (AC-S05-01, P-01, Q-01)
        """
        order = supabase_store.get_order(order_id)
        if not order:
            order = {
                "order_id": order_id,
                "seller_id": seller_id,
                "status": "S1",
                "items": [],
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            supabase_store.orders[order_id] = order

        # ตรวจสอบรูปแบบการนัดหมาย
        booking_type = req.booking_type.upper()
        if booking_type not in ["IMMEDIATE", "SCHEDULED"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="รูปแบบการนัดหมายต้องเป็น IMMEDIATE หรือ SCHEDULED เท่านั้น",
            )

        if booking_type == "SCHEDULED" and not req.scheduled_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="การนัดหมายล่วงหน้าต้องระบุวันที่นัดหมาย (scheduled_date)",
            )

        order["booking_type"] = booking_type
        order["scheduled_date"] = req.scheduled_date
        order["scheduled_slot"] = req.scheduled_slot
        if req.notes:
            order["appointment_notes"] = req.notes

        # เปลี่ยนสถานะจาก S1 เป็น S2 (Pending / Open)
        old_status = order.get("status", "S1")
        if old_status == "S1":
            order["status"] = "S2"

        order["updated_at"] = datetime.now(timezone.utc).isoformat()
        supabase_store.orders[order_id] = order

        # บันทึก Audit Log (REQ-SEC-001, P-01)
        supabase_store.add_audit_log(
            action="ORDER_SUBMITTED",
            entity_id=order_id,
            actor_id=seller_id,
            details={
                "booking_type": booking_type,
                "scheduled_date": req.scheduled_date,
                "scheduled_slot": req.scheduled_slot,
                "from_status": old_status,
                "to_status": order["status"],
            },
        )

        return BookingTrackingService.get_order_status(order_id, seller_id)

    @staticmethod
    def get_order_status(
        order_id: str, seller_id: str = "seller-01"
    ) -> OrderTrackingResponse:
        """
        ดึงสถานะความคืบหน้าคำขอ Stepper Timeline และข้อมูลซาเล้ง (AC-S05-02, AC-S05-04)
        """
        order = supabase_store.get_order(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ไม่พบคำขอนัดหมายรหัส {order_id}",
            )

        current_status = order.get("status", "S1")
        status_label = BookingTrackingService.STATUS_LABELS.get(
            current_status, current_status
        )
        stepper_step = BookingTrackingService.STEP_MAPPING.get(current_status, 1)

        # ตรวจสอบสิทธิ์การยกเลิกตามกฎเหล็ก BR-03 (P-03)
        # ผู้ขายยกเลิกได้เฉพาะก่อนที่ซาเล้งออกเดินทาง (S1..S3) เท่านั้น
        can_cancel = current_status in ["S1", "S2", "S3"]

        # จัดรูปแบบการแสดงผลเวลานัดหมาย
        b_type = order.get("booking_type", "IMMEDIATE")
        if b_type == "IMMEDIATE":
            time_display = "เรียกทันที (ด่วนใน 1–2 ชม.)"
        else:
            date_str = order.get("scheduled_date", "-")
            slot_code = order.get("scheduled_slot", "")
            slot_label = BookingTrackingService.SLOT_LABELS.get(slot_code, slot_code)
            time_display = f"วันที่ {date_str} {slot_label}"

        # ข้อมูลซาเล้งที่รับงาน (หากมี)
        assigned_saleng_data = None
        saleng_id = order.get("assigned_saleng_id")
        if saleng_id:
            raw_saleng = supabase_store.get_saleng_profile(saleng_id)
            if raw_saleng:
                assigned_saleng_data = {
                    "saleng_id": raw_saleng["saleng_id"],
                    "display_name": raw_saleng["display_name"],
                    "phone": raw_saleng["phone"],
                    "avatar_url": raw_saleng.get("avatar_url"),
                    "verified": raw_saleng.get("verified", True),
                    "rating": raw_saleng.get("rating", 5.0),
                    "vehicle_type": raw_saleng.get("vehicle_type", "TRICYCLE"),
                }

        # คำนวณระยะทางและ ETA หากอยู่ในสถานะ S4 (In-Transit)
        eta_minutes = None
        distance_km = None
        if current_status == "S4":
            distance_km = order.get("in_transit_distance_km", 1.5)
            # ประเมิน ETA ~4 นาทีต่อ 1 กม.
            eta_minutes = max(3, int(distance_km * 4))

        # นับจำนวนรายการของเก่า
        items = [
            it for it in supabase_store.items.values() if it.get("order_id") == order_id
        ]
        items_count = len(items)

        total_est = order.get(
            "total_estimated_price", {"min_price": 0.0, "max_price": 0.0}
        )

        return OrderTrackingResponse(
            order_id=order_id,
            seller_id=order.get("seller_id", seller_id),
            status=current_status,
            status_label=status_label,
            stepper_step=stepper_step,
            booking_type=b_type,
            scheduled_time_display=time_display,
            assigned_saleng=assigned_saleng_data,
            eta_minutes=eta_minutes,
            distance_km=distance_km,
            can_cancel=can_cancel,
            cancellation_reason=order.get("cancellation_reason"),
            items_count=items_count,
            total_estimated_price=total_est,
            updated_at=order.get("updated_at", datetime.now(timezone.utc).isoformat()),
        )

    @staticmethod
    def cancel_order(
        order_id: str, req: OrderCancellationRequest, seller_id: str = "seller-01"
    ) -> OrderTrackingResponse:
        """
        ยกเลิกนัดหมายของผู้ขายพร้อมบังคับใช้กฎเหล็ก BR-03 (AC-S05-03, P-03, Q-02)
        """
        order = supabase_store.get_order(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ไม่พบคำขอนัดหมายรหัส {order_id}",
            )

        current_status = order.get("status", "S1")

        # บังคับใช้กฎเหล็ก BR-03: ล็อกห้ามยกเลิกเมื่อเข้าสู่ S4 (In-Transit) ขึ้นไป
        if current_status in ["S4", "S5", "S6", "S7"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ไม่สามารถยกเลิกนัดหมายได้เนื่องจากซาเล้งกำลังเดินทางมายังหน้างานแล้วตามกฎ BR-03",
            )

        if current_status in ["S8", "S9"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"คำขอนี้ถูกปิดไปแล้ว (สถานะ: {current_status})",
            )

        # อนุญาตให้ยกเลิกในสถานะ S1, S2, S3
        order["status"] = "S8"  # Cancelled
        order["cancellation_reason"] = req.reason
        order["cancelled_by"] = seller_id
        order["cancelled_at"] = datetime.now(timezone.utc).isoformat()
        order["updated_at"] = datetime.now(timezone.utc).isoformat()
        supabase_store.orders[order_id] = order

        # บันทึก Audit Log (REQ-SEC-001, P-03)
        supabase_store.add_audit_log(
            action="ORDER_CANCELLED_BY_SELLER",
            entity_id=order_id,
            actor_id=seller_id,
            details={
                "reason": req.reason,
                "from_status": current_status,
                "to_status": "S8",
            },
        )

        return BookingTrackingService.get_order_status(order_id, seller_id)

    @staticmethod
    def simulate_status_change(
        order_id: str, req: SimulateStatusRequest, seller_id: str = "seller-01"
    ) -> OrderTrackingResponse:
        """
        จำลองการเปลี่ยนสถานะสำหรับชุดทดสอบ (S2 -> S3 -> S4 -> S5 -> S6 -> S7)
        """
        order = supabase_store.get_order(order_id)
        if not order:
            order = {
                "order_id": order_id,
                "seller_id": seller_id,
                "status": "S1",
                "items": [],
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            supabase_store.orders[order_id] = order

        old_status = order.get("status", "S1")
        order["status"] = req.target_status

        if req.target_status in ["S3", "S4", "S5"]:
            order["assigned_saleng_id"] = req.saleng_id or "saleng-01"

        if req.target_status == "S4":
            order["in_transit_distance_km"] = 1.4

        order["updated_at"] = datetime.now(timezone.utc).isoformat()
        supabase_store.orders[order_id] = order

        # บันทึก Audit Log
        supabase_store.add_audit_log(
            action="STATUS_SIMULATED",
            entity_id=order_id,
            actor_id=seller_id,
            details={"from_status": old_status, "to_status": req.target_status},
        )

        return BookingTrackingService.get_order_status(order_id, seller_id)

