"""
Data Models and Schemas for Admin Benchmark Price & Grading Management
รองรับ REQ-DAT-001, REQ-FN-003, BR-01, D-A02-01..06, CC-03, CC-04
"""

from typing import List, Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field, field_validator, model_validator


class BenchmarkPriceAdminItem(BaseModel):
    """
    ข้อมูลราคากลางอ้างอิงระดับแอดมิน
    รองรับ REQ-DAT-001, BR-01, D-A02-01
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category_code: str
    category_name: str
    unit: str  # 'kg', 'piece', 'bag', 'crate'
    min_price_per_unit: float
    max_price_per_unit: float
    grading_condition: Optional[str] = None
    effective_date: Optional[str] = None
    is_active: bool = True
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_by: Optional[str] = "admin-01"


class UpdateBenchmarkPriceRequest(BaseModel):
    """
    คำขอแก้ไขช่วงราคากลางรายวัน
    รองรับ D-A02-02, BR-01
    - min_price > 0
    - max_price >= min_price
    - ทศนิยมไม่เกิน 2 ตำแหน่ง
    - confirm_shift: ยืนยันการเปลี่ยนแปลงกรณีขยับเกิน 50%
    """
    min_price_per_unit: float
    max_price_per_unit: float
    grading_condition: Optional[str] = None
    confirm_shift: bool = False
    updated_by: Optional[str] = "admin-01"
    change_reason: Optional[str] = None

    @field_validator("min_price_per_unit", "max_price_per_unit")
    @classmethod
    def validate_positive_and_precision(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("ราคาต่อหน่วยต้องมากกว่า 0 (min_price > 0)")
        if round(v, 2) != v:
            raise ValueError("ค่าราคารองรับทศนิยมไม่เกิน 2 ตำแหน่ง")
        return v

    @model_validator(mode="after")
    def validate_min_max_relationship(self) -> "UpdateBenchmarkPriceRequest":
        if self.max_price_per_unit < self.min_price_per_unit:
            raise ValueError("ราคาสูงสุดต้องมากกว่าหรือเท่ากับราคาต่ำสุด (max_price >= min_price)")
        return self


class BatchUpdateItem(BaseModel):
    """
    รายการย่อยสำหรับการอัปเดตราคาแบบกลุ่ม
    """
    category_code: str
    min_price_per_unit: float
    max_price_per_unit: float
    grading_condition: Optional[str] = None
    confirm_shift: bool = False

    @field_validator("min_price_per_unit", "max_price_per_unit")
    @classmethod
    def validate_positive_and_precision(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("ราคาต่อหน่วยต้องมากกว่า 0")
        if round(v, 2) != v:
            raise ValueError("ค่าราคารองรับทศนิยมไม่เกิน 2 ตำแหน่ง")
        return v

    @model_validator(mode="after")
    def validate_min_max(self) -> "BatchUpdateItem":
        if self.max_price_per_unit < self.min_price_per_unit:
            raise ValueError("ราคาสูงสุดต้องมากกว่าหรือเท่ากับราคาต่ำสุด")
        return self


class BatchUpdateBenchmarkPricesRequest(BaseModel):
    """
    คำขออัปเดตราคากลางแบบกลุ่มประจำวัน
    รองรับ REQ-DAT-001, D-A02-01
    """
    items: List[BatchUpdateItem]
    effective_date: Optional[str] = None
    updated_by: Optional[str] = "admin-01"
    change_reason: Optional[str] = None


class QualityGradingRuleItem(BaseModel):
    """
    เกณฑ์คุณภาพและการหักสิ่งปนเปื้อน 3 ระดับ
    รองรับ REQ-FN-003, D-A02-03
    - GRADE_A: หัก 0% (max_price)
    - GRADE_B: หัก 5% (mid_price)
    - GRADE_C: หัก 10% (min_price)
    """
    rule_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category_code: str
    grade_level: str  # 'GRADE_A', 'GRADE_B', 'GRADE_C'
    grade_name: str
    description: str
    contamination_deduction_percent: float  # 0.0, 5.0, 10.0
    price_target: str = "MID"  # 'MAX', 'MID', 'MIN'
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_by: Optional[str] = "admin-01"

    @field_validator("contamination_deduction_percent")
    @classmethod
    def validate_deduction(cls, v: float) -> float:
        if v < 0 or v > 100:
            raise ValueError("เปอร์เซ็นต์การหักสิ่งปนเปื้อนต้องอยู่ระหว่าง 0 ถึง 100%")
        return v


class UpdateGradingRulesRequest(BaseModel):
    """
    คำขอปรับปรุงเกณฑ์คุณภาพสำหรับหมวดหมู่วัสดุ
    """
    rules: List[QualityGradingRuleItem]
    updated_by: Optional[str] = "admin-01"


class PriceHistoryLogItem(BaseModel):
    """
    ประวัติการปรับปรุงราคาย้อนหลัง
    """
    history_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category_code: str
    old_min_price: float
    old_max_price: float
    new_min_price: float
    new_max_price: float
    changed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    changed_by: str = "admin-01"
    change_reason: Optional[str] = None


class BenchmarkPriceResponse(BaseModel):
    """
    ผลลัพธ์การอัปเดตราคากลางรายการเดี่ยว
    """
    success: bool = True
    message: str
    category_code: str
    min_price_per_unit: float
    max_price_per_unit: float
    updated_at: str
    warning: Optional[str] = None


class BatchUpdateResponse(BaseModel):
    """
    ผลลัพธ์การอัปเดตราคากลางแบบกลุ่ม
    """
    success: bool = True
    message: str
    updated_count: int
    items: List[BenchmarkPriceAdminItem] = []


class GradingRulesResponse(BaseModel):
    """
    ผลลัพธ์การดึง/แก้ไขเกณฑ์คุณภาพ
    """
    success: bool = True
    category_code: str
    rules: List[QualityGradingRuleItem]

