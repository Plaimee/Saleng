"""
API Endpoints สำหรับระบบบัญชีและการยืนยันตัวตนซาเล้ง (Buyer 01: Account & KYC)
รองรับ UC-01, MD-DOM-04, REQ-FN-001, REQ-SEC-001, REQ-SEC-002, REQ-QA-001, CC-01..06, D-00-01, P-01..P-06
"""

from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException, status
from backend.app.models.collector_account_models import (
    CollectorOtpRequest,
    CollectorOtpRequestResponse,
    CollectorOtpVerifyRequest,
    CollectorAuthResponse,
    CollectorProfileResponse,
    CollectorProfileUpdateRequest,
    VehicleProfileUpdateRequest,
    KycSubmissionRequest,
    KycStatusResponse,
    JobClaimGateCheckResponse,
    MockKycReviewRequest,
)
from backend.app.services.collector_account_service import (
    CollectorAuthService,
    CollectorVehicleService,
    CollectorKycService,
)

router = APIRouter(prefix="/collectors", tags=["Collector Account & KYC"])


# -------------------------------------------------------------
# 1. การลงทะเบียนและการเข้าสู่ระบบ (AC-B01-01, P-01, Q-01)
# -------------------------------------------------------------
@router.post(
    "/auth/request-otp",
    response_model=CollectorOtpRequestResponse,
    summary="ขอรหัส OTP สำหรับซาเล้งเข้าสู่ระบบ (AC-B01-01)"
)
def request_collector_otp(req: CollectorOtpRequest):
    """
    รับเบอร์โทรศัพท์มือถือ 10 หลัก ออกรหัส OTP 6 หลัก พร้อม Cooldown 60s
    """
    return CollectorAuthService.request_otp(req.phone)


@router.post(
    "/auth/verify-otp",
    response_model=CollectorAuthResponse,
    summary="ยืนยันรหัส OTP และรับ Session Token (AC-B01-01)"
)
def verify_collector_otp(req: CollectorOtpVerifyRequest):
    """
    ตรวจสอบรหัส OTP 6 หลัก และออก Session Token สำหรับซาเล้ง
    """
    return CollectorAuthService.verify_otp(req.phone, req.otp_code)


@router.post(
    "/auth/logout",
    summary="ออกจากระบบและยกเลิกเซสชัน (AC-B01-01)"
)
def logout_collector(authorization: Optional[str] = Header(None)):
    """
    ออกจากระบบและยกเลิกโทเคน
    """
    token = authorization.replace("Bearer ", "") if authorization else ""
    return CollectorAuthService.logout(token)


# -------------------------------------------------------------
# 2. ข้อมูลโปรไฟล์และยานพาหนะ (AC-B01-02, P-02, Q-04)
# -------------------------------------------------------------
@router.get(
    "/{saleng_id}/profile",
    response_model=CollectorProfileResponse,
    summary="ดึงข้อมูลโปรไฟล์ของซาเล้ง (AC-B01-01..04)"
)
def get_collector_profile(saleng_id: str):
    """
    ดึงข้อมูลโปรไฟล์ ชื่อ เบอร์โทรศัพท์ และสถานะรถ
    """
    return CollectorVehicleService.get_profile(saleng_id)


@router.put(
    "/{saleng_id}/profile",
    response_model=CollectorProfileResponse,
    summary="อัปเดตชื่อโปรไฟล์ซาเล้ง (P-01)"
)
def update_collector_profile(saleng_id: str, req: CollectorProfileUpdateRequest):
    """
    แก้ไขชื่อที่แสดงของซาเล้ง
    """
    return CollectorVehicleService.update_profile(saleng_id, req.display_name)


@router.put(
    "/{saleng_id}/vehicle",
    response_model=CollectorProfileResponse,
    summary="ตั้งค่าประเภทยานพาหนะและความจุ (AC-B01-02)"
)
def update_collector_vehicle(saleng_id: str, req: VehicleProfileUpdateRequest):
    """
    เลือกประเภทยานพาหนะ 3 แบบ และกำหนดความจุสูงสุด (กก.) ตามกฎ BR-03
    """
    return CollectorVehicleService.update_vehicle(saleng_id, req)


# -------------------------------------------------------------
# 3. การยืนยันตัวตน KYC (AC-B01-03, P-03, Q-02, Q-03)
# -------------------------------------------------------------
@router.post(
    "/{saleng_id}/kyc/submit",
    response_model=KycStatusResponse,
    status_code=status.HTTP_201_CREATED,
    summary="ส่งเอกสารยืนยันตัวตน Thai-ID/DBD-ID (AC-B01-03)"
)
def submit_collector_kyc(saleng_id: str, req: KycSubmissionRequest):
    """
    ส่งเลขบัตร ปชช. 13 หลัก พร้อมภาพถ่าย 4 จุด เข้าสู่สถานะ PENDING_REVIEW
    """
    return CollectorKycService.submit_kyc(saleng_id, req)


@router.get(
    "/{saleng_id}/kyc/status",
    response_model=KycStatusResponse,
    summary="ตรวจสอบสถานะการยืนยันตัวตน KYC (AC-B01-03)"
)
def get_collector_kyc_status(saleng_id: str):
    """
    ตรวจสอบสถานะ KYC: UNVERIFIED, PENDING_REVIEW, VERIFIED, REJECTED
    """
    return CollectorKycService.get_kyc_status(saleng_id)


# -------------------------------------------------------------
# 4. Unverified Collector Job Claim Gate (AC-B01-04, D-00-01, P-05)
# -------------------------------------------------------------
@router.get(
    "/{saleng_id}/job-claim-gate",
    response_model=JobClaimGateCheckResponse,
    summary="ตรวจสอบสิทธิ์การกดรับงานตามกฎ Unverified Gate D-00-01 (AC-B01-04)"
)
def check_job_claim_gate(saleng_id: str):
    """
    ตรวจสอบว่าซาเล้งผ่าน KYC หรือไม่ หากยังไม่ผ่านจะโยน 403 Forbidden เสมอ
    """
    return CollectorKycService.assert_can_claim_job(saleng_id)


# -------------------------------------------------------------
# 5. Mock Endpoints สำหรับทดสอบ (Q-06, P-06)
# -------------------------------------------------------------
@router.post(
    "/{saleng_id}/mock-kyc-approval",
    response_model=KycStatusResponse,
    summary="จำลองการอนุมัติ KYC สำหรับทดสอบ (Q-06, P-06)"
)
def mock_approve_kyc(saleng_id: str):
    """
    จำลองการอนุมัติ KYC เป็น VERIFIED
    """
    return CollectorKycService.mock_approval(saleng_id)


@router.post(
    "/{saleng_id}/mock-kyc-rejection",
    response_model=KycStatusResponse,
    summary="จำลองการปฏิเสธ KYC สำหรับทดสอบ (Q-06, P-06)"
)
def mock_reject_kyc(saleng_id: str, req: Optional[MockKycReviewRequest] = None):
    """
    จำลองการปฏิเสธ KYC เป็น REJECTED พร้อมเหตุผล
    """
    reason = req.rejection_reason if req and req.rejection_reason else "ภาพถ่ายบัตรประชาชนไม่ชัดเจน"
    return CollectorKycService.mock_rejection(saleng_id, reason)

