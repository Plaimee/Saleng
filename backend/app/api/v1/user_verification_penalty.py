"""
FastAPI Router สำหรับระบบตรวจสอบและอนุมัติผู้ใช้งานฝั่งผู้ดูแลระบบ (Admin Feature 01)
รองรับ UC-11, AC-A01-01..05, CC-03, REQ-SEC-001, REQ-SEC-002, D-00-01, D-A01-01..06
"""

from typing import Optional, List
from fastapi import APIRouter, Header, HTTPException, status, Query
from backend.app.models.user_verification_penalty_models import (
    KYCSubmissionItem,
    KYCReviewRequest,
    KYCReviewResponse,
    UserAccountItem,
    UserPenaltyRequest,
    UserPenaltyResponse,
    UserReactivateRequest,
    UserReactivateResponse,
)
from backend.app.services.user_verification_penalty_service import admin_user_service

router = APIRouter(prefix="", tags=["Admin - User Verification & Penalty"])


def verify_admin_role(
    x_admin_role: Optional[str] = Header(None, alias="X-Admin-Role"),
    x_admin_id: Optional[str] = Header("admin-01", alias="X-Admin-Id"),
) -> str:
    """
    ตรวจสอบสิทธิ์ผู้ดูแลระบบตามข้อกำหนด CC-03 และ D-A01-05
    หากไม่มี Header หรือไม่ใช่ ADMIN จะส่งกลับ 403 Forbidden
    """
    if not x_admin_role or x_admin_role.upper() != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="สิทธิ์ไม่ถูกต้อง: เฉพาะผู้ดูแลระบบ (ADMIN) เท่านั้นที่สามารถเข้าถึงส่วนนี้ได้",
        )
    return x_admin_id or "admin-01"


@router.get(
    "/kyc/submissions",
    response_model=List[KYCSubmissionItem],
    summary="เรียกดูคิวคำขอยืนยันตัวตน KYC ของซาเล้ง (AC-A01-01, UC-11)",
)
def get_kyc_submissions(
    status: Optional[str] = Query("PENDING_REVIEW", description="ตัวกรองสถานะคำขอ (PENDING_REVIEW, ALL)"),
    admin_id: str = Header("admin-01", alias="X-Admin-Id"),
    x_admin_role: Optional[str] = Header(None, alias="X-Admin-Role"),
):
    verify_admin_role(x_admin_role, admin_id)
    return admin_user_service.list_kyc_submissions(status)


@router.post(
    "/kyc/review",
    response_model=KYCReviewResponse,
    summary="อนุมัติหรือปฏิเสธคำขอยืนยันตัวตน KYC ของซาเล้ง (AC-A01-02, UC-11)",
)
def review_kyc_submission(
    req: KYCReviewRequest,
    admin_id: str = Header("admin-01", alias="X-Admin-Id"),
    x_admin_role: Optional[str] = Header(None, alias="X-Admin-Role"),
):
    a_id = verify_admin_role(x_admin_role, admin_id)
    return admin_user_service.review_kyc_submission(a_id, req)


@router.get(
    "/users",
    response_model=List[UserAccountItem],
    summary="ดึงรายชื่อผู้ใช้งานทั้งหมด พร้อมสถานะบัญชีและบทลงโทษ (AC-A01-03, UC-11)",
)
def get_users(
    role: Optional[str] = Query(None, description="ตัวกรองบทบาท (COLLECTOR, SELLER, ALL)"),
    status: Optional[str] = Query(None, description="ตัวกรองสถานะ (ACTIVE, SUSPENDED_TEMPORARY, BANNED, ALL)"),
    search: Optional[str] = Query(None, description="คำค้นหารหัสหรือชื่อ"),
    admin_id: str = Header("admin-01", alias="X-Admin-Id"),
    x_admin_role: Optional[str] = Header(None, alias="X-Admin-Role"),
):
    verify_admin_role(x_admin_role, admin_id)
    return admin_user_service.list_users(role, status, search)


@router.post(
    "/users/penalty",
    response_model=UserPenaltyResponse,
    summary="สั่งระงับสิทธิ์บัญชีผู้ใช้ชั่วคราวหรือถาวร (AC-A01-03, UC-11)",
)
def penalize_user(
    req: UserPenaltyRequest,
    admin_id: str = Header("admin-01", alias="X-Admin-Id"),
    x_admin_role: Optional[str] = Header(None, alias="X-Admin-Role"),
):
    a_id = verify_admin_role(x_admin_role, admin_id)
    return admin_user_service.penalize_user(a_id, req)


@router.post(
    "/users/reactivate",
    response_model=UserReactivateResponse,
    summary="ปลดระงับสิทธิ์บัญชีผู้ใช้ คืนสถานะ ACTIVE (AC-A01-04, UC-11)",
)
def reactivate_user(
    req: UserReactivateRequest,
    admin_id: str = Header("admin-01", alias="X-Admin-Id"),
    x_admin_role: Optional[str] = Header(None, alias="X-Admin-Role"),
):
    a_id = verify_admin_role(x_admin_role, admin_id)
    return admin_user_service.reactivate_user(a_id, req)

