"""
Service Layer สำหรับระบบตรวจสอบและอนุมัติผู้ใช้งานฝั่งผู้ดูแลระบบ (Admin Feature 01)
รองรับ UC-11, REQ-QA-001, REQ-SEC-001, REQ-SEC-002, CC-03, CC-06, D-00-01, D-A01-01..06
"""

from typing import Optional, List
from datetime import datetime, timezone
from fastapi import HTTPException, status
from backend.app.core.supabase import supabase_store
from backend.app.models.user_verification_penalty_models import (
    mask_thai_id_card,
    KYCSubmissionItem,
    KYCReviewRequest,
    KYCReviewResponse,
    UserAccountItem,
    UserPenaltyRequest,
    UserPenaltyResponse,
    UserReactivateRequest,
    UserReactivateResponse,
)


class UserVerificationPenaltyService:
    """
    บริการตรรกะธุรกิจสำหรับผู้ดูแลระบบ (Admin Service)
    """

    @staticmethod
    def list_kyc_submissions(status_filter: Optional[str] = "PENDING_REVIEW") -> List[KYCSubmissionItem]:
        """
        ดึงรายการคำขอ KYC พร้อม Masking หมายเลขบัตรประชาชนตาม PDPA (AC-A01-01, REQ-SEC-002, CC-06)
        """
        raw_submissions = supabase_store.get_collector_kyc_submissions(status_filter)
        result: List[KYCSubmissionItem] = []

        for sub in raw_submissions:
            clean_id_card = sub.get("id_card_no", "1100200112233")
            masked_id = mask_thai_id_card(clean_id_card)
            result.append(
                KYCSubmissionItem(
                    id=sub["id"],
                    saleng_id=sub["saleng_id"],
                    id_card_no_masked=masked_id,
                    full_name=sub.get("full_name", f"ซาเล้ง {sub['saleng_id']}"),
                    id_card_photo_url=sub.get("id_card_photo_url", ""),
                    selfie_photo_url=sub.get("selfie_photo_url", ""),
                    vehicle_photo_url=sub.get("vehicle_photo_url"),
                    status=sub.get("status", "PENDING_REVIEW"),
                    rejection_reason=sub.get("rejection_reason"),
                    submitted_at=sub.get("submitted_at", datetime.now(timezone.utc).isoformat()),
                    reviewed_at=sub.get("reviewed_at"),
                    reviewed_by=sub.get("reviewed_by"),
                )
            )

        return result

    @staticmethod
    def review_kyc_submission(admin_id: str, req: KYCReviewRequest) -> KYCReviewResponse:
        """
        พิจารณาอนุมัติหรือปฏิเสธคำขอ KYC ซาเล้ง พร้อมบันทึก Audit Log (AC-A01-02, D-00-01)
        """
        sub = supabase_store.get_collector_kyc_submission(req.submission_id)
        if not sub:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ไม่พบคำขอ KYC รหัส {req.submission_id}",
            )

        try:
            reviewed_sub, reviewed_profile = supabase_store.review_collector_kyc(
                submission_id=req.submission_id,
                action=req.action,
                rejection_reason=req.rejection_reason,
                reviewed_by=admin_id,
            )
        except (ValueError, KeyError) as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )

        # บันทึก Audit Log แบบ Append-only ตาม REQ-SEC-001
        audit_action = "ADMIN_APPROVED_KYC" if req.action == "APPROVE" else "ADMIN_REJECTED_KYC"
        supabase_store.record_audit_log(
            action=audit_action,
            actor_id=admin_id,
            actor_role="ADMIN",
            entity_id=sub["saleng_id"],
            details={
                "submission_id": req.submission_id,
                "saleng_id": sub["saleng_id"],
                "action": req.action,
                "rejection_reason": req.rejection_reason,
                "verified": reviewed_profile.get("verified", False),
            },
        )

        msg = (
            f"อนุมัติคำขอยืนยันตัวตนของซาเล้ง {sub['saleng_id']} สำเร็จ (เปิดสิทธิ์ verified = true)"
            if req.action == "APPROVE"
            else f"ปฏิเสธคำขอยืนยันตัวตนของซาเล้ง {sub['saleng_id']} เรียบร้อยแล้ว"
        )

        return KYCReviewResponse(
            success=True,
            submission_id=reviewed_sub["id"],
            saleng_id=sub["saleng_id"],
            action=req.action,
            kyc_status=reviewed_sub["status"],
            verified=reviewed_profile.get("verified", False),
            rejection_reason=reviewed_sub.get("rejection_reason"),
            reviewed_at=reviewed_sub.get("reviewed_at", datetime.now(timezone.utc).isoformat()),
            reviewed_by=admin_id,
            message=msg,
        )

    @staticmethod
    def list_users(
        role_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
        search_query: Optional[str] = None,
    ) -> List[UserAccountItem]:
        """
        ดึงรายชื่อผู้ใช้งานทั้งหมด พร้อมข้อมูลบทลงโทษ (AC-A01-03)
        """
        raw_users = supabase_store.get_admin_users(role_filter, status_filter, search_query)
        result: List[UserAccountItem] = []
        for u in raw_users:
            result.append(UserAccountItem(**u))
        return result

    @staticmethod
    def penalize_user(admin_id: str, req: UserPenaltyRequest) -> UserPenaltyResponse:
        """
        สั่งระงับสิทธิ์บัญชีผู้ใช้ (ชั่วคราวหรือถาวร) พร้อมบันทึก Audit Log (AC-A01-03, D-A01-03, D-A01-04)
        """
        try:
            penalized = supabase_store.penalize_user_account(
                user_id=req.user_id,
                role=req.role,
                action=req.action,
                penalty_reason=req.penalty_reason,
                penalized_by=admin_id,
            )
        except KeyError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )

        # บันทึก Audit Log (REQ-SEC-001)
        supabase_store.record_audit_log(
            action="ADMIN_PENALIZED_USER",
            actor_id=admin_id,
            actor_role="ADMIN",
            entity_id=req.user_id,
            details={
                "user_id": req.user_id,
                "role": req.role,
                "action": req.action,
                "penalty_reason": req.penalty_reason,
                "duration_days": req.duration_days,
                "new_status": penalized.get("account_status"),
            },
        )

        action_th = "ระงับสิทธิ์ชั่วคราว" if req.action == "SUSPEND_TEMPORARY" else "ระงับสิทธิ์ถาวร (แบน)"
        msg = f"สั่ง{action_th} บัญชี {req.user_id} ({req.role}) สำเร็จ"

        return UserPenaltyResponse(
            success=True,
            user_id=req.user_id,
            role=req.role,
            account_status=penalized.get("account_status", "SUSPENDED_TEMPORARY"),
            penalty_reason=req.penalty_reason,
            penalized_at=penalized.get("penalized_at", datetime.now(timezone.utc).isoformat()),
            penalized_by=admin_id,
            message=msg,
        )

    @staticmethod
    def reactivate_user(admin_id: str, req: UserReactivateRequest) -> UserReactivateResponse:
        """
        ปลดระงับสิทธิ์ผู้ใช้ให้กลับมาเป็น ACTIVE (AC-A01-04)
        """
        try:
            reactivated = supabase_store.reactivate_user_account(
                user_id=req.user_id,
                role=req.role,
                reason=req.reason or "ADMIN_REINSTATED",
            )
        except KeyError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )

        # บันทึก Audit Log (REQ-SEC-001)
        supabase_store.record_audit_log(
            action="ADMIN_UNSUSPENDED_USER",
            actor_id=admin_id,
            actor_role="ADMIN",
            entity_id=req.user_id,
            details={
                "user_id": req.user_id,
                "role": req.role,
                "reason": req.reason,
                "account_status": "ACTIVE",
            },
        )

        return UserReactivateResponse(
            success=True,
            user_id=req.user_id,
            role=req.role,
            account_status="ACTIVE",
            message=f"ปลดระงับสิทธิ์บัญชี {req.user_id} คืนสถานะ ACTIVE สำเร็จ",
        )


admin_user_service = UserVerificationPenaltyService()

