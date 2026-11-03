"""
Pydantic Data Models สำหรับระบบบัญชีและการเข้าใช้งานของผู้ขาย (Seller Account & Access)
รองรับ UC-01, UC-02, MD-DOM-04, REQ-SEC-002, REQ-UX-002, REQ-QA-001, CC-04, P-01..P-04
"""

from datetime import datetime, timezone
from typing import List, Optional
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


class OtpRequest(BaseModel):
    """คำขอรหัส OTP เข้าสู่ระบบ (AC-S01-01, P-01)"""
    phone: str = Field(..., description="เบอร์โทรศัพท์มือถือ 10 หลัก (เช่น 0812345678)")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        cleaned = re.sub(r"\D", "", v)
        if len(cleaned) != 10 or not cleaned.startswith("0"):
            raise ValueError("เบอร์โทรศัพท์ต้องเป็นตัวเลข 10 หลักและขึ้นต้นด้วย 0")
        return cleaned


class OtpRequestResponse(BaseModel):
    """ผลการขอรหัส OTP (AC-S01-01)"""
    phone_masked: str
    expires_in_seconds: int = 300
    cooldown_seconds: int = 60
    message: str = "ระบบได้ส่งรหัส OTP ไปยังเบอร์โทรศัพท์ของท่านแล้ว"
    # ในโหมดทดสอบแนบ OTP มาด้วยเพื่ออำนวยความสะดวกในการเทสต์
    mock_otp: Optional[str] = None


class OtpVerifyRequest(BaseModel):
    """คำขอยืนยันรหัส OTP (AC-S01-01, P-01)"""
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
    def validate_otp(cls, v: str) -> str:
        if not v.isdigit() or len(v) != 6:
            raise ValueError("รหัส OTP ต้องเป็นตัวเลข 6 หลัก")
        return v


class AuthSessionResponse(BaseModel):
    """ผลการยืนยันตัวตนสำเร็จและออกเซสชันโทเคน (AC-S01-01, AC-S01-04, P-01)"""
    session_token: str
    seller_id: str
    phone_masked: str
    display_name: str
    expires_at: str
    is_new_user: bool = False
    message: str = "เข้าสู่ระบบสำเร็จ"


class SellerProfileResponse(BaseModel):
    """ข้อมูลโปรไฟล์ผู้ขาย (AC-S01-03, REQ-SEC-002)"""
    seller_id: str
    phone_masked: str
    display_name: str
    status: str = "ACTIVE"
    created_at: str


class SellerProfileUpdateRequest(BaseModel):
    """แก้ไขข้อมูลโปรไฟล์ (AC-S01-01)"""
    display_name: str = Field(..., min_length=1, max_length=100, description="ชื่อที่แสดงของผู้ขาย")


class GeoPoint(BaseModel):
    """พิกัดภูมิศาสตร์ละติจูด/ลองจิจูด (MD-DOM-04, PII)"""
    lat: float = Field(..., ge=-90.0, le=90.0, description="ละติจูด")
    lng: float = Field(..., ge=-180.0, le=180.0, description="ลองจิจูด")


class PickupLocationCreateRequest(BaseModel):
    """เพิ่มที่อยู่นัดหมายรับของเก่า (AC-S01-02, MD-DOM-04, Q-02, Q-03)"""
    label: str = Field(default="บ้าน", max_length=50, description="ป้ายกำกับ เช่น บ้าน, คอนโด, ร้านค้า")
    sub_district: str = Field(..., min_length=1, max_length=100, description="ตำบล/แขวง (เปิดเผยก่อนรับงาน)")
    address_text: str = Field(..., min_length=1, description="บ้านเลขที่ ซอย ถนน จุดสังเกต (PII)")
    geo_point: GeoPoint
    is_default: bool = Field(default=False, description="กำหนดเป็นที่อยู่เริ่มต้น")


class PickupLocationUpdateRequest(BaseModel):
    """แก้ไขที่อยู่นัดหมายรับของเก่า (AC-S01-02)"""
    label: Optional[str] = Field(default=None, max_length=50)
    sub_district: Optional[str] = Field(default=None, max_length=100)
    address_text: Optional[str] = Field(default=None)
    geo_point: Optional[GeoPoint] = None
    is_default: Optional[bool] = None


class PickupLocationResponse(BaseModel):
    """ข้อมูลที่อยู่นัดหมายรับของเก่า (AC-S01-02, MD-DOM-04)"""
    location_id: str
    seller_id: str
    label: str
    sub_district: str
    address_text: str
    geo_point: GeoPoint
    is_default: bool
    created_at: str
    updated_at: str


class PickupLocationListResponse(BaseModel):
    """รายการที่อยู่นัดหมายทั้งหมดของผู้ขาย (AC-S01-02)"""
    seller_id: str
    total_locations: int
    locations: List[PickupLocationResponse]

