"""
FastAPI Router สำหรับระบบค้นหาและเลือกผู้รับซื้อ (Buyer Search & Selection Endpoints)
รองรับ UC-03, REQ-FN-001, REQ-QA-001, REQ-UX-001, REQ-SEC-001, REQ-SEC-002, CC-03, CC-06, AC-S03-01..05
"""

from typing import List, Optional
from fastapi import APIRouter, Query, status
from backend.app.models.buyer_search_models import (
    SalengProfileResponse,
    CollectorListResponse,
    DirectAppointmentRequest,
    DirectAppointmentResponse,
    FavoriteToggleResponse,
)
from backend.app.services.buyer_search_service import BuyerSearchService

router = APIRouter(prefix="/buyer-search", tags=["Buyer Search & Selection"])


@router.get(
    "/collectors",
    response_model=CollectorListResponse,
    summary="ค้นหารายชื่อซาเล้งในพื้นที่และตัวกรองหลายมิติ (AC-S03-01..03)",
)
def search_collectors(
    seller_id: str = Query("seller-01", description="รหัสผู้ขาย"),
    order_id: Optional[str] = Query(None, description="รหัสคำขอโพสต์ขายของเก่า"),
    radius_km: float = Query(5.0, description="รัศมีค้นหา (กม.)"),
    vehicle_type: Optional[str] = Query(None, description="ประเภทยานพาหนะ"),
    min_rating: Optional[float] = Query(None, description="คะแนนรีวิวขั้นต่ำ"),
    category: Optional[str] = Query(None, description="หมวดหมู่ของที่รับ"),
):
    """
    ค้นหารายชื่อซาเล้งที่ผ่าน KYC 100% ในรัศมี พร้อมตรึงซาเล้งที่เคยใช้บริการไว้บนสุด
    """
    return BuyerSearchService.search_collectors(
        seller_id=seller_id,
        order_id=order_id,
        radius_km=radius_km,
        vehicle_type=vehicle_type,
        min_rating=min_rating,
        category=category,
    )


@router.get(
    "/collectors/{saleng_id}",
    response_model=SalengProfileResponse,
    summary="ดึงข้อมูลโปรไฟล์ละเอียดของซาเล้ง (AC-S03-01)",
)
def get_collector_profile(
    saleng_id: str,
    seller_id: str = Query("seller-01", description="รหัสผู้ขาย"),
):
    """
    ดึงโปรไฟล์ซาเล้งพร้อมสถานะยืนยันตัวตน และสถิติงานรับซื้อ
    """
    return BuyerSearchService.get_collector_profile(saleng_id=saleng_id, seller_id=seller_id)


@router.get(
    "/favorites",
    response_model=List[SalengProfileResponse],
    summary="ดึงรายชื่อซาเล้งที่เคยใช้บริการ (AC-S03-02)",
)
def get_favorites(
    seller_id: str = Query("seller-01", description="รหัสผู้ขาย"),
):
    """
    ดึงรายชื่อซาเล้งที่บันทึกไว้ในรายการโปรด
    """
    return BuyerSearchService.get_favorites(seller_id=seller_id)


@router.post(
    "/favorites/{saleng_id}/toggle",
    response_model=FavoriteToggleResponse,
    summary="เปิด/ปิดการบันทึกเป็นซาเล้งที่เคยใช้บริการ (AC-S03-02)",
)
def toggle_favorite(
    saleng_id: str,
    seller_id: str = Query("seller-01", description="รหัสผู้ขาย"),
):
    """
    สลับสถานะคนโปรดของผู้ขาย
    """
    is_fav = BuyerSearchService.toggle_favorite(seller_id=seller_id, saleng_id=saleng_id)
    msg = "บันทึกเป็นซาเล้งที่เคยใช้บริการแล้ว" if is_fav else "ยกเลิกการบันทึกเป็นซาเล้งที่เคยใช้บริการแล้ว"
    return FavoriteToggleResponse(saleng_id=saleng_id, is_favorite=is_fav, message=msg)


@router.post(
    "/orders/{order_id}/direct-request",
    response_model=DirectAppointmentResponse,
    status_code=status.HTTP_200_OK,
    summary="ส่งคำขอนัดหมายเจาะจงบุคคลและเปลี่ยนสถานะเป็น S2 (AC-S03-05)",
)
def send_direct_request(
    order_id: str,
    req: DirectAppointmentRequest,
    seller_id: str = Query("seller-01", description="รหัสผู้ขาย"),
):
    """
    ส่งคำขอไปยังซาเล้งที่เลือก พร้อมนับถอยหลัง 15 นาที และบันทึก Audit Log
    """
    return BuyerSearchService.send_direct_request(
        order_id=order_id,
        saleng_id=req.saleng_id,
        seller_id=seller_id,
        notes=req.notes,
    )

