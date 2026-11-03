"""
Supabase Client & Data Access Layer
รองรับ CC-04 (Relational Concurrency / ACID), REQ-DAT-001, REQ-SEC-001
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional
import uuid
from backend.app.core.config import settings


class SupabaseStore:
    """
    Mock/In-memory Supabase Database Adapter
    ให้ระบบรันชุดทดสอบอัตโนมัติได้อย่างรวดเร็วและเป็นอิสระจากเครือข่ายภายนอก (Offline Testing)
    พร้อมคง Schema และ Constraints ตาม PostgreSQL/Supabase
    """

    def __init__(self):
        self.benchmark_prices: Dict[str, dict] = {}
        self.orders: Dict[str, dict] = {}
        self.items: Dict[str, dict] = {}
        self.receipts: Dict[str, dict] = {}
        self.collector_reviews: Dict[str, dict] = {}
        self.seller_favorites: List[dict] = []
        self.audit_logs: List[dict] = []
        self._seed_default_benchmark_prices()

    def _seed_default_benchmark_prices(self):
        """กำหนดราคากลางตั้งต้นตามที่ระบุใน spec.md หัวข้อ 1.1 และ D-02"""
        default_prices = [
            {
                "id": str(uuid.uuid4()),
                "category_code": "MAT-CARDBOARD",
                "category_name": "กระดาษลัง",
                "unit": "kg",
                "min_price_per_unit": 3.0,
                "max_price_per_unit": 4.0,
                "grading_condition": "แห้ง สะอาด ไม่เปียกน้ำ",
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            {
                "id": str(uuid.uuid4()),
                "category_code": "MAT-WHITE-PAPER",
                "category_name": "กระดาษขาวดำ",
                "unit": "kg",
                "min_price_per_unit": 6.0,
                "max_price_per_unit": 7.0,
                "grading_condition": "แยกกระดาษขาว ไม่ปนกระดาษสี",
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            {
                "id": str(uuid.uuid4()),
                "category_code": "MAT-GLASS-BOTTLE",
                "category_name": "ขวดแก้ว",
                "unit": "kg",
                "min_price_per_unit": 1.0,
                "max_price_per_unit": 2.0,
                "grading_condition": "ขวดสมบูรณ์ ไม่แตกคละสี",
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            {
                "id": str(uuid.uuid4()),
                "category_code": "MAT-GLASS-BOTTLE-BAG",
                "category_name": "ขวดแก้ว (กระสอบ)",
                "unit": "bag",
                "min_price_per_unit": 40.0,
                "max_price_per_unit": 60.0,
                "grading_condition": "บรรจุกระสอบมาตรฐาน แยกตามสีขวด",
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            {
                "id": str(uuid.uuid4()),
                "category_code": "MAT-PLASTIC-BOTTLE",
                "category_name": "ขวดพลาสติก",
                "unit": "kg",
                "min_price_per_unit": 5.0,
                "max_price_per_unit": 8.0,
                "grading_condition": "เทน้ำออก บีบแบน สะอาด",
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            {
                "id": str(uuid.uuid4()),
                "category_code": "MAT-PLASTIC-BOTTLE-BAG",
                "category_name": "ขวดพลาสติก (กระสอบ)",
                "unit": "bag",
                "min_price_per_unit": 30.0,
                "max_price_per_unit": 50.0,
                "grading_condition": "บรรจุกระสอบมาตรฐาน เทน้ำบีบแบน",
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
        ]
        for p in default_prices:
            self.benchmark_prices[p["category_code"]] = p

    def get_benchmark_prices(self) -> List[dict]:
        return list(self.benchmark_prices.values())

    def get_price_by_category(self, category_code: str) -> Optional[dict]:
        return self.benchmark_prices.get(category_code)

    def upsert_benchmark_price(self, price_data: dict) -> dict:
        category_code = price_data["category_code"]
        if "id" not in price_data or not price_data["id"]:
            price_data["id"] = str(uuid.uuid4())
        if "updated_at" not in price_data or not price_data["updated_at"]:
            price_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        self.benchmark_prices[category_code] = price_data
        return price_data

    def create_order(self, order_data: dict, items_data: List[dict]) -> dict:
        order_id = str(uuid.uuid4())
        order_data["order_id"] = order_id
        order_data["created_at"] = datetime.now(timezone.utc).isoformat()
        order_data["version"] = 1
        self.orders[order_id] = order_data

        saved_items = []
        for item in items_data:
            item_id = str(uuid.uuid4())
            item["item_id"] = item_id
            item["order_id"] = order_id
            item["created_at"] = datetime.now(timezone.utc).isoformat()
            self.items[item_id] = item
            saved_items.append(item)

        order_data["items"] = saved_items
        return order_data

    def get_order(self, order_id: str) -> Optional[dict]:
        order = self.orders.get(order_id)
        if order:
            items = [item for item in self.items.values() if item["order_id"] == order_id]
            order["items"] = items
        return order

    def update_order(self, order_id: str, updates: dict) -> dict:
        order = self.orders.get(order_id)
        if not order:
            raise ValueError(f"ไม่พบคำขอรหัส: {order_id}")
        order.update(updates)
        order["version"] = order.get("version", 1) + 1
        self.orders[order_id] = order
        return self.get_order(order_id)

    def update_item(self, item_id: str, updates: dict) -> dict:
        item = self.items.get(item_id)
        if not item:
            raise ValueError(f"ไม่พบรายการรหัส: {item_id}")
        item.update(updates)
        self.items[item_id] = item
        return item

    def create_digital_receipt(self, receipt_data: dict) -> dict:
        receipt_id = receipt_data.get("receipt_id") or str(uuid.uuid4())
        receipt_data["receipt_id"] = receipt_id
        if "issued_at" not in receipt_data or not receipt_data["issued_at"]:
            receipt_data["issued_at"] = datetime.now(timezone.utc).isoformat()
        self.receipts[receipt_id] = receipt_data
        return receipt_data

    def get_receipt(self, receipt_id: str) -> Optional[dict]:
        return self.receipts.get(receipt_id)

    def get_receipt_by_order(self, order_id: str) -> Optional[dict]:
        for r in self.receipts.values():
            if r.get("order_id") == order_id:
                return r
        return None

    def add_audit_log(self, action: str, entity_id: str, actor_id: str, details: dict):
        log_entry = {
            "log_id": str(uuid.uuid4()),
            "action": action,
            "entity_id": entity_id,
            "actor_id": actor_id,
            "details": details,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.audit_logs.append(log_entry)
        return log_entry

    # -------------------------------------------------------------------------
    # ระบบรีวิวและให้คะแนนซาเล้ง (collector_reviews - UC-10, SC-05, AC-S07-01)
    # -------------------------------------------------------------------------
    def create_review(self, review_data: dict) -> dict:
        order_id = review_data.get("order_id")
        # ตรวจสอบความซ้ำซ้อน: 1 คำขอ รีวิวได้ 1 ครั้ง (P-01, Q-02)
        if self.get_review_by_order(order_id):
            raise ValueError(f"คำขอรหัส {order_id} ได้รับการส่งรีวิวแล้ว")

        review_id = review_data.get("id") or str(uuid.uuid4())
        review_data["id"] = review_id
        if "created_at" not in review_data or not review_data["created_at"]:
            review_data["created_at"] = datetime.now(timezone.utc).isoformat()

        self.collector_reviews[review_id] = review_data
        return review_data

    def get_review_by_order(self, order_id: str) -> Optional[dict]:
        for r in self.collector_reviews.values():
            if r.get("order_id") == order_id:
                return r
        return None

    def get_collector_reviews(self, collector_id: str) -> List[dict]:
        return [r for r in self.collector_reviews.values() if r.get("collector_id") == collector_id]

    def get_collector_rating_summary(self, collector_id: str) -> dict:
        reviews = self.get_collector_reviews(collector_id)
        if not reviews:
            return {"average_rating": 0.0, "total_reviews": 0}
        total = sum(r["rating"] for r in reviews)
        return {
            "average_rating": round(total / len(reviews), 2),
            "total_reviews": len(reviews),
        }

    # -------------------------------------------------------------------------
    # ระบบผู้รับซื้อประจำ (seller_favorites - UC-10, SC-05, AC-S07-02, Q-03)
    # -------------------------------------------------------------------------
    def add_favorite(self, seller_id: str, collector_id: str) -> dict:
        for fav in self.seller_favorites:
            if fav["seller_id"] == seller_id and fav["collector_id"] == collector_id:
                return fav
        fav_entry = {
            "id": str(uuid.uuid4()),
            "seller_id": seller_id,
            "collector_id": collector_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.seller_favorites.append(fav_entry)
        return fav_entry

    def remove_favorite(self, seller_id: str, collector_id: str) -> bool:
        initial_len = len(self.seller_favorites)
        self.seller_favorites = [
            fav for fav in self.seller_favorites
            if not (fav["seller_id"] == seller_id and fav["collector_id"] == collector_id)
        ]
        return len(self.seller_favorites) < initial_len

    def is_favorite(self, seller_id: str, collector_id: str) -> bool:
        return any(
            fav["seller_id"] == seller_id and fav["collector_id"] == collector_id
            for fav in self.seller_favorites
        )

    def get_seller_favorites(self, seller_id: str) -> List[str]:
        return [
            fav["collector_id"]
            for fav in self.seller_favorites
            if fav["seller_id"] == seller_id
        ]

    # -------------------------------------------------------------------------
    # ระบบประวัติการขายที่ปิดงานสำเร็จ (Sales History - REQ-FN-005, AC-S07-03)
    # -------------------------------------------------------------------------
    def get_completed_orders_for_seller(self, seller_id: str) -> List[dict]:
        completed = []
        for o in self.orders.values():
            if o.get("seller_id") == seller_id and o.get("status") == "S7":
                order_copy = dict(o)
                order_copy["items"] = [
                    item for item in self.items.values()
                    if item.get("order_id") == o["order_id"]
                ]
                completed.append(order_copy)
        return sorted(completed, key=lambda x: x.get("completed_at") or x.get("created_at") or "", reverse=True)


# Singleton instance สำหรับเข้าถึง Database
supabase_store = SupabaseStore()

