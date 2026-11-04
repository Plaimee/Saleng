"""
Supabase Client & Data Access Layer
รองรับ CC-04 (Relational Concurrency / ACID), REQ-DAT-001, REQ-SEC-001
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple, Any
import uuid
import re
from backend.app.core.config import settings
from backend.app.models.security_compliance_models import compute_audit_log_hash


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
        self.chat_messages: List[dict] = []
        self.collector_favorite_sellers: List[dict] = []
        self.dispute_reports: Dict[str, dict] = {}
        self.quality_grading_rules: Dict[str, List[dict]] = {}
        self.price_history_logs: List[dict] = []
        self.collector_gps_history: List[dict] = []
        self._seed_default_benchmark_prices()
        self._seed_default_scrap_categories()
        self._seed_default_saleng_profiles()
        self._seed_default_orders_s2()
        self._seed_default_sellers()
        self._seed_default_collector_kyc()
        self._seed_default_quality_grading_rules()
        self._seed_default_dispatch_dispute()
        self._seed_default_security_compliance()

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
                "effective_date": "2026-11-04",
                "is_active": True,
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "updated_by": "admin-01",
            },
            # ขยะชิ้นใหญ่เหมาจ่าย (หน่วย PIECE) รองรับ D-A02-04, UC-05, REQ-FN-003
            {
                "id": str(uuid.uuid4()),
                "category_code": "BULKY-FRIDGE",
                "category_name": "ตู้เย็น",
                "unit": "piece",
                "min_price_per_unit": 200.0,
                "max_price_per_unit": 300.0,
                "grading_condition": "คอมเพรสเซอร์ครบ อุปกรณ์ครบ ไม่บุบหนัก",
                "effective_date": "2026-11-04",
                "is_active": True,
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "updated_by": "admin-01",
            },
            {
                "id": str(uuid.uuid4()),
                "category_code": "BULKY-WASHING-MACHINE",
                "category_name": "เครื่องซักผ้า",
                "unit": "piece",
                "min_price_per_unit": 150.0,
                "max_price_per_unit": 250.0,
                "grading_condition": "ถังซักและมอเตอร์ครบ ไม่ผุกร่อนรุนแรง",
                "effective_date": "2026-11-04",
                "is_active": True,
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "updated_by": "admin-01",
            },
            {
                "id": str(uuid.uuid4()),
                "category_code": "BULKY-AIR-CONDITIONER",
                "category_name": "แอร์/เครื่องปรับอากาศ",
                "unit": "piece",
                "min_price_per_unit": 300.0,
                "max_price_per_unit": 500.0,
                "grading_condition": "คอยล์ทองแดงและคอมเพรสเซอร์สมบูรณ์",
                "effective_date": "2026-11-04",
                "is_active": True,
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "updated_by": "admin-01",
            },
            {
                "id": str(uuid.uuid4()),
                "category_code": "BULKY-TV",
                "category_name": "โทรทัศน์/จอภาพ",
                "unit": "piece",
                "min_price_per_unit": 50.0,
                "max_price_per_unit": 150.0,
                "grading_condition": "จอไม่แตก หลอดภาพ/บอร์ดหลักอยู่ครบ",
                "effective_date": "2026-11-04",
                "is_active": True,
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "updated_by": "admin-01",
            },
            {
                "id": str(uuid.uuid4()),
                "category_code": "BULKY-FURNITURE",
                "category_name": "เฟอร์นิเจอร์/เตียง/เบาะ",
                "unit": "piece",
                "min_price_per_unit": 10.0,
                "max_price_per_unit": 100.0,
                "grading_condition": "โครงไม้/เหล็กสมบูรณ์ ไม่ผุพัง",
                "effective_date": "2026-11-04",
                "is_active": True,
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "updated_by": "admin-01",
            },
        ]
        for p in default_prices:
            p.setdefault("effective_date", "2026-11-04")
            p.setdefault("is_active", True)
            p.setdefault("updated_by", "admin-01")
            self.benchmark_prices[str(p["category_code"])] = p

    def _seed_default_quality_grading_rules(self):
        """
        กำหนดเกณฑ์คุณภาพ 3 ระดับและการหักสิ่งปนเปื้อน 0%/5%/10%
        รองรับ REQ-FN-003, D-A02-03
        """
        now = datetime.now(timezone.utc).isoformat()
        categories = list(self.benchmark_prices.keys())
        for cat in categories:
            self.quality_grading_rules[cat] = [
                {
                    "rule_id": str(uuid.uuid4()),
                    "category_code": cat,
                    "grade_level": "GRADE_A",
                    "grade_name": "เกรด A (สะอาด/แห้ง/สมบูรณ์)",
                    "description": "วัสดุสะอาด แห้งสนิท ไม่เปียกชื้น ไม่มีสิ่งปนเปื้อน",
                    "contamination_deduction_percent": 0.0,
                    "price_target": "MAX",
                    "updated_at": now,
                    "updated_by": "admin-01",
                },
                {
                    "rule_id": str(uuid.uuid4()),
                    "category_code": cat,
                    "grade_level": "GRADE_B",
                    "grade_name": "เกรด B (ปนเปื้อน/ชื้นเล็กน้อย)",
                    "description": "มีสิ่งเจือปนเล็กน้อย คัดแยกไม่สมบูรณ์ หรือมีความชื้นปานกลาง",
                    "contamination_deduction_percent": 5.0,
                    "price_target": "MID",
                    "updated_at": now,
                    "updated_by": "admin-01",
                },
                {
                    "rule_id": str(uuid.uuid4()),
                    "category_code": cat,
                    "grade_level": "GRADE_C",
                    "grade_name": "เกรด C (ปนเปื้อนมาก/เปียกน้ำ)",
                    "description": "มีสิ่งเจือปนสูง เปียกน้ำ คละเกรด หรือมีสารเคมีเปรอะเปื้อน",
                    "contamination_deduction_percent": 10.0,
                    "price_target": "MIN",
                    "updated_at": now,
                    "updated_by": "admin-01",
                },
            ]

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
            self.scrap_categories[str(c["category_code"])] = c

    def _seed_default_saleng_profiles(self):
        """กำหนดรายชื่อซาเล้งตั้งต้นที่ผ่าน KYC และเปิดรับงาน (UC-03, REQ-QA-001, D-00-01)"""
        profiles: List[Dict[str, Any]] = [
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
            if "account_status" not in p:
                p["account_status"] = "ACTIVE"
            if "penalty_reason" not in p:
                p["penalty_reason"] = None
            if "penalized_at" not in p:
                p["penalized_at"] = None
            if "penalized_by" not in p:
                p["penalized_by"] = None
            self.saleng_profiles[str(p["saleng_id"])] = p

        # Seed favorite เบื้องต้นสำหรับ seller-01 -> saleng-01
        self.seller_favorites.append({
            "id": str(uuid.uuid4()),
            "seller_id": "seller-01",
            "collector_id": "saleng-01",
            "created_at": datetime.now(timezone.utc).isoformat(),
        })

    def _seed_default_sellers(self):
        """กำหนดรายชื่อผู้ขายตั้งต้นในระบบ (UC-01, AC-A01-03)"""
        now = datetime.now(timezone.utc).isoformat()
        if "seller-01" not in self.sellers:
            self.sellers["seller-01"] = {
                "seller_id": "seller-01",
                "phone": "081-234-5678",
                "display_name": "คุณวิภาดา",
                "account_status": "ACTIVE",
                "penalty_reason": None,
                "penalized_at": None,
                "penalized_by": None,
                "created_at": now,
            }
        if "seller-02" not in self.sellers:
            self.sellers["seller-02"] = {
                "seller_id": "seller-02",
                "phone": "0898765432",
                "display_name": "วิชัย รีไซเคิลบ้าน",
                "account_status": "ACTIVE",
                "penalty_reason": None,
                "penalized_at": None,
                "penalized_by": None,
                "created_at": now,
            }

    def _seed_default_collector_kyc(self):
        """กำหนดคำขอยืนยันตัวตน KYC ตั้งต้นสำหรับรอแอดมินตรวจ (UC-11, AC-A01-01)"""
        now = datetime.now(timezone.utc).isoformat()
        if "kyc-sub-01" not in self.collector_kyc_submissions:
            self.collector_kyc_submissions["kyc-sub-01"] = {
                "id": "kyc-sub-01",
                "saleng_id": "saleng-05",
                "id_card_no": "1100200112233",
                "full_name": "เอกชัย ขยันเก็บ",
                "id_card_photo_url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=300",
                "selfie_photo_url": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=300",
                "vehicle_photo_url": "https://images.unsplash.com/photo-1558981403-c5f9899a28bc?w=300",
                "status": "PENDING_REVIEW",
                "rejection_reason": None,
                "submitted_at": now,
                "reviewed_at": None,
                "reviewed_by": None,
            }

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
        updated_order = self.get_order(order_id)
        if updated_order is None:
            raise ValueError(f"ไม่พบคำขอรหัส: {order_id}")
        return updated_order

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

    def add_audit_log(self, action: str | dict, entity_id: str = "", actor_id: str = "", details: Optional[dict] = None, actor_role: Optional[str] = None):
        if isinstance(action, dict):
            entry = action
            action = entry.get("action", "")
            entity_id = entry.get("entity_id", "")
            actor_id = entry.get("actor_id", "")
            actor_role = entry.get("actor_role") or actor_role
            details = entry.get("details", {})
        
        if not actor_role:
            if actor_id:
                actor_id_lower = actor_id.lower()
                if actor_id.startswith("admin-") or "admin" in actor_id_lower:
                    actor_role = "ADMIN"
                elif actor_id.startswith("saleng-") or actor_id.startswith("col-"):
                    actor_role = "COLLECTOR"
                elif actor_id.startswith("seller-") or actor_id.startswith("sel-"):
                    actor_role = "SELLER"
                else:
                    actor_role = "SYSTEM"
            else:
                actor_role = "SYSTEM"

        timestamp = datetime.now(timezone.utc).isoformat()
        log_entry = {
            "log_id": str(uuid.uuid4()),
            "action": action,
            "entity_id": entity_id,
            "actor_id": actor_id,
            "actor_role": actor_role,
            "details": details or {},
            "timestamp": timestamp,
        }
        log_entry["log_hash"] = compute_audit_log_hash(log_entry)
        self.audit_logs.append(log_entry)
        return log_entry

    # -------------------------------------------------------------------------
    # ระบบรีวิวและให้คะแนนซาเล้ง (collector_reviews - UC-10, SC-05, AC-S07-01)
    # -------------------------------------------------------------------------
    def create_review(self, review_data: dict) -> dict:
        order_id = review_data.get("order_id")
        if not order_id:
            raise ValueError("review_data ต้องระบุ order_id")
        order_id_str = str(order_id)
        # ตรวจสอบความซ้ำซ้อน: 1 คำขอ รีวิวได้ 1 ครั้ง (P-01, Q-02)
        if self.get_review_by_order(order_id_str):
            raise ValueError(f"คำขอรหัส {order_id_str} ได้รับการส่งรีวิวแล้ว")

        review_id = review_data.get("id") or str(uuid.uuid4())
        review_data["id"] = review_id
        if "created_at" not in review_data or not review_data["created_at"]:
            review_data["created_at"] = datetime.now(timezone.utc).isoformat()

        self.collector_reviews[review_id] = review_data
        return review_data

    def get_review_by_order(self, order_id: Optional[str]) -> Optional[dict]:
        if not order_id:
            return None
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
        favorites: List[str] = []
        for fav in self.seller_favorites:
            if fav.get("seller_id") == seller_id:
                cid = fav.get("collector_id") or fav.get("saleng_id")
                if cid is not None:
                    favorites.append(str(cid))
        return favorites

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
        return self.add_audit_log(
            action=action,
            entity_id=entity_id or actor_id,
            actor_id=actor_id,
            actor_role=actor_role,
            details=details or {},
        )

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

    def get_order_chat_messages(self, order_id: str) -> List[dict]:
        """
        ดึงข้อความแชตทั้งหมดของ order_id เรียงตามลำดับเวลาที่ส่ง (sent_at)
        """
        messages = [m for m in self.chat_messages if m.get("order_id") == order_id]
        return sorted(messages, key=lambda x: x.get("sent_at", ""))

    def send_chat_message(
        self,
        order_id: str,
        sender_id: str,
        sender_role: str,
        message_text: str,
        is_quick_reply: bool = False,
    ) -> dict:
        """
        บันทึกข้อความแชตใหม่ลงตาราง chat_messages (D-B05-04, CC-04)
        """
        now = datetime.now(timezone.utc).isoformat()
        msg = {
            "message_id": f"msg-{uuid.uuid4().hex[:8]}",
            "order_id": order_id,
            "sender_id": sender_id,
            "sender_role": sender_role,
            "message_text": message_text,
            "is_quick_reply": is_quick_reply,
            "sent_at": now,
        }
        self.chat_messages.append(msg)
        return msg

    def log_communication_audit(
        self,
        order_id: str,
        saleng_id: str,
        action: str,
        details: Optional[dict] = None,
    ) -> dict:
        """
        บันทึกประวัติการสื่อสารลงใน audit_logs (REQ-SEC-001)
        action: "COLLECTOR_SENT_MESSAGE" หรือ "COLLECTOR_INITIATED_CALL"
        """
        details_copy = dict(details or {})
        details_copy.update({"order_id": order_id, "saleng_id": saleng_id})
        entry = self.add_audit_log(
            action=action,
            entity_id=order_id,
            actor_id=saleng_id,
            actor_role="COLLECTOR",
            details=details_copy,
        )
        entry["order_id"] = order_id
        entry["saleng_id"] = saleng_id
        return entry

    def get_order_weighing_sheet(self, order_id: str) -> Optional[dict]:
        """
        ดึงข้อมูลคำขอขายและรายการสิ่งของสำหรับใช้ในใบชั่งน้ำหนักหน้างาน (UC-05, REQ-FN-002)
        """
        order = self.orders.get(order_id)
        if not order:
            return None
        order_copy = dict(order)
        order_items = [dict(item) for item in self.items.values() if item.get("order_id") == order_id]
        if not order_items and order.get("items"):
            order_items = [dict(item) for item in order.get("items")]
        order_copy["items"] = order_items

        seller_id = order.get("seller_id", "seller-01")
        seller = self.sellers.get(seller_id) or {}
        order_copy["seller"] = seller
        raw_phone = order.get("seller_phone") or seller.get("phone", "0812345678")
        if len(raw_phone) >= 10:
            order_copy["seller_phone_masked"] = f"{raw_phone[:2]}X-XXX-{raw_phone[-4:]}"
        else:
            order_copy["seller_phone_masked"] = "08X-XXX-XXXX"
        return order_copy

    def update_order_payment_method(self, order_id: str, payment_method: str) -> dict:
        """
        อัปเดตช่องทางการชำระเงินที่ซาเล้งเลือก (D-B06-04)
        """
        order = self.orders.get(order_id)
        if not order:
            raise KeyError(f"ไม่พบคำขอขายรหัส {order_id}")
        order["payment_method"] = payment_method
        order["updated_at"] = datetime.now(timezone.utc).isoformat()
        return order

    def get_collector_favorite_sellers(self, collector_id: str) -> List[dict]:
        """
        ดึงรายการลูกค้าประจำที่ซาเล้งปักหมุดไว้ (UC-10, AC-B07-02, D-B07-03)
        """
        return [fav for fav in self.collector_favorite_sellers if fav.get("collector_id") == collector_id]

    def toggle_collector_favorite_seller(
        self,
        collector_id: str,
        seller_id: str,
        notes: Optional[str] = None,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        seller_name: Optional[str] = None,
        seller_phone_masked: Optional[str] = None,
    ) -> Tuple[bool, dict]:
        """
        สลับสถานะลูกค้าประจำ (Toggle Bookmark: เพิ่มเข้า / ยกเลิกออก) (AC-B07-02)
        """
        existing_idx = next(
            (idx for idx, f in enumerate(self.collector_favorite_sellers)
             if f.get("collector_id") == collector_id and f.get("seller_id") == seller_id),
            None
        )

        now = datetime.now(timezone.utc).isoformat()
        if existing_idx is not None:
            removed = self.collector_favorite_sellers.pop(existing_idx)
            return False, removed
        else:
            # ดึงข้อมูลผู้ขายหากไม่ได้ส่งมา
            seller = self.sellers.get(seller_id) or {}
            raw_phone = seller.get("phone", "0812345678")
            masked_phone = seller_phone_masked or (f"{raw_phone[:2]}X-XXX-{raw_phone[-4:]}" if len(raw_phone) >= 10 else "08X-XXX-XXXX")
            s_name = seller_name or seller.get("display_name", f"ลูกค้า {seller_id}")

            new_fav = {
                "id": str(uuid.uuid4()),
                "collector_id": collector_id,
                "seller_id": seller_id,
                "seller_name": s_name,
                "seller_phone_masked": masked_phone,
                "latitude": float(lat if lat is not None else seller.get("latitude", 13.7563)),
                "longitude": float(lng if lng is not None else seller.get("longitude", 100.5018)),
                "notes": notes or "",
                "created_at": now,
                "updated_at": now,
            }
            self.collector_favorite_sellers.append(new_fav)
            return True, new_fav

    def create_dispute_report(self, dispute_data: dict) -> dict:
        """
        บันทึกรายงานข้อพิพาทหน้างาน (UC-13, REQ-FN-006, AC-B07-03, D-B07-01)
        """
        dispute_id = dispute_data.get("dispute_id") or f"DISP-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
        dispute_data["dispute_id"] = dispute_id
        if "created_at" not in dispute_data:
            dispute_data["created_at"] = datetime.now(timezone.utc).isoformat()
        dispute_data["status"] = dispute_data.get("status", "PENDING_ADMIN")
        self.dispute_reports[dispute_id] = dispute_data
        return dispute_data

    def get_collector_kyc_submissions(self, status_filter: Optional[str] = None) -> List[dict]:
        """
        ดึงรายการคำขอยืนยันตัวตน KYC ของซาเล้ง (UC-11, AC-A01-01)
        """
        submissions = list(self.collector_kyc_submissions.values())
        if status_filter and status_filter.upper() != "ALL":
            submissions = [s for s in submissions if s.get("status") == status_filter.upper()]
        return sorted(submissions, key=lambda x: x.get("submitted_at", ""), reverse=True)

    def get_collector_kyc_submission(self, submission_id: str) -> Optional[dict]:
        """
        ดึงคำขอ KYC ตามรหัสอ้างอิง
        """
        return self.collector_kyc_submissions.get(submission_id)

    def review_collector_kyc(
        self,
        submission_id: str,
        action: str,
        rejection_reason: Optional[str] = None,
        reviewed_by: str = "ADMIN"
    ) -> Tuple[dict, dict]:
        """
        พิจารณาอนุมัติหรือปฏิเสธคำขอ KYC ซาเล้ง (UC-11, AC-A01-02, D-00-01)
        """
        submission = self.collector_kyc_submissions.get(submission_id)
        if not submission:
            raise KeyError(f"ไม่พบคำขอ KYC รหัส {submission_id}")

        saleng_id = submission.get("saleng_id", "")
        saleng_profile = self.saleng_profiles.get(saleng_id)
        if not saleng_profile:
            raise KeyError(f"ไม่พบข้อมูลซาเล้งรหัส {saleng_id}")

        now = datetime.now(timezone.utc).isoformat()
        if action == "APPROVE":
            submission["status"] = "VERIFIED"
            submission["rejection_reason"] = None
            submission["reviewed_at"] = now
            submission["reviewed_by"] = reviewed_by

            saleng_profile["verified"] = True
            saleng_profile["kyc_status"] = "VERIFIED"
            saleng_profile["rejection_reason"] = None
            saleng_profile["updated_at"] = now
        elif action == "REJECT":
            if not rejection_reason or not rejection_reason.strip():
                raise ValueError("ต้องระบุเหตุผลการปฏิเสธ (rejection_reason)")
            submission["status"] = "REJECTED"
            submission["rejection_reason"] = rejection_reason.strip()
            submission["reviewed_at"] = now
            submission["reviewed_by"] = reviewed_by

            saleng_profile["verified"] = False
            saleng_profile["kyc_status"] = "REJECTED"
            saleng_profile["rejection_reason"] = rejection_reason.strip()
            saleng_profile["updated_at"] = now
        else:
            raise ValueError(f"action ไม่ถูกต้อง: {action} (ต้องเป็น APPROVE หรือ REJECT)")

        return submission, saleng_profile

    def get_admin_users(
        self,
        role_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
        search_query: Optional[str] = None,
    ) -> List[dict]:
        """
        ดึงรายชื่อผู้ใช้งานทั้งหมด (ซาเล้งและผู้ขาย) พร้อมสถานะบัญชี (UC-11, AC-A01-03)
        """
        users: List[dict] = []

        # ดึงข้อมูลฝั่งซาเล้ง
        if not role_filter or role_filter.upper() in ("ALL", "COLLECTOR"):
            for s in self.saleng_profiles.values():
                raw_phone = str(s.get("phone", ""))
                masked_phone = str(s.get("phone_masked") or (
                    f"{raw_phone[:2]}X-XXX-{raw_phone[-4:]}" if len(raw_phone) >= 10 else "08X-XXX-XXXX"
                ))
                users.append({
                    "user_id": str(s["saleng_id"]),
                    "role": "COLLECTOR",
                    "display_name": str(s.get("display_name", f"ซาเล้ง {s['saleng_id']}")),
                    "phone_masked": masked_phone,
                    "account_status": str(s.get("account_status", "ACTIVE")),
                    "penalty_reason": s.get("penalty_reason"),
                    "penalized_at": s.get("penalized_at"),
                    "penalized_by": s.get("penalized_by"),
                    "verified": s.get("verified", False),
                })

        # ดึงข้อมูลฝั่งผู้ขาย
        if not role_filter or role_filter.upper() in ("ALL", "SELLER"):
            for seller_id, sel in self.sellers.items():
                raw_phone = str(sel.get("phone", ""))
                masked_phone = f"{raw_phone[:2]}X-XXX-{raw_phone[-4:]}" if len(raw_phone) >= 10 else "08X-XXX-XXXX"
                users.append({
                    "user_id": seller_id,
                    "role": "SELLER",
                    "display_name": str(sel.get("display_name", f"ผู้ขาย {seller_id}")),
                    "phone_masked": masked_phone,
                    "account_status": str(sel.get("account_status", "ACTIVE")),
                    "penalty_reason": sel.get("penalty_reason"),
                    "penalized_at": sel.get("penalized_at"),
                    "penalized_by": sel.get("penalized_by"),
                    "verified": None,
                })

        # กรองตามสถานะบัญชี
        if status_filter and status_filter.upper() != "ALL":
            target_status = status_filter.upper()
            users = [u for u in users if u.get("account_status") == target_status]

        # กรองตามคำค้นหา (user_id, display_name)
        if search_query and search_query.strip():
            sq = search_query.strip().lower()
            users = [u for u in users if sq in str(u["user_id"]).lower() or sq in str(u["display_name"]).lower()]

        return users

    def penalize_user_account(
        self,
        user_id: str,
        role: str,
        action: str,
        penalty_reason: str,
        penalized_by: str = "ADMIN",
    ) -> dict:
        """
        สั่งระงับสิทธิ์บัญชีผู้ใช้ชั่วคราวหรือถาวร (UC-11, AC-A01-03, D-A01-03, D-A01-04)
        """
        now = datetime.now(timezone.utc).isoformat()
        new_status = "BANNED" if action == "BAN" else "SUSPENDED_TEMPORARY"

        if role == "COLLECTOR":
            profile = self.saleng_profiles.get(user_id)
            if not profile:
                raise KeyError(f"ไม่พบข้อมูลซาเล้งรหัส {user_id}")
            profile["account_status"] = new_status
            profile["penalty_reason"] = penalty_reason
            profile["penalized_at"] = now
            profile["penalized_by"] = penalized_by
            profile["updated_at"] = now
            return dict(profile)
        elif role == "SELLER":
            seller = self.sellers.get(user_id)
            if not seller:
                raise KeyError(f"ไม่พบข้อมูลผู้ขายรหัส {user_id}")
            seller["account_status"] = new_status
            seller["penalty_reason"] = penalty_reason
            seller["penalized_at"] = now
            seller["penalized_by"] = penalized_by
            seller["updated_at"] = now
            return dict(seller)
        else:
            raise ValueError(f"บทบาทผู้ใช้ไม่ถูกต้อง: {role} (ต้องเป็น COLLECTOR หรือ SELLER)")

    def reactivate_user_account(
        self,
        user_id: str,
        role: str,
        reason: str = "ADMIN_REINSTATED",
    ) -> dict:
        """
        ปลดระงับสิทธิ์บัญชีผู้ใช้ คืนสถานะเป็น ACTIVE (UC-11, AC-A01-04)
        """
        now = datetime.now(timezone.utc).isoformat()

        if role == "COLLECTOR":
            profile = self.saleng_profiles.get(user_id)
            if not profile:
                raise KeyError(f"ไม่พบข้อมูลซาเล้งรหัส {user_id}")
            profile["account_status"] = "ACTIVE"
            profile["penalty_reason"] = None
            profile["penalized_at"] = None
            profile["penalized_by"] = None
            profile["updated_at"] = now
            return dict(profile)
        elif role == "SELLER":
            seller = self.sellers.get(user_id)
            if not seller:
                raise KeyError(f"ไม่พบข้อมูลผู้ขายรหัส {user_id}")
            seller["account_status"] = "ACTIVE"
            seller["penalty_reason"] = None
            seller["penalized_at"] = None
            seller["penalized_by"] = None
            seller["updated_at"] = now
            return dict(seller)
        else:
            raise ValueError(f"บทบาทผู้ใช้ไม่ถูกต้อง: {role} (ต้องเป็น COLLECTOR หรือ SELLER)")

    def get_all_benchmark_prices_admin(
        self,
        unit: Optional[str] = None,
        q: Optional[str] = None,
    ) -> List[dict]:
        """
        ดึงรายการราคากลางทั้งหมดสำหรับแอดมิน (UC-03, REQ-DAT-001, AC-A02-01)
        """
        prices = list(self.benchmark_prices.values())
        if unit and unit != "all":
            prices = [p for p in prices if p.get("unit") == unit]
        if q:
            query = q.strip().lower()
            prices = [
                p for p in prices
                if query in p.get("category_code", "").lower()
                or query in p.get("category_name", "").lower()
            ]
        # เรียงตาม category_code เพื่อความแน่นอน
        return sorted(prices, key=lambda x: x.get("category_code", ""))

    def update_benchmark_price(
        self,
        category_code: str,
        min_price: float,
        max_price: float,
        grading_condition: Optional[str] = None,
        updated_by: str = "admin-01",
        change_reason: Optional[str] = None,
    ) -> dict:
        """
        แก้ไขช่วงราคากลางรายวัน (UC-03, REQ-DAT-001, BR-01, D-A02-01..05, REQ-SEC-001)
        - บันทึกประวัติลง price_history_logs
        - บันทึก Audit Log (ADMIN_UPDATED_BENCHMARK_PRICE)
        - คำนวณราคาประเมินใหม่ให้กับออเดอร์ในสถานะ S1/S2 (D-A02-05)
        - ออเดอร์ S3..S7 ยังคงล็อกราคาเดิมตาม Price Snapshot (D-00-02)
        """
        item = self.benchmark_prices.get(category_code)
        if not item:
            raise KeyError(f"ไม่พบหมวดหมู่วัสดุรหัส {category_code}")

        old_min = float(item.get("min_price_per_unit", 0.0))
        old_max = float(item.get("max_price_per_unit", 0.0))
        now = datetime.now(timezone.utc).isoformat()

        # 1. บันทึกประวัติราคา
        history_entry = {
            "history_id": str(uuid.uuid4()),
            "category_code": category_code,
            "old_min_price": old_min,
            "old_max_price": old_max,
            "new_min_price": float(min_price),
            "new_max_price": float(max_price),
            "changed_at": now,
            "changed_by": updated_by,
            "change_reason": change_reason,
        }
        self.price_history_logs.append(history_entry)

        # 2. ปรับปรุงราคากลาง
        item["min_price_per_unit"] = float(min_price)
        item["max_price_per_unit"] = float(max_price)
        if grading_condition:
            item["grading_condition"] = grading_condition
        item["updated_at"] = now
        item["updated_by"] = updated_by
        self.benchmark_prices[category_code] = item

        # 3. บันทึก Audit Log (REQ-SEC-001, CC-03)
        self.add_audit_log(
            action="ADMIN_UPDATED_BENCHMARK_PRICE",
            entity_id=category_code,
            actor_id=updated_by,
            details={
                "category_code": category_code,
                "old_min_price": old_min,
                "old_max_price": old_max,
                "new_min_price": float(min_price),
                "new_max_price": float(max_price),
                "actor_role": "ADMIN",
                "change_reason": change_reason,
            },
        )

        # 4. ปรับราคาย้อนหลังเฉพาะออเดอร์ S1 และ S2 (D-A02-05)
        for order in self.orders.values():
            if order.get("status") in ["S1", "S2"]:
                updated = False
                for it in order.get("items", []):
                    if it.get("category_code") == category_code:
                        qty = float(it.get("quantity", 0.0))
                        it["est_min_price"] = round(qty * float(min_price), 2)
                        it["est_max_price"] = round(qty * float(max_price), 2)
                        if it.get("item_id") in self.items:
                            self.items[it["item_id"]] = it
                        updated = True
                if updated:
                    self._recalculate_order_totals(order["order_id"])

        return dict(item)

    def get_quality_grading_rules(self, category_code: str) -> List[dict]:
        """
        ดึงเกณฑ์คุณภาพและการหักสิ่งปนเปื้อน 3 ระดับ (REQ-FN-003, D-A02-03)
        """
        if category_code not in self.quality_grading_rules:
            # Fallback สร้างเกณฑ์มาตรฐานให้อัตโนมัติหากยังไม่มี
            now = datetime.now(timezone.utc).isoformat()
            self.quality_grading_rules[category_code] = [
                {
                    "rule_id": str(uuid.uuid4()),
                    "category_code": category_code,
                    "grade_level": "GRADE_A",
                    "grade_name": "เกรด A (สะอาด/แห้ง/สมบูรณ์)",
                    "description": "วัสดุสะอาด แห้งสนิท ไม่เปียกชื้น ไม่มีสิ่งปนเปื้อน",
                    "contamination_deduction_percent": 0.0,
                    "price_target": "MAX",
                    "updated_at": now,
                    "updated_by": "admin-01",
                },
                {
                    "rule_id": str(uuid.uuid4()),
                    "category_code": category_code,
                    "grade_level": "GRADE_B",
                    "grade_name": "เกรด B (ปนเปื้อน/ชื้นเล็กน้อย)",
                    "description": "มีสิ่งเจือปนเล็กน้อย คัดแยกไม่สมบูรณ์ หรือมีความชื้นปานกลาง",
                    "contamination_deduction_percent": 5.0,
                    "price_target": "MID",
                    "updated_at": now,
                    "updated_by": "admin-01",
                },
                {
                    "rule_id": str(uuid.uuid4()),
                    "category_code": category_code,
                    "grade_level": "GRADE_C",
                    "grade_name": "เกรด C (ปนเปื้อนมาก/เปียกน้ำ)",
                    "description": "มีสิ่งเจือปนสูง เปียกน้ำ คละเกรด หรือมีสารเคมีเปรอะเปื้อน",
                    "contamination_deduction_percent": 10.0,
                    "price_target": "MIN",
                    "updated_at": now,
                    "updated_by": "admin-01",
                },
            ]
        return list(self.quality_grading_rules[category_code])

    def update_quality_grading_rules(
        self,
        category_code: str,
        rules_data: List[dict],
        updated_by: str = "admin-01",
    ) -> List[dict]:
        """
        แก้ไขเกณฑ์คุณภาพ 3 ระดับและอัตราหักสิ่งปนเปื้อน (REQ-FN-003, D-A02-03, REQ-SEC-001)
        """
        now = datetime.now(timezone.utc).isoformat()
        normalized_rules = []
        for r in rules_data:
            rule_entry = {
                "rule_id": r.get("rule_id") or str(uuid.uuid4()),
                "category_code": category_code,
                "grade_level": r.get("grade_level", "GRADE_A"),
                "grade_name": r.get("grade_name", ""),
                "description": r.get("description", ""),
                "contamination_deduction_percent": float(r.get("contamination_deduction_percent", 0.0)),
                "price_target": r.get("price_target", "MID"),
                "updated_at": now,
                "updated_by": updated_by,
            }
            normalized_rules.append(rule_entry)

        self.quality_grading_rules[category_code] = normalized_rules

        # บันทึก Audit Log (REQ-SEC-001, CC-03)
        self.add_audit_log(
            action="ADMIN_UPDATED_GRADING_RULES",
            entity_id=category_code,
            actor_id=updated_by,
            details={
                "category_code": category_code,
                "rules_count": len(normalized_rules),
                "actor_role": "ADMIN",
            },
        )
        return list(normalized_rules)

    def batch_update_benchmark_prices(
        self,
        items_data: List[dict],
        effective_date: Optional[str] = None,
        updated_by: str = "admin-01",
        change_reason: Optional[str] = None,
    ) -> List[dict]:
        """
        อัปเดตราคากลางหลายหมวดหมู่พร้อมกัน (Batch Update)
        """
        updated_items = []
        for it in items_data:
            cat_code = it["category_code"]
            min_p = it["min_price_per_unit"]
            max_p = it["max_price_per_unit"]
            cond = it.get("grading_condition")
            updated = self.update_benchmark_price(
                category_code=cat_code,
                min_price=min_p,
                max_price=max_p,
                grading_condition=cond,
                updated_by=updated_by,
                change_reason=change_reason,
            )
            if effective_date:
                updated["effective_date"] = effective_date
                self.benchmark_prices[cat_code]["effective_date"] = effective_date
            updated_items.append(updated)
        return updated_items

    def get_benchmark_price_history(
        self,
        category_code: str,
        limit: int = 20,
    ) -> List[dict]:
        """
        ดึงประวัติการปรับเปลี่ยนราคาย้อนหลัง
        """
        history = [
            h for h in self.price_history_logs
            if h.get("category_code") == category_code
        ]
        return history[-limit:]

    def _seed_default_dispatch_dispute(self):
        """
        กำหนดข้อมูลคำขอตกค้าง (S2 > 30 นาที) และข้อพิพาทตั้งต้น (S8 / PENDING_ADMIN)
        รองรับ UC-13, D-A03-01..05
        """
        now = datetime.now(timezone.utc)
        stalled_time = (now - timedelta(minutes=45)).isoformat()
        dispute_time = (now - timedelta(minutes=25)).isoformat()
        two_hours_ago = (now - timedelta(hours=2)).isoformat()

        # 1. คำขอขาย S2 ที่ตกค้าง > 30 นาที
        self.pickup_locations["loc-s2-stalled-01"] = {
            "location_id": "loc-s2-stalled-01",
            "seller_id": "seller-01",
            "address_text": "99/1 ซอยประชาราษฎร์บำเพ็ญ 7",
            "subdistrict": "แขวงห้วยขวาง",
            "district": "เขตห้วยขวาง",
            "province": "กรุงเทพมหานคร",
            "lat": 13.7780,
            "lng": 100.5740,
            "is_default": False,
            "created_at": stalled_time,
        }
        self.orders["order-s2-stalled-01"] = {
            "order_id": "order-s2-stalled-01",
            "seller_id": "seller-01",
            "location_id": "loc-s2-stalled-01",
            "status": "S2",
            "total_est_min_price": 200.0,
            "total_est_max_price": 350.0,
            "total_est_weight_kg": 40.0,
            "need_lifting_help": False,
            "search_radius_km": 5.0,
            "is_manual_dispatched": False,
            "assigned_saleng_id": None,
            "version": 1,
            "created_at": stalled_time,
        }
        self.items["item-s2-stalled-01"] = {
            "item_id": "item-s2-stalled-01",
            "order_id": "order-s2-stalled-01",
            "category_code": "MAT-CARDBOARD",
            "category_group": "GENERAL_WEIGHT",
            "name": "กระดาษลัง",
            "est_weight_kg": 40.0,
            "est_min_price": 200.0,
            "est_max_price": 350.0,
            "created_at": stalled_time,
        }

        # 2. คำขอขายสถานะ S8 ที่มีข้อพิพาท
        self.orders["order-dispute-01"] = {
            "order_id": "order-dispute-01",
            "seller_id": "seller-02",
            "location_id": "loc-s2-02",
            "status": "S8",
            "assigned_saleng_id": "saleng-01",
            "buyer_id": "saleng-01",
            "collector_id": "saleng-01",
            "total_est_min_price": 300.0,
            "total_est_max_price": 450.0,
            "total_est_weight_kg": 60.0,
            "actual_weight_kg": 42.0,
            "re_quoted_price": 210.0,
            "created_at": two_hours_ago,
            "price_snapshot": {
                "MAT-PET-BOTTLE": {
                    "min_price": 5.0,
                    "max_price": 7.5,
                    "snapshot_at": two_hours_ago,
                }
            },
            "scale_photo_url": "https://storage.saleng.app/disputes/scale_photo_01.jpg",
            "seller_photo_urls": ["https://storage.saleng.app/disputes/seller_photo_01.jpg"],
            "version": 3,
        }
        self.items["item-disp-01"] = {
            "item_id": "item-disp-01",
            "order_id": "order-dispute-01",
            "category_code": "MAT-PET-BOTTLE",
            "category_group": "GENERAL_WEIGHT",
            "name": "ขวดพลาสติกใส PET",
            "est_weight_kg": 60.0,
            "actual_weight_kg": 42.0,
            "est_min_price": 300.0,
            "est_max_price": 450.0,
            "created_at": two_hours_ago,
        }

        self.dispute_reports["DISP-20261104-0001"] = {
            "dispute_id": "DISP-20261104-0001",
            "order_id": "order-dispute-01",
            "seller_id": "seller-02",
            "buyer_id": "saleng-01",
            "dispute_reason": "น้ำหนักขวดพลาสติกชั่งได้น้อยกว่าที่ประเมินมาก ซาเล้งแจ้งว่าหักสิ่งปนเปื้อนเกินจริง",
            "status": "PENDING_ADMIN",
            "re_quoted_price": 210.0,
            "scale_photo_url": "https://storage.saleng.app/disputes/scale_photo_01.jpg",
            "seller_photo_urls": ["https://storage.saleng.app/disputes/seller_photo_01.jpg"],
            "actual_weights": {"MAT-PET-BOTTLE": 42.0},
            "created_at": dispute_time,
        }

    def get_stalled_orders(self, min_wait_minutes: float = 30.0) -> List[dict]:
        """
        ดึงรายการคำขอขายสถานะ S2 (Pending) ที่ไม่มีซาเล้งกดรับเกินเกณฑ์เวลา (นาที)
        รองรับ UC-13, D-A03-02, CC-06
        """
        now = datetime.now(timezone.utc)
        results = []
        for order in self.orders.values():
            if order.get("status") != "S2":
                continue
            created_str = order.get("created_at")
            if not created_str:
                continue
            try:
                created_dt = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                elapsed_min = (now - created_dt).total_seconds() / 60.0
            except Exception:
                elapsed_min = 0.0

            if elapsed_min >= min_wait_minutes:
                loc = self.pickup_locations.get(order.get("location_id", ""), {})
                item = {
                    "order_id": order["order_id"],
                    "seller_id": order.get("seller_id", ""),
                    "status": order.get("status", "S2"),
                    "created_at": created_str,
                    "waiting_minutes": round(elapsed_min, 1),
                    "subdistrict": loc.get("subdistrict"),
                    "district": loc.get("district"),
                    "total_est_min_price": float(order.get("total_est_min_price", 0.0)),
                    "total_est_max_price": float(order.get("total_est_max_price", 0.0)),
                    "total_est_weight_kg": float(order.get("total_est_weight_kg", 0.0)),
                    "search_radius_km": float(order.get("search_radius_km", 5.0)),
                    "is_manual_dispatched": bool(order.get("is_manual_dispatched", False)),
                    "dispatched_by": order.get("dispatched_by"),
                    "dispatched_at": order.get("dispatched_at"),
                    "pickup_time": order.get("pickup_time"),
                }
                results.append(item)
        return sorted(results, key=lambda x: x["waiting_minutes"], reverse=True)

    def manual_dispatch_order(
        self,
        order_id: str,
        saleng_id: str,
        admin_id: str = "admin-01",
        notes: Optional[str] = None,
    ) -> Tuple[bool, dict, str]:
        """
        แอดมินมอบหมายงานตรงให้ซาเล้งเฉพาะราย (Direct Assign -> S3)
        รองรับ UC-13, D-A03-03, D-00-01, CC-03, REQ-SEC-001
        """
        order = self.orders.get(order_id)
        if not order:
            return False, {}, "ไม่พบคำขอนัดหมาย"
        if order.get("status") != "S2":
            return False, {}, "คำขอไม่ได้อยู่ในสถานะรอผู้รับงาน (S2)"

        saleng = self.saleng_profiles.get(saleng_id)
        if not saleng:
            return False, {}, "ไม่พบข้อมูลซาเล้ง"
        if not saleng.get("verified", False):
            return False, {}, "ซาเล้งยังไม่ผ่านการยืนยันตัวตน KYC (D-00-01)"
        if not saleng.get("is_online", False):
            return False, {}, "ซาเล้งไม่ได้เปิดสถานะพร้อมรับงาน (Online)"

        now_iso = datetime.now(timezone.utc).isoformat()
        order["status"] = "S3"
        order["assigned_saleng_id"] = saleng_id
        order["buyer_id"] = saleng_id
        order["collector_id"] = saleng_id
        order["is_manual_dispatched"] = True
        order["dispatched_by"] = admin_id
        order["dispatched_at"] = now_iso
        order["version"] = order.get("version", 1) + 1

        self.add_audit_log(
            action="ADMIN_MANUAL_DISPATCH",
            entity_id=order_id,
            actor_id=admin_id,
            details={
                "order_id": order_id,
                "assigned_saleng_id": saleng_id,
                "assigned_saleng_name": saleng.get("display_name"),
                "actor_role": "ADMIN",
                "notes": notes,
            },
        )
        return True, order, "มอบหมายงานสำเร็จ"

    def expand_order_search_radius(
        self,
        order_id: str,
        new_radius_km: float = 10.0,
        admin_id: str = "admin-01",
    ) -> Tuple[bool, dict, str]:
        """
        แอดมินขยายรัศมีการค้นหาของคำขอ (Expand Radius Broadcast)
        รองรับ UC-13, D-A03-03, REQ-SEC-001
        """
        order = self.orders.get(order_id)
        if not order:
            return False, {}, "ไม่พบคำขอนัดหมาย"
        if order.get("status") != "S2":
            return False, {}, "คำขอไม่ได้อยู่ในสถานะรอผู้รับงาน (S2)"

        old_radius = float(order.get("search_radius_km", 5.0))
        order["search_radius_km"] = float(new_radius_km)

        self.add_audit_log(
            action="ADMIN_EXPAND_DISPATCH_RADIUS",
            entity_id=order_id,
            actor_id=admin_id,
            details={
                "order_id": order_id,
                "old_radius_km": old_radius,
                "new_radius_km": float(new_radius_km),
                "actor_role": "ADMIN",
            },
        )
        return True, {
            "order_id": order_id,
            "old_radius_km": old_radius,
            "new_radius_km": float(new_radius_km),
        }, "ขยายรัศมีการค้นหาสำเร็จ"

    def get_disputes(self, status_filter: Optional[str] = "PENDING_ADMIN") -> List[dict]:
        """
        ดึงรายการข้อพิพาททั้งหมด หรือกรองตามสถานะ
        รองรับ UC-13, D-A03-01
        """
        results: List[dict] = []
        for disp in self.dispute_reports.values():
            if status_filter and status_filter.upper() != "ALL":
                if disp.get("status") != status_filter.upper():
                    continue
            order_id = str(disp.get("order_id") or "")
            order = self.orders.get(order_id, {}) if order_id else {}
            seller_id = str(disp.get("seller_id") or order.get("seller_id") or "")
            buyer_id = str(disp.get("buyer_id") or order.get("assigned_saleng_id") or order.get("collector_id") or "")
            seller = self.sellers.get(seller_id, {}) if seller_id else {}
            buyer = self.saleng_profiles.get(buyer_id, {}) if buyer_id else {}
            summary = {
                "dispute_id": disp.get("dispute_id"),
                "order_id": order_id,
                "seller_id": seller_id,
                "buyer_id": buyer_id,
                "seller_name": seller.get("display_name") or seller.get("name") or "ผู้ขาย",
                "buyer_name": buyer.get("display_name") or "ซาเล้ง",
                "dispute_reason": disp.get("dispute_reason", ""),
                "status": disp.get("status", "PENDING_ADMIN"),
                "created_at": disp.get("created_at"),
                "re_quoted_price": disp.get("re_quoted_price"),
                "arbitrated_amount": disp.get("arbitrated_amount"),
            }
            results.append(summary)
        return sorted(results, key=lambda x: str(x.get("created_at") or ""), reverse=True)

    def get_dispute_dossier(self, dispute_id: str) -> Optional[dict]:
        """
        ดึงสำนวนหลักฐานข้อพิพาท 4 มิติ
        รองรับ UC-13, REQ-FN-005, REQ-FN-004, D-A03-04
        """
        disp = self.dispute_reports.get(dispute_id)
        if not disp:
            return None

        order_id = str(disp.get("order_id") or "")
        order = self.orders.get(order_id, {}) if order_id else {}
        seller_id = str(disp.get("seller_id") or order.get("seller_id") or "")
        buyer_id = str(disp.get("buyer_id") or order.get("assigned_saleng_id") or "")
        seller = self.sellers.get(seller_id, {}) if seller_id else {}
        buyer = self.saleng_profiles.get(buyer_id, {}) if buyer_id else {}

        order_items = [it for it in self.items.values() if it.get("order_id") == order_id]
        if not order_items and "items" in order and isinstance(order["items"], list):
            order_items = order["items"]

        original_order = {
            "order_id": order_id,
            "total_est_min_price": float(order.get("total_est_min_price", 0.0)),
            "total_est_max_price": float(order.get("total_est_max_price", 0.0)),
            "total_est_weight_kg": float(order.get("total_est_weight_kg", 0.0)),
            "price_snapshot": order.get("price_snapshot", {}),
            "items": order_items,
        }
        saleng_verification = {
            "scale_photo_url": disp.get("scale_photo_url") or order.get("scale_photo_url"),
            "actual_weights": disp.get("actual_weights") or {"actual_weight_kg": order.get("actual_weight_kg")},
            "re_quoted_price": disp.get("re_quoted_price") or order.get("re_quoted_price"),
            "buyer_notes": disp.get("buyer_notes"),
        }
        seller_dispute = {
            "dispute_reason": disp.get("dispute_reason", ""),
            "seller_photo_urls": disp.get("seller_photo_urls") or order.get("seller_photo_urls", []),
            "seller_notes": disp.get("seller_notes"),
        }
        parties_contact = {
            "seller": {
                "seller_id": seller_id,
                "name": seller.get("display_name") or seller.get("name") or "ผู้ขาย",
                "phone_masked": seller.get("phone_masked") or "08X-XXX-XXXX",
            },
            "buyer": {
                "buyer_id": buyer_id,
                "name": buyer.get("display_name") or "ซาเล้ง",
                "phone_masked": buyer.get("phone_masked") or "08X-XXX-XXXX",
            },
        }

        arbitration_result = None
        if disp.get("status") in ["RESOLVED_COMPLETED", "RESOLVED_CANCELLED"]:
            arbitration_result = {
                "arbitrated_amount": disp.get("arbitrated_amount"),
                "arbitration_note": disp.get("arbitration_note"),
                "arbitrated_by": disp.get("arbitrated_by"),
                "arbitrated_at": disp.get("arbitrated_at"),
            }

        return {
            "dispute_id": dispute_id,
            "order_id": order_id,
            "seller_id": seller_id,
            "buyer_id": buyer_id,
            "status": disp.get("status", "PENDING_ADMIN"),
            "created_at": disp.get("created_at"),
            "dispute_reason": disp.get("dispute_reason", ""),
            "original_order": original_order,
            "saleng_verification": saleng_verification,
            "seller_dispute": seller_dispute,
            "parties_contact": parties_contact,
            "arbitration_result": arbitration_result,
        }

    def resolve_dispute(
        self,
        dispute_id: str,
        action: str,
        arbitrated_amount: Optional[float] = None,
        arbitration_note: Optional[str] = None,
        admin_id: str = "admin-01",
    ) -> Tuple[bool, dict, str]:
        """
        แอดมินตัดสินชี้ขาดข้อพิพาท:
        - RESOLVE_COMPLETE: สั่งปิดงาน (S7) พร้อมยอดเงินชี้ขาดสุทธิ และออกใบเสร็จ
        - RESOLVE_CANCEL: สั่งยกเลิก (S9) ไม่มีการชำระเงิน
        รองรับ UC-13, D-A03-01, D-A03-05, REQ-SEC-001
        """
        disp = self.dispute_reports.get(dispute_id)
        if not disp:
            return False, {}, "ไม่พบข้อพิพาท"
        if disp.get("status") != "PENDING_ADMIN":
            return False, {}, "ข้อพิพาทได้รับการตัดสินแล้ว"

        raw_order_id = disp.get("order_id")
        if not raw_order_id:
            return False, {}, "ไม่พบคำขอนัดหมายที่เชื่อมโยงกับข้อพิพาท"
        order_id = str(raw_order_id)
        order = self.orders.get(order_id)
        if not order:
            return False, {}, "ไม่พบคำขอนัดหมายที่เชื่อมโยงกับข้อพิพาท"

        now_iso = datetime.now(timezone.utc).isoformat()

        if action == "RESOLVE_COMPLETE":
            if arbitrated_amount is None or float(arbitrated_amount) <= 0:
                return False, {}, "การตัดสินให้ปิดงานต้องระบุยอดเงินชี้ขาดสุทธิที่มากกว่า 0 บาท"

            amount = float(arbitrated_amount)
            disp["status"] = "RESOLVED_COMPLETED"
            disp["arbitrated_amount"] = amount
            disp["arbitration_note"] = arbitration_note
            disp["arbitrated_by"] = admin_id
            disp["arbitrated_at"] = now_iso

            order["status"] = "S7"
            order["final_price"] = amount
            order["resolved_at"] = now_iso
            order["version"] = order.get("version", 1) + 1

            receipt_id = f"REC-DISP-{dispute_id}"
            receipt = {
                "receipt_id": receipt_id,
                "order_id": order_id,
                "seller_id": disp.get("seller_id"),
                "buyer_id": disp.get("buyer_id"),
                "total_amount": amount,
                "payment_method": "PROMPTPAY",
                "status": "ISSUED",
                "issued_at": now_iso,
                "notes": f"ออกใบเสร็จตามคำตัดสินชี้ขาดของแอดมิน: {arbitration_note or 'ระงับข้อพิพาทสำเร็จ'}",
            }
            self.receipts[receipt_id] = receipt

            self.add_audit_log(
                action="ADMIN_RESOLVED_DISPUTE",
                entity_id=dispute_id,
                actor_id=admin_id,
                details={
                    "dispute_id": dispute_id,
                    "order_id": order_id,
                    "arbitrated_amount": amount,
                    "arbitration_note": arbitration_note,
                    "actor_role": "ADMIN",
                    "receipt_id": receipt_id,
                },
            )
            return True, {
                "dispute": disp,
                "order_status": "S7",
                "receipt": receipt,
                "arbitrated_amount": amount,
            }, "ตัดสินชี้ขาดให้ปิดงานและออกใบเสร็จสำเร็จ"

        elif action == "RESOLVE_CANCEL":
            disp["status"] = "RESOLVED_CANCELLED"
            disp["arbitration_note"] = arbitration_note
            disp["arbitrated_by"] = admin_id
            disp["arbitrated_at"] = now_iso

            order["status"] = "S9"
            order["cancelled_reason"] = arbitration_note or "คำตัดสินแอดมินสั่งยกเลิกรายการ"
            order["cancelled_at"] = now_iso
            order["version"] = order.get("version", 1) + 1

            self.add_audit_log(
                action="ADMIN_CANCELLED_DISPUTE",
                entity_id=dispute_id,
                actor_id=admin_id,
                details={
                    "dispute_id": dispute_id,
                    "order_id": order_id,
                    "cancellation_reason": arbitration_note,
                    "actor_role": "ADMIN",
                },
            )
            return True, {
                "dispute": disp,
                "order_status": "S9",
                "cancellation_reason": arbitration_note,
            }, "ตัดสินสั่งยกเลิกคำขอสำเร็จ"

        else:
            return False, {}, f"ไม่รองรับคำสั่งตัดสิน: {action}"

    # -------------------------------------------------------------------------
    # ระบบความปลอดภัย ประวัติร่องรอยตรวจสอบ (Audit Trail) และ PDPA (UC-13, Admin 04)
    # -------------------------------------------------------------------------
    def _seed_default_security_compliance(self):
        """กำหนดข้อมูลเริ่มต้นสำหรับ Audit Trail, PDPA Data Retention และ Community Waste Report"""
        now = datetime.now(timezone.utc)
        
        # 1. ตรวจสอบและคำนวณ log_hash ให้กับ audit_logs ที่มีอยู่เดิม
        for log in self.audit_logs:
            if "actor_role" not in log or not log["actor_role"]:
                actor_id = str(log.get("actor_id", ""))
                log["actor_role"] = "ADMIN" if "admin" in actor_id.lower() else "SYSTEM"
            if "log_hash" not in log or not log["log_hash"]:
                log["log_hash"] = compute_audit_log_hash(log)

        # 2. เพิ่ม Seed Logs หากยังมีไม่มากพอ
        if len(self.audit_logs) < 3:
            baseline_logs: List[Dict[str, Any]] = [
                {
                    "action": "PRICE_BENCHMARK_UPDATED",
                    "actor_id": "admin-001",
                    "actor_role": "ADMIN",
                    "entity_id": "bench-cardboard-01",
                    "details": {"category": "MAT-CARDBOARD", "min_price": 3.0, "max_price": 4.0},
                },
                {
                    "action": "DISPATCH_OVERRIDE",
                    "actor_id": "admin-001",
                    "actor_role": "ADMIN",
                    "entity_id": "order-disp-01",
                    "details": {"order_id": "order-disp-01", "new_collector_id": "saleng-001", "reason": "คำสั่งแอดมินแทรกแซง"},
                },
                {
                    "action": "KYC_APPROVED",
                    "actor_id": "admin-001",
                    "actor_role": "ADMIN",
                    "entity_id": "kyc-saleng-01",
                    "details": {"collector_id": "saleng-001", "status": "APPROVED"},
                },
            ]
            for item in baseline_logs:
                details_dict = item.get("details")
                self.add_audit_log(
                    action=str(item.get("action", "")),
                    entity_id=str(item.get("entity_id", "")),
                    actor_id=str(item.get("actor_id", "")),
                    actor_role=str(item.get("actor_role", "ADMIN")),
                    details=details_dict if isinstance(details_dict, dict) else {},
                )

        # 3. Seed Collector GPS History สำหรับทดสอบ PDPA Retention (เกณฑ์ 90 วัน)
        self.collector_gps_history = [
            {
                "gps_id": "gps-seed-01",
                "collector_id": "saleng-001",
                "latitude": 13.736717,
                "longitude": 100.523186,
                "recorded_at": (now - timedelta(days=10)).isoformat(),
            },
            {
                "gps_id": "gps-seed-02",
                "collector_id": "saleng-001",
                "latitude": 13.736800,
                "longitude": 100.523200,
                "recorded_at": (now - timedelta(days=95)).isoformat(),
            },
            {
                "gps_id": "gps-seed-03",
                "collector_id": "saleng-002",
                "latitude": 13.740000,
                "longitude": 100.530000,
                "recorded_at": (now - timedelta(days=120)).isoformat(),
            },
        ]

        # 4. Seed Completed Orders สำหรับ Community Waste Report และ PDPA Address Masking
        order_comp_1 = {
            "id": "order-comp-comm-01",
            "order_id": "order-comp-comm-01",
            "order_number": "ORD-202611-COMM01",
            "seller_id": "sel-seed-01",
            "collector_id": "saleng-001",
            "status": "S7",
            "district": "ปทุมวัน",
            "subdistrict": "ลุมพินี",
            "seller_address": "99/1 ซอยร่วมฤดี แขวงลุมพินี เขตปทุมวัน กทม.",
            "seller_address_masked": "*** ซอยร่วมฤดี แขวงลุมพินี เขตปทุมวัน กทม.",
            "is_address_masked": False,
            "created_at": (now - timedelta(days=3, hours=2)).isoformat(),
            "updated_at": (now - timedelta(days=3)).isoformat(),
            "completed_at": (now - timedelta(days=3)).isoformat(),
            "total_weight": 35.0,
            "total_price": 147.5,
        }
        self.orders["order-comp-comm-01"] = order_comp_1
        self.items["item-comm-01"] = {
            "id": "item-comm-01",
            "order_id": "order-comp-comm-01",
            "category_code": "MAT-CARDBOARD",
            "category_name": "กระดาษลัง",
            "weight_kg": 25.0,
            "unit": "kg",
            "unit_price": 3.5,
            "total_price": 87.5,
        }
        self.items["item-comm-02"] = {
            "id": "item-comm-02",
            "order_id": "order-comp-comm-01",
            "category_code": "MAT-PLASTIC-BOTTLE",
            "category_name": "ขวดพลาสติก",
            "weight_kg": 10.0,
            "unit": "kg",
            "unit_price": 6.0,
            "total_price": 60.0,
        }

        order_comp_2 = {
            "id": "order-comp-comm-02",
            "order_id": "order-comp-comm-02",
            "order_number": "ORD-202611-COMM02",
            "seller_id": "sel-seed-02",
            "collector_id": "saleng-002",
            "status": "S7",
            "district": "คลองเตย",
            "subdistrict": "พระโขนง",
            "seller_address": "55/4 สุขุมวิท 42 แขวงพระโขนง เขตคลองเตย กทม.",
            "seller_address_masked": "*** สุขุมวิท 42 แขวงพระโขนง เขตคลองเตย กทม.",
            "is_address_masked": False,
            "created_at": (now - timedelta(hours=2)).isoformat(),
            "updated_at": (now - timedelta(hours=1)).isoformat(),
            "completed_at": (now - timedelta(hours=1)).isoformat(),
            "total_weight": 50.0,
            "total_price": 200.0,
        }
        self.orders["order-comp-comm-02"] = order_comp_2
        self.items["item-comm-03"] = {
            "id": "item-comm-03",
            "order_id": "order-comp-comm-02",
            "category_code": "MAT-CARDBOARD",
            "category_name": "กระดาษลัง",
            "weight_kg": 50.0,
            "unit": "kg",
            "unit_price": 4.0,
            "total_price": 200.0,
        }

    def query_audit_logs(
        self,
        action: Optional[str] = None,
        actor_role: Optional[str] = None,
        actor_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[int, List[dict]]:
        """
        สืบค้นประวัติ Audit Trail กรองตามเงื่อนไข พร้อมทำ Pagination
        รองรับ D-A04-01, REQ-SEC-001
        """
        results = list(self.audit_logs)

        if action:
            results = [log for log in results if log.get("action") == action]
        if actor_role:
            results = [log for log in results if str(log.get("actor_role", "")).upper() == actor_role.upper()]
        if actor_id:
            results = [log for log in results if log.get("actor_id") == actor_id]
        if start_date:
            results = [log for log in results if str(log.get("timestamp", "")) >= start_date]
        if end_date:
            results = [log for log in results if str(log.get("timestamp", "")) <= end_date]

        # เรียงลำดับจากใหม่ล่าสุดไปเก่าสุด
        results.sort(key=lambda x: str(x.get("timestamp", "")), reverse=True)
        total_records = len(results)
        paged_results = results[offset : offset + limit]
        return total_records, paged_results

    def verify_audit_logs_integrity(self) -> Tuple[int, bool, List[str]]:
        """
        ตรวจสอบความสมบูรณ์ของบันทึก Audit Logs ด้วย SHA-256 (Immutability Check)
        รองรับ REQ-SEC-001, P-07, D-A04-05
        """
        corrupted_log_ids: List[str] = []
        for log in self.audit_logs:
            expected_hash = compute_audit_log_hash(log)
            actual_hash = log.get("log_hash")
            if not actual_hash or actual_hash != expected_hash:
                corrupted_log_ids.append(log.get("log_id", "unknown"))

        is_valid = len(corrupted_log_ids) == 0
        return len(self.audit_logs), is_valid, corrupted_log_ids

    def get_community_waste_report(
        self,
        period: Optional[str] = None,
        district_filter: Optional[str] = None,
    ) -> List[dict]:
        """
        สร้างรายงานสถิติขยะรีไซเคิลชุมชนรายเขต/แขวง แบบนิรนาม 100% ปลอด PII
        รองรับ D-A04-03, REQ-SEC-002, AC-A04-05
        """
        grouped: Dict[Tuple[str, str, str], dict] = {}
        for order in self.orders.values():
            if order.get("status") not in ("S7", "COMPLETED"):
                continue

            district = order.get("district") or "ไม่ระบุเขต"
            subdistrict = order.get("subdistrict") or "ไม่ระบุแขวง"
            completed_at = order.get("completed_at") or order.get("updated_at") or ""
            current_period = completed_at[:7] if len(completed_at) >= 7 else "2026-11"

            if district_filter and district != district_filter:
                continue
            if period and not completed_at.startswith(period):
                continue

            order_id = order.get("id") or order.get("order_id")
            # ดึงรายการขยะที่อยู่ในออเดอร์นี้
            matched_items = [item for item in self.items.values() if item.get("order_id") == order_id]
            for item in matched_items:
                cat_name = item.get("category_name") or "ขยะรีไซเคิลทั่วไป"
                key = (district, subdistrict, cat_name)
                weight = float(item.get("weight_kg", 0.0))
                amount = float(item.get("total_price", 0.0))

                if key not in grouped:
                    grouped[key] = {
                        "district": district,
                        "subdistrict": subdistrict,
                        "category_name": cat_name,
                        "total_weight_kg": 0.0,
                        "total_amount_baht": 0.0,
                        "total_transactions": 0,
                        "period": period or current_period,
                    }
                grouped[key]["total_weight_kg"] += weight
                grouped[key]["total_amount_baht"] += amount
                grouped[key]["total_transactions"] += 1

        results = list(grouped.values())
        for r in results:
            r["total_weight_kg"] = round(r["total_weight_kg"], 2)
            r["total_amount_baht"] = round(r["total_amount_baht"], 2)
        return results

    def get_pdpa_retention_status(self) -> dict:
        """
        ตรวจสอบสถานะการเก็บรักษาข้อมูลตามกฎหมาย PDPA (GPS 90 วัน, Masked Address 24 ชม.)
        รองรับ D-A04-04, REQ-SEC-002, CT-01
        """
        now = datetime.now(timezone.utc)
        gps_cutoff = now - timedelta(days=90)
        address_cutoff = now - timedelta(hours=24)

        total_gps = len(self.collector_gps_history)
        expired_gps = 0
        for g in self.collector_gps_history:
            recorded_str = g.get("recorded_at", "")
            if recorded_str:
                rec_dt = datetime.fromisoformat(recorded_str.replace("Z", "+00:00"))
                if rec_dt < gps_cutoff:
                    expired_gps += 1

        completed_orders = [o for o in self.orders.values() if o.get("status") in ("S7", "S9", "COMPLETED", "CANCELLED")]
        unmasked_gt_24h = 0
        for o in completed_orders:
            completed_str = o.get("completed_at") or o.get("cancelled_at") or o.get("updated_at") or ""
            is_masked = o.get("is_address_masked", False)
            if completed_str and not is_masked:
                comp_dt = datetime.fromisoformat(completed_str.replace("Z", "+00:00"))
                if comp_dt < address_cutoff:
                    unmasked_gt_24h += 1

        return {
            "total_gps_records": total_gps,
            "expired_gps_records": expired_gps,
            "retention_policy_gps_days": 90,
            "total_completed_orders": len(completed_orders),
            "unmasked_completed_orders_gt_24h": unmasked_gt_24h,
            "retention_policy_address_hours": 24,
            "last_checked_at": now.isoformat(),
        }

    def purge_expired_pdpa_data(self, admin_id: str) -> Tuple[int, int]:
        """
        ล้างพิกัด GPS ซาเล้งที่เกิน 90 วัน และ Mask ข้อมูลที่อยู่ผู้ขายหลังจบงานเกิน 24 ชม. ถาวร
        รองรับ D-A04-04, REQ-SEC-002, CT-01
        """
        now = datetime.now(timezone.utc)
        gps_cutoff = now - timedelta(days=90)
        address_cutoff = now - timedelta(hours=24)

        initial_gps_count = len(self.collector_gps_history)
        self.collector_gps_history = [
            g for g in self.collector_gps_history
            if datetime.fromisoformat(g.get("recorded_at", "").replace("Z", "+00:00")) >= gps_cutoff
        ]
        purged_gps_count = initial_gps_count - len(self.collector_gps_history)

        completed_orders = [o for o in self.orders.values() if o.get("status") in ("S7", "S9", "COMPLETED", "CANCELLED")]
        masked_orders_count = 0
        for o in completed_orders:
            completed_str = o.get("completed_at") or o.get("cancelled_at") or o.get("updated_at") or ""
            is_masked = o.get("is_address_masked", False)
            if completed_str and not is_masked:
                comp_dt = datetime.fromisoformat(completed_str.replace("Z", "+00:00"))
                if comp_dt < address_cutoff:
                    masked_addr = o.get("seller_address_masked") or "*** (Masked ตามนโยบาย PDPA)"
                    o["seller_address"] = masked_addr
                    o["is_address_masked"] = True
                    masked_orders_count += 1

        # บันทึกประวัติการ Purge ลงใน Audit Trail
        self.add_audit_log(
            action="ADMIN_PURGED_EXPIRED_DATA",
            entity_id="pdpa-retention-job",
            actor_id=admin_id,
            actor_role="DPO",
            details={
                "purged_gps_count": purged_gps_count,
                "masked_orders_count": masked_orders_count,
                "retention_policy_gps_days": 90,
                "retention_policy_address_hours": 24,
            },
        )

        return purged_gps_count, masked_orders_count


# Singleton instance สำหรับเข้าถึง Database
supabase_store = SupabaseStore()

