"""
Data Models and Schemas for Buyer Communication System (In-App Chat & Quick Call)
รองรับ UC-08, REQ-UX-001, REQ-SEC-001, REQ-SEC-002, CC-01, CC-04, CC-06, D-B05-01..06
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """โมเดลตัวแทนข้อความแชต 1 ข้อความ (D-B05-04)"""
    message_id: str = Field(..., description="รหัสข้อความ (Unique Identifier)")
    order_id: str = Field(..., description="รหัสคำขอขายที่เกี่ยวข้อง")
    sender_id: str = Field(..., description="รหัสผู้ส่ง (saleng-xx หรือ seller-xx)")
    sender_role: str = Field(..., description="บทบาทผู้ส่ง (COLLECTOR หรือ SELLER)")
    message_text: str = Field(..., min_length=1, max_length=500, description="ข้อความที่ส่ง (สูงสุด 500 ตัวอักษร)")
    is_quick_reply: bool = Field(False, description="ส่งจากแถบข้อความด่วนหรือไม่")
    sent_at: str = Field(..., description="เวลาที่ส่งข้อความ (ISO 8601 UTC)")


class SendChatMessageRequest(BaseModel):
    """คำขอส่งข้อความแชตใหม่"""
    saleng_id: str = Field(..., min_length=1, description="รหัสซาเล้งผู้ส่ง")
    message_text: str = Field(..., min_length=1, max_length=500, description="เนื้อหาข้อความ (1-500 ตัวอักษร)")
    is_quick_reply: bool = Field(False, description="ส่งจากแถบข้อความด่วนหรือไม่")


class ChatMessageResponse(BaseModel):
    """การตอบกลับผลการส่งข้อความ"""
    status: str = Field("success", description="สถานะการส่ง")
    message: ChatMessage = Field(..., description="ข้อมูลข้อความที่ถูกบันทึก")


class SellerContactInfo(BaseModel):
    """ข้อมูลผู้ขายสำหรับแสดงในห้องแชต (ควบคุม PDPA ตาม D-B05-01, REQ-SEC-002)"""
    seller_id: str = Field(..., description="รหัสผู้ขาย")
    display_name: str = Field(..., description="ชื่อเรียกผู้ขาย")
    phone: Optional[str] = Field(None, description="เบอร์โทรศัพท์จริง (จะ Mask ซ่อนหากอยู่ในสถานะ S2 หรือ S7/S8)")
    phone_masked: bool = Field(True, description="เบอร์โทรศัพท์ถูก Mask อยู่หรือไม่")
    subdistrict: Optional[str] = Field(None, description="ตำบล/แขวง")


class ChatRoomResponse(BaseModel):
    """ข้อมูลห้องแชตและประวัติข้อความทั้งหมด (D-B05-01, D-B05-05)"""
    order_id: str = Field(..., description="รหัสคำขอขาย")
    order_status: str = Field(..., description="สถานะคำขอขายปัจจุบัน (S2..S8)")
    is_read_only: bool = Field(False, description="ห้องแชตล็อกเป็น Read-Only หรือไม่")
    read_only_reason: Optional[str] = Field(None, description="เหตุผลที่ห้องแชตถูกล็อก")
    seller_info: SellerContactInfo = Field(..., description="ข้อมูลติดต่อของผู้ขาย")
    messages: List[ChatMessage] = Field(default_factory=list, description="รายการข้อความทั้งหมด")


class LogCallRequest(BaseModel):
    """คำขอบันทึกประวัติการกดโทรด่วน (REQ-SEC-001, D-B05-02)"""
    saleng_id: str = Field(..., min_length=1, description="รหัสซาเล้งที่กดโทร")
    dialed_phone: str = Field(..., min_length=9, max_length=15, description="หมายเลขโทรศัพท์ที่โทรออก")


class LogCallResponse(BaseModel):
    """ผลการบันทึกประวัติการโทร"""
    status: str = Field("logged", description="สถานะการบันทึก")
    action: str = Field("COLLECTOR_INITIATED_CALL", description="ชื่อ Action ที่บันทึก")
    order_id: str = Field(..., description="รหัสคำขอขาย")
    saleng_id: str = Field(..., description="รหัสซาเล้ง")


class QuickReplyItem(BaseModel):
    """รายการข้อความด่วนสำเร็จรูป 1 ข้อความ (D-B05-03)"""
    id: str = Field(..., description="รหัสข้อความด่วน เช่น qr-01")
    text: str = Field(..., description="เนื้อหาข้อความภาษาไทย")
    emoji: str = Field(..., description="ไอคอน Emoji ประจำข้อความ")


class QuickRepliesResponse(BaseModel):
    """ชุดข้อความด่วนมาตรฐาน 4 ข้อความ (D-B05-03)"""
    quick_replies: List[QuickReplyItem] = Field(default_factory=list, description="รายการข้อความด่วน")


DEFAULT_QUICK_REPLIES: List[QuickReplyItem] = [
    QuickReplyItem(id="qr-01", text="กำลังเดินทางไปครับ", emoji="🚚"),
    QuickReplyItem(id="qr-02", text="ถึงหน้าบ้านแล้วครับ", emoji="📍"),
    QuickReplyItem(id="qr-03", text="ช่วยออกมารับหน่อยครับ", emoji="🚪"),
    QuickReplyItem(id="qr-04", text="ขอเลื่อนเวลาประมาณ 15 นาทีครับ", emoji="⏰"),
]

