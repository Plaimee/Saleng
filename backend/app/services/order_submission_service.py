"""
Order Submission & Threshold Guard Service
รองรับ REQ-FN-001, REQ-FN-006, REQ-SEC-001, AC-S04-03, P-03, P-05, D-01, D-03
"""

from datetime import datetime, timezone
from typing import Dict, Any, List
from backend.app.core.config import settings
from backend.app.core.supabase import supabase_store
from backend.app.models.pricing_models import (
    OrderSubmissionInput,
    OrderSubmissionResponse,
    WasteItemEstimateInput,
)
from backend.app.services.pricing_service import pricing_service


class MinimumThresholdError(Exception):
    def __init__(self, message: str, total_est_min_price: float, total_bags: int, allowed_alternatives: List[str]):
        super().__init__(message)
        self.message = message
        self.total_est_min_price = total_est_min_price
        self.total_bags = total_bags
        self.allowed_alternatives = allowed_alternatives


class OrderSubmissionService:
    def __init__(self, store=supabase_store, pricing=pricing_service):
        self.store = store
        self.pricing = pricing

    def check_threshold(self, items: List[WasteItemEstimateInput]) -> Dict[str, Any]:
        """
        ตรวจสอบเกณฑ์มูลค่าประเมินขั้นต่ำ
        รองรับ D-01: ใช้ min_price >= 500 บาท หรือขวดแก้ว/พลาสติก >= 2 กระสอบ
        """
        estimate = self.pricing.calculate_estimate(items)
        total_min_price = estimate.total_est_min_price

        # นับจำนวนกระสอบของขวดแก้ว/พลาสติก (D-01, AC-S04-03)
        total_bags = sum(
            int(item.quantity)
            for item in items
            if item.unit == "bag" and any(k in item.category_code for k in ["GLASS", "PLASTIC"])
        )

        is_pass = (total_min_price >= settings.THRESHOLD_MIN_ESTIMATED_BAHT) or (
            total_bags >= settings.THRESHOLD_MIN_BAGS
        )

        return {
            "is_pass": is_pass,
            "total_est_min_price": total_min_price,
            "total_est_max_price": estimate.total_est_max_price,
            "total_bags": total_bags,
            "estimate_details": estimate,
            "allowed_alternatives": ["ROUTE_DROP_IN", "BUILDING_GROUP"] if not is_pass else []
        }

    def submit_order(self, submission: OrderSubmissionInput) -> OrderSubmissionResponse:
        """
        ประเมินเกณฑ์และบันทึกคำขอนัดหมาย
        รองรับ AC-S04-03, REQ-FN-001, REQ-FN-006, D-01, D-03
        """
        threshold_info = self.check_threshold(submission.items)
        is_pass = threshold_info["is_pass"]
        total_min = threshold_info["total_est_min_price"]
        total_max = threshold_info["total_est_max_price"]

        is_route_drop = False
        is_building_group = False
        message = ""

        if submission.submission_type == "DIRECT":
            if not is_pass:
                raise MinimumThresholdError(
                    message="มูลค่าประเมินขั้นต่ำต้องไม่น้อยกว่า 500 บาท หรือมีขวดแก้ว/พลาสติกตั้งแต่ 2 กระสอบขึ้นไป สำหรับการนัดหมายเดี่ยว",
                    total_est_min_price=total_min,
                    total_bags=threshold_info["total_bags"],
                    allowed_alternatives=["ROUTE_DROP_IN", "BUILDING_GROUP"]
                )
            message = "สร้างคำขอนัดหมายเดี่ยวสำเร็จ รอผู้รับซื้อในพื้นที่ตอบรับ"

        elif submission.submission_type == "ROUTE_DROP_IN":
            # ทางเลือกฝากรวมจุดรับทางผ่าน (REQ-FN-001, D-03)
            is_route_drop = True
            message = "สร้างคำขอนัดหมายแบบฝากรวมจุดรับทางผ่านสำเร็จ ผู้รับซื้อในเส้นทางจะสามารถเห็นและแวะรับได้"

        elif submission.submission_type == "BUILDING_GROUP":
            # ทางเลือกจุดรับรวมประจำอาคาร/หอพัก (REQ-FN-006, D-03)
            is_building_group = True
            message = f"สร้างคำขอนัดหมายแบบจุดรับรวมประจำอาคารสำเร็จ ระบบจะรวบรวมน้ำหนักในอาคารให้ครบ {settings.THRESHOLD_BUILDING_KG} กก. ก่อนส่งให้ผู้รับซื้อ"

        else:
            raise ValueError(f"ไม่รู้จักประเภทการส่งคำขอ: {submission.submission_type}")

        # เตรียมข้อมูลสำหรับบันทึกลง Database
        order_data = {
            "seller_id": submission.seller_id,
            "pickup_location_id": submission.pickup_location_id,
            "status": "S2",  # S2: รอผู้รับซื้อ ตาม D-03
            "total_est_min_price": total_min,
            "total_est_max_price": total_max,
            "is_route_drop_in": is_route_drop,
            "is_building_group_drop": is_building_group,
            "building_id": submission.building_id,
        }

        items_data = [
            {
                "category_code": item.category_code,
                "unit": item.unit,
                "est_quantity": item.quantity,
                "est_min_price": out.est_min_price,
                "est_max_price": out.est_max_price,
                "locked_unit_price": None,  # ล็อกตอน S2 -> S3 (REQ-BR-002, D-04)
            }
            for item, out in zip(submission.items, threshold_info["estimate_details"].items)
        ]

        saved_order = self.store.create_order(order_data, items_data)

        # บันทึก Audit Log การเปลี่ยนสถานะใบงานเป็น S2 (REQ-SEC-001)
        self.store.add_audit_log(
            action="ORDER_CREATED_AND_SUBMITTED",
            entity_id=saved_order["order_id"],
            actor_id=submission.seller_id,
            details={
                "submission_type": submission.submission_type,
                "status": "S2",
                "total_est_min_price": total_min,
                "total_est_max_price": total_max,
                "is_route_drop_in": is_route_drop,
                "is_building_group_drop": is_building_group,
            }
        )

        return OrderSubmissionResponse(
            order_id=saved_order["order_id"],
            status=saved_order["status"],
            total_est_min_price=saved_order["total_est_min_price"],
            total_est_max_price=saved_order["total_est_max_price"],
            is_route_drop_in=saved_order["is_route_drop_in"],
            is_building_group_drop=saved_order["is_building_group_drop"],
            message=message,
            created_at=saved_order["created_at"]
        )

    def accept_order_and_lock_price(self, order_id: str, buyer_id: str) -> Dict[str, Any]:
        """
        จังหวะที่ซาเล้งกดรับนัดหมาย (S2 -> S3)
        ล็อกราคากลาง snapshot ในฐานข้อมูล เพื่อป้องกันข้อพิพาทเมื่อราคาเปลี่ยนในวันถัดไป
        รองรับ REQ-BR-002, D-04, REQ-SEC-001
        """
        order = self.store.get_order(order_id)
        if not order:
            raise ValueError(f"ไม่พบใบงานรหัส: {order_id}")

        if order["status"] != "S2":
            raise ValueError(f"ไม่สามารถรับงานได้ ใบงานไม่ได้อยู่ในสถานะ S2 (สถานะปัจจุบัน: {order['status']})")

        # ล็อกราคากลาง Snapshot ให้กับทุกรายการในใบงาน
        updated_items = []
        for item in order["items"]:
            # ดึงราคากลางปัจจุบันของหมวดหมู่นี้ตามหน่วยนับ (D-02, D-04)
            cat_code = item["category_code"]
            if item["unit"] == "bag" and not cat_code.endswith("-BAG"):
                bag_code = f"{cat_code}-BAG"
                if self.store.get_price_by_category(bag_code):
                    cat_code = bag_code

            benchmark = self.store.get_price_by_category(cat_code)
            # บันทึก locked_unit_price snapshot
            locked_price = benchmark["min_price_per_unit"] if benchmark else item["est_min_price"]
            item["locked_unit_price"] = locked_price
            self.store.items[item["item_id"]] = item
            updated_items.append(item)

        order["status"] = "S3"  # S3: Assigned / Accepted
        order["buyer_id"] = buyer_id
        order["version"] = order.get("version", 1) + 1
        order["items"] = updated_items
        self.store.orders[order_id] = order

        # บันทึก Audit Log (REQ-SEC-001)
        self.store.add_audit_log(
            action="ORDER_ACCEPTED_PRICE_LOCKED",
            entity_id=order_id,
            actor_id=buyer_id,
            details={
                "previous_status": "S2",
                "new_status": "S3",
                "buyer_id": buyer_id,
                "locked_items_count": len(updated_items),
            }
        )

        return order


order_submission_service = OrderSubmissionService()

