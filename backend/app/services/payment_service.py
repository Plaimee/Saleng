"""
Payment & Verification Service
รองรับ REQ-FN-004, REQ-FN-005, REQ-FN-006, REQ-BR-002, REQ-SEC-001, REQ-SEC-002, AC-S06-01..05, P-01..P-06
"""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from backend.app.core.supabase import supabase_store
from backend.app.models.payment_models import (
    RecordWeighingRequest,
    WeighingRecordResponse,
    SettledItemOutput,
    WeightConfirmationRequest,
    WeightConfirmationResponse,
    RequestReweighRequest,
    DisputeRequest,
    DisputeResponse,
    PaymentConfirmationRequest,
    PaymentConfirmationResponse,
    DigitalReceiptResponse,
    DigitalReceiptItem,
)


def mask_phone(phone: Optional[str]) -> str:
    """
    ปกปิดเบอร์โทรศัพท์ตามรูปแบบ 08X-XXX-XXXX (คงเลข 2 หลักแรกและ 4 หลักท้าย)
    เช่น 0812345678 -> 08X-XXX-5678
    รองรับ REQ-SEC-002, CC-06, AC-S06-04
    """
    if not phone:
        # ไม่มีข้อมูลเบอร์โทร: ปกปิดทั้งหมด ไม่เดาค่า
        return "XXX-XXX-XXXX"
    digits = "".join(ch for ch in str(phone) if ch.isdigit())
    if len(digits) < 6:
        return "XXX-XXX-XXXX"
    return f"{digits[:2]}X-XXX-{digits[-4:]}"


class PaymentService:
    def __init__(self, store=supabase_store):
        self.store = store

    def record_weighing(self, order_id: str, request: RecordWeighingRequest) -> WeighingRecordResponse:
        """
        บันทึกผลชั่งจริงหน้างานโดยซาเล้ง พร้อมคำนวณยอดเงินสุทธิ
        รองรับ REQ-BR-002, P-03, D-04
        """
        order = self.store.get_order(order_id)
        if not order:
            raise ValueError(f"ไม่พบใบงานรหัส: {order_id}")

        # อนุญาตเฉพาะใบงานสถานะ S4 (ชั่งของหน้างาน) หรือ S5 (แก้ไขผลชั่งเดิม)
        if order["status"] not in ["S3", "S4", "S5"]:
            raise ValueError(f"ไม่สามารถบันทึกผลชั่งจริงได้ ใบงานอยู่ในสถานะ {order['status']} (ต้องเป็น S4 หรือ S5)")

        existing_items_map = {item["item_id"]: item for item in order.get("items", [])}
        total_settled = 0.0
        settled_outputs: List[SettledItemOutput] = []

        for w_item in request.items:
            if w_item.item_id not in existing_items_map:
                raise ValueError(f"ไม่พบรายการรหัส {w_item.item_id} ในใบงานนี้")

            item = existing_items_map[w_item.item_id]
            locked_price = item.get("locked_unit_price")
            if locked_price is None or locked_price <= 0:
                # กรณีฉุกเฉิน: ใช้ est_min_price ถ้ายังไม่มีราคาล็อก
                locked_price = item.get("est_min_price", 0.0)

            item_settled = round(w_item.actual_quantity * locked_price, 2)
            total_settled += item_settled

            # อัปเดตรายการในฐานข้อมูล
            self.store.update_item(w_item.item_id, {
                "actual_quantity": w_item.actual_quantity,
                "settled_item_price": item_settled,
                "locked_unit_price": locked_price,
            })

            # ดึงชื่อประเภทวัสดุ
            bench = self.store.get_price_by_category(item["category_code"])
            cat_name = bench["category_name"] if bench else item["category_code"]

            settled_outputs.append(
                SettledItemOutput(
                    item_id=w_item.item_id,
                    category_code=item["category_code"],
                    category_name=cat_name,
                    unit=item.get("unit", "kg"),
                    est_quantity=item.get("est_quantity", 0.0),
                    actual_quantity=w_item.actual_quantity,
                    locked_unit_price=locked_price,
                    settled_item_price=item_settled,
                )
            )

        total_settled = round(total_settled, 2)

        # อัปเดตสถานะใบงานเป็น S5 (Re-Quote / Weight Confirmed Gate)
        self.store.update_order(order_id, {
            "status": "S5",
            "scale_photo_url": request.scale_photo_url,
            "total_settled_amount": total_settled,
            "seller_confirmed_weight_at": None,  # รีเซ็ตการยืนยันของผู้ขายเมื่อมีการชั่งใหม่
        })

        # บันทึก Audit Log (REQ-SEC-001)
        self.store.add_audit_log(
            action="ORDER_WEIGHING_RECORDED",
            entity_id=order_id,
            actor_id=order.get("buyer_id", "SYSTEM"),
            details={
                "previous_status": order["status"],
                "new_status": "S5",
                "total_settled_amount": total_settled,
                "scale_photo_url": request.scale_photo_url,
                "items_count": len(request.items),
            }
        )

        return WeighingRecordResponse(
            order_id=order_id,
            status="S5",
            scale_photo_url=request.scale_photo_url,
            items=settled_outputs,
            total_settled_amount=total_settled,
            seller_confirmed_weight=False,
            message="บันทึกผลชั่งจริงแล้ว รอผู้ขายกดยืนยันตัวเลขน้ำหนักบนหน้าจอ",
        )

    def confirm_weights(self, order_id: str, request: WeightConfirmationRequest) -> WeightConfirmationResponse:
        """
        ผู้ขายตรวจสอบและกดยืนยันตัวเลขน้ำหนักชั่งจริง (100% Confirmation Gate)
        รองรับ REQ-FN-004, REQ-SEC-001, AC-S06-01, P-01, Q-01
        """
        order = self.store.get_order(order_id)
        if not order:
            raise ValueError(f"ไม่พบใบงานรหัส: {order_id}")

        # กฎเหล็ก: ผู้ที่มีสิทธิ์ยืนยันตัวเลขน้ำหนักต้องเป็นผู้ขายเจ้าของคำขอเท่านั้น
        if order.get("seller_id") != request.seller_id:
            raise PermissionError("ผู้ที่มีสิทธิ์ยืนยันตัวเลขน้ำหนักต้องเป็นผู้ขายเจ้าของคำขอเท่านั้น")

        # ตรวจสอบสถานะใบงาน ต้องอยู่ในสถานะ S5 (รอผู้ขายกดยืนยันน้ำหนัก)
        if order.get("status") != "S5":
            if order.get("status") in ["S1", "S2", "S3", "S4"]:
                raise ValueError("ซาเล้งยังไม่ได้บันทึกผลชั่งจริง ไม่สามารถยืนยันน้ำหนักได้")
            elif order.get("status") == "S6":
                raise ValueError("ผู้ขายได้กดยืนยันตัวเลขน้ำหนักไปแล้ว ใบงานอยู่ในสถานะรอยืนยันชำระเงิน (S6)")
            else:
                raise ValueError(f"ไม่สามารถยืนยันน้ำหนักได้ ใบงานอยู่ในสถานะ {order.get('status')}")

        # ตรวจสอบว่ามีรายการและทุกรายการมีค่าน้ำหนักชั่งจริง
        items = order.get("items", [])
        if not items or not all(item.get("actual_quantity") is not None for item in items):
            raise ValueError("ค่าน้ำหนักชั่งจริงยังไม่ครบถ้วน ไม่สามารถยืนยันได้")

        confirmed_at = datetime.now(timezone.utc).isoformat()
        total_settled = order.get("total_settled_amount", 0.0)

        # ปลดล็อกและเปลี่ยนสถานะเป็น S6 (รอยืนยันชำระเงิน)
        self.store.update_order(order_id, {
            "status": "S6",
            "seller_confirmed_weight_at": confirmed_at,
        })

        # บันทึก Audit Log (REQ-SEC-001)
        self.store.add_audit_log(
            action="SELLER_WEIGHT_CONFIRMED",
            entity_id=order_id,
            actor_id=request.seller_id,
            details={
                "previous_status": "S5",
                "new_status": "S6",
                "total_settled_amount": total_settled,
                "confirmed_at": confirmed_at,
            }
        )

        return WeightConfirmationResponse(
            order_id=order_id,
            status="S6",
            seller_confirmed_weight_at=confirmed_at,
            total_settled_amount=total_settled,
            message="ผู้ขายยืนยันตัวเลขน้ำหนักเรียบร้อยแล้ว พร้อมสำหรับการชำระเงิน",
        )

    def request_reweigh(self, order_id: str, request: RequestReweighRequest):
        """
        ผู้ขายส่งคำขอให้ซาเล้งตรวจสอบและชั่งน้ำหนักซ้ำ
        รองรับ AC-S06-02, Q-02
        """
        order = self.store.get_order(order_id)
        if not order:
            raise ValueError(f"ไม่พบใบงานรหัส: {order_id}")

        if order.get("seller_id") != request.seller_id:
            raise PermissionError("ผู้ที่มีสิทธิ์ขอชั่งซ้ำต้องเป็นผู้ขายเจ้าของคำขอเท่านั้น")

        if order.get("status") not in ["S4", "S5"]:
            raise ValueError(f"ไม่สามารถขอชั่งซ้ำได้ ใบงานอยู่ในสถานะ {order.get('status')}")

        # ปรับสถานะกลับไป S4 และล้างการยืนยันเดิม
        self.store.update_order(order_id, {
            "status": "S4",
            "seller_confirmed_weight_at": None,
            "reweigh_requested": True,
            "reweigh_reason": request.reason,
        })

        # บันทึก Audit Log (REQ-SEC-001)
        self.store.add_audit_log(
            action="SELLER_REQUESTED_REWEIGH",
            entity_id=order_id,
            actor_id=request.seller_id,
            details={
                "previous_status": order.get("status"),
                "new_status": "S4",
                "reason": request.reason,
            }
        )

        from backend.app.models.payment_models import RequestReweighResponse
        return RequestReweighResponse(
            order_id=order_id,
            status="S4",
            message="ส่งคำขอชั่งซ้ำแล้ว ซาเล้งจะทำการตรวจสอบและชั่งน้ำหนักใหม่",
        )

    def raise_dispute(self, order_id: str, request: DisputeRequest) -> DisputeResponse:
        """
        ผู้ขายปฏิเสธผลชั่งและส่งคำขอเข้าสู่ข้อพิพาท (S8: Disputed)
        พร้อมล็อกหลักฐานภาพตาชั่งและราคาที่ล็อกไว้เพื่อส่งให้ Admin ตรวจสอบ
        รองรับ REQ-FN-006, REQ-SEC-001, AC-S06-02, P-02, Q-02
        """
        order = self.store.get_order(order_id)
        if not order:
            raise ValueError(f"ไม่พบใบงานรหัส: {order_id}")

        if order.get("seller_id") != request.seller_id:
            raise PermissionError("ผู้ที่มีสิทธิ์แจ้งข้อพิพาทต้องเป็นผู้ขายเจ้าของคำขอเท่านั้น")

        if order.get("status") in ["S1", "S2", "S7"]:
            raise ValueError(f"ไม่สามารถแจ้งข้อพิพาทผลชั่งได้ในสถานะ {order.get('status')}")

        disputed_at = datetime.now(timezone.utc).isoformat()

        # เปลี่ยนสถานะเป็น S8 (Disputed) และล็อกข้อมูลหลักฐาน
        self.store.update_order(order_id, {
            "status": "S8",
            "dispute_reason": request.dispute_reason,
            "disputed_at": disputed_at,
            "is_frozen": True,  # ล็อกหลักฐานภาพถ่ายหน้าตาชั่ง พิกัด GPS และราคาที่ล็อกไว้ (REQ-FN-006)
        })

        # บันทึก Audit Log (REQ-SEC-001)
        self.store.add_audit_log(
            action="ORDER_DISPUTED",
            entity_id=order_id,
            actor_id=request.seller_id,
            details={
                "previous_status": order.get("status"),
                "new_status": "S8",
                "dispute_reason": request.dispute_reason,
                "scale_photo_url": order.get("scale_photo_url"),
                "total_settled_amount": order.get("total_settled_amount"),
                "disputed_at": disputed_at,
            }
        )

        return DisputeResponse(
            order_id=order_id,
            status="S8",
            dispute_reason=request.dispute_reason,
            disputed_at=disputed_at,
            message="ส่งข้อพิพาทเรียบร้อยแล้ว ระบบล็อกข้อมูลและส่งต่อให้ผู้ดูแลระบบตรวจสอบ",
        )

    def _generate_receipt_no(self, issued_at: datetime) -> str:
        """
        สร้างรหัสใบเสร็จไม่ซ้ำรูปแบบ REC-YYYYMMDD-XXXX (เลขลำดับรายวัน)
        รองรับ REQ-FN-005, Q-04
        """
        date_part = issued_at.strftime("%Y%m%d")
        prefix = f"REC-{date_part}-"
        same_day = [r for r in self.store.receipts.values() if str(r.get("receipt_no", "")).startswith(prefix)]
        return f"{prefix}{len(same_day) + 1:04d}"

    def confirm_payment(self, order_id: str, request: PaymentConfirmationRequest) -> PaymentConfirmationResponse:
        """
        ผู้ขายกดยืนยันรับเงิน (เงินสด / PromptPay) บนหน้าจอของตนเอง (S6 -> S7)
        และสร้างใบเสร็จดิจิทัลพร้อมปกปิดเบอร์โทรศัพท์
        รองรับ UC-07, REQ-FN-005, REQ-SEC-001, REQ-SEC-002, AC-S06-03, AC-S06-04, P-04, P-05, Q-03, Q-04
        """
        order = self.store.get_order(order_id)
        if not order:
            raise ValueError(f"ไม่พบใบงานรหัส: {order_id}")

        # Q-03: ผู้ขายเจ้าของคำขอเท่านั้นที่ยืนยันรับเงินได้
        if order.get("seller_id") != request.seller_id:
            raise PermissionError("ผู้ที่มีสิทธิ์ยืนยันรับเงินต้องเป็นผู้ขายเจ้าของคำขอเท่านั้น")

        # ต้องผ่าน 100% Weight Confirmation Gate (S6) ก่อนเท่านั้น (REQ-FN-004)
        status = order.get("status")
        if status != "S6":
            if status == "S7":
                raise ValueError("ใบงานนี้ยืนยันรับเงินและปิดงานไปแล้ว (S7)")
            if status == "S8" or order.get("is_frozen"):
                raise ValueError("ใบงานอยู่ระหว่างข้อพิพาท (S8) ไม่สามารถยืนยันรับเงินได้")
            raise ValueError(f"ยังไม่สามารถยืนยันรับเงินได้ ผู้ขายต้องยืนยันตัวเลขน้ำหนักก่อน (สถานะปัจจุบัน: {status})")

        now = datetime.now(timezone.utc)
        confirmed_at = now.isoformat()

        # สร้าง Snapshot รายการสำหรับใบเสร็จ (REQ-BR-002: ใช้ราคาที่ล็อกไว้)
        receipt_items: List[Dict[str, Any]] = []
        total_amount = 0.0
        for item in order.get("items", []):
            bench = self.store.get_price_by_category(item["category_code"])
            settled = item.get("settled_item_price")
            if settled is None:
                settled = round((item.get("actual_quantity") or 0.0) * (item.get("locked_unit_price") or 0.0), 2)
            total_amount += settled
            receipt_items.append({
                "category_code": item["category_code"],
                "category_name": bench["category_name"] if bench else item["category_code"],
                "unit": item.get("unit", "kg"),
                "actual_quantity": item.get("actual_quantity") or 0.0,
                "locked_unit_price": item.get("locked_unit_price") or 0.0,
                "settled_item_price": settled,
            })
        total_amount = round(total_amount, 2)

        receipt_no = self._generate_receipt_no(now)
        receipt = self.store.create_digital_receipt({
            "receipt_no": receipt_no,
            "order_id": order_id,
            "seller_id": order.get("seller_id"),
            "buyer_id": order.get("buyer_id") or "",
            # REQ-SEC-002: ปกปิดเบอร์โทรศัพท์ ไม่เก็บเบอร์เต็มในใบเสร็จ
            "seller_phone_masked": mask_phone(order.get("seller_phone")),
            "buyer_phone_masked": mask_phone(order.get("buyer_phone")),
            "total_amount": total_amount,
            "payment_method": request.payment_method,
            "items": receipt_items,
            "issued_at": confirmed_at,
        })

        # เปลี่ยนสถานะเป็น S7 (Completed)
        self.store.update_order(order_id, {
            "status": "S7",
            "payment_method": request.payment_method,
            "payment_confirmed_at": confirmed_at,
            "total_settled_amount": total_amount,
            "receipt_id": receipt["receipt_id"],
        })

        # บันทึก Audit Log (REQ-SEC-001)
        self.store.add_audit_log(
            action="SELLER_PAYMENT_CONFIRMED",
            entity_id=order_id,
            actor_id=request.seller_id,
            details={
                "previous_status": "S6",
                "new_status": "S7",
                "payment_method": request.payment_method,
                "total_amount": total_amount,
                "receipt_no": receipt_no,
            }
        )

        return PaymentConfirmationResponse(
            order_id=order_id,
            status="S7",
            payment_method=request.payment_method,
            payment_confirmed_at=confirmed_at,
            receipt_id=receipt["receipt_id"],
            receipt_no=receipt_no,
            total_amount=total_amount,
            message="ยืนยันรับเงินสำเร็จ ปิดงานและสร้างใบเสร็จดิจิทัลเรียบร้อย",
        )

    def get_receipt(self, order_id: str) -> DigitalReceiptResponse:
        """
        ดึงใบเสร็จดิจิทัลของคำขอ
        รองรับ REQ-FN-005, REQ-SEC-002, AC-S06-04
        """
        receipt = self.store.get_receipt_by_order(order_id)
        if not receipt:
            raise LookupError(f"ไม่พบใบเสร็จดิจิทัลของใบงานรหัส: {order_id}")
        return DigitalReceiptResponse(**receipt)


payment_service = PaymentService()

