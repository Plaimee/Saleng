"""
Pydantic Models สำหรับระบบหลังทำธุรกรรม (Post-Transaction)
รองรับ Use Case UC-10, SC-05, REQ-FN-005, REQ-SEC-002, AC-S07-01..05
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ReviewCreateRequest(BaseModel):
    """คำขอส่งคะแนนรีวิวซาเล้ง (UC-10, AC-S07-01, Q-01, Q-02)"""
    seller_id: str = Field(..., description="รหัสผู้ขายที่เป็นเจ้าของคำขอ")
    rating: int = Field(..., ge=1, le=5, description="คะแนนดาว 1 ถึง 5 ดาว")
    comment: Optional[str] = Field(default=None, max_length=500, description="ข้อความรีวิวเพิ่มเติม ไม่เกิน 500 ตัวอักษร")


class ReviewResponse(BaseModel):
    """ข้อมูลการรีวิว (Review Response)"""
    id: str
    order_id: str
    seller_id: str
    collector_id: str
    rating: int
    comment: Optional[str] = None
    created_at: str


class FavoriteCollectorRequest(BaseModel):
    """คำขอบันทึกผู้รับซื้อประจำ (UC-10, SC-05, AC-S07-02, Q-03)"""
    collector_id: str = Field(..., description="รหัสซาเล้งที่ต้องการบันทึกเป็นผู้รับซื้อประจำ")


class FavoriteCollectorResponse(BaseModel):
    """ผลลัพธ์การบันทึก/สลับสถานะผู้รับซื้อประจำ"""
    seller_id: str
    collector_id: str
    is_favorite: bool
    message: str
    created_at: Optional[str] = None


class SalesSummaryResponse(BaseModel):
    """สถิติสรุปสะสมการขายของเก่า (REQ-FN-005, AC-S07-03, Q-04)"""
    total_sales_amount: float = Field(default=0.0, description="ยอดเงินสะสมทั้งหมดที่ได้รับ (บาท)")
    total_weight_kg: float = Field(default=0.0, description="น้ำหนักของเก่าสะสมทั้งหมด (กก.)")
    total_completed_orders: int = Field(default=0, description="จำนวนครั้งที่ซื้อขายสำเร็จ (ครั้ง)")


class SalesOrderItem(BaseModel):
    """รายละเอียดวัสดุในประวัติการขาย"""
    category_code: str
    category_name: str
    actual_quantity: float
    unit: str
    locked_unit_price: float
    settled_item_price: float


class SalesOrderHistoryItem(BaseModel):
    """ข้อมูลใบงานสำเร็จในประวัติการขาย (REQ-FN-005, REQ-SEC-002, AC-S07-03)"""
    order_id: str
    completed_at: str
    collector_id: str
    collector_name: str
    collector_phone_masked: str = Field(..., description="เบอร์โทรศัพท์ที่ถูกปกปิดตาม REQ-SEC-002: 08X-XXX-XXXX")
    is_favorite_collector: bool = Field(default=False, description="เป็นผู้รับซื้อประจำหรือไม่")
    total_settled_amount: float
    payment_method: str
    receipt_no: Optional[str] = None
    items: List[SalesOrderItem] = Field(default_factory=list)
    status: str = Field(default="S7", description="สถานะใบงาน (S7)")
    has_reviewed: bool = Field(default=False, description="ผู้ขายส่งรีวิวแล้วหรือไม่")


class SalesHistoryResponse(BaseModel):
    """ผลลัพธ์ประวัติการขายทั้งหมดของผู้ขาย (AC-S07-03)"""
    seller_id: str
    summary: SalesSummaryResponse
    orders: List[SalesOrderHistoryItem]

