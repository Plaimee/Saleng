"""
Data Models and Schemas for Buyer Billing & Receipt System
รองรับ UC-05, UC-06, UC-07, REQ-FN-002, REQ-FN-004, REQ-FN-005, REQ-BR-002, REQ-SEC-002, CC-01, CC-04, CC-06, D-B06-01..06
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class WeighingItemInput(BaseModel):
    """ข้อมูลน้ำหนักชั่งจริงของแต่ละสิ่งของ (REQ-FN-002)"""
    item_id: str = Field(..., description="รหัสรายการสิ่งของในคำขอ")
    actual_quantity: float = Field(..., gt=0, description="น้ำหนักชั่งจริงหน้างาน (ต้องมากกว่า 0)")


class SubmitWeighingRequest(BaseModel):
    """คำขอบันทึกผลชั่งจริงหน้างานโดยซาเล้ง (REQ-FN-002, D-B06-02)"""
    saleng_id: str = Field(..., min_length=1, description="รหัสซาเล้งผู้ชั่งของ")
    scale_photo_url: str = Field(..., min_length=5, description="URL ภาพถ่ายหน้าตาชั่งดิจิทัล (บังคับ)")
    items: List[WeighingItemInput] = Field(..., min_length=1, description="รายการผลชั่งจริง")
    idempotency_key: Optional[str] = Field(None, description="คีย์ป้องกันการส่งซ้ำในโหมดกึ่งออฟไลน์ (REQ-OP-001)")


class WeighingSheetItem(BaseModel):
    """ข้อมูลแต่ละรายการในใบชั่งน้ำหนัก"""
    item_id: str = Field(..., description="รหัสรายการสิ่งของ")
    category_code: str = Field(..., description="รหัสหมวดหมู่วัสดุ")
    category_name: str = Field(..., description="ชื่อหมวดหมู่วัสดุ")
    estimated_quantity: float = Field(..., description="ปริมาณประเมินเบื้องต้น")
    actual_quantity: Optional[float] = Field(None, description="ปริมาณชั่งจริงหน้างาน")
    unit: str = Field("กก.", description="หน่วยนับ (กก. หรือ กระสอบ)")
    locked_unit_price: float = Field(..., ge=0, description="ราคาต่อหน่วยที่ล็อกไว้ตอนนัดหมาย (REQ-BR-002)")
    settled_item_price: Optional[float] = Field(None, description="ยอดเงินสุทธิของรายการ")


class WeighingSheetResponse(BaseModel):
    """ข้อมูลสรุปใบชั่งน้ำหนักของคำขอขายสำหรับหน้าจอซาเล้ง"""
    order_id: str = Field(..., description="รหัสคำขอขาย")
    order_status: str = Field(..., description="สถานะคำขอขายปัจจุบัน (S4..S7)")
    seller_name: str = Field(..., description="ชื่อเรียกผู้ขาย")
    seller_phone_masked: str = Field(..., description="เบอร์โทรศัพท์ผู้ขายที่ Mask แล้ว")
    scale_photo_url: Optional[str] = Field(None, description="URL ภาพถ่ายหน้าตาชั่ง")
    seller_confirmed_weight: bool = Field(False, description="ผู้ขายกดยืนยันน้ำหนักแล้วหรือไม่ (100% Gate)")
    total_settled_amount: Optional[float] = Field(None, description="ยอดเงินสุทธิรวม")
    payment_method: Optional[str] = Field(None, description="ช่องทางชำระเงินที่เลือก")
    items: List[WeighingSheetItem] = Field(default_factory=list, description="รายการสิ่งของทั้งหมด")


class WeighingResultResponse(BaseModel):
    """ผลการบันทึกการชั่งน้ำหนักหน้างาน (S4 -> S5 หรือ S6)"""
    status: str = Field("success", description="สถานะการบันทึก")
    order_id: str = Field(..., description="รหัสคำขอขาย")
    new_status: str = Field(..., description="สถานะใหม่ (S5 หากต่างเกิน 15% หรือ S4/S5 รอผู้ขายยืนยัน)")
    is_re_quote: bool = Field(False, description="ส่วนต่างน้ำหนักเกิน ±15% หรือไม่ (MD-STM-04)")
    total_settled_amount: float = Field(..., ge=0, description="ยอดเงินสุทธิรวมหลังคำนวณด้วยราคาล็อก")
    scale_photo_url: str = Field(..., description="URL ภาพถ่ายหน้าตาชั่ง")
    seller_confirmed_weight: bool = Field(False, description="สถานะการยืนยันของผู้ขาย")


class SelectPaymentMethodRequest(BaseModel):
    """คำขอเลือกช่องทางการชำระเงินหน้างาน (D-B06-04)"""
    saleng_id: str = Field(..., min_length=1, description="รหัสซาเล้งผู้จ่ายเงิน")
    payment_method: str = Field(..., description="ช่องทางชำระเงิน (CASH หรือ PROMPTPAY)")


class PaymentMethodSelectionResponse(BaseModel):
    """ผลการเลือกช่องทางการชำระเงิน"""
    status: str = Field("success", description="สถานะการเลือก")
    order_id: str = Field(..., description="รหัสคำขอขาย")
    payment_method: str = Field(..., description="ช่องทางชำระเงินที่บันทึก")
    order_status: str = Field(..., description="สถานะคำขอขาย (S6)")


class DigitalReceiptItem(BaseModel):
    """รายการสิ่งของบนใบเสร็จดิจิทัล (SC-03, REQ-FN-005)"""
    category_name: str = Field(..., description="ชื่อหมวดหมู่วัสดุ")
    actual_quantity: float = Field(..., description="น้ำหนักชั่งจริง")
    unit: str = Field("กก.", description="หน่วยนับ")
    locked_unit_price: float = Field(..., description="ราคาต่อหน่วยที่ล็อกไว้ (บาท)")
    settled_item_price: float = Field(..., description="ยอดเงินรวมของรายการ (บาท)")


class DigitalReceiptSummaryResponse(BaseModel):
    """ใบเสร็จสรุปรายการดิจิทัลเมื่อจบงาน (S7) พร้อม Mask เบอร์โทรศัพท์ (REQ-SEC-002, CC-06)"""
    receipt_id: str = Field(..., description="รหัสอ้างอิงใบเสร็จไม่ซ้ำ (เช่น REC-YYYYMMDD-XXXX)")
    order_id: str = Field(..., description="รหัสคำขอขายที่เกี่ยวข้อง")
    issued_at: str = Field(..., description="วันที่และเวลาที่ออกใบเสร็จ (ISO 8601 UTC)")
    seller_name: str = Field(..., description="ชื่อผู้ขาย")
    seller_phone_masked: str = Field(..., description="เบอร์โทรศัพท์ผู้ขายที่ Mask แล้ว (08X-XXX-XXXX)")
    collector_name: str = Field(..., description="ชื่อซาเล้ง")
    collector_phone_masked: str = Field(..., description="เบอร์โทรศัพท์ซาเล้งที่ Mask แล้ว (08X-XXX-XXXX)")
    payment_method: str = Field(..., description="ช่องทางชำระเงิน (CASH หรือ PROMPTPAY)")
    total_settled_amount: float = Field(..., ge=0, description="ยอดเงินสุทธิรวมทั้งสิ้น (บาท)")
    items: List[DigitalReceiptItem] = Field(default_factory=list, description="รายการของเก่าที่ซื้อขายทั้งหมด")

