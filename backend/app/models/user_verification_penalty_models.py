"""
Pydantic Models สำหรับระบบตรวจสอบและอนุมัติผู้ใช้งานฝั่งผู้ดูแลระบบ (Admin Feature 01)
รองรับ UC-11, REQ-QA-001, REQ-SEC-001, REQ-SEC-002, D-00-01, D-A01-01..06
"""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field, field_validator


def mask_thai_id_card(id_card_no: str) -> str:
    """
    แปลงหมายเลขบัตรประชาชน 13 หลักเป็นรูปแบบ Masking ตาม PDPA (REQ-SEC-002, CC-06)
    ตัวอย่าง: 1100200112233 -> 1-1002-XXXXX-XX-3
    """
    clean_id = str(id_card_no).replace("-", "").strip()
    if len(clean_id) == 13:
        return f"{clean_id[0]}-{clean_id[1:5]}-XXXXX-XX-{clean_id[-1]}"
    return "1-1002-XXXXX-XX-X"


class KYCSubmissionItem(BaseModel):
    """รายการคำขอยืนยันตัวตน KYC ของซาเล้ง (AC-A01-01)"""
    id: str = Field(..., description="รหัสอ้างอิงคำขอ KYC (UUID)")
    saleng_id: str = Field(..., description="รหัสอ้างอิงซาเล้ง (saleng-xx)")
    id_card_no_masked: str = Field(..., description="หมายเลขบัตรประชาชนแบบ Masking (1-1002-XXXXX-XX-X)")
    full_name: str = Field(..., description="ชื่อ-นามสกุลตามบัตรประชาชน")
    id_card_photo_url: str = Field(..., description="URL รูปถ่ายหน้าบัตรประชาชน")
    selfie_photo_url: str = Field(..., description="URL รูปถ่ายหน้าตรงถือบัตรประชาชน")
    vehicle_photo_url: Optional[str] = Field(None, description="URL รูปถ่ายยานพาหนะพร้อมป้ายทะเบียน")
    status: Literal["PENDING_REVIEW", "VERIFIED", "REJECTED"] = Field(..., description="สถานะคำขอ")
    rejection_reason: Optional[str] = Field(None, description="เหตุผลในการปฏิเสธคำขอ")
    submitted_at: str = Field(..., description="วันเวลาที่ส่งเอกสาร (ISO 8601)")
    reviewed_at: Optional[str] = Field(None, description="วันเวลาที่ตรวจสอบ")
    reviewed_by: Optional[str] = Field(None, description="รหัสแอดมินผู้ตรวจสอบ")


class KYCReviewRequest(BaseModel):
    """คำขออนุมัติหรือปฏิเสธเอกสาร KYC (AC-A01-02)"""
    submission_id: str = Field(..., min_length=1, description="รหัสอ้างอิงคำขอ KYC")
    action: Literal["APPROVE", "REJECT"] = Field(..., description="ผลการพิจารณา APPROVE หรือ REJECT")
    rejection_reason: Optional[str] = Field(None, description="เหตุผลการปฏิเสธ (บังคับระบุเมื่อ action = REJECT)")

    @field_validator("rejection_reason")
    @classmethod
    def validate_rejection_reason(cls, v, info):
        action = info.data.get("action")
        if action == "REJECT" and (not v or not v.strip()):
            raise ValueError("ต้องระบุเหตุผลการปฏิเสธ (rejection_reason) เมื่อผลการพิจารณาเป็น REJECT")
        return v.strip() if v else None


class KYCReviewResponse(BaseModel):
    """ผลการพิจารณาคำขอ KYC (AC-A01-02)"""
    success: bool = True
    submission_id: str
    saleng_id: str
    action: str
    kyc_status: str
    verified: bool
    rejection_reason: Optional[str] = None
    reviewed_at: str
    reviewed_by: str
    message: str


class UserAccountItem(BaseModel):
    """ข้อมูลบัญชีผู้ใช้งานสำหรับหน้าแดชบอร์ดบทลงโทษ (AC-A01-03)"""
    user_id: str = Field(..., description="รหัสผู้ใช้งาน (saleng-xx หรือ seller-xx)")
    role: Literal["COLLECTOR", "SELLER"] = Field(..., description="บทบาทผู้ใช้")
    display_name: str = Field(..., description="ชื่อที่แสดงในระบบ")
    phone_masked: str = Field(..., description="เบอร์โทรศัพท์แบบ Masking (08X-XXX-XXXX)")
    account_status: Literal["ACTIVE", "SUSPENDED_TEMPORARY", "BANNED"] = Field("ACTIVE", description="สถานะบัญชี")
    penalty_reason: Optional[str] = Field(None, description="เหตุผลการระงับสิทธิ์")
    penalized_at: Optional[str] = Field(None, description="วันเวลาที่ถูกลงโทษ")
    penalized_by: Optional[str] = Field(None, description="รหัสแอดมินผู้สั่งลงโทษ")
    verified: Optional[bool] = Field(None, description="สถานะการยืนยันตัวตน KYC (เฉพาะซาเล้ง)")


class UserPenaltyRequest(BaseModel):
    """คำสั่งระงับสิทธิ์ผู้ใช้งาน (AC-A01-03)"""
    user_id: str = Field(..., min_length=1, description="รหัสผู้ใช้งานที่ต้องการลงโทษ")
    role: Literal["COLLECTOR", "SELLER"] = Field(..., description="บทบาทผู้ใช้")
    action: Literal["SUSPEND_TEMPORARY", "BAN"] = Field(..., description="ประเภทบทลงโทษ")
    penalty_reason: str = Field(..., min_length=3, max_length=500, description="เหตุผลการระงับสิทธิ์")
    duration_days: Optional[int] = Field(None, ge=1, le=365, description="ระยะเวลาแบนชั่วคราว (วัน)")


class UserPenaltyResponse(BaseModel):
    """ผลการสั่งระงับสิทธิ์ผู้ใช้งาน (AC-A01-03)"""
    success: bool = True
    user_id: str
    role: str
    account_status: str
    penalty_reason: str
    penalized_at: str
    penalized_by: str
    message: str


class UserReactivateRequest(BaseModel):
    """คำขอปลดระงับสิทธิ์ผู้ใช้งาน (AC-A01-04)"""
    user_id: str = Field(..., min_length=1, description="รหัสผู้ใช้งานที่ต้องการปลดระงับ")
    role: Literal["COLLECTOR", "SELLER"] = Field(..., description="บทบาทผู้ใช้")
    reason: Optional[str] = Field("ADMIN_REINSTATED", description="เหตุผลการปลดระงับ")


class UserReactivateResponse(BaseModel):
    """ผลการปลดระงับสิทธิ์ผู้ใช้งาน (AC-A01-04)"""
    success: bool = True
    user_id: str
    role: str
    account_status: str = "ACTIVE"
    message: str

