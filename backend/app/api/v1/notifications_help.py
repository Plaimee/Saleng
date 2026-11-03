"""
API Endpoints สำหรับระบบแจ้งเตือนและการช่วยเหลือ (Notifications & Help Center API)
รองรับ UC-08, UC-13, REQ-OP-001, REQ-SEC-001, REQ-SEC-002, AC-S08-01..05, P-01..P-05
"""

from typing import Optional
from fastapi import APIRouter, status, Query
from backend.app.models.notification_help_models import (
    NotificationListResponse,
    NotificationMarkReadResponse,
    SortingGuideListResponse,
    FaqListResponse,
    SupportTicketCreateRequest,
    SupportTicketResponse,
    SupportContactInfoResponse,
)
from backend.app.services.notification_help_service import (
    NotificationService,
    KnowledgeBaseService,
    SupportTicketService,
)

notifications_help_router = APIRouter(prefix="/api/v1", tags=["notifications-and-help"])


# -----------------------------------------------------------------------------
# 1. ศูนย์แจ้งเตือน (In-App Notification Center - AC-S08-01)
# -----------------------------------------------------------------------------
@notifications_help_router.get(
    "/sellers/{seller_id}/notifications",
    response_model=NotificationListResponse,
    summary="ดึงรายการแจ้งเตือนทั้งหมดของผู้ขาย (AC-S08-01, UC-08, Q-01)"
)
def get_seller_notifications(seller_id: str):
    """
    ดึงรายการแจ้งเตือนทั้งหมดของผู้ขาย พร้อมตรวจหาคำขอค้างใน S1 > 3 วัน เพื่อสร้าง Draft Reminder
    """
    return NotificationService.get_seller_notifications(seller_id=seller_id)


@notifications_help_router.patch(
    "/notifications/{notification_id}/read",
    response_model=NotificationMarkReadResponse,
    summary="ทำเครื่องหมายแจ้งเตือนว่าอ่านแล้ว (AC-S08-01)"
)
def mark_notification_as_read(notification_id: str):
    """ทำเครื่องหมายว่าอ่านแล้วสำหรับแจ้งเตือนที่ระบุ"""
    return NotificationService.mark_as_read(notification_id=notification_id)


@notifications_help_router.post(
    "/sellers/{seller_id}/notifications/mark-all-read",
    summary="ทำเครื่องหมายแจ้งเตือนทั้งหมดว่าอ่านแล้ว (AC-S08-01, P-05)"
)
def mark_all_notifications_as_read(seller_id: str):
    """ทำเครื่องหมายว่าอ่านแล้วสำหรับการแจ้งเตือนทั้งหมดของผู้ขาย"""
    return NotificationService.mark_all_as_read(seller_id=seller_id)


# -----------------------------------------------------------------------------
# 2. คู่มือแนะนำการคัดแยกขยะ (Waste Sorting Guide - AC-S08-02)
# -----------------------------------------------------------------------------
@notifications_help_router.get(
    "/help/sorting-guides",
    response_model=SortingGuideListResponse,
    summary="ดึงข้อมูลคู่มือแนะนำการคัดแยกขยะ 4 หมวดหลัก (AC-S08-02, Q-02)"
)
def get_sorting_guides():
    """ดึงคู่มือแนะนำการคัดแยกขยะเพื่อเพิ่มมูลค่าราคา (4 หมวดหลัก)"""
    return KnowledgeBaseService.get_sorting_guides()


# -----------------------------------------------------------------------------
# 3. คำถามที่พบบ่อย (FAQ Knowledge Base - AC-S08-03)
# -----------------------------------------------------------------------------
@notifications_help_router.get(
    "/help/faqs",
    response_model=FaqListResponse,
    summary="ดึงข้อมูลคำถามที่พบบ่อย 3 หมวดหมู่ พร้อมค้นหา (AC-S08-03, Q-03)"
)
def get_faqs(query: Optional[str] = Query(None, description="คำค้นหาคำสำคัญ")):
    """ดึงคำถามที่พบบ่อย (FAQ) แบ่งเป็น 3 หมวดหมู่ พร้อมรองรับการค้นหาคำสำคัญ"""
    return KnowledgeBaseService.get_faqs(query=query)


# -----------------------------------------------------------------------------
# 4. คำร้องขอความช่วยเหลือและสายด่วน (Support Ticket & Hotline - AC-S08-04)
# -----------------------------------------------------------------------------
@notifications_help_router.post(
    "/sellers/{seller_id}/support-tickets",
    response_model=SupportTicketResponse,
    status_code=status.HTTP_201_CREATED,
    summary="ส่งคำร้องขอความช่วยเหลือ (Support Ticket - AC-S08-04, UC-13, Q-04)"
)
def submit_support_ticket(seller_id: str, payload: SupportTicketCreateRequest):
    """
    ผู้ขายส่งคำร้องขอความช่วยเหลือไปยังศูนย์ดูแลระบบ พร้อมปกปิดเบอร์โทรศัพท์ตาม REQ-SEC-002
    """
    return SupportTicketService.create_ticket(
        seller_id=seller_id,
        category=payload.category,
        subject=payload.subject,
        description=payload.description,
        contact_phone=payload.contact_phone,
    )


@notifications_help_router.get(
    "/help/contact-info",
    response_model=SupportContactInfoResponse,
    summary="ดึงข้อมูลติดต่อสายด่วน Call Center และ LINE Official (AC-S08-04)"
)
def get_contact_info():
    """ดึงข้อมูลช่องทางติดต่อฝ่ายดูแลลูกค้าด่วน"""
    return SupportTicketService.get_contact_info()

