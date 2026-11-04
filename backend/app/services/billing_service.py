"""
Buyer Billing & Receipt Service (บริการคิดเงินและออกใบเสร็จฝั่งซาเล้ง)
รองรับ UC-05, UC-06, UC-07, REQ-FN-002, REQ-FN-004, REQ-FN-005, REQ-BR-002, REQ-SEC-001, REQ-SEC-002, REQ-OP-001, CC-01, CC-04, CC-06, D-B06-01..06
"""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import uuid

from backend.app.core.supabase import supabase_store
from backend.app.models.billing_models import (
    WeighingItemInput,
    SubmitWeighingRequest,
    WeighingSheetItem,
    WeighingSheetResponse,
    WeighingResultResponse,
    SelectPaymentMethodRequest,
    PaymentMethodSelectionResponse,
    DigitalReceiptItem,
    DigitalReceiptSummaryResponse,
)


def mask_phone(phone: Optional[str]) -> str:
    """
    ปกปิดเบอร์โทรศัพท์ตามรูปแบบ 08X-XXX-XXXX (REQ-SEC-002, CC-06)
    เช่น 0812345678 -> 08X-XXX-5678
    """
    if not phone:
        return "XXX-XXX-XXXX"
    digits = "".join(ch for ch in str(phone) if ch.isdigit())
    if len(digits) < 6:
        return "XXX-XXX-XXXX"
    return f"{digits[:2]}X-XXX-{digits[-4:]}"


class BillingService:
    def __init__(self, store=supabase_store):
        self.store = store
        self._processed_idempotency: Dict[str, WeighingResultResponse] = {}

    def _verify_saleng_kyc(self, saleng_id: str) -> dict:
        """ตรวจสอบสถานะการยืนยันตัวตน KYC ของซาเล้ง (D-00-01)"""
        collector = self.store.saleng_profiles.get(saleng_id)
        if not collector:
            raise KeyError(f"ไม่พบโปรไฟล์ซาเล้งรหัส {saleng_id}")
        if not collector.get("verified") or collector.get("kyc_status") != "VERIFIED":
            raise PermissionError("ต้องผ่านการยืนยันตัวตน KYC ก่อนจึงจะเข้าใช้งานระบบคิดเงินและออกใบเสร็จได้ (D-00-01)")
        return collector

    def get_weighing_sheet(self, order_id: str, saleng_id: str) -> WeighingSheetResponse:
        """
        ดึงข้อมูลใบชั่งน้ำหนักหน้างานสำหรับซาเล้ง (UC-05, REQ-FN-002, REQ-BR-002)
        """
        self._verify_saleng_kyc(saleng_id)
        order = self.store.get_order(order_id)
        if not order:
            raise KeyError(f"ไม่พบคำขอขายรหัส {order_id}")

        # ตรวจสอบสิทธิ์การเข้าถึงใบงาน
        assigned_saleng = order.get("buyer_id") or order.get("saleng_id")
        if assigned_saleng and assigned_saleng != saleng_id:
            raise PermissionError("ไม่มีสิทธิ์เข้าถึงใบชั่งน้ำหนักของคำขอขายนี้")

        # ตรวจสอบข้อมูลผู้ขาย
        seller_id = order.get("seller_id", "seller-01")
        seller = self.store.sellers.get(seller_id) or {}
        raw_seller_phone = order.get("seller_phone") or seller.get("phone")
        seller_phone_masked = mask_phone(raw_seller_phone)

        # รวบรวมรายการสิ่งของ
        items_data = order.get("items", [])
        if not items_data:
            items_data = [item for item in self.store.items.values() if item.get("order_id") == order_id]

        sheet_items: List[WeighingSheetItem] = []
        for it in items_data:
            cat_code = it.get("category_code", "UNKNOWN")
            bench = self.store.get_price_by_category(cat_code)
            cat_name = it.get("category_name") or (bench["category_name"] if bench else cat_code)
            locked_price = it.get("locked_unit_price") or it.get("unit_price") or it.get("est_min_price") or 0.0

            sheet_items.append(
                WeighingSheetItem(
                    item_id=it.get("item_id", ""),
                    category_code=cat_code,
                    category_name=cat_name,
                    estimated_quantity=float(it.get("estimated_quantity") or it.get("est_quantity") or 0.0),
                    actual_quantity=it.get("actual_quantity"),
                    unit=it.get("unit", "กก."),
                    locked_unit_price=float(locked_price),
                    settled_item_price=it.get("settled_item_price"),
                )
            )

        return WeighingSheetResponse(
            order_id=order_id,
            order_status=order.get("status", "S4"),
            seller_name=order.get("seller_name") or seller.get("display_name", "ผู้ขาย"),
            seller_phone_masked=seller_phone_masked,
            scale_photo_url=order.get("scale_photo_url"),
            seller_confirmed_weight=order.get("seller_confirmed_weight", False),
            total_settled_amount=order.get("total_settled_amount"),
            payment_method=order.get("payment_method"),
            items=sheet_items,
        )

    def submit_weighing(self, order_id: str, request: SubmitWeighingRequest) -> WeighingResultResponse:
        """
        บันทึกผลชั่งจริงหน้างานโดยซาเล้ง (S4 -> S5)
        คำนวณราคาด้วย locked_unit_price (REQ-BR-002, D-B06-03)
        บังคับแนบรูปถ่ายตาชั่ง (REQ-FN-002, D-B06-02)
        ตรวจสอบเกณฑ์ ±15% (MD-STM-04)
        """
        self._verify_saleng_kyc(request.saleng_id)

        # ตรวจสอบ Idempotency Key (REQ-OP-001)
        if request.idempotency_key and request.idempotency_key in self._processed_idempotency:
            return self._processed_idempotency[request.idempotency_key]

        order = self.store.get_order(order_id)
        if not order:
            raise KeyError(f"ไม่พบคำขอขายรหัส {order_id}")

        # ตรวจสอบสถานะใบงาน ต้องอยู่ใน S4 หรือ S5 (กรณีชั่งใหม่)
        current_status = order.get("status")
        if current_status not in ["S3", "S4", "S5"]:
            raise ValueError(f"ไม่สามารถบันทึกผลชั่งจริงได้ คำขอขายอยู่ในสถานะ {current_status} (ต้องเป็น S4 หรือ S5)")

        # บังคับรูปตาชั่ง (REQ-FN-002, D-B06-02)
        if not request.scale_photo_url or not request.scale_photo_url.strip():
            raise ValueError("จำเป็นต้องแนบภาพถ่ายหน้าตาชั่งดิจิทัล (scale_photo_url) เพื่อเป็นหลักฐาน (REQ-FN-002)")

        if not request.items:
            raise ValueError("ต้องมีรายการน้ำหนักชั่งจริงอย่างน้อย 1 รายการ")

        # ดึงรายการสิ่งของเดิมใน order
        items_map = {item.get("item_id"): item for item in order.get("items", [])}
        if not items_map:
            items_map = {item["item_id"]: item for item in self.store.items.values() if item.get("order_id") == order_id}

        total_settled = 0.0
        total_estimated = 0.0
        total_actual = 0.0

        for w_item in request.items:
            if w_item.actual_quantity <= 0:
                raise ValueError(f"น้ำหนักชั่งจริงของรายการ {w_item.item_id} ต้องมากกว่า 0 (REQ-FN-002)")

            if w_item.item_id not in items_map:
                raise KeyError(f"ไม่พบรายการรหัส {w_item.item_id} ในคำขอขายนี้")

            item = items_map[w_item.item_id]
            locked_price = item.get("locked_unit_price") or item.get("unit_price") or item.get("est_min_price") or 0.0
            item_settled = round(w_item.actual_quantity * locked_price, 2)
            total_settled += item_settled

            est_qty = float(item.get("estimated_quantity") or item.get("est_quantity") or 0.0)
            total_estimated += est_qty
            total_actual += w_item.actual_quantity

            # อัปเดตรายการใน store
            self.store.update_item(w_item.item_id, {
                "actual_quantity": w_item.actual_quantity,
                "settled_item_price": item_settled,
                "locked_unit_price": locked_price,
            })

        total_settled = round(total_settled, 2)

        # คำนวณส่วนต่างปริมาณ ±15% (MD-STM-04)
        is_re_quote = False
        if total_estimated > 0:
            diff_ratio = abs(total_actual - total_estimated) / total_estimated
            if diff_ratio > 0.15:
                is_re_quote = True

        # อัปเดตสถานะ order เป็น S5 (รอผู้ขายกดยืนยันน้ำหนัก 100% Confirmation Gate)
        self.store.update_order(order_id, {
            "status": "S5",
            "scale_photo_url": request.scale_photo_url,
            "total_settled_amount": total_settled,
            "seller_confirmed_weight": False,
            "seller_confirmed_weight_at": None,
            "is_re_quote": is_re_quote,
        })

        # บันทึก Audit Log (REQ-SEC-001)
        self.store.add_audit_log(
            action="COLLECTOR_RECORDED_WEIGHING",
            entity_id=order_id,
            actor_id=request.saleng_id,
            details={
                "actor_role": "COLLECTOR",
                "previous_status": current_status,
                "new_status": "S5",
                "total_settled_amount": total_settled,
                "scale_photo_url": request.scale_photo_url,
                "is_re_quote": is_re_quote,
                "items_count": len(request.items),
            }
        )

        response = WeighingResultResponse(
            status="success",
            order_id=order_id,
            new_status="S5",
            is_re_quote=is_re_quote,
            total_settled_amount=total_settled,
            scale_photo_url=request.scale_photo_url,
            seller_confirmed_weight=False,
        )

        if request.idempotency_key:
            self._processed_idempotency[request.idempotency_key] = response

        return response

    def select_payment_method(self, order_id: str, request: SelectPaymentMethodRequest) -> PaymentMethodSelectionResponse:
        """
        เลือกช่องทางการชำระเงินหน้างาน (D-B06-04)
        บล็อกการทำงานจนกว่าผู้ขายจะกดยืนยันน้ำหนัก 100% (REQ-FN-004, AC-B06-03, D-B06-01)
        """
        self._verify_saleng_kyc(request.saleng_id)
        order = self.store.get_order(order_id)
        if not order:
            raise KeyError(f"ไม่พบคำขอขายรหัส {order_id}")

        # 100% Confirmation Gate (REQ-FN-004, AC-B06-03, D-B06-01)
        # ตรวจสอบว่าผู้ขายกดยืนยันผลการชั่งน้ำหนักแล้วหรือยัง
        if not order.get("seller_confirmed_weight") and order.get("status") != "S6":
            raise PermissionError(
                "ผู้ขายยังไม่ได้ยืนยันผลการชั่งน้ำหนัก (100% Confirmation Gate) "
                "กรุณารอการยืนยันจากหน้าจอผู้ขายก่อนเลือกชำระเงิน"
            )

        method = request.payment_method.upper().strip()
        if method not in ["CASH", "PROMPTPAY"]:
            raise ValueError("ช่องทางการชำระเงินต้องเป็น 'CASH' หรือ 'PROMPTPAY' เท่านั้น (D-B06-04)")

        # อัปเดตช่องทางการชำระเงิน
        self.store.update_order_payment_method(order_id, method)

        # บันทึก Audit Log (REQ-SEC-001)
        self.store.add_audit_log(
            action="COLLECTOR_SELECTED_PAYMENT_METHOD",
            entity_id=order_id,
            actor_id=request.saleng_id,
            details={
                "actor_role": "COLLECTOR",
                "payment_method": method,
                "order_status": order.get("status", "S6"),
            }
        )

        return PaymentMethodSelectionResponse(
            status="success",
            order_id=order_id,
            payment_method=method,
            order_status=order.get("status", "S6"),
        )

    def get_receipt(self, order_id: str, saleng_id: str) -> DigitalReceiptSummaryResponse:
        """
        ดึงข้อมูลใบเสร็จสรุปรายการดิจิทัลเมื่อจบงาน (S7) พร้อม Mask เบอร์โทรศัพท์ (REQ-FN-005, REQ-SEC-002, CC-06)
        """
        collector = self._verify_saleng_kyc(saleng_id)
        order = self.store.get_order(order_id)
        if not order:
            raise KeyError(f"ไม่พบคำขอขายรหัส {order_id}")

        # สองฝ่ายต้องยืนยันจบงานแล้ว (สถานะต้องเป็น S7)
        if order.get("status") != "S7":
            raise ValueError(
                f"คำขอขายยังไม่อยู่ในสถานะเสร็จสิ้น (S7) สถานะปัจจุบันคือ {order.get('status')} "
                "ผู้ขายต้องกดยืนยันการรับเงินก่อนจึงจะออกใบเสร็จได้"
            )

        seller_id = order.get("seller_id", "seller-01")
        seller = self.store.sellers.get(seller_id) or {}
        raw_seller_phone = order.get("seller_phone") or seller.get("phone")
        raw_collector_phone = collector.get("phone")

        receipt_id = order.get("receipt_id") or f"REC-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{order_id[:4].upper()}"
        issued_at = order.get("payment_confirmed_at") or order.get("completed_at") or datetime.now(timezone.utc).isoformat()

        items_data = order.get("items", [])
        if not items_data:
            items_data = [item for item in self.store.items.values() if item.get("order_id") == order_id]

        receipt_items: List[DigitalReceiptItem] = []
        for it in items_data:
            cat_code = it.get("category_code", "UNKNOWN")
            bench = self.store.get_price_by_category(cat_code)
            cat_name = it.get("category_name") or (bench["category_name"] if bench else cat_code)
            actual_qty = float(it.get("actual_quantity") or 0.0)
            locked_price = float(it.get("locked_unit_price") or it.get("unit_price") or 0.0)
            settled_price = float(it.get("settled_item_price") or round(actual_qty * locked_price, 2))

            receipt_items.append(
                DigitalReceiptItem(
                    category_name=cat_name,
                    actual_quantity=actual_qty,
                    unit=it.get("unit", "กก."),
                    locked_unit_price=locked_price,
                    settled_item_price=settled_price,
                )
            )

        return DigitalReceiptSummaryResponse(
            receipt_id=receipt_id,
            order_id=order_id,
            issued_at=issued_at,
            seller_name=order.get("seller_name") or seller.get("display_name", "ผู้ขาย"),
            seller_phone_masked=mask_phone(raw_seller_phone),
            collector_name=collector.get("name", "สมชาย ซาเล้ง"),
            collector_phone_masked=mask_phone(raw_collector_phone),
            payment_method=order.get("payment_method", "CASH"),
            total_settled_amount=float(order.get("total_settled_amount") or 0.0),
            items=receipt_items,
        )


billing_service = BillingService()

