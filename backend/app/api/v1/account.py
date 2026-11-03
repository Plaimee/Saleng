"""
FastAPI Router สำหรับระบบบัญชีและการเข้าใช้งานของผู้ขาย (Seller Account & Access API)
รองรับ UC-01, UC-02, REQ-SEC-001, REQ-SEC-002, REQ-QA-001, REQ-UX-002, CC-01, CC-04, P-01..P-06
"""

from fastapi import APIRouter, Header, HTTPException, status
from typing import Optional

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
)
from backend.app.services.account_service import (
    SellerAuthService,
    PickupLocationService,
    verify_seller_session,
)

account_router = APIRouter(prefix="/sellers", tags=["Seller Account & Access"])


# -------------------------------------------------------------
# Authentication & Profile Endpoints (UC-01, AC-S01-01, AC-S01-03)
# -------------------------------------------------------------
@account_router.post(
    "/auth/request-otp",
    response_model=OtpRequestResponse,
    summary="ขอรหัส OTP สำหรับเข้าสู่ระบบ (AC-S01-01)",
)
def request_otp(req: OtpRequest):
    return SellerAuthService.request_otp(req)


@account_router.post(
    "/auth/verify-otp",
    response_model=AuthSessionResponse,
    summary="ยืนยันรหัส OTP และออกเซสชันโทเคน (AC-S01-01, AC-S01-04)",
)
def verify_otp(req: OtpVerifyRequest):
    return SellerAuthService.verify_otp(req)


@account_router.post(
    "/auth/logout",
    summary="ออกจากระบบและยกเลิกเซสชัน (AC-S01-05)",
)
def logout(authorization: Optional[str] = Header(None)):
    token = authorization.replace("Bearer ", "") if authorization else ""
    return SellerAuthService.logout(token)


@account_router.get(
    "/{seller_id}/profile",
    response_model=SellerProfileResponse,
    summary="ดึงข้อมูลโปรไฟล์ผู้ขายพร้อม PDPA Masked Phone (AC-S01-03)",
)
def get_profile(seller_id: str):
    return SellerAuthService.get_profile(seller_id)


@account_router.put(
    "/{seller_id}/profile",
    response_model=SellerProfileResponse,
    summary="แก้ไขชื่อที่แสดงของผู้ขาย (AC-S01-01)",
)
def update_profile(seller_id: str, req: SellerProfileUpdateRequest):
    return SellerAuthService.update_profile(seller_id, req)


# -------------------------------------------------------------
# Pickup Location Endpoints (UC-01, UC-02, AC-S01-02, P-02)
# -------------------------------------------------------------
@account_router.get(
    "/{seller_id}/locations",
    response_model=PickupLocationListResponse,
    summary="ดึงรายการที่อยู่นัดหมายทั้งหมดของผู้ขาย (AC-S01-02)",
)
def list_locations(seller_id: str):
    return PickupLocationService.list_locations(seller_id)


@account_router.post(
    "/{seller_id}/locations",
    response_model=PickupLocationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="เพิ่มที่อยู่นัดหมายใหม่ พร้อมพิกัด GPS (AC-S01-02)",
)
def create_location(seller_id: str, req: PickupLocationCreateRequest):
    return PickupLocationService.create_location(seller_id, req)


@account_router.get(
    "/{seller_id}/locations/default",
    response_model=Optional[PickupLocationResponse],
    summary="ดึงที่อยู่นัดหมายเริ่มต้นสำหรับเตรียมส่งต่อให้ UC-02 (P-06)",
)
def get_default_location(seller_id: str):
    return PickupLocationService.get_default_location(seller_id)


@account_router.put(
    "/{seller_id}/locations/{location_id}",
    response_model=PickupLocationResponse,
    summary="แก้ไขที่อยู่นัดหมาย (AC-S01-02)",
)
def update_location(
    seller_id: str, location_id: str, req: PickupLocationUpdateRequest
):
    return PickupLocationService.update_location(seller_id, location_id, req)


@account_router.delete(
    "/{seller_id}/locations/{location_id}",
    summary="ลบที่อยู่นัดหมาย (AC-S01-02)",
)
def delete_location(seller_id: str, location_id: str):
    return PickupLocationService.delete_location(seller_id, location_id)


@account_router.patch(
    "/{seller_id}/locations/{location_id}/default",
    response_model=PickupLocationResponse,
    summary="ตั้งค่าที่อยู่นี้เป็นที่อยู่เริ่มต้น (AC-S01-02, Q-03)",
)
def set_default_location(seller_id: str, location_id: str):
    return PickupLocationService.set_default_location(seller_id, location_id)

