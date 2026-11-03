"""
Pydantic Data Models สำหรับระบบบัญชีและการยืนยันตัวตนซาเล้ง (Collector Account & KYC)
รองรับ UC-01, MD-DOM-04, REQ-FN-001, REQ-SEC-001, REQ-SEC-002, REQ-QA-001, CC-01..06, D-00-01, P-01..P-06
"""

from datetime import datetime, timezone
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator
import re


def mask_phone_number(phone: str) -> str:
    """
    แปลงเบอร์โทรศัพท์เป็น 08X-XXX-XXXX ตาม REQ-SEC-002 และ EV-09
    """
    cleaned = re.sub(r"\D", "", phone or "")
    if len(cleaned) == 10:
        return f"{cleaned[:2]}X-XXX-{cleaned[6:]}"
    elif len(cleaned) == 9:
        return f"{cleaned[:2]}X-XXX-{cleaned[5:]}"
    return "08X-XXX-XXXX"


def validate_thai_id(id_card_no: str) -> bool:
    """
    ตรวจสอบความถูกต้องของเลขประจำตัวประชาชนไทย 13 หลักตามมาตรฐาน Checksum
    """
    cleaned = re.sub(r"\D", "", id_card_no or "")
    if len(cleaned) != 13:
        return False
    # ตรวจสอบ check digit
    total = sum(int(cleaned[i]) * (13 - i) for i in range(12))
    check_digit = (11 - (total % 11)) % 10
    return int(cleaned[12]) == check_digit


class CollectorOtpRequest(BaseModel):
    """คำขอรหัส OTP สำหรับเข้าสู่ระบบซาเล้ง (AC-B01-01, P-01)"""
    phone: str = Field(..., description="เบอร์โทรศัพท์มือถือ 10 หลัก (เช่น 0812345678)")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        cleaned = re.sub(r"\D", "", v)
        if len(cleaned) != 10 or not cleaned.startswith("0"):
            raise ValueError("เบอร์โทรศัพท์ต้องเป็นตัวเลข 10 หลักและขึ้นต้นด้วย 0")
        return cleaned


class CollectorOtpRequestResponse(BaseModel):
    """ผลการขอรหัส OTP สำหรับซาเล้ง (AC-B01-01)"""
    phone_masked: str
    expires_in_seconds: int = 300
    cooldown_seconds: int = 60
    message: str = "ระบบได้ส่งรหัส OTP ไปยังเบอร์โทรศัพท์ของท่านแล้ว"
    mock_otp: Optional[str] = "123456"


class CollectorOtpVerifyRequest(BaseModel):
    """คำขอยืนยันรหัส OTP ซาเล้ง (AC-B01-01, P-01)"""
    phone: str = Field(..., description="เบอร์โทรศัพท์มือถือ 10 หลัก")
    otp_code: str = Field(..., min_length=6, max_length=6, description="รหัส OTP 6 หลัก")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        cleaned = re.sub(r"\D", "", v)
        if len(cleaned) != 10 or not cleaned.startswith("0"):
            raise ValueError("เบอร์โทรศัพท์ต้องเป็นตัวเลข 10 หลักและขึ้นต้นด้วย 0")
        return cleaned

    @field_validator("otp_code")
    @classmethod
    def validate_otp_code(cls, v: str) -> str:
        cleaned = re.sub(r"\D", "", v)
        if len(cleaned) != 6:
            raise ValueError("รหัส OTP ต้องเป็นตัวเลข 6 หลัก")
        return cleaned


class CollectorAuthResponse(BaseModel):
    """ข้อมูลผลลัพธ์หลังยืนยัน OTP ซาเล้งสำเร็จ (AC-B01-01, REQ-SEC-002)"""
    saleng_id: str
    display_name: str
    phone_masked: str
    session_token: str
    verified: bool = False
    kyc_status: Literal["UNVERIFIED", "PENDING_REVIEW", "VERIFIED", "REJECTED"] = "UNVERIFIED"
    vehicle_type: str = "TRICYCLE"
    max_capacity_kg: float = 150.0
    message: Optional[str] = "เข้าสู่ระบบสำเร็จ"


class CollectorProfileUpdateRequest(BaseModel):
    """คำขออัปเดตชื่อโปรไฟล์ซาเล้ง (P-01)"""
    display_name: str = Field(..., min_length=2, max_length=100, description="ชื่อ-นามสกุล หรือชื่อเรียกซาเล้ง")


class VehicleProfileUpdateRequest(BaseModel):
    """คำขอตั้งค่าประเภทยานพาหนะและความจุ (AC-B01-02, REQ-FN-001, MD-DOM-04, BR-03, Q-04, P-02)"""
    vehicle_type: Literal["TRICYCLE", "SIDE_CAR_MOTORCYCLE", "PICKUP_TRUCK"] = Field(
        ..., description="ประเภทยานพาหนะ (TRICYCLE, SIDE_CAR_MOTORCYCLE, PICKUP_TRUCK)"
    )
    license_plate: Optional[str] = Field(None, max_length=50, description="เลขทะเบียนรถ (ถ้ามี)")
    max_capacity_kg: float = Field(..., gt=0.0, le=5000.0, description="น้ำหนักบรรทุกสูงสุด (กก.) ต้องมากกว่า 0")


class KycSubmissionRequest(BaseModel):
    """คำขอส่งเอกสารยืนยันตัวตน Thai-ID/DBD-ID (AC-B01-03, SC-04, Q-02, P-03)"""
    id_card_no: str = Field(..., description="เลขประจำตัวประชาชน 13 หลัก")
    full_name: str = Field(..., min_length=2, max_length=150, description="ชื่อ-นามสกุลจริงตามบัตรประชาชน")
    id_card_photo_url: str = Field(..., description="URL หรือ path รูปถ่ายบัตรประชาชนด้านหน้า")
    selfie_photo_url: str = Field(..., description="URL หรือ path รูปถ่ายหน้าตรงคู่กับบัตรประชาชน")
    vehicle_photo_url: Optional[str] = Field(None, description="URL หรือ path รูปถ่ายยานพาหนะพร้อมป้ายทะเบียน")

    @field_validator("id_card_no")
    @classmethod
    def validate_id_card(cls, v: str) -> str:
        cleaned = re.sub(r"\D", "", v)
        if len(cleaned) != 13:
            raise ValueError("เลขบัตรประชาชนต้องเป็นตัวเลข 13 หลัก")
        # ตรวจสอบ checksum หากเป็นตัวเลข 13 หลัก
        if not validate_thai_id(cleaned):
            raise ValueError("เลขบัตรประชาชนไม่ถูกต้องตามรูปแบบ Checksum ของกรมการปกครอง")
        return cleaned


class KycStatusResponse(BaseModel):
    """สถานะการยืนยันตัวตน KYC (AC-B01-03, Q-03, P-03)"""
    saleng_id: str
    kyc_status: Literal["UNVERIFIED", "PENDING_REVIEW", "VERIFIED", "REJECTED"]
    verified: bool
    id_card_masked: Optional[str] = None
    full_name: Optional[str] = None
    rejection_reason: Optional[str] = None
    submitted_at: Optional[str] = None
    reviewed_at: Optional[str] = None


class JobClaimGateCheckResponse(BaseModel):
    """ผลการตรวจสอบสิทธิ์การกดรับงานตามกฎ Unverified Gate D-00-01 (AC-B01-04, P-05, Q-05)"""
    saleng_id: str
    can_claim_job: bool
    verified: bool
    kyc_status: str
    reason: Optional[str] = None
    required_action: Optional[str] = None


class MockKycReviewRequest(BaseModel):
    """คำขอจำลองการพิจารณา KYC สำหรับทดสอบ (Q-06, P-06)"""
    rejection_reason: Optional[str] = Field(None, description="เหตุผลที่ปฏิเสธ (กรณีไม่อนุมัติ)")


class CollectorProfileResponse(BaseModel):
    """ข้อมูลโปรไฟล์ซาเล้งฉบับเต็มสำหรับแสดงผลบนแผงควบคุม (AC-B01-01..04)"""
    saleng_id: str
    display_name: str
    phone: str
    phone_masked: str
    avatar_url: Optional[str] = None
    vehicle_type: str = "TRICYCLE"
    license_plate: Optional[str] = None
    max_capacity_kg: float = 150.0
    verified: bool = False
    kyc_status: Literal["UNVERIFIED", "PENDING_REVIEW", "VERIFIED", "REJECTED"] = "UNVERIFIED"
    rejection_reason: Optional[str] = None
    rating: float = 5.0
    completed_jobs_count: int = 0
    is_online: bool = False
    created_at: str
    updated_at: Optional[str] = None

