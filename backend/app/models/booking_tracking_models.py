"""
Pydantic Data Models สำหรับระบบนัดหมายและติดตามสถานะ (Booking & Status Tracking)
รองรับ UC-04, MD-STM-04, BR-03, REQ-FN-003, REQ-SEC-001, REQ-SEC-002, AC-S05-01..05
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class BookingSlotRequest(BaseModel):
    """
    คำขอเลือกช่วงเวลานัดหมายและยืนยันส่งคำขอ (AC-S05-01, Q-01)
    """
    booking_type: str = Field(..., description="IMMEDIATE หรือ SCHEDULED")
    scheduled_date: Optional[str] = Field(None, description="วันที่นัดหมาย (YYYY-MM-DD)")
    scheduled_slot: Optional[str] = Field(
        None, description="ช่วงเวลา: MORNING_09_12, AFTERNOON_13_16, EVENING_16_18"
    )
    notes: Optional[str] = None


class OrderCancellationRequest(BaseModel):
    """
    คำขอยกเลิกนัดหมายของผู้ขายตามกฎ BR-03 (AC-S05-03, Q-02)
    """
    reason: str = Field(..., min_length=2, description="เหตุผลการยกเลิกนัดหมาย")


class OrderTrackingResponse(BaseModel):
    """
    ข้อมูลติดตามสถานะคำขอและ Stepper Timeline (AC-S05-02, AC-S05-04)
    """
    order_id: str
    seller_id: str
    status: str
    status_label: str
    stepper_step: int  # 1 ถึง 5
    booking_type: str = "IMMEDIATE"
    scheduled_time_display: str = "เรียกทันที (ด่วนใน 1–2 ชม.)"
    assigned_saleng: Optional[Dict[str, Any]] = None
    eta_minutes: Optional[int] = None
    distance_km: Optional[float] = None
    can_cancel: bool = True  # True สำหรับ S1..S3, False สำหรับ S4..S9 ตาม BR-03
    cancellation_reason: Optional[str] = None
    items_count: int = 0
    total_estimated_price: Dict[str, float] = {"min_price": 0.0, "max_price": 0.0}
    updated_at: str


class SimulateStatusRequest(BaseModel):
    """
    คำขอจำลองสถานะเพื่อการทดสอบ (S2 -> S3 -> S4 -> S5 -> S6 -> S7)
    """
    target_status: str = Field(..., description="สถานะเป้าหมาย S1..S9")
    saleng_id: Optional[str] = "saleng-01"

