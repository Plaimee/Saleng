"""
Communication Service for In-App Direct Chat and Quick Call
รองรับ UC-08, REQ-UX-001, REQ-SEC-001, REQ-SEC-002, CC-01, CC-04, CC-06, D-B05-01..06
"""

from typing import Optional
from backend.app.models.communication_models import (
    ChatMessage,
    SendChatMessageRequest,
    ChatMessageResponse,
    SellerContactInfo,
    ChatRoomResponse,
    LogCallRequest,
    LogCallResponse,
    QuickRepliesResponse,
    DEFAULT_QUICK_REPLIES,
)
from backend.app.core.supabase import supabase_store


class CommunicationService:
    """Service จัดการการสื่อสาร ข้อความแชต และโทรด่วน พร้อมบังคับใช้นโยบาย PDPA และ Read-Only"""

    @classmethod
    def get_chat_room(cls, order_id: str, saleng_id: str) -> ChatRoomResponse:
        """
        ดึงข้อมูลห้องแชต ประวัติข้อความ และสถานะสิทธิ์ตามวงจรชีวิตคำขอ (D-B05-01, D-B05-05)
        """
        # 1. ตรวจสอบ KYC (D-00-01)
        collector = supabase_store.saleng_profiles.get(saleng_id)
        if not collector:
            raise KeyError(f"ไม่พบโปรไฟล์ซาเล้งรหัส {saleng_id}")
        if not collector.get("verified") or collector.get("kyc_status") != "VERIFIED":
            raise PermissionError("ต้องผ่านการยืนยันตัวตน KYC ก่อนจึงจะเข้าใช้งานห้องแชตได้")

        # 2. ตรวจสอบคำขอขาย
        order = supabase_store.orders.get(order_id)
        if not order:
            raise KeyError(f"ไม่พบคำขอขายรหัส {order_id}")

        status = order.get("status", "S2")
        seller_id = order.get("seller_id", "seller-01")
        seller = supabase_store.sellers.get(seller_id) or {}
        display_name = seller.get("display_name", "คุณวิภาดา")

        loc_id = order.get("location_id")
        location = supabase_store.get_pickup_location(loc_id) if loc_id else None
        subdistrict = location.get("subdistrict", "แขวงสามเสนนอก") if location else "แขวงสามเสนนอก"

        # 3. ตรวจสอบเงื่อนไข PDPA และ Read-Only ตามสถานะคำขอ
        if status == "S2":
            # ใน S2: Mask เบอร์โทรศัพท์ และปิดใช้งานปุ่มโทรด่วน (D-B05-01, REQ-SEC-002)
            seller_info = SellerContactInfo(
                seller_id=seller_id,
                display_name=display_name,
                phone=None,
                phone_masked=True,
                subdistrict=subdistrict,
            )
            is_read_only = False
            read_only_reason = None
        elif status in ("S3", "S4", "S5", "S6"):
            # ใน S3..S6: เปิดเผยเบอร์โทรศัพท์จริง และเปิดใช้งานปุ่มโทรด่วน
            real_phone = seller.get("phone", "081-234-5678")
            seller_info = SellerContactInfo(
                seller_id=seller_id,
                display_name=display_name,
                phone=real_phone,
                phone_masked=False,
                subdistrict=subdistrict,
            )
            is_read_only = False
            read_only_reason = None
        else:
            # ใน S7 (Completed) หรือ S8 (Cancelled): ล็อก Read-only และซ่อนเบอร์โทรศัพท์ (D-B05-05)
            seller_info = SellerContactInfo(
                seller_id=seller_id,
                display_name=display_name,
                phone=None,
                phone_masked=True,
                subdistrict=subdistrict,
            )
            is_read_only = True
            read_only_reason = "การทำธุรกรรมเสร็จสิ้นแล้ว ห้องแชตถูกปิดเพื่อความปลอดภัยของข้อมูลส่วนบุคคลตามกฎหมาย PDPA"

        # 4. ดึงประวัติข้อความ
        raw_msgs = supabase_store.get_order_chat_messages(order_id)
        messages = [ChatMessage(**m) for m in raw_msgs]

        return ChatRoomResponse(
            order_id=order_id,
            order_status=status,
            is_read_only=is_read_only,
            read_only_reason=read_only_reason,
            seller_info=seller_info,
            messages=messages,
        )

    @classmethod
    def send_message(cls, order_id: str, req: SendChatMessageRequest) -> ChatMessageResponse:
        """
        ส่งข้อความแชตใหม่ (ข้อความอิสระ หรือ Quick Reply)
        (AC-B05-01, AC-B05-02, D-B05-04, D-B05-05)
        """
        saleng_id = req.saleng_id

        # 1. ตรวจสอบ KYC (D-00-01)
        collector = supabase_store.saleng_profiles.get(saleng_id)
        if not collector:
            raise KeyError(f"ไม่พบโปรไฟล์ซาเล้งรหัส {saleng_id}")
        if not collector.get("verified") or collector.get("kyc_status") != "VERIFIED":
            raise PermissionError("ต้องผ่านการยืนยันตัวตน KYC ก่อนจึงจะส่งข้อความได้")

        # 2. ตรวจสอบคำขอขายและสถานะ Read-only
        order = supabase_store.orders.get(order_id)
        if not order:
            raise KeyError(f"ไม่พบคำขอขายรหัส {order_id}")

        status = order.get("status")
        if status in ("S7", "S8"):
            raise PermissionError("ห้องแชตถูกปิดเนื่องจากการทำธุรกรรมเสร็จสิ้นแล้วตามนโยบาย PDPA (Read-only)")

        # 3. ตรวจสอบข้อความ
        text = req.message_text.strip()
        if not text:
            raise ValueError("ข้อความแชตต้องไม่เป็นค่าว่าง")
        if len(text) > 500:
            raise ValueError("ข้อความต้องมีความยาวไม่เกิน 500 ตัวอักษร")

        # 4. บันทึกข้อความลง Store
        saved = supabase_store.send_chat_message(
            order_id=order_id,
            sender_id=saleng_id,
            sender_role="COLLECTOR",
            message_text=text,
            is_quick_reply=req.is_quick_reply,
        )

        # 5. บันทึก Audit Log (REQ-SEC-001)
        supabase_store.record_audit_log(
            action="COLLECTOR_SENT_MESSAGE",
            actor_id=saleng_id,
            actor_role="COLLECTOR",
            entity_id=order_id,
            details={
                "message_id": saved["message_id"],
                "is_quick_reply": req.is_quick_reply,
            },
        )

        return ChatMessageResponse(status="success", message=ChatMessage(**saved))

    @classmethod
    def log_call(cls, order_id: str, req: LogCallRequest) -> LogCallResponse:
        """
        บันทึก Audit Log การกดโทรด่วนหาผู้ขาย (AC-B05-03, REQ-SEC-001, D-B05-02)
        """
        saleng_id = req.saleng_id

        # 1. ตรวจสอบ KYC (D-00-01)
        collector = supabase_store.saleng_profiles.get(saleng_id)
        if not collector:
            raise KeyError(f"ไม่พบโปรไฟล์ซาเล้งรหัส {saleng_id}")
        if not collector.get("verified") or collector.get("kyc_status") != "VERIFIED":
            raise PermissionError("ต้องผ่านการยืนยันตัวตน KYC ก่อนจึงจะโทรออกได้")

        # 2. ตรวจสอบคำขอขายและสถานะ
        order = supabase_store.orders.get(order_id)
        if not order:
            raise KeyError(f"ไม่พบคำขอขายรหัส {order_id}")

        status = order.get("status")
        if status == "S2":
            raise PermissionError("ยังไม่ได้รับงาน ไม่สามารถโทรหาผู้ขายได้ตามนโยบายคุ้มครองข้อมูลส่วนบุคคล")
        if status in ("S7", "S8"):
            raise PermissionError("ธุรกรรมเสร็จสิ้นแล้ว ไม่สามารถโทรหาผู้ขายได้ตามนโยบาย PDPA")

        # 3. บันทึก Audit Log
        supabase_store.record_audit_log(
            action="COLLECTOR_INITIATED_CALL",
            actor_id=saleng_id,
            actor_role="COLLECTOR",
            entity_id=order_id,
            details={"dialed_phone": req.dialed_phone},
        )

        return LogCallResponse(
            status="logged",
            action="COLLECTOR_INITIATED_CALL",
            order_id=order_id,
            saleng_id=saleng_id,
        )

    @classmethod
    def get_quick_replies(cls) -> QuickRepliesResponse:
        """
        ดึงชุดข้อความด่วนสำเร็จรูป 4 ข้อความมาตรฐาน (AC-B05-02, D-B05-03)
        """
        return QuickRepliesResponse(quick_replies=DEFAULT_QUICK_REPLIES)

