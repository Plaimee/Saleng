"""
Supabase Client & Data Access Layer
รองรับ CC-04 (Relational Concurrency / ACID), REQ-DAT-001, REQ-SEC-001
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
import uuid
import re
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
        self.seller_notifications: Dict[str, dict] = {}
        self.support_tickets: Dict[str, dict] = {}
        self.safety_evidences: Dict[str, dict] = {}
        self.emergency_contacts: Dict[str, dict] = {}
        self.sos_alerts: Dict[str, dict] = {}
        self.sellers: Dict[str, dict] = {}
        self.seller_otps: List[dict] = []
        self.seller_sessions: Dict[str, dict] = {}
        self.pickup_locations: Dict[str, dict] = {}
        self.scrap_categories: Dict[str, dict] = {}
        self.saleng_profiles: Dict[str, dict] = {}
        self.collector_otps: List[dict] = []
        self.collector_sessions: Dict[str, dict] = {}
        self.collector_kyc_submissions: Dict[str, dict] = {}
        self.audit_logs: List[dict] = []
        self._seed_default_benchmark_prices()
        self._seed_default_scrap_categories()
        self._seed_default_saleng_profiles()
        self._seed_default_orders_s2()

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

    def _seed_default_scrap_categories(self):
        """กำหนดหมวดหมู่ของเก่าและคู่มือภาพ 3 กลุ่มหลักตาม spec.md และ Card 03"""
        categories = [
            # 1. หมวดชั่งกิโลกรัมทั่วไป (GENERAL_WEIGHT)
            {
                "category_code": "MAT-CARDBOARD",
                "category_group": "GENERAL_WEIGHT",
                "name": "กระดาษลัง",
                "icon": "📦",
                "unit": "kg",
                "min_price_per_unit": 3.0,
                "max_price_per_unit": 4.0,
                "sub_categories": None,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            {
                "category_code": "MAT-WHITE-PAPER",
                "category_group": "GENERAL_WEIGHT",
                "name": "กระดาษขาวดำ",
                "icon": "📄",
                "unit": "kg",
                "min_price_per_unit": 6.0,
                "max_price_per_unit": 7.0,
                "sub_categories": None,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            {
                "category_code": "MAT-PET-BOTTLE",
                "category_group": "GENERAL_WEIGHT",
                "name": "ขวดพลาสติกใส PET",
                "icon": "🧴",
                "unit": "kg",
                "min_price_per_unit": 5.0,
                "max_price_per_unit": 8.0,
                "sub_categories": None,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            {
                "category_code": "MAT-ALU-CAN",
                "category_group": "GENERAL_WEIGHT",
                "name": "กระป๋องอลูมิเนียม",
                "icon": "🥫",
                "unit": "kg",
                "min_price_per_unit": 30.0,
                "max_price_per_unit": 40.0,
                "sub_categories": None,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            {
                "category_code": "MAT-SCRAP-IRON",
                "category_group": "GENERAL_WEIGHT",
                "name": "เศษเหล็กทั่วไป",
                "icon": "⚙️",
                "unit": "kg",
                "min_price_per_unit": 4.0,
                "max_price_per_unit": 6.0,
                "sub_categories": None,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            # 2. หมวดวัสดุบรรจุลัง/กระสอบแยกเฉพาะ (BOXED_CRATE_ITEMS - Card 03)
            {
                "category_code": "BOXED-GLASS",
                "category_group": "BOXED_CRATE_ITEMS",
                "name": "ขวดแก้วบรรจุลัง",
                "icon": "🍾",
                "unit": "crate",
                "min_price_per_unit": 15.0,
                "max_price_per_unit": 25.0,
                "sub_categories": ["ขวดเบียร์ลัง", "ขวดน้ำปลาลัง", "ขวดซอส/น้ำหวานลัง"],
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            {
                "category_code": "BOXED-PLASTIC",
                "category_group": "BOXED_CRATE_ITEMS",
                "name": "ขวดพลาสติกบรรจุกระสอบ",
                "icon": "🛍️",
                "unit": "bag",
                "min_price_per_unit": 20.0,
                "max_price_per_unit": 30.0,
                "sub_categories": ["พลาสติกใสกระสอบ", "พลาสติกรวมกระสอบ"],
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            # 3. หมวดของชิ้นใหญ่แบบเหมาจ่าย (BULKY_FLAT_RATE - Card 03)
            {
                "category_code": "BULKY-APPLIANCE",
                "category_group": "BULKY_FLAT_RATE",
                "name": "ของชิ้นใหญ่แบบเหมาจ่าย",
                "icon": "🧊",
                "unit": "piece",
                "min_price_per_unit": 100.0,
                "max_price_per_unit": 500.0,
                "sub_categories": [
                    "ตู้เย็น",
                    "เครื่องซักผ้า",
                    "แอร์/คอมเพรสเซอร์",
                    "โซฟา/เฟอร์นิเจอร์",
                ],
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
        ]
        for c in categories:
            self.scrap_categories[c["category_code"]] = c

    def _seed_default_saleng_profiles(self):
        """กำหนดรายชื่อซาเล้งตั้งต้นที่ผ่าน KYC และเปิดรับงาน (UC-03, REQ-QA-001, D-00-01)"""
        profiles = [
            {
                "saleng_id": "saleng-01",
                "display_name": "ลุงสมชาย ซาเล้งสุทธิสาร",
                "phone": "081-234-5678",
                "phone_masked": "08X-XXX-5678",
                "avatar_url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150",
                "verified": True,
                "kyc_status": "VERIFIED",
                "rating": 4.9,
                "completed_jobs_count": 142,
                "vehicle_type": "TRICYCLE",
                "license_plate": "1กข-9999",
                "max_capacity_kg": 200.0,
                "current_lat": 13.7900,
                "current_lng": 100.5750,
                "is_online": True,
                "accepted_categories": [
                    "MAT-CARDBOARD",
                    "MAT-WHITE-PAPER",
                    "MAT-GLASS-BOTTLE",
                    "MAT-PLASTIC-BOTTLE",
                    "BOXED-GLASS",
                    "BOXED-PLASTIC",
                ],
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
            {
                "saleng_id": "saleng-02",
                "display_name": "พี่วิชัย รถกระบะรีไซเคิล",
                "phone": "089-876-5432",
                "phone_masked": "08X-XXX-5432",
                "avatar_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150",
                "verified": True,
                "kyc_status": "VERIFIED",
                "rating": 4.8,
                "completed_jobs_count": 215,
                "vehicle_type": "PICKUP_TRUCK",
                "license_plate": "2ฒณ-8888",
                "max_capacity_kg": 1000.0,
                "current_lat": 13.7920,
                "current_lng": 100.5770,
                "is_online": True,
                "accepted_categories": [
                    "MAT-CARDBOARD",
                    "MAT-PLASTIC-BOTTLE",
                    "BOXED-GLASS",
                    "BOXED-PLASTIC",
                    "BULKY-APPLIANCE",
                ],
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
            {
                "saleng_id": "saleng-03",
                "display_name": "อนันต์ ซาเล้งพ่วงข้างใหญ่",
                "phone": "086-555-1234",
                "phone_masked": "08X-XXX-1234",
                "avatar_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150",
                "verified": True,
                "kyc_status": "VERIFIED",
                "rating": 4.7,
                "completed_jobs_count": 89,
                "vehicle_type": "LARGE_SIDECAR",
                "license_plate": "3จจ-7777",
                "max_capacity_kg": 400.0,
                "current_lat": 13.8050,
                "current_lng": 100.5800,
                "is_online": True,
                "accepted_categories": [
                    "MAT-CARDBOARD",
                    "MAT-WHITE-PAPER",
                    "BULKY-APPLIANCE",
                ],
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
            {
                "saleng_id": "saleng-04",
                "display_name": "นพดล ซาเล้ง (พักกะ)",
                "phone": "082-111-2222",
                "phone_masked": "08X-XXX-2222",
                "avatar_url": None,
                "verified": True,
                "kyc_status": "VERIFIED",
                "rating": 4.5,
                "completed_jobs_count": 50,
                "vehicle_type": "TRICYCLE",
                "license_plate": "4ขข-6666",
                "max_capacity_kg": 200.0,
                "current_lat": 13.7910,
                "current_lng": 100.5760,
                "is_online": False,  # ออฟไลน์ ปิดรับงาน
                "accepted_categories": ["MAT-CARDBOARD"],
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
            {
                "saleng_id": "saleng-05",
                "display_name": "เอกชัย ยังไม่ยืนยัน",
                "phone": "083-333-4444",
                "phone_masked": "08X-XXX-4444",
                "avatar_url": None,
                "verified": False,  # ยังไม่ผ่าน KYC ห้ามแสดงผล
                "kyc_status": "UNVERIFIED",
                "rating": 3.0,
                "completed_jobs_count": 5,
                "vehicle_type": "TRICYCLE",
                "license_plate": None,
                "max_capacity_kg": 200.0,
                "current_lat": 13.7905,
                "current_lng": 100.5755,
                "is_online": True,
                "accepted_categories": ["MAT-CARDBOARD"],
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
        ]
        for p in profiles:
            self.saleng_profiles[p["saleng_id"]] = p

        # Seed favorite เบื้องต้นสำหรับ seller-01 -> saleng-01
        self.seller_favorites.append({
            "id": str(uuid.uuid4()),
            "seller_id": "seller-01",
            "collector_id": "saleng-01",
            "created_at": datetime.now(timezone.utc).isoformat(),
        })

    def get_saleng_profile(self, saleng_id: str) -> Optional[dict]:
        """ดึงข้อมูลโปรไฟล์ซาเล้งตาม ID (AC-S03-01)"""
        return self.saleng_profiles.get(saleng_id)

    def get_all_saleng_profiles(self) -> List[dict]:
        """ดึงรายการโปรไฟล์ซาเล้งทั้งหมดในระบบ"""
        return list(self.saleng_profiles.values())

    def update_saleng_profile(self, saleng_id: str, data: dict) -> Optional[dict]:
        """อัปเดตข้อมูลโปรไฟล์ซาเล้ง"""
        profile = self.saleng_profiles.get(saleng_id)
        if not profile:
            return None
        profile.update(data)
        profile["updated_at"] = datetime.now(timezone.utc).isoformat()
        return profile

    def get_scrap_categories(self) -> List[dict]:
        """ดึงรายการหมวดหมู่และคู่มือภาพทั้งหมด (AC-S02-01)"""
        return list(self.scrap_categories.values())

    def get_scrap_category(self, category_code: str) -> Optional[dict]:
        """ดึงข้อมูลหมวดหมู่ตามรหัส"""
        return self.scrap_categories.get(category_code)

    def add_item_to_order(self, order_id: str, item_data: dict) -> dict:
        """เพิ่มรายการของเก่าลงในคำขอ (AC-S02-01..03)"""
        item_id = item_data.get("item_id") or str(uuid.uuid4())
        item_data["item_id"] = item_id
        item_data["order_id"] = order_id
        if "created_at" not in item_data:
            item_data["created_at"] = datetime.now(timezone.utc).isoformat()
        if "photo_urls" not in item_data:
            item_data["photo_urls"] = []
        self.items[item_id] = item_data

        # คำนวณช่วงราคาประเมินรวมใหม่ของคำขอ
        self._recalculate_order_totals(order_id)
        return item_data

    def delete_item_from_order(self, order_id: str, item_id: str) -> bool:
        """ลบรายการของเก่าออกจากคำขอ"""
        if item_id in self.items and self.items[item_id].get("order_id") == order_id:
            del self.items[item_id]
            self._recalculate_order_totals(order_id)
            return True
        return False

    def attach_photo_to_item(self, item_id: str, photo_url: str) -> Optional[dict]:
        """แนบรูปถ่ายของเก่า (AC-S02-04)"""
        item = self.items.get(item_id)
        if not item:
            return None
        if "photo_urls" not in item:
            item["photo_urls"] = []
        if len(item["photo_urls"]) >= 5:
            raise ValueError("สามารถแนบรูปถ่ายได้สูงสุดไม่เกิน 5 รูปต่อรายการ")
        item["photo_urls"].append(photo_url)
        return item

    def delete_photo_from_item(self, item_id: str, photo_idx: int) -> Optional[dict]:
        """ลบรูปถ่ายของเก่า (AC-S02-04)"""
        item = self.items.get(item_id)
        if not item or "photo_urls" not in item:
            return None
        if 0 <= photo_idx < len(item["photo_urls"]):
            item["photo_urls"].pop(photo_idx)
            return item
        raise IndexError("ไม่พบดัชนีรูปภาพที่ระบุ")

    def _recalculate_order_totals(self, order_id: str):
        """คำนวณยอดเงินประเมินรวม Min-Max ใหม่ของคำขอ"""
        order = self.orders.get(order_id)
        if not order:
            return
        order_items = [i for i in self.items.values() if i.get("order_id") == order_id]
        total_min = sum(i.get("est_min_price", 0.0) for i in order_items)
        total_max = sum(i.get("est_max_price", 0.0) for i in order_items)
        order["total_est_min_price"] = total_min
        order["total_est_max_price"] = total_max
        order["updated_at"] = datetime.now(timezone.utc).isoformat()

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

    def add_audit_log(self, action: str | dict, entity_id: str = "", actor_id: str = "", details: dict = None):
        if isinstance(action, dict):
            entry = action
            action = entry.get("action", "")
            entity_id = entry.get("entity_id", "")
            actor_id = entry.get("actor_id", "")
            details = entry.get("details", {})
        log_entry = {
            "log_id": str(uuid.uuid4()),
            "action": action,
            "entity_id": entity_id,
            "actor_id": actor_id,
            "details": details or {},
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
            if not (fav["seller_id"] == seller_id and (fav.get("collector_id") == collector_id or fav.get("saleng_id") == collector_id))
        ]
        return len(self.seller_favorites) < initial_len

    def is_favorite(self, seller_id: str, collector_id: str) -> bool:
        return any(
            fav["seller_id"] == seller_id and (fav.get("collector_id") == collector_id or fav.get("saleng_id") == collector_id)
            for fav in self.seller_favorites
        )

    def get_seller_favorites(self, seller_id: str) -> List[str]:
        return [
            fav.get("collector_id") or fav.get("saleng_id")
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


    # -------------------------------------------------------------------------
    # ระบบแจ้งเตือนผู้ขาย (seller_notifications - UC-08, AC-S08-01, P-01)
    # -------------------------------------------------------------------------
    def create_notification(self, notif_data: dict) -> dict:
        notif_id = notif_data.get("id") or str(uuid.uuid4())
        notif_data["id"] = notif_id
        if "is_read" not in notif_data:
            notif_data["is_read"] = False
        if "created_at" not in notif_data or not notif_data["created_at"]:
            notif_data["created_at"] = datetime.now(timezone.utc).isoformat()
        self.seller_notifications[notif_id] = notif_data
        return notif_data

    def get_seller_notifications(self, seller_id: str) -> List[dict]:
        notifs = [
            n for n in self.seller_notifications.values()
            if n.get("seller_id") == seller_id
        ]
        return sorted(notifs, key=lambda x: x.get("created_at", ""), reverse=True)

    def mark_notification_as_read(self, notification_id: str) -> Optional[dict]:
        notif = self.seller_notifications.get(notification_id)
        if notif:
            notif["is_read"] = True
            self.seller_notifications[notification_id] = notif
        return notif

    def mark_all_notifications_as_read(self, seller_id: str) -> int:
        count = 0
        for notif in self.seller_notifications.values():
            if notif.get("seller_id") == seller_id and not notif.get("is_read", False):
                notif["is_read"] = True
                count += 1
        return count

    def generate_draft_reminders_for_seller(self, seller_id: str):
        """
        ตรวจสอบคำขอสถานะ S1 ที่ค้างเกิน 3 วัน (72 ชม.) และสร้าง Draft Reminder หากยังไม่มี (AC-S08-01, Q-01)
        """
        now = datetime.now(timezone.utc)
        for o in self.orders.values():
            if o.get("seller_id") == seller_id and o.get("status") == "S1":
                created_at_str = o.get("created_at")
                if created_at_str:
                    try:
                        # parse ISO timestamp
                        dt = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                        delta_days = (now - dt).total_seconds() / 86400.0
                    except Exception:
                        delta_days = 0.0

                    if delta_days >= 3.0:
                        order_id = o["order_id"]
                        # ตรวจสอบว่ามี reminder ของ order นี้หรือยัง
                        existing = any(
                            n.get("seller_id") == seller_id
                            and n.get("order_id") == order_id
                            and n.get("type") == "DRAFT_REMINDER"
                            for n in self.seller_notifications.values()
                        )
                        if not existing:
                            self.create_notification({
                                "seller_id": seller_id,
                                "type": "DRAFT_REMINDER",
                                "title": "แจ้งเตือน: รายการของเก่าค้างในฉบับร่าง",
                                "message": f"คุณมีรายการของเก่าคำขอ {order_id} บันทึกค้างไว้เกิน 3 วัน อย่าลืมส่งคำขอนัดหมายเพื่อระบายของเก่าก่อนล้นพื้นที่",
                                "order_id": order_id,
                                "is_read": False,
                            })

    # -------------------------------------------------------------------------
    # ระบบคำร้องขอความช่วยเหลือ (support_tickets - UC-13, REQ-SEC-002, AC-S08-04)
    # -------------------------------------------------------------------------
    def create_support_ticket(self, ticket_data: dict) -> dict:
        ticket_id = ticket_data.get("id") or str(uuid.uuid4())
        ticket_data["id"] = ticket_id
        if "status" not in ticket_data:
            ticket_data["status"] = "OPEN"
        if "created_at" not in ticket_data or not ticket_data["created_at"]:
            ticket_data["created_at"] = datetime.now(timezone.utc).isoformat()
        self.support_tickets[ticket_id] = ticket_data
        return ticket_data

    def get_support_tickets_by_seller(self, seller_id: str) -> List[dict]:
        tickets = [
            t for t in self.support_tickets.values()
            if t.get("seller_id") == seller_id
        ]
        return sorted(tickets, key=lambda x: x.get("created_at", ""), reverse=True)


    # -------------------------------------------------------------------------
    # ระบบความปลอดภัยขณะทำธุรกรรม (Safety Evidences & SOS - UC-09, AC-S09-01..05)
    # -------------------------------------------------------------------------
    def add_safety_evidence(self, evidence_data: dict) -> dict:
        ev_id = evidence_data.get("id") or str(uuid.uuid4())
        evidence_data["id"] = ev_id
        if "is_locked" not in evidence_data:
            evidence_data["is_locked"] = False
        if "created_at" not in evidence_data or not evidence_data["created_at"]:
            evidence_data["created_at"] = datetime.now(timezone.utc).isoformat()
        self.safety_evidences[ev_id] = evidence_data
        return evidence_data

    def get_safety_evidences_by_order(self, order_id: str) -> List[dict]:
        evs = [
            e for e in self.safety_evidences.values()
            if e.get("order_id") == order_id
        ]
        return sorted(evs, key=lambda x: x.get("created_at", ""))

    def lock_safety_evidences_for_order(self, order_id: str) -> int:
        """ล็อกหลักฐานของคำขอเป็น Read-only เมื่อเกิดข้อพิพาทหรือ SOS (REQ-FN-006, AC-S09-04)"""
        count = 0
        for e in self.safety_evidences.values():
            if e.get("order_id") == order_id:
                e["is_locked"] = True
                count += 1
        return count

    def get_emergency_contact(self, seller_id: str) -> Optional[dict]:
        return self.emergency_contacts.get(seller_id)

    def upsert_emergency_contact(self, contact_data: dict) -> dict:
        seller_id = contact_data["seller_id"]
        if "updated_at" not in contact_data or not contact_data["updated_at"]:
            contact_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        self.emergency_contacts[seller_id] = contact_data
        return contact_data

    def create_sos_alert(self, sos_data: dict) -> dict:
        alert_id = sos_data.get("id") or str(uuid.uuid4())
        sos_data["id"] = alert_id
        if "status" not in sos_data:
            sos_data["status"] = "TRIGGERED"
        if "created_at" not in sos_data or not sos_data["created_at"]:
            sos_data["created_at"] = datetime.now(timezone.utc).isoformat()
        self.sos_alerts[alert_id] = sos_data
        return sos_data

    def get_sos_alerts_by_order(self, order_id: str) -> List[dict]:
        alerts = [
            a for a in self.sos_alerts.values()
            if a.get("order_id") == order_id
        ]
        return sorted(alerts, key=lambda x: x.get("created_at", ""), reverse=True)

    # -------------------------------------------------------------
    # Seller Account, OTP, Session & Location Methods (UC-01, UC-02)
    # -------------------------------------------------------------
    def save_seller_otp(self, otp_data: dict) -> dict:
        """บันทึก OTP ชั่วคราว (AC-S01-01)"""
        otp_id = otp_data.get("id") or str(uuid.uuid4())
        otp_data["id"] = otp_id
        if "created_at" not in otp_data:
            otp_data["created_at"] = datetime.now(timezone.utc).isoformat()
        if "is_used" not in otp_data:
            otp_data["is_used"] = False
        self.seller_otps.append(otp_data)
        return otp_data

    def get_latest_seller_otp(self, phone: str) -> Optional[dict]:
        """ดึง OTP ล่าสุดของเบอร์โทรศัพท์ที่ยังไม่ถูกใช้"""
        matching = [
            o for o in self.seller_otps
            if o.get("phone") == phone and not o.get("is_used")
        ]
        if not matching:
            return None
        return sorted(matching, key=lambda x: x.get("created_at", ""), reverse=True)[0]

    def mark_seller_otp_used(self, otp_id: str):
        """ระบุว่า OTP ถูกใช้แล้ว"""
        for o in self.seller_otps:
            if o.get("id") == otp_id:
                o["is_used"] = True

    def get_seller_by_phone(self, phone: str) -> Optional[dict]:
        """ค้นหาผู้ขายจากเบอร์โทรศัพท์"""
        for s in self.sellers.values():
            if s.get("phone") == phone:
                return s
        return None

    def get_seller(self, seller_id: str) -> Optional[dict]:
        """ค้นหาผู้ขายจาก seller_id"""
        return self.sellers.get(seller_id)

    def create_seller(self, seller_data: dict) -> dict:
        """สร้างข้อมูลบัญชีผู้ขายใหม่ (AC-S01-01)"""
        seller_id = seller_data.get("seller_id") or f"SEL-{uuid.uuid4().hex[:8].upper()}"
        seller_data["seller_id"] = seller_id
        if "status" not in seller_data:
            seller_data["status"] = "ACTIVE"
        now = datetime.now(timezone.utc).isoformat()
        if "created_at" not in seller_data:
            seller_data["created_at"] = now
        if "updated_at" not in seller_data:
            seller_data["updated_at"] = now
        self.sellers[seller_id] = seller_data
        return seller_data

    def update_seller(self, seller_id: str, update_data: dict) -> Optional[dict]:
        """แก้ไขข้อมูลบัญชีผู้ขาย"""
        seller = self.sellers.get(seller_id)
        if not seller:
            return None
        seller.update(update_data)
        seller["updated_at"] = datetime.now(timezone.utc).isoformat()
        return seller

    def create_seller_session(self, session_data: dict) -> dict:
        """สร้างเซสชันการเข้าสู่ระบบ (AC-S01-01, AC-S01-04)"""
        token = session_data.get("session_token") or str(uuid.uuid4())
        session_data["session_token"] = token
        if "created_at" not in session_data:
            session_data["created_at"] = datetime.now(timezone.utc).isoformat()
        self.seller_sessions[token] = session_data
        return session_data

    def get_seller_session(self, session_token: str) -> Optional[dict]:
        """ดึงเซสชันจาก token"""
        return self.seller_sessions.get(session_token)

    def delete_seller_session(self, session_token: str) -> bool:
        """ลบเซสชัน (Logout)"""
        if session_token in self.seller_sessions:
            del self.seller_sessions[session_token]
            return True
        return False

    def create_pickup_location(self, loc_data: dict) -> dict:
        """เพิ่มที่อยู่นัดหมายรับของเก่า (AC-S01-02, MD-DOM-04)"""
        loc_id = loc_data.get("location_id") or f"LOC-{uuid.uuid4().hex[:8].upper()}"
        loc_data["location_id"] = loc_id
        seller_id = loc_data["seller_id"]
        now = datetime.now(timezone.utc).isoformat()
        if "created_at" not in loc_data:
            loc_data["created_at"] = now
        if "updated_at" not in loc_data:
            loc_data["updated_at"] = now

        # ถ้าตั้งค่าเป็น default ให้ปลด default ของที่อยู่อื่นของผู้ขายรายนี้
        if loc_data.get("is_default"):
            for l in self.pickup_locations.values():
                if l.get("seller_id") == seller_id:
                    l["is_default"] = False

        self.pickup_locations[loc_id] = loc_data
        return loc_data

    def get_pickup_location(self, location_id: str) -> Optional[dict]:
        """ดึงข้อมูลที่อยู่นัดหมาย"""
        return self.pickup_locations.get(location_id)

    def get_pickup_locations_by_seller(self, seller_id: str) -> List[dict]:
        """ดึงรายการที่อยู่นัดหมายทั้งหมดของผู้ขาย"""
        locs = [
            l for l in self.pickup_locations.values()
            if l.get("seller_id") == seller_id
        ]
        # ให้ default ขึ้นก่อน ตามด้วยวันที่สร้าง
        return sorted(
            locs,
            key=lambda x: (not x.get("is_default", False), x.get("created_at", "")),
        )

    def update_pickup_location(self, location_id: str, update_data: dict) -> Optional[dict]:
        """แก้ไขข้อมูลที่อยู่นัดหมาย"""
        loc = self.pickup_locations.get(location_id)
        if not loc:
            return None
        seller_id = loc["seller_id"]

        # ถ้าสลับเป็น default ให้ปลดอันอื่น
        if update_data.get("is_default"):
            for l in self.pickup_locations.values():
                if l.get("seller_id") == seller_id and l.get("location_id") != location_id:
                    l["is_default"] = False

        loc.update(update_data)
        loc["updated_at"] = datetime.now(timezone.utc).isoformat()
        return loc

    def delete_pickup_location(self, location_id: str) -> bool:
        """ลบที่อยู่นัดหมาย"""
        if location_id in self.pickup_locations:
            del self.pickup_locations[location_id]
            return True
        return False

    def set_default_pickup_location(self, seller_id: str, location_id: str) -> Optional[dict]:
        """กำหนดที่อยู่นี้เป็นที่อยู่เริ่มต้น (AC-S01-02, Q-03)"""
        target = self.pickup_locations.get(location_id)
        if not target or target.get("seller_id") != seller_id:
            return None
        for l in self.pickup_locations.values():
            if l.get("seller_id") == seller_id:
                l["is_default"] = (l.get("location_id") == location_id)
        target["updated_at"] = datetime.now(timezone.utc).isoformat()
        return target

    def get_default_pickup_location(self, seller_id: str) -> Optional[dict]:
        """ดึงที่อยู่เริ่มต้นสำหรับเตรียมส่งต่อให้ UC-02 (P-06)"""
        locs = self.get_pickup_locations_by_seller(seller_id)
        for l in locs:
            if l.get("is_default"):
                return l
        # หากไม่มี default ให้คืนที่อยู่อันแรกถ้ามี
        return locs[0] if locs else None

    # -------------------------------------------------------------
    # ระบบบัญชีและการยืนยันตัวตนซาเล้ง (Buyer 01: Account & KYC)
    # -------------------------------------------------------------
    def get_collector_by_phone(self, phone: str) -> Optional[dict]:
        """ค้นหาข้อมูลซาเล้งจากเบอร์โทรศัพท์ (P-01)"""
        cleaned_target = re.sub(r"\D", "", phone or "")
        for c in self.saleng_profiles.values():
            c_phone = re.sub(r"\D", "", c.get("phone", ""))
            if c_phone == cleaned_target:
                return c
        return None

    def create_collector_otp(self, phone: str, otp_code: str, expires_in_seconds: int = 300) -> dict:
        """บันทึกรหัส OTP สำหรับซาเล้ง (AC-B01-01)"""
        now = datetime.now(timezone.utc)
        otp_data = {
            "id": str(uuid.uuid4()),
            "phone": phone,
            "otp_code": otp_code,
            "expires_at": (now + timedelta(seconds=expires_in_seconds)).isoformat(),
            "is_used": False,
            "created_at": now.isoformat(),
        }
        self.collector_otps.append(otp_data)
        return otp_data

    def get_latest_collector_otp(self, phone: str) -> Optional[dict]:
        """ดึง OTP ล่าสุดของซาเล้งที่ยังไม่ถูกใช้"""
        matching = [
            o for o in self.collector_otps
            if o.get("phone") == phone and not o.get("is_used")
        ]
        if not matching:
            return None
        return sorted(matching, key=lambda x: x.get("created_at", ""), reverse=True)[0]

    def mark_collector_otp_used(self, otp_id: str):
        """ระบุว่า OTP ของซาเล้งถูกใช้แล้ว"""
        for o in self.collector_otps:
            if o.get("id") == otp_id:
                o["is_used"] = True

    def create_collector_session(self, saleng_id: str, expires_in_days: int = 30) -> dict:
        """สร้างเซสชันโทเคนสำหรับซาเล้ง (AC-B01-01)"""
        token = f"saleng_tok_{uuid.uuid4().hex}"
        now = datetime.now(timezone.utc)
        session_data = {
            "token": token,
            "saleng_id": saleng_id,
            "created_at": now.isoformat(),
            "expires_at": (now + timedelta(days=expires_in_days)).isoformat(),
            "is_active": True,
        }
        self.collector_sessions[token] = session_data
        return session_data

    def get_collector_session(self, token: str) -> Optional[dict]:
        """ดึงเซสชันซาเล้งจาก Token"""
        session = self.collector_sessions.get(token)
        if not session or not session.get("is_active"):
            return None
        return session

    def delete_collector_session(self, token: str) -> bool:
        """ยกเลิกเซสชันซาเล้ง (Logout)"""
        if token in self.collector_sessions:
            self.collector_sessions[token]["is_active"] = False
            del self.collector_sessions[token]
            return True
        return False

    def create_collector_profile(self, phone: str, display_name: Optional[str] = None) -> dict:
        """สร้างโปรไฟล์ซาเล้งใหม่เมื่อเข้าใช้งานครั้งแรก (P-01, AC-B01-01)"""
        saleng_id = f"saleng-{uuid.uuid4().hex[:6]}"
        from backend.app.models.collector_account_models import mask_phone_number
        phone_masked = mask_phone_number(phone)
        name = display_name or f"ซาเล้ง {phone_masked[-4:]}"
        now = datetime.now(timezone.utc).isoformat()
        profile = {
            "saleng_id": saleng_id,
            "display_name": name,
            "phone": phone,
            "phone_masked": phone_masked,
            "avatar_url": None,
            "vehicle_type": "TRICYCLE",
            "license_plate": None,
            "max_capacity_kg": 150.0,
            "verified": False,
            "kyc_status": "UNVERIFIED",
            "rejection_reason": None,
            "rating": 5.0,
            "completed_jobs_count": 0,
            "current_lat": 13.7563,
            "current_lng": 100.5018,
            "is_online": False,
            "accepted_categories": [
                "MAT-CARDBOARD",
                "MAT-WHITE-PAPER",
                "MAT-GLASS-BOTTLE",
                "MAT-PLASTIC-BOTTLE",
            ],
            "created_at": now,
            "updated_at": now,
        }
        self.saleng_profiles[saleng_id] = profile
        return profile

    def submit_collector_kyc(self, saleng_id: str, kyc_data: dict) -> dict:
        """บันทึกคำขอส่งเอกสารยืนยันตัวตน KYC (AC-B01-03, P-03)"""
        submission_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        submission = {
            "id": submission_id,
            "saleng_id": saleng_id,
            "id_card_no": kyc_data["id_card_no"],
            "full_name": kyc_data["full_name"],
            "id_card_photo_url": kyc_data["id_card_photo_url"],
            "selfie_photo_url": kyc_data["selfie_photo_url"],
            "vehicle_photo_url": kyc_data.get("vehicle_photo_url"),
            "status": "PENDING_REVIEW",
            "rejection_reason": None,
            "submitted_at": now,
            "reviewed_at": None,
            "reviewed_by": None,
        }
        self.collector_kyc_submissions[submission_id] = submission

        # อัปเดตสถานะใน saleng_profiles
        if saleng_id in self.saleng_profiles:
            self.saleng_profiles[saleng_id]["kyc_status"] = "PENDING_REVIEW"
            self.saleng_profiles[saleng_id]["rejection_reason"] = None
            self.saleng_profiles[saleng_id]["updated_at"] = now
        return submission

    def get_collector_latest_kyc(self, saleng_id: str) -> Optional[dict]:
        """ดึงประวัติการส่งเอกสาร KYC ล่าสุดของซาเล้ง (AC-B01-03)"""
        matching = [
            sub for sub in self.collector_kyc_submissions.values()
            if sub.get("saleng_id") == saleng_id
        ]
        if not matching:
            return None
        return sorted(matching, key=lambda x: x.get("submitted_at", ""), reverse=True)[0]

    def update_collector_kyc_status(
        self,
        saleng_id: str,
        status: str,
        rejection_reason: Optional[str] = None,
        reviewed_by: str = "SYSTEM_ADMIN"
    ) -> Optional[dict]:
        """อัปเดตผลการตรวจสอบ KYC (อนุมัติ/ปฏิเสธ) (AC-B01-03, Q-06, P-06)"""
        profile = self.saleng_profiles.get(saleng_id)
        if not profile:
            return None

        now = datetime.now(timezone.utc).isoformat()
        is_verified = (status == "VERIFIED")
        profile["kyc_status"] = status
        profile["verified"] = is_verified
        profile["rejection_reason"] = rejection_reason if status == "REJECTED" else None
        profile["updated_at"] = now

        # อัปเดตใน submission ล่าสุดด้วย
        latest_sub = self.get_collector_latest_kyc(saleng_id)
        if latest_sub:
            latest_sub["status"] = status
            latest_sub["rejection_reason"] = rejection_reason if status == "REJECTED" else None
            latest_sub["reviewed_at"] = now
            latest_sub["reviewed_by"] = reviewed_by

        return profile

    # -------------------------------------------------------------
    # ระบบค้นหาและแสดงงานรับซื้อตามพิกัด (Buyer 02: Job Search & Map, UC-04)
    # -------------------------------------------------------------

    def _seed_default_orders_s2(self):
        """กำหนดคำขอขายตั้งต้นสถานะ S2 (Pending) ในพื้นที่กรุงเทพฯ สำหรับซาเล้งค้นหางาน (UC-04)"""
        now = datetime.now(timezone.utc).isoformat()
        
        # 1. งานที่ 1: รัชดาภิเษก 18 (แขวงสามเสนนอก เขตห้วยขวาง) ห่างจาก saleng-01 ~ 0.5 กม.
        self.pickup_locations["loc-s2-01"] = {
            "location_id": "loc-s2-01",
            "seller_id": "seller-01",
            "address_text": "123/45 ซอยรัชดาภิเษก 18",
            "subdistrict": "แขวงสามเสนนอก",
            "district": "เขตห้วยขวาง",
            "province": "กรุงเทพมหานคร",
            "lat": 13.7930,
            "lng": 100.5780,
            "is_default": True,
            "created_at": now,
        }
        self.orders["order-s2-01"] = {
            "order_id": "order-s2-01",
            "seller_id": "seller-01",
            "location_id": "loc-s2-01",
            "status": "S2",
            "total_est_min_price": 150.0,
            "total_est_max_price": 220.0,
            "total_est_weight_kg": 25.0,
            "need_lifting_help": False,
            "assigned_saleng_id": None,
            "version": 1,
            "created_at": now,
        }
        self.items["item-s2-01-1"] = {
            "item_id": "item-s2-01-1",
            "order_id": "order-s2-01",
            "category_code": "MAT-CARDBOARD",
            "category_group": "GENERAL_WEIGHT",
            "name": "กระดาษลัง",
            "est_weight_kg": 20.0,
            "est_min_price": 80.0,
            "est_max_price": 100.0,
            "created_at": now,
        }
        self.items["item-s2-01-2"] = {
            "item_id": "item-s2-01-2",
            "order_id": "order-s2-01",
            "category_code": "MAT-ALU-CAN",
            "category_group": "GENERAL_WEIGHT",
            "name": "กระป๋องอลูมิเนียม",
            "est_weight_kg": 5.0,
            "est_min_price": 70.0,
            "est_max_price": 120.0,
            "created_at": now,
        }

        # 2. งานที่ 2: รัชดาภิเษก 32 (แขวงจันทรเกษม เขตจตุจักร) ห่างจาก saleng-01 ~ 1.3 กม.
        self.pickup_locations["loc-s2-02"] = {
            "location_id": "loc-s2-02",
            "seller_id": "seller-02",
            "address_text": "88 ซอยรัชดาภิเษก 32",
            "subdistrict": "แขวงจันทรเกษม",
            "district": "เขตจตุจักร",
            "province": "กรุงเทพมหานคร",
            "lat": 13.8010,
            "lng": 100.5720,
            "is_default": True,
            "created_at": now,
        }
        self.orders["order-s2-02"] = {
            "order_id": "order-s2-02",
            "seller_id": "seller-02",
            "location_id": "loc-s2-02",
            "status": "S2",
            "total_est_min_price": 300.0,
            "total_est_max_price": 450.0,
            "total_est_weight_kg": 60.0,
            "need_lifting_help": True,
            "assigned_saleng_id": None,
            "version": 1,
            "created_at": now,
        }
        self.items["item-s2-02-1"] = {
            "item_id": "item-s2-02-1",
            "order_id": "order-s2-02",
            "category_code": "MAT-PET-BOTTLE",
            "category_group": "GENERAL_WEIGHT",
            "name": "ขวดพลาสติกใส PET",
            "est_weight_kg": 60.0,
            "est_min_price": 300.0,
            "est_max_price": 450.0,
            "created_at": now,
        }

        # 3. งานที่ 3: ประชาสงเคราะห์ 23 (แขวงดินแดง เขตดินแดง) ห่างจาก saleng-01 ~ 1.2 กม.
        self.pickup_locations["loc-s2-03"] = {
            "location_id": "loc-s2-03",
            "seller_id": "seller-03",
            "address_text": "50 ซอยประชาสงเคราะห์ 23",
            "subdistrict": "แขวงดินแดง",
            "district": "เขตดินแดง",
            "province": "กรุงเทพมหานคร",
            "lat": 13.7820,
            "lng": 100.5690,
            "is_default": True,
            "created_at": now,
        }
        self.orders["order-s2-03"] = {
            "order_id": "order-s2-03",
            "seller_id": "seller-03",
            "location_id": "loc-s2-03",
            "status": "S2",
            "total_est_min_price": 500.0,
            "total_est_max_price": 800.0,
            "total_est_weight_kg": 120.0,
            "need_lifting_help": True,
            "assigned_saleng_id": None,
            "version": 1,
            "created_at": now,
        }
        self.items["item-s2-03-1"] = {
            "item_id": "item-s2-03-1",
            "order_id": "order-s2-03",
            "category_code": "BULKY-APPLIANCE",
            "category_group": "BULKY_FLAT_RATE",
            "name": "ของชิ้นใหญ่แบบเหมาจ่าย",
            "est_weight_kg": 120.0,
            "est_min_price": 500.0,
            "est_max_price": 800.0,
            "created_at": now,
        }

        # 4. งานที่ 4: พหลโยธิน ลาดยาว (ห่าง ~ 7.5 กม. จาก saleng-01 สำหรับทดสอบการขยาย 10 กม. AC-B02-02)
        self.pickup_locations["loc-s2-04"] = {
            "location_id": "loc-s2-04",
            "seller_id": "seller-04",
            "address_text": "999 ถนนพหลโยธิน",
            "subdistrict": "แขวงลาดยาว",
            "district": "เขตจตุจักร",
            "province": "กรุงเทพมหานคร",
            "lat": 13.8500,
            "lng": 100.5850,
            "is_default": True,
            "created_at": now,
        }
        self.orders["order-s2-04"] = {
            "order_id": "order-s2-04",
            "seller_id": "seller-04",
            "location_id": "loc-s2-04",
            "status": "S2",
            "total_est_min_price": 60.0,
            "total_est_max_price": 90.0,
            "total_est_weight_kg": 15.0,
            "need_lifting_help": False,
            "assigned_saleng_id": None,
            "version": 1,
            "created_at": now,
        }
        self.items["item-s2-04-1"] = {
            "item_id": "item-s2-04-1",
            "order_id": "order-s2-04",
            "category_code": "MAT-CARDBOARD",
            "category_group": "GENERAL_WEIGHT",
            "name": "กระดาษลัง",
            "est_weight_kg": 15.0,
            "est_min_price": 60.0,
            "est_max_price": 90.0,
            "created_at": now,
        }

    def get_open_orders_s2(self) -> List[dict]:
        """ดึงรายการคำขอขายสถานะ S2 (Pending) ที่ยังไม่มีซาเล้งรับงาน (UC-04, D-00-03)"""
        open_orders = []
        for o in self.orders.values():
            if o.get("status") in ("S2", "PENDING") and not o.get("assigned_saleng_id"):
                order_copy = dict(o)
                order_items = [item for item in self.items.values() if item.get("order_id") == o.get("order_id")]
                if not order_items and o.get("items"):
                    order_items = o.get("items")
                order_copy["items"] = order_items
                open_orders.append(order_copy)
        return open_orders

    def add_simulated_order(
        self,
        order_data: dict,
        location_data: dict,
        items_data: Optional[List[dict]] = None
    ) -> dict:
        """จำลองสร้างคำขอขายใหม่สถานะ S2 เพื่อทดสอบ Polling & Live Alert (Q-02)"""
        now = datetime.now(timezone.utc).isoformat()
        order_id = order_data.get("order_id") or f"order-sim-{uuid.uuid4().hex[:8]}"
        loc_id = location_data.get("location_id") or f"loc-sim-{uuid.uuid4().hex[:8]}"

        location_data["location_id"] = loc_id
        if "created_at" not in location_data:
            location_data["created_at"] = now
        self.pickup_locations[loc_id] = location_data

        order_data["order_id"] = order_id
        order_data["location_id"] = loc_id
        order_data["status"] = "S2"
        order_data["assigned_saleng_id"] = None
        if "version" not in order_data:
            order_data["version"] = 1
        if "created_at" not in order_data:
            order_data["created_at"] = now
        self.orders[order_id] = order_data

        saved_items = []
        if items_data:
            for item in items_data:
                item_id = item.get("item_id") or f"item-sim-{uuid.uuid4().hex[:8]}"
                item["item_id"] = item_id
                item["order_id"] = order_id
                if "created_at" not in item:
                    item["created_at"] = now
                self.items[item_id] = item
                saved_items.append(item)
        else:
            item_id = f"item-sim-{uuid.uuid4().hex[:8]}"
            default_item = {
                "item_id": item_id,
                "order_id": order_id,
                "category_code": order_data.get("categories", ["MAT-CARDBOARD"])[0],
                "category_group": "GENERAL_WEIGHT",
                "name": "ของเก่าทั่วไป",
                "est_weight_kg": order_data.get("total_est_weight_kg", 20.0),
                "est_min_price": order_data.get("total_est_min_price", 100.0),
                "est_max_price": order_data.get("total_est_max_price", 150.0),
                "created_at": now,
            }
            self.items[item_id] = default_item
            saved_items.append(default_item)

        order_copy = dict(order_data)
        order_copy["items"] = saved_items
        return order_copy

    def record_audit_log(
        self,
        action: str,
        actor_id: str,
        actor_role: str = "COLLECTOR",
        details: Optional[dict] = None,
        entity_id: str = "",
    ) -> dict:
        """บันทึกประวัติการทำงานลง audit_logs ตาม REQ-SEC-001"""
        log_entry = {
            "log_id": str(uuid.uuid4()),
            "action": action,
            "entity_id": entity_id or actor_id,
            "actor_id": actor_id,
            "actor_role": actor_role,
            "details": details or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.audit_logs.append(log_entry)
        return log_entry

    def get_audit_logs(self, action_filter: Optional[str] = None) -> List[dict]:
        """ดึงรายการ audit_logs ทั้งหมดหรือกรองตาม action"""
        if action_filter:
            return [l for l in self.audit_logs if l.get("action") == action_filter]
        return list(self.audit_logs)

    # -------------------------------------------------------------
    # ระบบประเมินงานและค่าน้ำมันก่อนรับ (Buyer 03: Pre-Acceptance Evaluation, UC-04, Card 02)
    # -------------------------------------------------------------

    def get_saleng_current_load(self, saleng_id: str) -> float:
        """คำนวณน้ำหนักบรรทุกปัจจุบันในรถซาเล้ง (กก.) ตามกฎ BR-03"""
        profile = self.saleng_profiles.get(saleng_id)
        if not profile:
            return 0.0

        # หากมี current_load_kg ระบุไว้โดยตรงในโปรไฟล์
        if "current_load_kg" in profile and profile["current_load_kg"] is not None:
            return float(profile["current_load_kg"])

        # รวมน้ำหนักของงานในมือที่กำลังวิ่งไปรับ (สถานะ S3 หรือ S4)
        active_weight = 0.0
        for o in self.orders.values():
            if (
                o.get("assigned_saleng_id") == saleng_id
                or o.get("buyer_id") == saleng_id
            ) and o.get("status") in ("S3", "S4"):
                active_weight += float(o.get("total_est_weight_kg", 0.0))

        return round(active_weight, 2)

    def set_saleng_current_load(self, saleng_id: str, load_kg: float) -> Optional[dict]:
        """กำหนดค่าน้ำหนักบรรทุกปัจจุบันของซาเล้งสำหรับการทดสอบและจำลองรอบวิ่ง (BR-03)"""
        profile = self.saleng_profiles.get(saleng_id)
        if not profile:
            return None
        profile["current_load_kg"] = round(float(load_kg), 2)
        profile["updated_at"] = datetime.now(timezone.utc).isoformat()
        return profile

    def update_saleng_online_status(
        self,
        saleng_id: str,
        is_online: bool,
        current_lat: Optional[float] = None,
        current_lng: Optional[float] = None,
    ) -> Optional[dict]:
        """สลับสถานะความพร้อมรับงาน Online / Offline และซิงก์พิกัดล่าสุด (CC-02)"""
        profile = self.saleng_profiles.get(saleng_id)
        if not profile:
            return None
        profile["is_online"] = is_online
        if current_lat is not None:
            profile["current_lat"] = current_lat
        if current_lng is not None:
            profile["current_lng"] = current_lng
        profile["updated_at"] = datetime.now(timezone.utc).isoformat()
        return profile

    def get_order_evaluation_data(self, order_id: str) -> Optional[dict]:
        """ดึงข้อมูลคำขอขายพร้อมรายการสิ่งของและพิกัดสำหรับใช้ประเมินงาน (Card 02)"""
        order = self.orders.get(order_id)
        if not order:
            return None
        order_copy = dict(order)
        order_items = [item for item in self.items.values() if item.get("order_id") == order_id]
        if not order_items and order.get("items"):
            order_items = order.get("items")
        order_copy["items"] = order_items

        loc_id = order.get("location_id")
        if loc_id:
            order_copy["location"] = self.pickup_locations.get(loc_id)
        return order_copy

    def claim_order_occ(self, order_id: str, saleng_id: str, expected_version: int) -> dict:
        """
        กดรับงานแบบ Atomic ด้วย Optimistic Concurrency Control (OCC) (BR-02, CC-04, D-B04-01)
        หากชนกันหรือมีผู้รับไปแล้วจะ raise ValueError
        """
        order = self.orders.get(order_id)
        if not order:
            raise KeyError(f"ไม่พบคำขอขายรหัส {order_id}")

        current_status = order.get("status")
        if current_status != "S2":
            raise ValueError(f"คำขอขายนี้ไม่อยู่ในสถานะรอผู้รับงาน (สถานะปัจจุบัน: {current_status}) มีผู้รับงานนี้แล้ว")

        current_version = order.get("version", 1)
        if current_version != expected_version:
            raise ValueError(f"ข้อมูลคำขอขายถูกแก้ไขโดยผู้ใช้อื่นแล้ว (version mismatch: {current_version} != {expected_version}) มีผู้รับงานนี้แล้ว")

        now = datetime.now(timezone.utc).isoformat()
        order["status"] = "S3"
        order["collector_id"] = saleng_id
        order["assigned_saleng_id"] = saleng_id
        order["version"] = current_version + 1
        order["claimed_at"] = now
        order["updated_at"] = now
        return order

    def revert_order_to_pending(self, order_id: str, saleng_id: str, reason: str, note: Optional[str] = None) -> dict:
        """
        คืนสถานะคำขอขายกลับเป็น S2 (Pending) เมื่อซาเล้งกดยกเลิกในสถานะ S3 (D-B04-04, MD-STM-04)
        """
        order = self.orders.get(order_id)
        if not order:
            raise KeyError(f"ไม่พบคำขอขายรหัส {order_id}")

        current_collector = order.get("collector_id") or order.get("assigned_saleng_id")
        if current_collector != saleng_id:
            raise ValueError("คุณไม่ใช่ผู้รับผิดชอบคำขอขายนี้ จึงไม่สามารถยกเลิกได้")

        now = datetime.now(timezone.utc).isoformat()
        order["status"] = "S2"
        order["collector_id"] = None
        order["assigned_saleng_id"] = None
        order["version"] = order.get("version", 1) + 1
        order["cancel_reason"] = reason
        order["cancel_note"] = note
        order["cancelled_at"] = now
        order["updated_at"] = now
        return order

    def get_collector_active_jobs(self, saleng_id: str) -> List[dict]:
        """
        ดึงรายการงานทั้งหมดในคิวของซาเล้งที่อยู่ในสถานะ S3 (Assigned) หรือ S4 (In-Transit)
        """
        active_jobs = []
        for o in self.orders.values():
            o_collector = o.get("collector_id") or o.get("assigned_saleng_id")
            if o_collector == saleng_id and o.get("status") in ("S3", "S4"):
                active_jobs.append(dict(o))
        return active_jobs


# Singleton instance สำหรับเข้าถึง Database
supabase_store = SupabaseStore()

