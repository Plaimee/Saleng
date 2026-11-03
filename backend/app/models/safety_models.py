"""
Pydantic Models สำหรับระบบความปลอดภัยขณะทำธุรกรรม (Transaction Safety & SOS Models)
รองรับ UC-09, UC-13, REQ-SEC-001, REQ-SEC-002, REQ-QA-001, REQ-UX-001, REQ-FN-006, CC-01, CC-04, AC-S09-01..05, P-01..P-04
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


# -----------------------------------------------------------------------------
# 1. Models สำหรับการบันทึกเสียงและคลิปวิดีโอหลักฐาน (AC-S09-01, P-01, Q-01)
# -----------------------------------------------------------------------------
class EvidenceUploadRequest(BaseModel):
    """คำขออัปโหลด/บันทึกไฟล์หลักฐานเสียงหรือวิดีโอ"""
    media_type: str = Field(..., description="ประเภทสื่อ: 'AUDIO' หรือ 'VIDEO'")
    duration_seconds: int = Field(..., ge=1, le=900, description="ความยาวเป็นวินาที (สูงสุด 15 นาที หรือ 900 วินาที)")
    file_size_bytes: int = Field(..., ge=1, le=25 * 1024 * 1024, description="ขนาดไฟล์ (ไบต์) สูงสุด 25 MB (CC-01)")
    file_url: Optional[str] = Field(None, description="URL หรือ Data URI ของไฟล์หลักฐาน")


class EvidenceItemResponse(BaseModel):
    """ข้อมูลรายการหลักฐานที่บันทึกแล้ว"""
    id: str
    evidence_id: str = Field(..., description="รหัสหลักฐาน: EVD-YYYYMMDD-XXXX")
    order_id: str
    seller_id: str
    media_type: str
    file_url: str
    file_size_bytes: int
    duration_seconds: int
    is_locked: bool = Field(default=False, description="สถานะล็อกห้ามลบ/แก้ไขเมื่อมีข้อพิพาทหรือ SOS (REQ-FN-006)")
    created_at: str


class EvidenceListResponse(BaseModel):
    """รายการหลักฐานทั้งหมดของคำขอ"""
    order_id: str
    total_evidences: int
    evidences: List[EvidenceItemResponse]


# -----------------------------------------------------------------------------
# 2. Models สำหรับเบอร์ผู้ติดต่อฉุกเฉินที่ไว้ใจได้ (AC-S09-03, P-03, Q-03)
# -----------------------------------------------------------------------------
class EmergencyContactUpdateRequest(BaseModel):
    """คำขอบันทึกหรือแก้ไขผู้ติดต่อฉุกเฉิน"""
    contact_name: str = Field(..., min_length=2, max_length=120, description="ชื่อบุคคลที่ติดต่อได้")
    relationship: str = Field(..., min_length=2, max_length=60, description="ความสัมพันธ์ เช่น บุตรหลาน ญาติ หรือเพื่อนบ้าน")
    contact_phone: str = Field(..., pattern=r"^0\d{8,9}$", description="เบอร์โทรศัพท์ 9-10 หลัก เช่น 0812345678")


class EmergencyContactResponse(BaseModel):
    """ข้อมูลผู้ติดต่อฉุกเฉินที่ไว้ใจได้ (แสดงผลแบบ Mask PII ตาม REQ-SEC-002)"""
    seller_id: str
    contact_name: str
    relationship: str
    contact_phone_masked: str = Field(..., description="เบอร์โทรศัพท์ที่ถูกปกปิดตาม REQ-SEC-002: 08X-XXX-XXXX")
    is_default: bool = Field(default=False, description="เป็นเบอร์สายด่วนส่วนกลาง Saleng Hotline กรณีผู้ขายยังไม่ได้ระบุญาติ")
    updated_at: str


# -----------------------------------------------------------------------------
# 3. Models สำหรับการส่งสัญญาณฉุกเฉิน SOS One-Tap Trigger (AC-S09-02, P-02, Q-02)
# -----------------------------------------------------------------------------
class SosTriggerRequest(BaseModel):
    """คำขอกดส่งสัญญาณฉุกเฉิน SOS"""
    current_lat: Optional[float] = Field(None, description="พิกัดละติจูดปัจจุบันของจุดเกิดเหตุ")
    current_lng: Optional[float] = Field(None, description="พิกัดลองจิจูดปัจจุบันของจุดเกิดเหตุ")
    notes: Optional[str] = Field(None, description="หมายเหตุเพิ่มเติมหากมี")


class SosAlertResponse(BaseModel):
    """ผลการตอบรับการแจ้งเหตุฉุกเฉิน SOS"""
    id: str
    sos_id: str = Field(..., description="รหัสแจ้งเหตุฉุกเฉิน: SOS-YYYYMMDD-XXXX")
    order_id: str
    seller_id: str
    saleng_id: str
    geo_point: Dict[str, float]
    status: str = Field(default="TRIGGERED", description="สถานะแจ้งเหตุ: TRIGGERED, DISPATCHED, RESOLVED")
    emergency_phone_to_call: str = Field(..., description="เบอร์โทรศัพท์สำหรับโทรออกด่วน (Direct Dial)")
    emergency_contact_name: str = Field(..., description="ชื่อผู้รับสายฉุกเฉิน")
    created_at: str
    response_time_ms: float = Field(..., description="เวลาที่ใช้ในการประมวลผล (ต้อง < 2000 ms ตาม REQ-QA-001)")
    message: str


# -----------------------------------------------------------------------------
# 4. Models สำหรับการล็อกหลักฐาน (AC-S09-04, P-04, Q-04)
# -----------------------------------------------------------------------------
class LockEvidenceResponse(BaseModel):
    """ผลการล็อกหลักฐานเมื่อมีข้อพิพาทหรือ SOS"""
    order_id: str
    locked_count: int
    is_locked: bool = True
    message: str

