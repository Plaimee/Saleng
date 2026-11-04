"""
Post-Job Management Service for Saleng (บริการระบบหลังจบงานฝั่งซาเล้ง)
รองรับ UC-10, UC-13, REQ-FN-005, REQ-FN-006, REQ-SEC-001, REQ-SEC-002, CC-01, CC-04, CC-06, D-B07-01..06
"""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from backend.app.core.supabase import supabase_store
from backend.app.models.post_job_models import (
    PurchaseHistorySummary,
    PurchaseHistoryItem,
    PurchaseHistoryResponse,
    RegularCustomerItem,
    ToggleRegularCustomerRequest,
    ToggleRegularCustomerResponse,
    ReportSellerMismatchRequest,
    ReportSellerMismatchResponse,
)


def mask_phone(phone: Optional[str]) -> str:
    """ปกปิดเบอร์โทรศัพท์ตามรูปแบบ 08X-XXX-XXXX (REQ-SEC-002, CC-06)"""
    if not phone:
        return "XXX-XXX-XXXX"
    digits = "".join(ch for ch in str(phone) if ch.isdigit())
    if len(digits) < 6:
        return "XXX-XXX-XXXX"
    return f"{digits[:2]}X-XXX-{digits[-4:]}"


class PostJobService:
    def __init__(self, store=supabase_store):
        self.store = store

    def _verify_saleng_kyc(self, saleng_id: str) -> dict:
        """ตรวจสอบสถานะการยืนยันตัวตน KYC ของซาเล้ง (D-00-01)"""
        collector = self.store.saleng_profiles.get(saleng_id)
        if not collector:
            raise KeyError(f"ไม่พบโปรไฟล์ซาเล้งรหัส {saleng_id}")
        if not collector.get("verified") or collector.get("kyc_status") != "VERIFIED":
            raise PermissionError("ต้องผ่านการยืนยันตัวตน KYC ก่อนจึงจะเข้าใช้งานระบบหลังจบงานได้ (D-00-01)")
        return collector

    def get_purchase_history(self, saleng_id: str, period: str = "all") -> PurchaseHistoryResponse:
        """
        ดึงประวัติการรับซื้อของเก่าที่เสร็จสิ้นแล้ว (S7) พร้อมสรุปสถิติสะสม 3 มิติ (UC-10, REQ-FN-005, D-B07-05)
        """
        self._verify_saleng_kyc(saleng_id)

        # ดึงรายชื่อลูกค้าประจำเพื่อนำมาเทียบสถานะ is_regular_customer
        fav_sellers = {fav["seller_id"] for fav in self.store.get_collector_favorite_sellers(saleng_id)}

        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        month_str = datetime.now(timezone.utc).strftime("%Y-%m")

        history_items: List[PurchaseHistoryItem] = []

        for order in self.store.orders.values():
            assigned_saleng = order.get("buyer_id") or order.get("saleng_id") or order.get("assigned_saleng_id")
            if assigned_saleng != saleng_id:
                continue

            # กรองเฉพาะสถานะ S7: Completed
            if order.get("status") != "S7":
                continue

            completed_at = order.get("completed_at") or order.get("payment_confirmed_at") or order.get("created_at") or datetime.now(timezone.utc).isoformat()

            # กรองตามช่วงเวลา
            if period == "today" and not completed_at.startswith(today_str):
                continue
            elif period == "month" and not completed_at.startswith(month_str):
                continue

            order_id = order.get("order_id", "")
            seller_id = order.get("seller_id", "")
            seller = self.store.sellers.get(seller_id) or {}
            raw_phone = order.get("seller_phone") or seller.get("phone")
            masked_phone = mask_phone(raw_phone)
            seller_name = order.get("seller_name") or seller.get("display_name", f"คุณผู้ขาย {seller_id}")

            # ดึงรายการสิ่งของ
            order_items = [it for it in self.store.items.values() if it.get("order_id") == order_id]
            if not order_items and order.get("items"):
                order_items = order.get("items")

            total_weight = 0.0
            summaries = []
            for it in order_items:
                w = float(it.get("actual_quantity") or it.get("est_quantity") or it.get("estimated_quantity") or 0.0)
                total_weight += w
                c_name = it.get("category_name", "ของเก่า")
                u = it.get("unit", "กก.")
                summaries.append(f"{c_name} ({w:.1f} {u})")

            items_summary_str = ", ".join(summaries) if summaries else "ของเก่าคละรายการ"
            total_settled = float(order.get("total_settled_amount") or 0.0)

            history_items.append(
                PurchaseHistoryItem(
                    order_id=order_id,
                    completed_at=completed_at,
                    seller_name=seller_name,
                    seller_phone_masked=masked_phone,
                    total_settled_amount=total_settled,
                    total_weight_kg=round(total_weight, 2),
                    payment_method=order.get("payment_method", "CASH"),
                    status="S7",
                    is_regular_customer=(seller_id in fav_sellers),
                    items_summary=items_summary_str,
                    receipt_id=order.get("receipt_id"),
                )
            )

        # เรียงลำดับจากล่าสุดไปเก่าสุด
        history_items.sort(key=lambda x: x.completed_at, reverse=True)

        summary = PurchaseHistorySummary(
            total_expense_baht=round(sum(it.total_settled_amount for it in history_items), 2),
            total_weight_kg=round(sum(it.total_weight_kg for it in history_items), 2),
            total_completed_jobs=len(history_items),
        )

        return PurchaseHistoryResponse(
            period=period,
            summary=summary,
            items=history_items,
        )

    def get_regular_customers(self, saleng_id: str) -> List[RegularCustomerItem]:
        """ดึงรายชื่อลูกค้าประจำที่ซาเล้งปักหมุดไว้ (UC-10, AC-B07-02, D-B07-03)"""
        self._verify_saleng_kyc(saleng_id)
        raw_favs = self.store.get_collector_favorite_sellers(saleng_id)
        return [RegularCustomerItem(**f) for f in raw_favs]

    def toggle_regular_customer(self, saleng_id: str, req: ToggleRegularCustomerRequest) -> ToggleRegularCustomerResponse:
        """สลับสถานะ Toggle ปักหมุด/ยกเลิกลูกค้าประจำ (AC-B07-02)"""
        self._verify_saleng_kyc(saleng_id)

        is_fav, fav_data = self.store.toggle_collector_favorite_seller(
            collector_id=saleng_id,
            seller_id=req.seller_id,
            notes=req.notes,
            lat=req.latitude,
            lng=req.longitude,
            seller_name=req.seller_name,
            seller_phone_masked=req.seller_phone_masked,
        )

        action = "COLLECTOR_BOOKMARKED_CUSTOMER" if is_fav else "COLLECTOR_UNBOOKMARKED_CUSTOMER"
        msg = "บันทึกเป็นลูกค้าประจำเรียบร้อยแล้ว" if is_fav else "ยกเลิกการบันทึกลูกค้าประจำเรียบร้อยแล้ว"

        self.store.add_audit_log(
            action=action,
            entity_id=req.seller_id,
            actor_id=saleng_id,
            details={
                "actor_role": "COLLECTOR",
                "seller_id": req.seller_id,
                "is_favorite": is_fav,
                "notes": req.notes,
            }
        )

        return ToggleRegularCustomerResponse(
            status="success",
            seller_id=req.seller_id,
            is_favorite=is_fav,
            message=msg,
        )

    def report_seller_mismatch(self, order_id: str, req: ReportSellerMismatchRequest) -> ReportSellerMismatchResponse:
        """
        รายงานข้อพิพาทหน้างานกรณี No-show หรือของไม่ตรงสเปก (S3/S4 -> S8)
        รองรับ UC-13, REQ-FN-006, REQ-SEC-001, AC-B07-03, D-B07-01, D-B07-02
        """
        self._verify_saleng_kyc(req.saleng_id)
        order = self.store.get_order(order_id)
        if not order:
            raise KeyError(f"ไม่พบคำขอขายรหัส {order_id}")

        assigned_saleng = order.get("buyer_id") or order.get("saleng_id") or order.get("assigned_saleng_id")
        if assigned_saleng and assigned_saleng != req.saleng_id:
            raise PermissionError("ไม่มีสิทธิ์รายงานปัญหาของคำขอขายนี้")

        current_status = order.get("status")
        if current_status not in ["S3", "S4"]:
            raise ValueError(
                f"ไม่สามารถรายงานปัญหาหน้างานได้ คำขอขายอยู่ในสถานะ {current_status} "
                "(อนุญาตเฉพาะสถานะ S3: En Route หรือ S4: Weighing เท่านั้น ตาม D-B07-02)"
            )

        if not req.evidence_photo_url or not req.evidence_photo_url.strip():
            raise ValueError("จำเป็นต้องแนบภาพถ่ายหน้างานเป็นหลักฐาน (evidence_photo_url) เพื่อส่งต่อให้ Admin (REQ-FN-006)")

        # บันทึกรายงานข้อพิพาท
        dispute_data = {
            "order_id": order_id,
            "reporter_id": req.saleng_id,
            "reporter_role": "COLLECTOR",
            "mismatch_reason": req.mismatch_reason,
            "evidence_photo_url": req.evidence_photo_url.strip(),
            "notes": req.notes,
            "gps_lat": req.current_lat,
            "gps_lng": req.current_lng,
        }
        saved_dispute = self.store.create_dispute_report(dispute_data)

        # ปรับสถานะคำขอเป็น S8: Disputed และปลดล็อกซาเล้ง (D-B07-01)
        self.store.update_order(order_id, {
            "status": "S8",
            "dispute_id": saved_dispute["dispute_id"],
            "dispute_reason": req.mismatch_reason,
            "dispute_reported_at": datetime.now(timezone.utc).isoformat(),
            "active_collector_lock": False,
        })

        # บันทึก Audit Log (REQ-SEC-001)
        self.store.add_audit_log(
            action="COLLECTOR_REPORTED_MISMATCH",
            entity_id=order_id,
            actor_id=req.saleng_id,
            details={
                "actor_role": "COLLECTOR",
                "previous_status": current_status,
                "new_status": "S8",
                "dispute_id": saved_dispute["dispute_id"],
                "mismatch_reason": req.mismatch_reason,
                "evidence_photo_url": req.evidence_photo_url,
            }
        )

        return ReportSellerMismatchResponse(
            status="success",
            order_id=order_id,
            new_status="S8",
            dispute_id=saved_dispute["dispute_id"],
            message="ส่งรายงานข้อพิพาทให้ผู้ดูแลระบบ (Admin) ตรวจสอบเรียบร้อยแล้ว และปลดล็อกใบงานให้คุณรับงานถัดไปได้ทันที",
        )


post_job_service = PostJobService()

