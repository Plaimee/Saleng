"""
Service Layer สำหรับระบบหลังทำธุรกรรม (Post-Transaction Service)
รองรับ UC-10, SC-05, REQ-FN-005, REQ-SEC-001, REQ-SEC-002, AC-S07-01..05, P-01..P-05
"""

from typing import Dict, List, Optional
from fastapi import HTTPException, status
from backend.app.core.supabase import supabase_store
from backend.app.services.payment_service import mask_phone


class PostTransactionService:
    """
    บริการจัดการกิจกรรมหลังจบการซื้อขาย:
    1. ส่งคะแนนรีวิวและประเมินบริการซาเล้ง (UC-10, AC-S07-01, P-01)
    2. จัดการผู้รับซื้อประจำ Bookmark (UC-10, AC-S07-02, P-02)
    3. ดึงประวัติการขาย สรุปสถิติสะสม และ PII Masking (REQ-FN-005, REQ-SEC-002, AC-S07-03, P-03)
    """

    @staticmethod
    def submit_review(
        order_id: str,
        seller_id: str,
        rating: int,
        comment: Optional[str] = None
    ) -> Dict:
        """
        บันทึกคะแนนรีวิวของซาเล้งหลังจบงาน (AC-S07-01, P-01, Q-01, Q-02)
        - ต้องเป็นคำขอสถานะ S7: Completed
        - ผู้เรียกต้องเป็นผู้ขายเจ้าของคำขอ (seller_id)
        - ส่งได้เพียง 1 ครั้งต่อคำขอ (ห้ามส่งซ้ำ 409 Conflict)
        - บันทึก Audit Log SELLER_SUBMIT_REVIEW
        """
        order = supabase_store.get_order(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ไม่พบคำขอรหัส: {order_id}"
            )

        # ตรวจสอบสถานะต้องเป็น S7 เท่านั้น (CC-03, MD-STM-04)
        if order.get("status") != "S7":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="สามารถส่งรีวิวได้เฉพาะคำขอที่จบงานสมบูรณ์แล้ว (S7) เท่านั้น"
            )

        # ตรวจสอบความเป็นเจ้าของคำขอ
        if order.get("seller_id") != seller_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="ไม่มีสิทธิ์ส่งรีวิวสำหรับคำขอนี้ เนื่องจากไม่ใช่ผู้ขายของคำขอ"
            )

        # ตรวจสอบการส่งรีวิวซ้ำ (P-01, Q-02)
        existing_review = supabase_store.get_review_by_order(order_id)
        if existing_review:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="คำขอนี้ได้รับการส่งรีวิวแล้ว ไม่สามารถส่งซ้ำหรือแก้ไขได้"
            )

        # ตรวจสอบค่าคะแนนดาว
        if rating < 1 or rating > 5:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="คะแนนดาวต้องอยู่ระหว่าง 1 ถึง 5 ดาว"
            )

        # ตรวจสอบความยาวคอมเมนต์
        if comment and len(comment) > 500:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="ข้อความรีวิวต้องมีความยาวไม่เกิน 500 ตัวอักษร"
            )

        collector_id = order.get("collector_id") or "COLLECTOR-DEFAULT"

        review_data = {
            "order_id": order_id,
            "seller_id": seller_id,
            "collector_id": collector_id,
            "rating": rating,
            "comment": comment,
        }

        created_review = supabase_store.create_review(review_data)

        # บันทึก Audit Log (REQ-SEC-001, AC-S07-05)
        supabase_store.add_audit_log(
            action="SELLER_SUBMIT_REVIEW",
            entity_id=order_id,
            actor_id=seller_id,
            details={
                "rating": rating,
                "collector_id": collector_id,
                "review_id": created_review["id"],
            }
        )

        return created_review

    @staticmethod
    def get_review(order_id: str) -> Optional[Dict]:
        """ดึงข้อมูลรีวิวของคำขอ (หากมี)"""
        review = supabase_store.get_review_by_order(order_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ไม่พบรีวิวสำหรับคำขอรหัส: {order_id}"
            )
        return review

    @staticmethod
    def toggle_favorite(seller_id: str, collector_id: str) -> Dict:
        """
        สลับสถานะ (Toggle) บันทึก/ยกเลิกซาเล้งเป็นผู้รับซื้อประจำ (AC-S07-02, P-02, Q-03)
        """
        is_fav = supabase_store.is_favorite(seller_id, collector_id)
        if is_fav:
            supabase_store.remove_favorite(seller_id, collector_id)
            action = "SELLER_REMOVE_FAVORITE"
            message = "ยกเลิกผู้รับซื้อประจำเรียบร้อยแล้ว"
            new_fav_status = False
        else:
            supabase_store.add_favorite(seller_id, collector_id)
            action = "SELLER_ADD_FAVORITE"
            message = "บันทึกเป็นผู้รับซื้อประจำเรียบร้อยแล้ว"
            new_fav_status = True

        # บันทึก Audit Log (REQ-SEC-001, AC-S07-05)
        supabase_store.add_audit_log(
            action=action,
            entity_id=collector_id,
            actor_id=seller_id,
            details={"is_favorite": new_fav_status}
        )

        return {
            "seller_id": seller_id,
            "collector_id": collector_id,
            "is_favorite": new_fav_status,
            "message": message,
        }

    @staticmethod
    def get_favorites(seller_id: str) -> List[str]:
        """ดึงรายการรหัสซาเล้งที่เป็นผู้รับซื้อประจำของผู้ขาย (AC-S07-02)"""
        return supabase_store.get_seller_favorites(seller_id)

    @staticmethod
    def get_sales_history(seller_id: str) -> Dict:
        """
        ดึงประวัติการขายที่ปิดงานสำเร็จ (S7) พร้อมสรุปสถิติสะสม 3 ด้าน และ PII Masking (AC-S07-03, P-03)
        """
        completed_orders = supabase_store.get_completed_orders_for_seller(seller_id)

        total_amount = 0.0
        total_weight = 0.0
        orders_history_list = []

        favorite_collectors = set(supabase_store.get_seller_favorites(seller_id))

        for o in completed_orders:
            order_id = o["order_id"]
            collector_id = o.get("collector_id") or "UNKNOWN_COLLECTOR"
            collector_name = o.get("collector_name") or "ลุงสมคิด (ซาเล้ง)"
            raw_phone = o.get("buyer_phone") or o.get("collector_phone") or "0899887766"
            collector_phone_masked = mask_phone(raw_phone)

            # ยอดเงินสุทธิจริงของใบงานนี้
            settled_amount = float(o.get("total_settled_amount") or o.get("total_amount") or 0.0)
            total_amount += settled_amount

            # รายการวัสดุ
            items_list = []
            order_weight = 0.0
            for item in o.get("items", []):
                qty = float(item.get("actual_quantity") or item.get("quantity") or 0.0)
                unit_price = float(item.get("locked_unit_price") or 0.0)
                item_price = float(item.get("settled_item_price") or (qty * unit_price))
                order_weight += qty

                items_list.append({
                    "category_code": item.get("category_code", ""),
                    "category_name": item.get("category_name", ""),
                    "actual_quantity": qty,
                    "unit": item.get("unit", "kg"),
                    "locked_unit_price": unit_price,
                    "settled_item_price": item_price,
                })

            total_weight += order_weight

            # ดึงใบเสร็จถ้ามี
            receipt = supabase_store.get_receipt_by_order(order_id)
            receipt_no = receipt.get("receipt_no") if receipt else None

            # ตรวจสอบว่าเคยรีวิวแล้วหรือไม่
            has_reviewed = supabase_store.get_review_by_order(order_id) is not None

            orders_history_list.append({
                "order_id": order_id,
                "completed_at": o.get("payment_confirmed_at") or o.get("created_at") or "",
                "collector_id": collector_id,
                "collector_name": collector_name,
                "collector_phone_masked": collector_phone_masked,
                "is_favorite_collector": collector_id in favorite_collectors,
                "total_settled_amount": round(settled_amount, 2),
                "payment_method": o.get("payment_method") or "CASH",
                "receipt_no": receipt_no,
                "items": items_list,
                "status": "S7",
                "has_reviewed": has_reviewed,
            })

        summary = {
            "total_sales_amount": round(total_amount, 2),
            "total_weight_kg": round(total_weight, 2),
            "total_completed_orders": len(completed_orders),
        }

        return {
            "seller_id": seller_id,
            "summary": summary,
            "orders": orders_history_list,
        }

