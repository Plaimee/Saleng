"""
Data Models for Payment & Verification Feature
รองรับ MD-DOM-04, REQ-FN-004, REQ-FN-005, REQ-FN-006, REQ-BR-002, REQ-SEC-001, REQ-SEC-002, AC-S06-01..05
"""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator


class ActualWeightItemInput(BaseModel):
    """
    ค่าน้ำหนักชั่งจริงหน้างานของแต่ละรายการ
    รองรับ REQ-FN-004, REQ-BR-002
    """
    item_id: str = Field(..., description="รหัสรายการของเก่า")
    actual_quantity: float = Field(..., description="น้ำหนักชั่งจริง (กก.) หรือจำนวนกระสอบ")

    @field_validator("actual_quantity")
    @classmethod
    def validate_positive_quantity(cls, v):
        if v <= 0:
            raise ValueError("ค่าน้ำหนักจริงต้องมากกว่า 0")
        return v


class RecordWeighingRequest(BaseModel):
    """
    คำขอบันทึกผลชั่งจริงหน้างาน (โดยซาเล้ง)
    รองรับ REQ-FN-004, REQ-BR-002
    """
    scale_photo_url: str = Field(..., description="URL ภาพถ่ายหน้าตาชั่งดิจิทัล")
    items: List[ActualWeightItemInput] = Field(..., min_length=1, description="รายการผลชั่งจริง")


class SettledItemOutput(BaseModel):
    """
    รายการของเก่าพร้อมน้ำหนักจริงและยอดคำนวณสุทธิ
    """
    item_id: str
    category_code: str
    category_name: str
    unit: Literal["kg", "bag"]
    est_quantity: float
    actual_quantity: float
    locked_unit_price: float
    settled_item_price: float


class WeighingRecordResponse(BaseModel):
    """
    ผลลัพธ์การบันทึกผลชั่งจริง
    รองรับ S5 (Re-Quote / Weight Confirmed Gate)
    """
    order_id: str
    status: str = "S5"
    scale_photo_url: str
    items: List[SettledItemOutput]
    total_settled_amount: float
    seller_confirmed_weight: bool = False
    message: str = "บันทึกผลชั่งจริงแล้ว รอผู้ขายกดยืนยันตัวเลขน้ำหนักบนหน้าจอ"


class WeightConfirmationRequest(BaseModel):
    """
    คำขอยืนยันผลชั่งจริงโดยผู้ขาย
    รองรับ REQ-FN-004, AC-S06-01, Q-01
    """
    seller_id: str = Field(..., description="รหัสผู้ขายที่ต้องการยืนยัน")


class WeightConfirmationResponse(BaseModel):
    """
    ผลลัพธ์หลังผู้ขายกดยืนยันน้ำหนัก (S5 -> S6)
    """
    order_id: str
    status: str = "S6"
    seller_confirmed_weight_at: str
    total_settled_amount: float
    message: str = "ผู้ขายยืนยันตัวเลขน้ำหนักเรียบร้อยแล้ว พร้อมสำหรับการชำระเงิน"


class RequestReweighRequest(BaseModel):
    """
    คำขอให้ซาเล้งชั่งน้ำหนักซ้ำ
    รองรับ AC-S06-02, Q-02
    """
    seller_id: str
    reason: Optional[str] = "ผู้ขายขอให้ตรวจสอบและชั่งน้ำหนักซ้ำ"


class RequestReweighResponse(BaseModel):
    """
    ผลลัพธ์การขอชั่งซ้ำ
    """
    order_id: str
    status: str = "S4"
    message: str = "ส่งคำขอชั่งซ้ำแล้ว ซาเล้งจะทำการตรวจสอบและชั่งน้ำหนักใหม่"


class DisputeRequest(BaseModel):
    """
    คำขอปฏิเสธผลชั่งและแจ้งข้อพิพาท
    รองรับ REQ-FN-006, AC-S06-02, Q-02
    """
    seller_id: str
    dispute_reason: str = Field(..., min_length=5, description="เหตุผลในการปฏิเสธผลชั่งหรือแจ้งข้อพิพาท")


class DisputeResponse(BaseModel):
    """
    ผลลัพธ์การส่งข้อพิพาท (S8: Disputed)
    """
    order_id: str
    status: str = "S8"
    dispute_reason: str
    disputed_at: str
    message: str = "ส่งข้อพิพาทเรียบร้อยแล้ว ระบบล็อกข้อมูลและส่งต่อให้ผู้ดูแลระบบตรวจสอบ"


class PaymentConfirmationRequest(BaseModel):
    """
    คำขอยืนยันการรับเงินโดยผู้ขาย
    รองรับ UC-07, AC-S06-03, Q-03
    """
    seller_id: str = Field(..., description="รหัสผู้ขายที่ยืนยันรับเงิน")
    payment_method: Literal["CASH", "PROMPTPAY"] = Field(..., description="ช่องทางที่ได้รับเงิน")


class PaymentConfirmationResponse(BaseModel):
    """
    ผลลัพธ์หลังผู้ขายยืนยันรับเงิน (S6 -> S7)
    """
    order_id: str
    status: str = "S7"
    payment_method: str
    payment_confirmed_at: str
    receipt_id: str
    receipt_no: str
    total_amount: float
    message: str = "ยืนยันรับเงินสำเร็จ ปิดงานและสร้างใบเสร็จดิจิทัลเรียบร้อย"


class DigitalReceiptItem(BaseModel):
    category_code: str
    category_name: str
    unit: str
    actual_quantity: float
    locked_unit_price: float
    settled_item_price: float


class DigitalReceiptResponse(BaseModel):
    """
    ใบเสร็จดิจิทัลสรุปรายการซื้อขาย
    รองรับ REQ-FN-005, REQ-SEC-002, SC-03, AC-S06-04, Q-04
    """
    receipt_id: str
    receipt_no: str
    order_id: str
    seller_id: str
    buyer_id: str
    seller_phone_masked: str  # 08X-XXX-XXXX
    buyer_phone_masked: str   # 08X-XXX-XXXX
    total_amount: float
    payment_method: Literal["CASH", "PROMPTPAY"]
    items: List[DigitalReceiptItem]
    issued_at: str

