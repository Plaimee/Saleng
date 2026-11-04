"""
Data Models for Pricing & Decision Feature
รองรับ MD-DOM-04, REQ-DAT-001, BR-01, AC-S04-01, AC-S04-02, AC-S04-03, AC-S04-04, AC-S04-05
"""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator


class BenchmarkPrice(BaseModel):
    """
    ตารางราคากลางอ้างอิงรายวัน
    รองรับ REQ-DAT-001, AC-S04-01, D-04
    """
    id: str
    category_code: str
    category_name: str
    unit: Literal["kg", "bag", "piece", "crate"] = "kg"
    min_price_per_unit: float = Field(..., gt=0, description="ราคาต่ำสุดต่อหน่วย (บาท)")
    max_price_per_unit: float = Field(..., gt=0, description="ราคาสูงสุดต่อหน่วย (บาท)")
    grading_condition: Optional[str] = None
    updated_at: str

    @field_validator("max_price_per_unit")
    @classmethod
    def validate_price_range(cls, v, info):
        min_p = info.data.get("min_price_per_unit")
        if min_p is not None and v < min_p:
            raise ValueError("max_price_per_unit ต้องไม่น้อยกว่า min_price_per_unit")
        return v


class BenchmarkPriceListResponse(BaseModel):
    prices: List[BenchmarkPrice]
    last_updated_at: str


class WasteItemEstimateInput(BaseModel):
    """
    ข้อมูลของเก่าแต่ละรายการที่ผู้ขายกรอกเพื่อประเมินราคา
    รองรับ AC-S04-02, AC-S04-04 (Invalid Quantity Guard), AC-S04-05 (Bag Unit)
    """
    category_code: str
    unit: Literal["kg", "bag", "piece", "crate"] = "kg"
    quantity: float = Field(..., description="ปริมาณของเก่า (กก. หรือ กระสอบ)")

    @field_validator("quantity")
    @classmethod
    def validate_quantity_positive(cls, v):
        if v <= 0:
            raise ValueError("กรุณากรอกปริมาณมากกว่า 0")
        return v


class CalculationEstimateRequest(BaseModel):
    """
    Request Payload สำหรับคำนวณราคาประเมิน
    รองรับ Card 01, AC-S04-02, D-06
    """
    items: List[WasteItemEstimateInput] = Field(..., min_length=1, description="รายการของเก่าที่ต้องการประเมินราคา")


class WasteItemEstimateOutput(BaseModel):
    category_code: str
    category_name: str
    unit: Literal["kg", "bag"]
    quantity: float
    unit_min_price: float
    unit_max_price: float
    est_min_price: float
    est_max_price: float


class CalculationEstimateResponse(BaseModel):
    """
    ผลลัพธ์การคำนวณช่วงราคาประเมินและยอดรวมตะกร้า
    รองรับ Card 01, BR-01, AC-S04-02, D-06
    """
    items: List[WasteItemEstimateOutput]
    total_est_min_price: float
    total_est_max_price: float
    disclaimer: str = "ราคาจริงขึ้นกับสภาพของหน้างาน"
    calculation_time_ms: float


class OrderSubmissionInput(BaseModel):
    """
    คำขอส่งใบงานนัดหมาย
    รองรับ REQ-FN-001, REQ-FN-006, AC-S04-03, D-01, D-03
    """
    seller_id: str
    pickup_location_id: str
    items: List[WasteItemEstimateInput]
    submission_type: Literal["DIRECT", "ROUTE_DROP_IN", "BUILDING_GROUP"] = "DIRECT"
    building_id: Optional[str] = None


class OrderSubmissionResponse(BaseModel):
    order_id: str
    status: str = "S2"
    total_est_min_price: float
    total_est_max_price: float
    is_route_drop_in: bool = False
    is_building_group_drop: bool = False
    message: str
    created_at: str

