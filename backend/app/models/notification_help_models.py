"""
Pydantic Models สำหรับระบบแจ้งเตือนและการช่วยเหลือ (Notifications & Help Center)
รองรับ UC-08, UC-13, REQ-OP-001, REQ-SEC-002, AC-S08-01..05, P-01..P-04
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class NotificationItem(BaseModel):
    """ข้อมูลรายการแจ้งเตือน 1 รายการ (UC-08, AC-S08-01, Q-01)"""
    id: str
    seller_id: str
    type: str = Field(..., description="ประเภท: DRAFT_REMINDER หรือ ORDER_STATUS_UPDATE")
    title: str
    message: str
    order_id: Optional[str] = None
    is_read: bool = False
    created_at: str


class NotificationListResponse(BaseModel):
    """รายการแจ้งเตือนทั้งหมดของผู้ขาย (AC-S08-01)"""
    seller_id: str
    unread_count: int
    notifications: List[NotificationItem]


class NotificationMarkReadResponse(BaseModel):
    """ผลลัพธ์การทำเครื่องหมายว่าอ่านแล้ว"""
    notification_id: str
    is_read: bool
    message: str


class SortingGuideItem(BaseModel):
    """ข้อมูลคู่มือแนะนำการคัดแยกขยะ 1 หมวดหมู่ (AC-S08-02, Q-02)"""
    category_code: str
    category_name: str
    icon: str
    value_add_tips: List[str] = Field(default_factory=list, description="เคล็ดลับการเตรียมเพื่อเพิ่มมูลค่าราคา")
    price_impact_description: str
    precautions: List[str] = Field(default_factory=list, description="ข้อควรระวัง")


class SortingGuideListResponse(BaseModel):
    """รายการคู่มือแนะนำการคัดแยกขยะทั้งหมด (AC-S08-02)"""
    guides: List[SortingGuideItem]


class FaqItem(BaseModel):
    """ข้อคำถามและคำตอบ FAQ 1 ข้อ (AC-S08-03, Q-03)"""
    id: str
    question: str
    answer: str
    category: str


class FaqCategory(BaseModel):
    """หมวดหมู่คำถามที่พบบ่อย"""
    category_id: str
    category_name: str
    faqs: List[FaqItem]


class FaqListResponse(BaseModel):
    """รายการคำถามที่พบบ่อยแยกหมวดหมู่ (AC-S08-03)"""
    categories: List[FaqCategory]
    total_faqs: int


class SupportTicketCreateRequest(BaseModel):
    """คำขอส่งคำร้องขอความช่วยเหลือ (Support Ticket - AC-S08-04, UC-13, Q-04)"""
    category: str = Field(..., description="หมวดหมู่ปัญหา: BOOKING, WEIGHING, PAYMENT, APP_ISSUE, OTHER")
    subject: str = Field(..., min_length=3, max_length=150, description="หัวข้อปัญหา")
    description: str = Field(..., min_length=10, max_length=1000, description="รายละเอียดปัญหา")
    contact_phone: str = Field(..., min_length=9, max_length=15, description="เบอร์โทรศัพท์สำหรับติดต่อกลับ")


class SupportTicketResponse(BaseModel):
    """ข้อมูลคำร้องขอความช่วยเหลือที่บันทึกแล้ว (AC-S08-04)"""
    id: str
    ticket_no: str = Field(..., description="รหัสตั๋ว: TCK-YYYYMMDD-XXXX")
    seller_id: str
    category: str
    subject: str
    description: str
    contact_phone_masked: str = Field(..., description="เบอร์โทรศัพท์ที่ถูกปกปิดตาม REQ-SEC-002: 08X-XXX-XXXX")
    status: str = Field(default="OPEN", description="สถานะ: OPEN, IN_PROGRESS, RESOLVED")
    created_at: str


class SupportContactInfoResponse(BaseModel):
    """ข้อมูลช่องทางติดต่อฝ่ายดูแลลูกค้าด่วน (AC-S08-04)"""
    call_center_phone: str = "02-123-4567"
    operating_hours: str = "ทุกวัน 08:00 - 18:00 น."
    line_official: str = "@saleng-help"
    emergency_notice: str = "หากเกิดเหตุฉุกเฉินหรือมีข้อพิพาทหน้างาน สามารถกดปุ่มฉุกเฉินในแอปหรือโทรเข้าสายด่วนได้ทันที"

