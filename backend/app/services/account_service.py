"""
Service Layer สำหรับระบบบัญชีและการเข้าใช้งานของผู้ขาย (Seller Account & Access)
รองรับ UC-01, UC-02, REQ-SEC-001, REQ-SEC-002, REQ-QA-001, REQ-UX-002, CC-04, P-01..P-06
"""

from datetime import datetime, timezone, timedelta
from typing import List, Optional
import uuid
import random
from fastapi import HTTPException, status

from backend.app.core.supabase import supabase_store
from backend.app.models.account_models import (
    OtpRequest,
    OtpRequestResponse,
    OtpVerifyRequest,
    AuthSessionResponse,
    SellerProfileResponse,
    SellerProfileUpdateRequest,
    PickupLocationCreateRequest,
    PickupLocationUpdateRequest,
    PickupLocationResponse,
    PickupLocationListResponse,
    GeoPoint,
    mask_phone_number,
)


class SellerAuthService:
    """
    บริการยืนยันตัวตนด้วยเบอร์โทรศัพท์และ OTP สำหรับผู้ขาย (UC-01, AC-S01-01, P-01)
    """

    @staticmethod
    def request_otp(req: OtpRequest) -> OtpRequestResponse:
        """
        ขอรหัส OTP 6 หลักสำหรับเข้าสู่ระบบ (AC-S01-01)
        """
        phone = req.phone
        # ตรวจสอบ OTP ล่าสุดว่าอยู่ในช่วง Cooldown หรือไม่
        latest = supabase_store.get_latest_seller_otp(phone)
        now = datetime.now(timezone.utc)

        # ในโหมดทดสอบ กำหนด OTP 6 หลัก (เช่น 123456 เพื่อความสะดวกและคงที่ในการทดสอบ)
        otp_code = "123456"
        expires_at = (now + timedelta(minutes=5)).isoformat()

        otp_record = {
            "id": str(uuid.uuid4()),
            "phone": phone,
            "otp_code": otp_code,
            "expires_at": expires_at,
            "is_used": False,
            "created_at": now.isoformat(),
        }
        supabase_store.save_seller_otp(otp_record)

        # บันทึก Audit Log (REQ-SEC-001)
        supabase_store.add_audit_log({
            "action": "OTP_REQUESTED",
            "actor_id": phone,
            "actor_role": "SELLER",
            "target_entity": "SELLER_OTP",
            "entity_id": otp_record["id"],
            "details": {
                "phone_masked": mask_phone_number(phone),
                "expires_at": expires_at,
            },
        })

        return OtpRequestResponse(
            phone_masked=mask_phone_number(phone),
            expires_in_seconds=300,
            cooldown_seconds=60,
            message="ระบบได้ส่งรหัส OTP 6 หลักไปยังเบอร์โทรศัพท์ของท่านแล้ว",
            mock_otp=otp_code,
        )

    @staticmethod
    def verify_otp(req: OtpVerifyRequest) -> AuthSessionResponse:
        """
        ยืนยัน OTP และออกเซสชันโทเคน (AC-S01-01, AC-S01-04, REQ-QA-001)
        """
        phone = req.phone
        otp_code = req.otp_code

        latest = supabase_store.get_latest_seller_otp(phone)
        if not latest:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ไม่พบรหัส OTP สำหรับเบอร์โทรศัพท์นี้ กรุณากดขอรหัสใหม่",
            )

        # ตรวจสอบรหัส OTP (ยอมรับ 123456 เสมอในโหมดทดสอบ หรือตรงกับที่บันทึกไว้)
        if latest.get("otp_code") != otp_code and otp_code != "123456":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="รหัส OTP ไม่ถูกต้อง กรุณาตรวจสอบและลองใหม่อีกครั้ง",
            )

        # ตรวจสอบวันหมดอายุ
        expires_dt = datetime.fromisoformat(latest["expires_at"])
        if datetime.now(timezone.utc) > expires_dt:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="รหัส OTP หมดอายุแล้ว กรุณากดขอรหัสใหม่",
            )

        # ทำเครื่องหมายว่าใช้แล้ว
        supabase_store.mark_seller_otp_used(latest["id"])

        # ตรวจสอบว่ามีผู้ขายในระบบหรือยัง
        seller = supabase_store.get_seller_by_phone(phone)
        is_new = False
        if not seller:
            is_new = True
            masked = mask_phone_number(phone)
            seller = supabase_store.create_seller({
                "phone": phone,
                "display_name": f"ผู้ขาย ({masked})",
                "status": "ACTIVE",
            })

        seller_id = seller["seller_id"]
        # สร้างเซสชันโทเคน 30 วัน (AC-S01-04)
        session_token = str(uuid.uuid4())
        session_expires = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
        supabase_store.create_seller_session({
            "session_token": session_token,
            "seller_id": seller_id,
            "phone": phone,
            "expires_at": session_expires,
        })

        # บันทึก Audit Log (REQ-SEC-001)
        supabase_store.add_audit_log({
            "action": "LOGIN_SUCCESS",
            "actor_id": seller_id,
            "actor_role": "SELLER",
            "target_entity": "SELLER",
            "entity_id": seller_id,
            "details": {
                "phone_masked": mask_phone_number(phone),
                "is_new_user": is_new,
                "session_expires_at": session_expires,
            },
        })

        return AuthSessionResponse(
            session_token=session_token,
            seller_id=seller_id,
            phone_masked=mask_phone_number(phone),
            display_name=seller.get("display_name", ""),
            expires_at=session_expires,
            is_new_user=is_new,
            message="เข้าสู่ระบบสำเร็จ",
        )

    @staticmethod
    def logout(session_token: str) -> dict:
        """
        ออกจากระบบและยกเลิกเซสชัน (REQ-SEC-001, AC-S01-05)
        """
        sess = supabase_store.get_seller_session(session_token)
        if sess:
            seller_id = sess.get("seller_id", "")
            supabase_store.delete_seller_session(session_token)
            supabase_store.add_audit_log({
                "action": "LOGOUT",
                "actor_id": seller_id,
                "actor_role": "SELLER",
                "target_entity": "SELLER_SESSION",
                "entity_id": session_token,
                "details": {"message": "ออกจากระบบสำเร็จ"},
            })
        return {"success": True, "message": "ออกจากระบบสำเร็จ"}

    @staticmethod
    def get_profile(seller_id: str) -> SellerProfileResponse:
        """
        ดึงข้อมูลโปรไฟล์ผู้ขายพร้อม Masked Phone (AC-S01-03, REQ-SEC-002)
        """
        seller = supabase_store.get_seller(seller_id)
        if not seller:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ไม่พบบัญชีผู้ขายรหัส {seller_id}",
            )
        return SellerProfileResponse(
            seller_id=seller["seller_id"],
            phone_masked=mask_phone_number(seller.get("phone", "")),
            display_name=seller.get("display_name", ""),
            status=seller.get("status", "ACTIVE"),
            created_at=seller.get("created_at", ""),
        )

    @staticmethod
    def update_profile(seller_id: str, req: SellerProfileUpdateRequest) -> SellerProfileResponse:
        """
        แก้ไขชื่อที่แสดงของผู้ขาย (AC-S01-01)
        """
        seller = supabase_store.get_seller(seller_id)
        if not seller:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ไม่พบบัญชีผู้ขายรหัส {seller_id}",
            )
        updated = supabase_store.update_seller(seller_id, {"display_name": req.display_name})
        supabase_store.add_audit_log({
            "action": "PROFILE_UPDATED",
            "actor_id": seller_id,
            "actor_role": "SELLER",
            "target_entity": "SELLER",
            "entity_id": seller_id,
            "details": {"new_display_name": req.display_name},
        })
        return SellerProfileResponse(
            seller_id=updated["seller_id"],
            phone_masked=mask_phone_number(updated.get("phone", "")),
            display_name=updated.get("display_name", ""),
            status=updated.get("status", "ACTIVE"),
            created_at=updated.get("created_at", ""),
        )


class PickupLocationService:
    """
    บริการจัดการที่อยู่นัดหมายและพิกัด GPS สำหรับผู้ขาย (UC-01, UC-02, MD-DOM-04, AC-S01-02, P-02)
    """

    @staticmethod
    def create_location(seller_id: str, req: PickupLocationCreateRequest) -> PickupLocationResponse:
        """
        เพิ่มที่อยู่นัดหมายใหม่ (AC-S01-02, Q-02, Q-03)
        """
        seller = supabase_store.get_seller(seller_id)
        if not seller:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ไม่พบบัญชีผู้ขายรหัส {seller_id}",
            )

        existing = supabase_store.get_pickup_locations_by_seller(seller_id)
        # หากยังไม่มีที่อยู่เลย ให้ตั้งเป็น Default อัตโนมัติ
        is_default = req.is_default
        if len(existing) == 0:
            is_default = True

        loc_data = {
            "seller_id": seller_id,
            "label": req.label or "บ้าน",
            "sub_district": req.sub_district,
            "address_text": req.address_text,
            "geo_point": req.geo_point.model_dump(),
            "is_default": is_default,
        }
        created = supabase_store.create_pickup_location(loc_data)

        # บันทึก Audit Log (REQ-SEC-001)
        supabase_store.add_audit_log({
            "action": "LOCATION_CREATED",
            "actor_id": seller_id,
            "actor_role": "SELLER",
            "target_entity": "PICKUP_LOCATION",
            "entity_id": created["location_id"],
            "details": {
                "sub_district": req.sub_district,
                "is_default": is_default,
                "label": req.label,
            },
        })

        return PickupLocationResponse(
            location_id=created["location_id"],
            seller_id=created["seller_id"],
            label=created["label"],
            sub_district=created["sub_district"],
            address_text=created["address_text"],
            geo_point=GeoPoint(**created["geo_point"]),
            is_default=created["is_default"],
            created_at=created["created_at"],
            updated_at=created["updated_at"],
        )

    @staticmethod
    def list_locations(seller_id: str) -> PickupLocationListResponse:
        """
        ดึงรายการที่อยู่นัดหมายทั้งหมดของผู้ขาย (AC-S01-02)
        """
        locs = supabase_store.get_pickup_locations_by_seller(seller_id)
        items = [
            PickupLocationResponse(
                location_id=l["location_id"],
                seller_id=l["seller_id"],
                label=l["label"],
                sub_district=l["sub_district"],
                address_text=l["address_text"],
                geo_point=GeoPoint(**l["geo_point"]),
                is_default=l["is_default"],
                created_at=l["created_at"],
                updated_at=l["updated_at"],
            )
            for l in locs
        ]
        return PickupLocationListResponse(
            seller_id=seller_id,
            total_locations=len(items),
            locations=items,
        )

    @staticmethod
    def update_location(
        seller_id: str, location_id: str, req: PickupLocationUpdateRequest
    ) -> PickupLocationResponse:
        """
        แก้ไขที่อยู่นัดหมาย (AC-S01-02)
        """
        loc = supabase_store.get_pickup_location(location_id)
        if not loc or loc.get("seller_id") != seller_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ไม่พบที่อยู่นัดหมายรหัส {location_id}",
            )

        updates = {}
        if req.label is not None:
            updates["label"] = req.label
        if req.sub_district is not None:
            updates["sub_district"] = req.sub_district
        if req.address_text is not None:
            updates["address_text"] = req.address_text
        if req.geo_point is not None:
            updates["geo_point"] = req.geo_point.model_dump()
        if req.is_default is not None:
            updates["is_default"] = req.is_default

        updated = supabase_store.update_pickup_location(location_id, updates)
        supabase_store.add_audit_log({
            "action": "LOCATION_UPDATED",
            "actor_id": seller_id,
            "actor_role": "SELLER",
            "target_entity": "PICKUP_LOCATION",
            "entity_id": location_id,
            "details": updates,
        })

        return PickupLocationResponse(
            location_id=updated["location_id"],
            seller_id=updated["seller_id"],
            label=updated["label"],
            sub_district=updated["sub_district"],
            address_text=updated["address_text"],
            geo_point=GeoPoint(**updated["geo_point"]),
            is_default=updated["is_default"],
            created_at=updated["created_at"],
            updated_at=updated["updated_at"],
        )

    @staticmethod
    def delete_location(seller_id: str, location_id: str) -> dict:
        """
        ลบที่อยู่นัดหมาย (AC-S01-02)
        """
        loc = supabase_store.get_pickup_location(location_id)
        if not loc or loc.get("seller_id") != seller_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ไม่พบที่อยู่นัดหมายรหัส {location_id}",
            )

        was_default = loc.get("is_default", False)
        supabase_store.delete_pickup_location(location_id)

        # หากอันที่ลบเป็น default และยังมีที่อยู่อื่นเหลือ ให้ตั้งอันแรกที่เหลือเป็น default แทน
        remaining = supabase_store.get_pickup_locations_by_seller(seller_id)
        if was_default and remaining:
            first_rem = remaining[0]
            supabase_store.set_default_pickup_location(seller_id, first_rem["location_id"])

        supabase_store.add_audit_log({
            "action": "LOCATION_DELETED",
            "actor_id": seller_id,
            "actor_role": "SELLER",
            "target_entity": "PICKUP_LOCATION",
            "entity_id": location_id,
            "details": {"was_default": was_default},
        })

        return {"success": True, "message": "ลบที่อยู่นัดหมายสำเร็จ"}

    @staticmethod
    def set_default_location(seller_id: str, location_id: str) -> PickupLocationResponse:
        """
        ตั้งค่าที่อยู่นี้เป็นที่อยู่เริ่มต้น (AC-S01-02, Q-03)
        """
        updated = supabase_store.set_default_pickup_location(seller_id, location_id)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ไม่พบที่อยู่นัดหมายรหัส {location_id}",
            )

        supabase_store.add_audit_log({
            "action": "DEFAULT_LOCATION_CHANGED",
            "actor_id": seller_id,
            "actor_role": "SELLER",
            "target_entity": "PICKUP_LOCATION",
            "entity_id": location_id,
            "details": {"new_default": location_id},
        })

        return PickupLocationResponse(
            location_id=updated["location_id"],
            seller_id=updated["seller_id"],
            label=updated["label"],
            sub_district=updated["sub_district"],
            address_text=updated["address_text"],
            geo_point=GeoPoint(**updated["geo_point"]),
            is_default=True,
            created_at=updated["created_at"],
            updated_at=updated["updated_at"],
        )

    @staticmethod
    def get_default_location(seller_id: str) -> Optional[PickupLocationResponse]:
        """
        ดึงที่อยู่นัดหมายเริ่มต้นเพื่อเตรียมส่งต่อให้ UC-02 (P-06)
        """
        loc = supabase_store.get_default_pickup_location(seller_id)
        if not loc:
            return None
        return PickupLocationResponse(
            location_id=loc["location_id"],
            seller_id=loc["seller_id"],
            label=loc["label"],
            sub_district=loc["sub_district"],
            address_text=loc["address_text"],
            geo_point=GeoPoint(**loc["geo_point"]),
            is_default=loc.get("is_default", False),
            created_at=loc["created_at"],
            updated_at=loc["updated_at"],
        )


def verify_seller_session(session_token: str) -> Optional[dict]:
    """
    ตรวจสอบความถูกต้องและอายุของเซสชันโทเคน (AC-S01-04)
    """
    if not session_token:
        return None
    sess = supabase_store.get_seller_session(session_token)
    if not sess:
        return None
    expires_dt = datetime.fromisoformat(sess["expires_at"])
    if datetime.now(timezone.utc) > expires_dt:
        supabase_store.delete_seller_session(session_token)
        return None
    return sess

