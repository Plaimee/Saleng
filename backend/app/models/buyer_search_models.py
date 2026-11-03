"""
Pydantic Data Models สำหรับระบบค้นหาและเลือกผู้รับซื้อ (Buyer Search & Selection)
รองรับ UC-03, REQ-FN-001, REQ-QA-001, REQ-UX-001, REQ-SEC-001, REQ-SEC-002, CC-03, CC-06, Card 03
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SalengProfileResponse(BaseModel):
    """
    ข้อมูลโปรไฟล์ซาเล้งสำหรับแสดงผลฝั่งผู้ขาย
    รองรับ REQ-QA-001, REQ-UX-001, AC-S03-01
    """
    saleng_id: str
    display_name: str
    phone: str
    avatar_url: Optional[str] = None
    verified: bool = True
    rating: float = 5.0
    completed_jobs_count: int = 0
    vehicle_type: str  # 'TRICYCLE', 'LARGE_SIDECAR', 'PICKUP_TRUCK'
    max_capacity_kg: float = 200.0
    current_lat: float
    current_lng: float
    distance_km: float = 0.0
    is_favorite: bool = False
    is_online: bool = True
    accepted_categories: List[str] = []


class CollectorSearchQuery(BaseModel):
    """
    พารามิเตอร์การค้นหาและกรองผู้รับซื้อ
    รองรับ REQ-FN-001, CC-03, Card 03, AC-S03-03
    """
    order_id: Optional[str] = None
    radius_km: float = 5.0
    vehicle_type: Optional[str] = None
    min_rating: Optional[float] = None
    category: Optional[str] = None


class CollectorListResponse(BaseModel):
    """
    ผลลัพธ์รายการซาเล้งในพื้นที่ พร้อมแจ้งเตือนหากคำขอมีของชิ้นใหญ่
    รองรับ AC-S03-01, AC-S03-02, AC-S03-03
    """
    collectors: List[SalengProfileResponse]
    total_count: int
    has_bulky_items: bool = False
    bulky_warning_message: Optional[str] = None


class DirectAppointmentRequest(BaseModel):
    """
    คำขอส่งนัดหมายเจาะจงบุคคล (Direct Request)
    รองรับ REQ-SEC-001, MD-STM-04, AC-S03-05
    """
    saleng_id: str
    notes: Optional[str] = None


class DirectAppointmentResponse(BaseModel):
    """
    การตอบกลับเมื่อส่งคำขอนัดหมายเจาะจงบุคคลสำเร็จ
    รองรับ AC-S03-05, S1 -> S2 Transition
    """
    order_id: str
    assigned_saleng: SalengProfileResponse
    status: str = "S2"
    direct_request_expires_at: str
    message: str


class FavoriteToggleResponse(BaseModel):
    """
    ผลการเปิด/ปิดบันทึกเป็นซาเล้งที่เคยใช้บริการ
    รองรับ AC-S03-02, REQ-UX-001
    """
    saleng_id: str
    is_favorite: bool
    message: str

