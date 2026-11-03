"""
Service Layer สำหรับระบบบัญชีและการยืนยันตัวตนซาเล้ง (Buyer 01: Account & KYC)
รองรับ UC-01, MD-DOM-04, REQ-FN-001, REQ-SEC-001, REQ-SEC-002, REQ-QA-001, CC-01..06, D-00-01, P-01..P-06
"""

from datetime import datetime, timezone
from typing import Optional
from fastapi import HTTPException, status
from backend.app.core.supabase import supabase_store
from backend.app.models.collector_account_models import (
    CollectorOtpRequestResponse,
    CollectorAuthResponse,
    CollectorProfileResponse,
    VehicleProfileUpdateRequest,
    KycSubmissionRequest,
    KycStatusResponse,
    JobClaimGateCheckResponse,
    mask_phone_number,
)


class CollectorAuthService:
    """
    บริการจัดการการลงทะเบียนและเข้าสู่ระบบด้วย Phone OTP ของซาเล้ง (AC-B01-01, P-01, Q-01)
    """

    @staticmethod
    def request_otp(phone: str) -> CollectorOtpRequestResponse:
        """
        ขอรับรหัส OTP 6 หลัก สำหรับเบอร์โทรศัพท์ซาเล้ง (AC-B01-01)
        """
        # ตรวจสอบ Cooldown 60 วินาที
        latest = supabase_store.get_latest_collector_otp(phone)
        if latest:
            created_at = datetime.fromisoformat(latest["created_at"])
            elapsed = (datetime.now(timezone.utc) - created_at).total_seconds()
            if elapsed < 60:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"กรุณารอ {int(60 - elapsed)} วินาทีก่อนขอรหัส OTP ใหม่อีกครั้ง"
                )

        # สร้าง Mock OTP 6 หลัก
        otp_code = "123456"
        otp_entry = supabase_store.create_collector_otp(phone, otp_code, expires_in_seconds=300)

        # บันทึก Security Audit Log (REQ-SEC-001, AC-B01-05)
        phone_masked = mask_phone_number(phone)
        supabase_store.add_audit_log(
            action="COLLECTOR_OTP_REQUESTED",
            entity_id=otp_entry["id"],
            actor_id=phone_masked,
            details={
                "phone_masked": phone_masked,
                "otp_id": otp_entry["id"],
                "expires_in_seconds": 300,
            }
        )

        return CollectorOtpRequestResponse(
            phone_masked=phone_masked,
            expires_in_seconds=300,
            cooldown_seconds=60,
            message="ระบบได้ส่งรหัส OTP ไปยังเบอร์โทรศัพท์ของท่านแล้ว",
            mock_otp=otp_code
        )

    @staticmethod
    def verify_otp(phone: str, otp_code: str) -> CollectorAuthResponse:
        """
        ยืนยันรหัส OTP และสร้างหรือค้นหาโปรไฟล์ซาเล้ง พร้อมออก Session Token (AC-B01-01, P-01)
        """
        latest_otp = supabase_store.get_latest_collector_otp(phone)
        if not latest_otp:
            # ยอมรับ mock 123456 ในการทดสอบ
            if otp_code != "123456":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="ไม่พบรหัส OTP หรือรหัสหมดอายุแล้ว กรุณาขอรหัสใหม่"
                )
        else:
            # ตรวจสอบวันหมดอายุ
            expires_at = datetime.fromisoformat(latest_otp["expires_at"])
            if datetime.now(timezone.utc) > expires_at:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="รหัส OTP หมดอายุแล้ว กรุณาขอรหัสใหม่"
                )
            if latest_otp["otp_code"] != otp_code and otp_code != "123456":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="รหัส OTP ไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง"
                )
            # ทำเครื่องหมายว่าใช้แล้ว
            supabase_store.mark_collector_otp_used(latest_otp["id"])

        # ค้นหาโปรไฟล์ซาเล้งเดิม หรือสร้างใหม่หากใช้งานครั้งแรก
        collector = supabase_store.get_collector_by_phone(phone)
        if not collector:
            collector = supabase_store.create_collector_profile(phone)

        # ออก Session Token
        session = supabase_store.create_collector_session(collector["saleng_id"])

        # บันทึก Security Audit Log (REQ-SEC-001, AC-B01-05)
        phone_masked = collector.get("phone_masked") or mask_phone_number(phone)
        supabase_store.add_audit_log(
            action="COLLECTOR_LOGIN_SUCCESS",
            entity_id=collector["saleng_id"],
            actor_id=collector["saleng_id"],
            details={
                "saleng_id": collector["saleng_id"],
                "phone_masked": phone_masked,
                "verified": collector.get("verified", False),
                "kyc_status": collector.get("kyc_status", "UNVERIFIED"),
            }
        )

        return CollectorAuthResponse(
            saleng_id=collector["saleng_id"],
            display_name=collector.get("display_name", ""),
            phone_masked=phone_masked,
            session_token=session["token"],
            verified=collector.get("verified", False),
            kyc_status=collector.get("kyc_status", "UNVERIFIED"),
            vehicle_type=collector.get("vehicle_type", "TRICYCLE"),
            max_capacity_kg=collector.get("max_capacity_kg", 150.0),
            message="เข้าสู่ระบบสำเร็จ"
        )

    @staticmethod
    def logout(session_token: str) -> dict:
        """
        ออกจากระบบและยกเลิก Session Token (AC-B01-01)
        """
        success = supabase_store.delete_collector_session(session_token)
        return {"message": "ออกจากระบบสำเร็จ" if success else "เซสชันไม่ถูกต้องหรือถูกยกเลิกแล้ว"}


class CollectorVehicleService:
    """
    บริการจัดการโปรไฟล์และประเภทยานพาหนะของซาเล้ง (AC-B01-02, REQ-FN-001, MD-DOM-04, BR-03, Q-04, P-02)
    """

    @staticmethod
    def get_profile(saleng_id: str) -> CollectorProfileResponse:
        """
        ดึงข้อมูลโปรไฟล์ของซาเล้ง (AC-B01-01..04)
        """
        profile = supabase_store.get_saleng_profile(saleng_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ไม่พบข้อมูลซาเล้งรหัส {saleng_id}"
            )
        phone = profile.get("phone", "")
        phone_masked = profile.get("phone_masked") or mask_phone_number(phone)
        return CollectorProfileResponse(
            saleng_id=profile["saleng_id"],
            display_name=profile.get("display_name", ""),
            phone=phone,
            phone_masked=phone_masked,
            avatar_url=profile.get("avatar_url"),
            vehicle_type=profile.get("vehicle_type", "TRICYCLE"),
            license_plate=profile.get("license_plate"),
            max_capacity_kg=float(profile.get("max_capacity_kg", 150.0)),
            verified=profile.get("verified", False),
            kyc_status=profile.get("kyc_status", "UNVERIFIED"),
            rejection_reason=profile.get("rejection_reason"),
            rating=float(profile.get("rating", 5.0)),
            completed_jobs_count=int(profile.get("completed_jobs_count", 0)),
            is_online=profile.get("is_online", False),
            created_at=profile.get("created_at", datetime.now(timezone.utc).isoformat()),
            updated_at=profile.get("updated_at"),
        )

    @staticmethod
    def update_profile(saleng_id: str, display_name: str) -> CollectorProfileResponse:
        """
        อัปเดตชื่อโปรไฟล์ของซาเล้ง (P-01)
        """
        profile = supabase_store.get_saleng_profile(saleng_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ไม่พบข้อมูลซาเล้งรหัส {saleng_id}"
            )
        updated = supabase_store.update_saleng_profile(saleng_id, {"display_name": display_name})
        return CollectorVehicleService.get_profile(saleng_id)

    @staticmethod
    def update_vehicle(saleng_id: str, req: VehicleProfileUpdateRequest) -> CollectorProfileResponse:
        """
        อัปเดตประเภทรถ เลขทะเบียน และความจุน้ำหนักสูงสุด (AC-B01-02, REQ-FN-001, MD-DOM-04, BR-03, Q-04, P-02)
        """
        profile = supabase_store.get_saleng_profile(saleng_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ไม่พบข้อมูลซาเล้งรหัส {saleng_id}"
            )

        if req.max_capacity_kg <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ค่าน้ำหนักบรรทุกสูงสุดต้องมากกว่า 0 กก."
            )

        update_data = {
            "vehicle_type": req.vehicle_type,
            "license_plate": req.license_plate,
            "max_capacity_kg": req.max_capacity_kg,
        }
        supabase_store.update_saleng_profile(saleng_id, update_data)

        # บันทึก Security Audit Log (REQ-SEC-001, AC-B01-05)
        supabase_store.add_audit_log(
            action="COLLECTOR_VEHICLE_UPDATED",
            entity_id=saleng_id,
            actor_id=saleng_id,
            details={
                "saleng_id": saleng_id,
                "vehicle_type": req.vehicle_type,
                "license_plate": req.license_plate,
                "max_capacity_kg": req.max_capacity_kg,
            }
        )

        return CollectorVehicleService.get_profile(saleng_id)


class CollectorKycService:
    """
    บริการจัดการเอกสาร KYC และกฎเหล็ก Unverified Collector Gate (AC-B01-03..05, D-00-01, SC-04, Q-02, Q-03, Q-05, Q-06)
    """

    @staticmethod
    def submit_kyc(saleng_id: str, req: KycSubmissionRequest) -> KycStatusResponse:
        """
        ส่งเอกสารยืนยันตัวตน Thai-ID/DBD-ID (AC-B01-03, SC-04, Q-02, P-03)
        """
        profile = supabase_store.get_saleng_profile(saleng_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ไม่พบข้อมูลซาเล้งรหัส {saleng_id}"
            )

        # บันทึกคำขอ KYC
        sub_data = req.model_dump()
        submission = supabase_store.submit_collector_kyc(saleng_id, sub_data)

        # บันทึก Audit Log (REQ-SEC-001, AC-B01-05)
        masked_id = f"{req.id_card_no[:1]}-XXXX-XXXXX-{req.id_card_no[-2:]}"
        supabase_store.add_audit_log(
            action="COLLECTOR_KYC_SUBMITTED",
            entity_id=submission["id"],
            actor_id=saleng_id,
            details={
                "saleng_id": saleng_id,
                "id_card_masked": masked_id,
                "submission_id": submission["id"],
                "status": "PENDING_REVIEW",
            }
        )

        return KycStatusResponse(
            saleng_id=saleng_id,
            kyc_status="PENDING_REVIEW",
            verified=False,
            id_card_masked=masked_id,
            full_name=req.full_name,
            submitted_at=submission["submitted_at"],
        )

    @staticmethod
    def get_kyc_status(saleng_id: str) -> KycStatusResponse:
        """
        ตรวจสอบสถานะการยืนยันตัวตนปัจจุบัน (AC-B01-03)
        """
        profile = supabase_store.get_saleng_profile(saleng_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ไม่พบข้อมูลซาเล้งรหัส {saleng_id}"
            )

        latest_sub = supabase_store.get_collector_latest_kyc(saleng_id)
        masked_id = None
        full_name = None
        if latest_sub:
            raw_id = latest_sub.get("id_card_no", "")
            if len(raw_id) == 13:
                masked_id = f"{raw_id[:1]}-XXXX-XXXXX-{raw_id[-2:]}"
            full_name = latest_sub.get("full_name")

        return KycStatusResponse(
            saleng_id=saleng_id,
            kyc_status=profile.get("kyc_status", "UNVERIFIED"),
            verified=profile.get("verified", False),
            id_card_masked=masked_id,
            full_name=full_name,
            rejection_reason=profile.get("rejection_reason"),
            submitted_at=latest_sub.get("submitted_at") if latest_sub else None,
            reviewed_at=latest_sub.get("reviewed_at") if latest_sub else None,
        )

    @staticmethod
    def assert_can_claim_job(saleng_id: str) -> JobClaimGateCheckResponse:
        """
        ตรวจสอบสิทธิ์การกดรับงานตามกฎ Unverified Gate D-00-01 (AC-B01-04, P-05, Q-05)
        หาก verified = False ต้องโยน HTTP 403 Forbidden เสมอ
        """
        profile = supabase_store.get_saleng_profile(saleng_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ไม่พบข้อมูลซาเล้งรหัส {saleng_id}"
            )

        kyc_status = profile.get("kyc_status", "UNVERIFIED")
        is_verified = profile.get("verified", False)

        if not is_verified:
            # โยน HTTP 403 Forbidden ตามกฎเหล็ก D-00-01
            reason_map = {
                "UNVERIFIED": "ท่านยังไม่ได้ยื่นเอกสารยืนยันตัวตน (KYC) กรุณาส่งเอกสารก่อนกดรับงาน",
                "PENDING_REVIEW": "เอกสารยืนยันตัวตนของท่านอยู่ระหว่างการตรวจสอบ เจ้าหน้าที่จะอนุมัติภายใน 24 ชม.",
                "REJECTED": f"เอกสารยืนยันตัวตนไม่ผ่านการอนุมัติ: {profile.get('rejection_reason') or 'กรุณาส่งใหม่อีกครั้ง'}",
            }
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=reason_map.get(kyc_status, "ซาเล้งต้องผ่านการยืนยันตัวตน (verified = true) ก่อนกดรับงานตามกฎ D-00-01")
            )

        return JobClaimGateCheckResponse(
            saleng_id=saleng_id,
            can_claim_job=True,
            verified=True,
            kyc_status="VERIFIED",
            reason="ผ่านการยืนยันตัวตนเรียบร้อยแล้ว สามารถกดรับงานได้",
            required_action=None,
        )

    @staticmethod
    def mock_approval(saleng_id: str) -> KycStatusResponse:
        """
        จำลองผลการอนุมัติ KYC สำหรับ Dev / Automated Tests (Q-06, P-06)
        """
        profile = supabase_store.get_saleng_profile(saleng_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ไม่พบข้อมูลซาเล้งรหัส {saleng_id}"
            )

        updated = supabase_store.update_collector_kyc_status(
            saleng_id=saleng_id,
            status="VERIFIED",
            rejection_reason=None,
            reviewed_by="MOCK_ADMIN"
        )

        # บันทึก Security Audit Log (REQ-SEC-001, AC-B01-05)
        supabase_store.add_audit_log(
            action="COLLECTOR_KYC_APPROVED",
            entity_id=saleng_id,
            actor_id="MOCK_ADMIN",
            details={
                "saleng_id": saleng_id,
                "verified": True,
                "kyc_status": "VERIFIED",
                "reviewed_by": "MOCK_ADMIN",
            }
        )

        return CollectorKycService.get_kyc_status(saleng_id)

    @staticmethod
    def mock_rejection(saleng_id: str, reason: str = "ภาพถ่ายบัตรประชาชนไม่ชัดเจน") -> KycStatusResponse:
        """
        จำลองผลการปฏิเสธ KYC พร้อมระบุเหตุผล สำหรับ Dev / Automated Tests (Q-06, P-06)
        """
        profile = supabase_store.get_saleng_profile(saleng_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ไม่พบข้อมูลซาเล้งรหัส {saleng_id}"
            )

        updated = supabase_store.update_collector_kyc_status(
            saleng_id=saleng_id,
            status="REJECTED",
            rejection_reason=reason,
            reviewed_by="MOCK_ADMIN"
        )

        # บันทึก Security Audit Log (REQ-SEC-001, AC-B01-05)
        supabase_store.add_audit_log(
            action="COLLECTOR_KYC_REJECTED",
            entity_id=saleng_id,
            actor_id="MOCK_ADMIN",
            details={
                "saleng_id": saleng_id,
                "verified": False,
                "kyc_status": "REJECTED",
                "rejection_reason": reason,
                "reviewed_by": "MOCK_ADMIN",
            }
        )

        return CollectorKycService.get_kyc_status(saleng_id)
