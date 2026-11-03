"""
Pydantic Data Models สำหรับระบบโพสต์ขายของเก่าของผู้ขาย (Scrap Posting)
รองรับ UC-02, REQ-UX-002, REQ-FN-003, REQ-FN-004, REQ-DAT-001, Card 03, MD-DOM-04, P-01..P-06
"""

from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class ScrapCategoryResponse(BaseModel):
    """ข้อมูลหมวดหมู่ของเก่าและคู่มือภาพ (AC-S02-01, P-01)"""
    category_code: str
    category_group: str = Field(..., description="GENERAL_WEIGHT | BOXED_CRATE_ITEMS | BULKY_FLAT_RATE")
    name: str
    icon: str
    unit: str = Field(..., description="kg | crate | bag | piece")
    min_price_per_unit: float
    max_price_per_unit: float
    sub_categories: Optional[List[str]] = None


class CategoryCatalogResponse(BaseModel):
    """รายการหมวดหมู่และคู่มือภาพทั้งหมด (AC-S02-01)"""
    categories: List[ScrapCategoryResponse]


class WasteItemCreateRequest(BaseModel):
    """เพิ่มรายการของเก่าลงในฉบับร่าง (AC-S02-01, AC-S02-02, Card 03)"""
    category_code: str
    sub_category: Optional[str] = None
    quantity: float = Field(..., gt=0, description="ปริมาณต้องมากกว่า 0")
    photo_urls: Optional[List[str]] = Field(default_factory=list, description="แนบรูปได้สูงสุด 5 รูป")

    @field_validator("photo_urls")
    @classmethod
    def validate_photo_urls(cls, v: Optional[List[str]]) -> List[str]:
        if v and len(v) > 5:
            raise ValueError("สามารถแนบรูปถ่ายได้สูงสุดไม่เกิน 5 รูปต่อรายการ")
        return v or []


class WasteItemResponse(BaseModel):
    """ข้อมูลรายการของเก่าในคำขอ (MD-DOM-04, AC-S02-01..04)"""
    item_id: str
    order_id: str
    category_code: str
    category_name: str
    category_group: str
    sub_category: Optional[str] = None
    quantity: float
    unit: str
    est_min_price: float
    est_max_price: float
    photo_urls: List[str] = Field(default_factory=list)


class LiftingHelpUpdateRequest(BaseModel):
    """ปรับปรุงบริการเสริมขอคนช่วยยกของหนักและหมายเหตุ (AC-S02-05, P-05)"""
    need_lifting_help: bool
    lifting_help_notes: Optional[str] = Field(default=None, max_length=500)


class DraftOrderCreateRequest(BaseModel):
    """สร้างคำขอโพสต์ขายของเก่าฉบับร่าง (S1 Draft, P-06)"""
    seller_id: str
    pickup_location_id: Optional[str] = None


class DraftOrderResponse(BaseModel):
    """ข้อมูลคำขอโพสต์ขายของเก่าฉบับร่างและรายการของเก่า (MD-DOM-04, AC-S02-01..05)"""
    order_id: str
    seller_id: str
    pickup_location_id: Optional[str] = None
    pickup_location: Optional[dict] = None
    status: str = "S1"
    need_lifting_help: bool = False
    lifting_help_notes: Optional[str] = None
    total_est_min_price: float = 0.0
    total_est_max_price: float = 0.0
    items: List[WasteItemResponse] = Field(default_factory=list)
    created_at: str
    updated_at: str

