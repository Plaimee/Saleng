"""
Data Models and Schemas for Admin Security, Audit Trail & PDPA Compliance
รองรับ UC-13, REQ-SEC-001, REQ-SEC-002, CT-01, P-07, D-A04-01..06, CC-03, CC-04, CC-05, CC-06
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import hashlib
import json
from pydantic import BaseModel, Field, field_validator


def compute_audit_log_hash(log_data: Dict[str, Any]) -> str:
    """
    คำนวณ SHA-256 Checksum สำหรับ Audit Log เพื่อยืนยัน Immutability
    รองรับ REQ-SEC-001, P-07, D-A04-05
    """
    actor_id = str(log_data.get("actor_id", ""))
    actor_role = str(log_data.get("actor_role", ""))
    action = str(log_data.get("action", ""))
    entity_id = str(log_data.get("entity_id", ""))
    timestamp = str(log_data.get("timestamp", ""))
    details = log_data.get("details", {})
    
    # Serialize details in canonical order
    details_str = json.dumps(details, sort_keys=True, ensure_ascii=False)
    raw_payload = f"{actor_id}:{actor_role}:{action}:{entity_id}:{timestamp}:{details_str}"
    return hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()


class AuditLogQueryFilter(BaseModel):
    """
    ตัวกรองสำหรับสืบค้นประวัติ Audit Trail
    รองรับ D-A04-01
    """
    action: Optional[str] = None
    actor_role: Optional[str] = None
    actor_id: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    limit: int = Field(default=50, ge=1, le=10000)
    offset: int = Field(default=0, ge=0)


class AuditLogItem(BaseModel):
    """
    ระเบียนบันทึกประวัติร่องรอยตรวจสอบ (Audit Log Entry)
    รองรับ REQ-SEC-001, D-A04-01, D-A04-05
    """
    log_id: str
    action: str
    entity_id: Optional[str] = None
    actor_id: str
    actor_role: str
    details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str
    log_hash: str


class AuditLogListResponse(BaseModel):
    """
    ผลลัพธ์รายการ Audit Log พร้อมการแบ่งหน้า (Pagination)
    """
    total_records: int
    limit: int
    offset: int
    logs: List[AuditLogItem]


class AuditLogExportResponse(BaseModel):
    """
    ผลลัพธ์การส่งออก Audit Log (CSV / JSON)
    รองรับ D-A04-01
    """
    exported_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    total_records: int
    format: str  # 'csv' | 'json'
    filename: str
    content: Optional[str] = None


class VerifyIntegrityResponse(BaseModel):
    """
    ผลลัพธ์การตรวจสอบความสมบูรณ์ของ SHA-256 Hash
    รองรับ AC-A04-02, D-A04-05
    """
    total_checked: int
    is_valid: bool
    corrupted_log_ids: List[str] = Field(default_factory=list)
    verified_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    message: str


class CommunityWasteSummaryItem(BaseModel):
    """
    สรุปสถิติขยะชุมชนจัดกลุ่มตามเขต/แขวง และหมวดหมู่วัสดุ
    รองรับ AC-A04-05, D-A04-03, CC-06 (No PII)
    """
    subdistrict: str
    district: str
    category_code: str
    category_name: str
    total_weight_kg: float
    total_amount_thb: float
    completed_trips_count: int
    period_month: str


class CommunityWasteReportResponse(BaseModel):
    """
    รายงานสถิติปริมาณขยะรีไซเคิลชุมชนแบบไม่ระบุตัวตน (Anonymized Report)
    รองรับ AC-A04-05, D-A04-03
    """
    period: Optional[str] = None
    district: Optional[str] = None
    summary_items: List[CommunityWasteSummaryItem]
    grand_total_weight_kg: float
    grand_total_amount_thb: float
    total_completed_trips: int
    exported_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    is_anonymized: bool = True


class DataRetentionStatusResponse(BaseModel):
    """
    สถานะการจัดเก็บและทำลายข้อมูลตามกฎหมาย PDPA
    รองรับ AC-A04-04, D-A04-04
    """
    gps_retention_days: int = 90
    expired_gps_coordinates_count: int
    unmasked_completed_orders_count: int
    total_audit_logs_count: int
    checked_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class PurgeExpiredDataRequest(BaseModel):
    """
    คำสั่งประมวลผลล้างข้อมูลหมดอายุตามนโยบาย PDPA
    รองรับ AC-A04-04, D-A04-04
    """
    admin_id: str = "dpo-01"
    confirm_purge: bool = True

    @field_validator("confirm_purge")
    @classmethod
    def validate_confirmation(cls, v: bool) -> bool:
        if not v:
            raise ValueError("ต้องยืนยันการล้างข้อมูล (confirm_purge = True)")
        return v


class PurgeExpiredDataResponse(BaseModel):
    """
    ผลลัพธ์การล้างข้อมูลหมดอายุตามนโยบาย PDPA
    รองรับ AC-A04-04, D-A04-04
    """
    success: bool = True
    purged_gps_points_count: int
    masked_orders_count: int
    purged_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    purged_by: str
    message: str
