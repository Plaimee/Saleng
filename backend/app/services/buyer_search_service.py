"""
Buyer Search Service: ค้นหา กรอง ตรึงคนโปรด และส่งคำขอนัดหมายเจาะจงบุคคล
รองรับ UC-03, REQ-FN-001, REQ-QA-001, REQ-UX-001, REQ-SEC-001, REQ-SEC-002, CC-03, CC-06, Card 03, P-01..P-06
"""

import math
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from fastapi import HTTPException, status
from backend.app.core.supabase import supabase_store
from backend.app.models.buyer_search_models import (
    SalengProfileResponse,
    CollectorListResponse,
    DirectAppointmentResponse,
)


class BuyerSearchService:
    @staticmethod
    def calculate_haversine_distance(
        lat1: float, lon1: float, lat2: float, lon2: float
    ) -> float:
        """
        คำนวณระยะทางแบบเส้นตรงด้วยสูตร Haversine พร้อมตัวคูณชดเชยถนนจริง 1.35
        รองรับ CC-03, REQ-OP-002
        """
        R = 6371.0  # รัศมีโลกเฉลี่ย (กม.)
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_phi / 2.0) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
        )
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        straight_km = R * c

        # คูณค่าชดเชยถนนจริง 1.35 ตามข้อกำหนด CC-03
        road_km = straight_km * 1.35
        return round(road_km, 2)

    @staticmethod
    def search_collectors(
        seller_id: str = "seller-01",
        order_id: Optional[str] = None,
        radius_km: float = 5.0,
        vehicle_type: Optional[str] = None,
        min_rating: Optional[float] = None,
        category: Optional[str] = None,
    ) -> CollectorListResponse:
        """
        ค้นหารายชื่อซาเล้งในพื้นที่ตามเงื่อนไข (AC-S03-01..03, P-01..P-03)
        """
        # 1. ระบุพิกัดตั้งต้นของผู้ขาย
        origin_lat = 13.7890
        origin_lng = 100.5740

        default_loc = supabase_store.get_default_pickup_location(seller_id)
        if default_loc and "geo_point" in default_loc:
            origin_lat = default_loc["geo_point"].get("latitude", origin_lat)
            origin_lng = default_loc["geo_point"].get("longitude", origin_lng)

        # 2. ตรวจสอบว่าคำขอมีของชิ้นใหญ่หรือไม่ (Bulky Auto-Detection Card 03, P-03)
        has_bulky = False
        bulky_warning = None
        if order_id:
            order = supabase_store.get_order(order_id)
            if order and "pickup_location" in order:
                loc = order["pickup_location"]
                if "geo_point" in loc:
                    origin_lat = loc["geo_point"].get("latitude", origin_lat)
                    origin_lng = loc["geo_point"].get("longitude", origin_lng)

            # ตรวจสอบรายการของเก่าในคำขอนี้
            for item in supabase_store.items.values():
                if item.get("order_id") == order_id:
                    code = item.get("category_code") or ""
                    if "BULKY" in code or code == "BULKY-APPLIANCE":
                        has_bulky = True
                        bulky_warning = (
                            "📦 คำขอของคุณมีของชิ้นใหญ่ (ตู้เย็น/เครื่องซักผ้า) "
                            "ระบบแนะนำซาเล้งที่มีรถกระบะหรือซาเล้งขนาดใหญ่"
                        )
                        break

        # 3. ดึงซาเล้งและกรองตามเงื่อนไข
        all_profiles = supabase_store.get_all_saleng_profiles()
        matched = []

        for p in all_profiles:
            # D-00-01: ต้องผ่าน KYC 100%
            if not p.get("verified", False):
                continue

            # ต้องเปิดสถานะ Online พร้อมรับงาน
            if not p.get("is_online", False):
                continue

            # คำนวณระยะทาง
            dist = BuyerSearchService.calculate_haversine_distance(
                origin_lat, origin_lng, p["current_lat"], p["current_lng"]
            )

            # กรองตามรัศมี
            if dist > radius_km:
                continue

            # กรองตามประเภทยานพาหนะ
            if vehicle_type and p.get("vehicle_type") != vehicle_type:
                continue

            # กรองตามคะแนนรีวิวขั้นต่ำ
            if min_rating and p.get("rating", 0.0) < min_rating:
                continue

            # กรองตามชนิดของที่รับ
            if category:
                accepted = p.get("accepted_categories", [])
                if category not in accepted:
                    continue

            # ตรวจสอบสถานะคนโปรด (AC-S03-02, P-02)
            is_fav = supabase_store.is_favorite(seller_id, p["saleng_id"])

            matched.append(
                SalengProfileResponse(
                    saleng_id=p["saleng_id"],
                    display_name=p["display_name"],
                    phone=p["phone"],
                    avatar_url=p.get("avatar_url"),
                    verified=p.get("verified", True),
                    rating=p.get("rating", 5.0),
                    completed_jobs_count=p.get("completed_jobs_count", 0),
                    vehicle_type=p["vehicle_type"],
                    max_capacity_kg=p.get("max_capacity_kg", 200.0),
                    current_lat=p["current_lat"],
                    current_lng=p["current_lng"],
                    distance_km=dist,
                    is_favorite=is_fav,
                    is_online=p.get("is_online", True),
                    accepted_categories=p.get("accepted_categories", []),
                )
            )

        # 4. สองระดับการจัดเรียง (Two-tier sorting): คนโปรดไว้บนสุดเสมอ -> ระยะทางใกล้ที่สุด -> คะแนนรีวิวสูงสุด (Q-02, P-02)
        matched.sort(
            key=lambda x: (not x.is_favorite, x.distance_km, -x.rating)
        )

        return CollectorListResponse(
            collectors=matched,
            total_count=len(matched),
            has_bulky_items=has_bulky,
            bulky_warning_message=bulky_warning,
        )

    @staticmethod
    def get_collector_profile(
        saleng_id: str, seller_id: str = "seller-01"
    ) -> SalengProfileResponse:
        """
        ดึงข้อมูลโปรไฟล์ละเอียดของซาเล้ง (AC-S03-01)
        """
        p = supabase_store.get_saleng_profile(saleng_id)
        if not p:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ไม่พบข้อมูลผู้รับซื้อรหัส {saleng_id}",
            )

        is_fav = supabase_store.is_favorite(seller_id, saleng_id)
        return SalengProfileResponse(
            saleng_id=p["saleng_id"],
            display_name=p["display_name"],
            phone=p["phone"],
            avatar_url=p.get("avatar_url"),
            verified=p.get("verified", True),
            rating=p.get("rating", 5.0),
            completed_jobs_count=p.get("completed_jobs_count", 0),
            vehicle_type=p["vehicle_type"],
            max_capacity_kg=p.get("max_capacity_kg", 200.0),
            current_lat=p["current_lat"],
            current_lng=p["current_lng"],
            distance_km=0.0,
            is_favorite=is_fav,
            is_online=p.get("is_online", True),
            accepted_categories=p.get("accepted_categories", []),
        )

    @staticmethod
    def toggle_favorite(seller_id: str, saleng_id: str) -> bool:
        """
        เปิด/ปิดการบันทึกเป็นซาเล้งที่เคยใช้บริการ (AC-S03-02, P-02)
        """
        p = supabase_store.get_saleng_profile(saleng_id)
        if not p:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ไม่พบข้อมูลผู้รับซื้อรหัส {saleng_id}",
            )

        if supabase_store.is_favorite(seller_id, saleng_id):
            supabase_store.remove_favorite(seller_id, saleng_id)
            return False
        else:
            supabase_store.add_favorite(seller_id, saleng_id)
            return True

    @staticmethod
    def get_favorites(seller_id: str = "seller-01") -> List[SalengProfileResponse]:
        """
        ดึงรายชื่อซาเล้งที่เคยใช้บริการทั้งหมดของผู้ขาย (AC-S03-02)
        """
        fav_ids = supabase_store.get_seller_favorites(seller_id)
        result = []
        for fid in fav_ids:
            p = supabase_store.get_saleng_profile(fid)
            if p:
                result.append(
                    SalengProfileResponse(
                        saleng_id=p["saleng_id"],
                        display_name=p["display_name"],
                        phone=p["phone"],
                        avatar_url=p.get("avatar_url"),
                        verified=p.get("verified", True),
                        rating=p.get("rating", 5.0),
                        completed_jobs_count=p.get("completed_jobs_count", 0),
                        vehicle_type=p["vehicle_type"],
                        max_capacity_kg=p.get("max_capacity_kg", 200.0),
                        current_lat=p["current_lat"],
                        current_lng=p["current_lng"],
                        distance_km=0.0,
                        is_favorite=True,
                        is_online=p.get("is_online", True),
                        accepted_categories=p.get("accepted_categories", []),
                    )
                )
        return result

    @staticmethod
    def send_direct_request(
        order_id: str,
        saleng_id: str,
        seller_id: str = "seller-01",
        notes: Optional[str] = None,
    ) -> DirectAppointmentResponse:
        """
        ส่งคำขอนัดหมายเจาะจงบุคคล เปลี่ยนสถานะคำขอเป็น S2 พร้อมนับถอยหลัง 15 นาที (AC-S03-05, P-05, Q-01)
        """
        saleng = supabase_store.get_saleng_profile(saleng_id)
        if not saleng:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ไม่พบผู้รับซื้อรหัส {saleng_id}",
            )

        if not saleng.get("verified", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ไม่สามารถนัดหมายซาเล้งที่ยังไม่ผ่านการยืนยันตัวตนได้",
            )

        if not saleng.get("is_online", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ซาเล้งท่านนี้ปิดสถานะรับงานชั่วคราว กรุณาเลือกท่านอื่น",
            )

        # ตรวจสอบหรือสร้างคำขอ
        order = supabase_store.get_order(order_id)
        if not order:
            # สร้าง mock draft order ให้หากไม่มี เพื่อความยืดหยุ่นในการทดสอบ
            order = {
                "order_id": order_id,
                "seller_id": seller_id,
                "status": "S1",
                "items": [],
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            supabase_store.orders[order_id] = order

        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
        expires_str = expires_at.isoformat()

        order["assigned_saleng_id"] = saleng_id
        order["status"] = "S2"  # Transition S1 -> S2 Matched / Pending
        order["direct_request_expires_at"] = expires_str
        if notes:
            order["appointment_notes"] = notes

        # บันทึก Audit Log (REQ-SEC-001, P-05)
        supabase_store.add_audit_log(
            action="COLLECTOR_DIRECT_REQUESTED",
            entity_id=order_id,
            actor_id=seller_id,
            details={
                "saleng_id": saleng_id,
                "saleng_name": saleng["display_name"],
                "expires_at": expires_str,
                "notes": notes,
            },
        )

        saleng_resp = SalengProfileResponse(
            saleng_id=saleng["saleng_id"],
            display_name=saleng["display_name"],
            phone=saleng["phone"],
            avatar_url=saleng.get("avatar_url"),
            verified=saleng.get("verified", True),
            rating=saleng.get("rating", 5.0),
            completed_jobs_count=saleng.get("completed_jobs_count", 0),
            vehicle_type=saleng["vehicle_type"],
            max_capacity_kg=saleng.get("max_capacity_kg", 200.0),
            current_lat=saleng["current_lat"],
            current_lng=saleng["current_lng"],
            distance_km=0.0,
            is_favorite=supabase_store.is_favorite(seller_id, saleng_id),
            is_online=saleng.get("is_online", True),
            accepted_categories=saleng.get("accepted_categories", []),
        )

        return DirectAppointmentResponse(
            order_id=order_id,
            assigned_saleng=saleng_resp,
            status="S2",
            direct_request_expires_at=expires_str,
            message=f"ส่งคำขอนัดหมายไปยัง {saleng['display_name']} เรียบร้อยแล้ว (รอการตอบรับภายใน 15 นาที)",
        )

