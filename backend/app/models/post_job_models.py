"""
Data Models and Schemas for Buyer Post-Job Management System (ระบบหลังจบงานซาเล้ง)
รองรับ UC-10, UC-13, REQ-FN-005, REQ-FN-006, REQ-SEC-001, REQ-SEC-002, CC-01, CC-04, CC-06, D-B07-01..06
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class PurchaseHistorySummary(BaseModel):
    """สรุปสถิติสะสมการรับซื้อของเก่า 3 มิติ (D-B07-05)"""
    total_expense_baht: float = Field(..., ge=0, description="รายจ่ายค่าซื้อของเก่ารวม (บาท)")
    total_weight_kg: float = Field(..., ge=0, description="น้ำหนักวัสดุรับซื้อรวม (กก.)")
    total_completed_jobs: int = Field(..., ge=0, description="จำนวนงานที่รับซื้อสำเร็จ (ครั้ง)")


class PurchaseHistoryItem(BaseModel):
    """รายการประวัติคำขอขายที่รับซื้อสำเร็จแล้ว (S7: Completed)"""
    order_id: str = Field(..., description="รหัสคำขอขาย")
    completed_at: str = Field(..., description="วันที่และเวลาที่ทำรายการสำเร็จ (ISO 8601)")
    seller_name: str = Field(..., description="ชื่อผู้ขาย")
    seller_phone_masked: str = Field(..., description="เบอร์โทรศัพท์ผู้ขายที่ Mask แล้ว (08X-XXX-XXXX)")
    total_settled_amount: float = Field(..., ge=0, description="ยอดเงินสุทธิที่จ่าย (บาท)")
    total_weight_kg: float = Field(..., ge=0, description="น้ำหนักรวมที่รับซื้อ (กก.)")
    payment_method: str = Field(..., description="ช่องทางชำระเงิน (CASH หรือ PROMPTPAY)")
    status: str = Field("S7", description="สถานะคำขอ (S7)")
    is_regular_customer: bool = Field(False, description="ผู้ขายนี้อยู่ในรายการลูกค้าประจำหรือไม่")
    items_summary: str = Field("", description="สรุปรายการของเก่า เช่น กระดาษลัง (50 กก.)")
    receipt_id: Optional[str] = Field(None, description="รหัสอ้างอิงใบเสร็จดิจิทัล")


class PurchaseHistoryResponse(BaseModel):
    """ผลลัพธ์หน้ารวมประวัติการรับซื้อของเก่าพร้อมสถิติสะสม"""
    period: str = Field("all", description="ช่วงเวลาตัวกรอง (all, today, month)")
    summary: PurchaseHistorySummary = Field(..., description="สถิติสรุปสะสม")
    items: List[PurchaseHistoryItem] = Field(default_factory=list, description="รายการคำขอย้อนหลัง")


class RegularCustomerItem(BaseModel):
    """ข้อมูลลูกค้าประจำที่ซาเล้งปักหมุดไว้ (Regular Customer Bookmark)"""
    id: str = Field(..., description="รหัสอ้างอิงรายการบันทึก")
    collector_id: str = Field(..., description="รหัสซาเล้งผู้บันทึก")
    seller_id: str = Field(..., description="รหัสผู้ขายลูกค้าประจำ")
    seller_name: str = Field(..., description="ชื่อผู้ขาย / ป้ายกำกับ")
    seller_phone_masked: str = Field(..., description="เบอร์โทรศัพท์ที่ Mask แล้ว (08X-XXX-XXXX)")
    latitude: float = Field(..., description="ละติจูดจุดรับซื้อเพื่อการวางแผนเส้นทาง")
    longitude: float = Field(..., description="ลองจิจูดจุดรับซื้อเพื่อการวางแผนเส้นทาง")
    notes: Optional[str] = Field(None, max_length=200, description="บันทึกย่อส่วนตัวของซาเล้ง (ไม่เกิน 200 ตัวอักษร)")
    created_at: str = Field(..., description="วันที่บันทึก (ISO 8601)")
    updated_at: Optional[str] = Field(None, description="วันที่แก้ไขบันทึกย่อล่าสุด")


class ToggleRegularCustomerRequest(BaseModel):
    """คำขอปักหมุด/ยกเลิกผู้ขายเป็นลูกค้าประจำ (Toggle Bookmark)"""
    saleng_id: str = Field(..., min_length=1, description="รหัสซาเล้งผู้บันทึก")
    seller_id: str = Field(..., min_length=1, description="รหัสผู้ขาย")
    notes: Optional[str] = Field(None, max_length=200, description="บันทึกย่อช่วยจำ (ไม่เกิน 200 ตัวอักษร)")
    latitude: Optional[float] = Field(None, description="ละติจูดจุดรับซื้อ")
    longitude: Optional[float] = Field(None, description="ลองจิจูดจุดรับซื้อ")
    seller_name: Optional[str] = Field(None, description="ชื่อผู้ขาย / ป้ายกำกับ")
    seller_phone_masked: Optional[str] = Field(None, description="เบอร์โทรศัพท์ Mask")


class ToggleRegularCustomerResponse(BaseModel):
    """ผลการสลับสถานะลูกค้าประจำ"""
    status: str = Field("success", description="สถานะการดำเนินการ")
    seller_id: str = Field(..., description="รหัสผู้ขาย")
    is_favorite: bool = Field(..., description="สถานะการปักหมุดปัจจุบัน (True = เป็นลูกค้าประจำ, False = ยกเลิกแล้ว)")
    message: str = Field(..., description="ข้อความแจ้งเตือนผลลัพธ์")


class ReportSellerMismatchRequest(BaseModel):
    """คำขอรายงานข้อพิพาทหน้างาน (Seller Mismatch & No-Show Report)"""
    saleng_id: str = Field(..., min_length=1, description="รหัสซาเล้งผู้รายงาน")
    order_id: str = Field(..., min_length=1, description="รหัสคำขอขายที่พบปัญหา")
    mismatch_reason: str = Field(..., description="สาเหตุ: SELLER_NO_SHOW, CONTAMINATED_WASTE, QUANTITY_MISMATCH, OTHER")
    evidence_photo_url: str = Field(..., min_length=5, description="URL รูปถ่ายหลักฐานหน้างาน (บังคับตาม REQ-FN-006)")
    notes: Optional[str] = Field(None, description="คำอธิบายรายละเอียดเหตุการณ์")
    current_lat: Optional[float] = Field(None, description="ละติจูดพิกัด GPS ขณะกดรายงาน")
    current_lng: Optional[float] = Field(None, description="ลองจิจูดพิกัด GPS ขณะกดรายงาน")


class ReportSellerMismatchResponse(BaseModel):
    """ผลลัพธ์การรายงานข้อพิพาทหน้างาน (S3/S4 -> S8)"""
    status: str = Field("success", description="สถานะการรายงาน")
    order_id: str = Field(..., description="รหัสคำขอขาย")
    new_status: str = Field("S8", description="สถานะใหม่ของคำขอขาย (S8: Disputed)")
    dispute_id: str = Field(..., description="รหัสข้อพิพาท DISP-YYYYMMDD-XXXX")
    message: str = Field(..., description="ข้อความแจ้งเตือนผลลัพธ์")

