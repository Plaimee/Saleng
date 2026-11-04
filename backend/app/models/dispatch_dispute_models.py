"""
Data Models and Schemas for Admin Dispatch & Dispute Management
รองรับ UC-13, REQ-FN-005, REQ-FN-004, REQ-BR-002, REQ-SEC-001, CC-03, CC-04, CC-05, D-A03-01..06
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator


class DisputeActionEnum(str, Enum):
    RESOLVE_COMPLETE = "RESOLVE_COMPLETE"
    RESOLVE_CANCEL = "RESOLVE_CANCEL"


# Alias สำหรับเรียกใช้งานตามสเปก
ResolveDisputeAction = DisputeActionEnum


class DisputeStatusEnum(str, Enum):
    PENDING_ADMIN = "PENDING_ADMIN"
    RESOLVED_COMPLETED = "RESOLVED_COMPLETED"
    RESOLVED_CANCELLED = "RESOLVED_CANCELLED"


class StalledOrderItem(BaseModel):
    """
    ข้อมูลคำขอขายสถานะ S2 ที่ตกค้างเกินเกณฑ์เวลา
    รองรับ UC-13, D-A03-02, CC-06
    """
    order_id: str
    seller_id: str
    status: str = "S2"
    created_at: str
    waiting_minutes: float
    subdistrict: Optional[str] = None
    district: Optional[str] = None
    total_est_min_price: float = 0.0
    total_est_max_price: float = 0.0
    total_est_weight_kg: float = 0.0
    search_radius_km: float = 5.0
    is_manual_dispatched: bool = False
    dispatched_by: Optional[str] = None
    dispatched_at: Optional[str] = None
    pickup_time: Optional[str] = None


class ManualDispatchAssignRequest(BaseModel):
    """
    คำขอมอบหมายงานตรงให้ซาเล้งเฉพาะราย (Direct Assign)
    รองรับ UC-13, D-A03-03, D-00-01
    """
    order_id: str
    saleng_id: str
    admin_id: str = "admin-01"
    notes: Optional[str] = None

    @field_validator("order_id", "saleng_id")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("รหัสคำขอและรหัสซาเล้งต้องไม่เป็นค่าว่าง")
        return v.strip()


class ManualDispatchResponse(BaseModel):
    """
    ผลลัพธ์การมอบหมายงานตรง
    รองรับ D-A03-03
    """
    success: bool = True
    order_id: str
    status: str = "S3"
    assigned_saleng_id: str
    assigned_saleng_name: Optional[str] = None
    message: str = "มอบหมายงานสำเร็จ"
    dispatched_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ExpandDispatchRadiusRequest(BaseModel):
    """
    คำขอขยายรัศมีการค้นหาของคำขอ (Expand Radius Broadcast)
    รองรับ UC-13, D-A03-03
    """
    order_id: str
    new_radius_km: float = 10.0
    admin_id: str = "admin-01"

    @field_validator("new_radius_km")
    @classmethod
    def validate_radius(cls, v: float) -> float:
        if v <= 5.0:
            raise ValueError("รัศมีใหม่ต้องมากกว่า 5.0 กม. (ค่าเริ่มต้น 10.0 กม.)")
        return round(v, 1)


class ExpandRadiusResponse(BaseModel):
    """
    ผลลัพธ์การขยายรัศมีการค้นหา
    รองรับ D-A03-03
    """
    success: bool = True
    order_id: str
    old_radius_km: float
    new_radius_km: float
    message: str = "ขยายรัศมีการค้นหาสำเร็จ"


class DisputeSummaryItem(BaseModel):
    """
    สรุปรายการข้อพิพาทสำหรับแสดงในตารางคิวงาน
    รองรับ UC-13, D-A03-01
    """
    dispute_id: str
    order_id: str
    seller_id: Optional[str] = None
    buyer_id: Optional[str] = None
    seller_name: Optional[str] = None
    buyer_name: Optional[str] = None
    dispute_reason: str = ""
    status: str = "PENDING_ADMIN"
    created_at: str
    re_quoted_price: Optional[float] = None
    arbitrated_amount: Optional[float] = None


class DisputeDossierResponse(BaseModel):
    """
    สำนวนหลักฐานข้อพิพาท 4 มิติ
    รองรับ UC-13, REQ-FN-005, REQ-FN-004, D-A03-04
    1. ข้อมูลคำขอเดิม & Price Snapshot
    2. ข้อมูลหน้างานจากซาเล้ง (น้ำหนักจริง, ภาพตาชั่ง)
    3. ข้อมูลข้อโต้แย้งจากผู้ขาย
    4. ข้อมูลคู่กรณี
    """
    dispute_id: str
    order_id: str
    seller_id: Optional[str] = None
    buyer_id: Optional[str] = None
    status: str = "PENDING_ADMIN"
    created_at: str
    dispute_reason: str = ""
    original_order: Dict[str, Any]
    saleng_verification: Dict[str, Any]
    seller_dispute: Dict[str, Any]
    parties_contact: Dict[str, Any]
    arbitration_result: Optional[Dict[str, Any]] = None


class ResolveDisputeRequest(BaseModel):
    """
    คำขอตัดสินชี้ขาดข้อพิพาท
    รองรับ UC-13, D-A03-01, D-A03-05
    """
    action: DisputeActionEnum
    arbitrated_amount: Optional[float] = None
    arbitration_note: Optional[str] = None
    admin_id: str = "admin-01"

    @model_validator(mode="after")
    def validate_action_fields(self) -> "ResolveDisputeRequest":
        if self.action == DisputeActionEnum.RESOLVE_COMPLETE:
            if self.arbitrated_amount is None or self.arbitrated_amount <= 0:
                raise ValueError("การตัดสินให้ปิดงาน (RESOLVE_COMPLETE) ต้องระบุยอดเงินชี้ขาดสุทธิที่มากกว่า 0 บาท")
        elif self.action == DisputeActionEnum.RESOLVE_CANCEL:
            if not self.arbitration_note or not self.arbitration_note.strip():
                raise ValueError("การตัดสินสั่งยกเลิก (RESOLVE_CANCEL) ต้องระบุเหตุผลการยกเลิกในช่อง arbitration_note")
        return self


class ResolveDisputeResponse(BaseModel):
    """
    ผลลัพธ์การตัดสินชี้ขาดข้อพิพาท
    รองรับ D-A03-01, D-A03-05
    """
    success: bool = True
    dispute_id: str
    order_id: str
    dispute_status: str
    order_status: str
    action_taken: str
    arbitrated_amount: Optional[float] = None
    arbitration_note: Optional[str] = None
    receipt: Optional[Dict[str, Any]] = None
    message: str
