"""
Service Layer สำหรับระบบแจ้งเตือนและการช่วยเหลือ (Notification & Help Center Service)
รองรับ UC-08, UC-13, REQ-OP-001, REQ-SEC-001, REQ-SEC-002, CC-05, AC-S08-01..05, P-01..P-05
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from fastapi import HTTPException, status
from backend.app.core.supabase import supabase_store
from backend.app.services.payment_service import mask_phone


# -----------------------------------------------------------------------------
# 1. ข้อมูลคู่มือแนะนำการคัดแยกขยะ 4 หมวดหลัก (AC-S08-02, P-02, Q-02)
# -----------------------------------------------------------------------------
DEFAULT_SORTING_GUIDES = [
    {
        "category_code": "MAT-CARDBOARD",
        "category_name": "กระดาษลัง / กล่องลูกฟูก",
        "icon": "📦",
        "value_add_tips": [
            "แกะเทปกาว เชือก และลวดเย็บกระดาษออกให้หมด",
            "คลี่กล่องออกและพับให้แบนเป็นระเบียบ",
            "มัดรวมเป็นตั้งด้วยเชือกเพื่อสะดวกต่อการชั่งน้ำหนัก",
        ],
        "price_impact_description": "กระดาษลังที่พับแบนและแห้งสนิท จะได้ราคาสูงสุดตามเกณฑ์ราคากลาง (3–4 บาท/กก.) โดยไม่ถูกหักค่าน้ำหนักสิ่งเจือปน",
        "precautions": [
            "ห้ามเปียกน้ำหรือมีความชื้นเด็ดขาด",
            "ห้ามปนเปื้อนคราบน้ำมัน อาหาร หรือสารเคมี",
        ],
    },
    {
        "category_code": "MAT-WHITE-PAPER",
        "category_name": "กระดาษขาวดำ (A4 / เอกสารสำนักงาน)",
        "icon": "📄",
        "value_add_tips": [
            "แยกกระดาษขาวล้วนออกจากกระดาษสี กระดาษหนังสือพิมพ์ และกระดาษคาร์บอน",
            "แกะคลิปหนีบกระดาษ ลวดเย็บ และสันห่วงพลาสติกออก",
            "จัดเรียงซ้อนกันเป็นระเบียบหรือมัดรวม",
        ],
        "price_impact_description": "การแยกกระดาษขาวดำล้วนจะช่วยเพิ่มมูลค่าขายได้ถึง 6–7 บาท/กก. (สูงกว่ากระดาษลังเกือบเท่าตัว)",
        "precautions": [
            "ไม่ปนเปื้อนกระดาษเคลือบพลาสติกหรือกระดาษความร้อน (สลิปใบเสร็จ)",
        ],
    },
    {
        "category_code": "MAT-GLASS-BOTTLE",
        "category_name": "ขวดแก้ว (ใส / ชา / เขียว)",
        "icon": "🍾",
        "value_add_tips": [
            "เทของเหลวและสิ่งตกค้างออกให้หมด ล้างน้ำและคว่ำให้แห้ง",
            "แยกสีของขวดแก้ว: ขวดใส (เหล้าขาว/น้ำปลา), ขวดสีชา (เบียร์/เครื่องดื่มชูกำลัง), ขวดสีเขียว",
            "แกะฝาอะลูมิเนียมหรือฝาพลาสติกออกแยกชั่งต่างหาก",
        ],
        "price_impact_description": "ขวดแก้วที่สมบูรณ์แยกสีชัดเจนและบรรจุใส่กระสอบจะคิดราคาได้ 45–50 บาท/กระสอบ หรือ 1–2 บาท/กก.",
        "precautions": [
            "ระวังขวดแตก ห้ามปนเศษแก้วแตกคละสีลงในกระสอบ",
            "ไม่รับหลอดไฟ กระจกเงา หรือแก้วทนความร้อน (Pyrex)",
        ],
    },
    {
        "category_code": "MAT-PLASTIC-PET",
        "category_name": "ขวดพลาสติกใส (PET)",
        "icon": "🧴",
        "value_add_tips": [
            "เทน้ำหรือเครื่องดื่มออกให้หมด บ้วนน้ำสะอาด 1 ครั้ง",
            "ลอกฉลากพลาสติกและแกะฝาเกลียวออก",
            "บีบหรือเหยียบขวดให้แบนเพื่อประหยัดพื้นที่จัดเก็บและขนส่ง",
        ],
        "price_impact_description": "ขวด PET ใสสะอาดที่บีบแบนแล้ว เป็นที่ต้องการสูงสุดของโรงงานรีไซเคิลและรับซื้อในราคาเต็มเกณฑ์",
        "precautions": [
            "ไม่ปนเปื้อนน้ำมันเครื่อง สารกำจัดศัตรูพืช หรือของเหลวอันตราย",
        ],
    },
]


# -----------------------------------------------------------------------------
# 2. ข้อมูลคำถามที่พบบ่อย (FAQ) 3 หมวดหมู่ (AC-S08-03, P-03, Q-03)
# -----------------------------------------------------------------------------
DEFAULT_FAQS = [
    {
        "category_id": "MINIMUM_AND_BOOKING",
        "category_name": "เงื่อนไขขั้นต่ำและการนัดหมาย",
        "faqs": [
            {
                "id": "FAQ-01",
                "question": "เกณฑ์ขั้นต่ำในการเรียกรถซาเล้งคือเท่าใด?",
                "answer": "ยอดประเมินรวมต้องไม่ต่ำกว่า 500 บาท หรือมีของเก่าบรรจุถุง/กระสอบมาตรฐานอย่างน้อย 2 กระสอบ เพื่อให้คุ้มค่าการเดินทางของซาเล้ง (BR-02)",
                "category": "MINIMUM_AND_BOOKING",
            },
            {
                "id": "FAQ-02",
                "question": "หากของเก่าไม่ถึง 500 บาท สามารถขายได้หรือไม่?",
                "answer": "สามารถเลือกใช้ฟังก์ชัน 'ฝากรวมจุดรับทางผ่าน' (Aggregated Route) โดยระบบจะจับคู่กับซาเล้งที่มีเส้นทางวิ่งผ่านหน้าบ้านของคุณในวันนั้น",
                "category": "MINIMUM_AND_BOOKING",
            },
            {
                "id": "FAQ-03",
                "question": "นัดหมายแล้วซาเล้งจะมาถึงภายในกี่นาที?",
                "answer": "เมื่อซาเล้งกดรับงาน คุณสามารถติดตามสถานะการเดินทาง (ETA) ได้แบบเรียลไทม์ และระบบมีระบบแจ้งเตือนเมื่อซาเล้งใกล้ถึงหน้าบ้าน",
                "category": "MINIMUM_AND_BOOKING",
            },
        ],
    },
    {
        "category_id": "WEIGHING_AND_PRICING",
        "category_name": "การชั่งน้ำหนักและราคากลาง",
        "faqs": [
            {
                "id": "FAQ-04",
                "question": "ราคากลางที่เห็นในแอปจะเปลี่ยนแปลงหรือไม่ตอนชั่งของจริง?",
                "answer": "ไม่เปลี่ยนแปลงครับ ระบบมีนโยบาย Price Snapshot (REQ-BR-002) ล็อกราคากลาง ณ เวลาที่ยืนยันนัดหมายไว้ใช้คิดเงินเสมอ แม้ราคากลางประจำวันจะปรับขึ้นลง",
                "category": "WEIGHING_AND_PRICING",
            },
            {
                "id": "FAQ-05",
                "question": "ทำไมต้องถ่ายรูปหน้าตาชั่งดิจิทัลตอนชั่งของหน้างาน?",
                "answer": "เพื่อความโปร่งใสสูงสุด ซาเล้งต้องถ่ายรูปหน้าตาชั่งส่งเข้าแอปให้ผู้ขายตรวจดูตัวเลขจริงบนหน้าจอของตนเองก่อนสรุปยอดเงิน (REQ-FN-002, REQ-FN-004)",
                "category": "WEIGHING_AND_PRICING",
            },
            {
                "id": "FAQ-06",
                "question": "หากไม่เห็นด้วยกับผลชั่งจริงสามารถทำอย่างไรได้บ้าง?",
                "answer": "ผู้ขายสามารถกดปุ่ม 'ขอให้ชั่งซ้ำ' เพื่อให้ซาเล้งตรวจสอบตาชั่งใหม่ หรือกด 'ปฏิเสธผลชั่ง / แจ้งข้อพิพาท' เพื่อส่งเรื่องให้แอดมินตรวจสอบทันที (REQ-FN-006)",
                "category": "WEIGHING_AND_PRICING",
            },
        ],
    },
    {
        "category_id": "PAYMENT_AND_RECEIPT",
        "category_name": "การชำระเงินและใบเสร็จดิจิทัล",
        "faqs": [
            {
                "id": "FAQ-07",
                "question": "สามารถรับเงินผ่านช่องทางใดได้บ้าง?",
                "answer": "รองรับ 2 ช่องทาง: 1. รับเงินสดหน้างานจากซาเล้ง 2. แสดง QR Code PromptPay ให้ซาเล้งสแกนโอนเงินเข้าบัญชีของคุณโดยตรง",
                "category": "PAYMENT_AND_RECEIPT",
            },
            {
                "id": "FAQ-08",
                "question": "ใบเสร็จดิจิทัลสามารถเปิดดูย้อนหลังได้หรือไม่?",
                "answer": "เปิดดูได้ตลอดเวลาจากเมนู 'ประวัติการขาย' พร้อมดาวน์โหลดเป็นรูปภาพ และสามารถเปิดดูใบเสร็จที่เคยบันทึกไว้ได้แม้ไม่มีสัญญาณอินเทอร์เน็ต (REQ-FN-005, CC-05)",
                "category": "PAYMENT_AND_RECEIPT",
            },
        ],
    },
]


# -----------------------------------------------------------------------------
# 3. Notification Service (AC-S08-01, P-01)
# -----------------------------------------------------------------------------
class NotificationService:
    @staticmethod
    def get_seller_notifications(seller_id: str) -> Dict:
        """
        ดึงรายการแจ้งเตือนทั้งหมดของผู้ขาย พร้อมสร้าง Draft Reminder อัตโนมัติ (AC-S08-01, P-01, Q-01)
        """
        # ตรวจสอบคำขอค้างใน S1 > 3 วัน
        supabase_store.generate_draft_reminders_for_seller(seller_id)

        notifications = supabase_store.get_seller_notifications(seller_id)
        unread_count = sum(1 for n in notifications if not n.get("is_read", False))

        return {
            "seller_id": seller_id,
            "unread_count": unread_count,
            "notifications": notifications,
        }

    @staticmethod
    def mark_as_read(notification_id: str) -> Dict:
        """ทำเครื่องหมายแจ้งเตือนว่าอ่านแล้ว"""
        notif = supabase_store.mark_notification_as_read(notification_id)
        if not notif:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ไม่พบการแจ้งเตือนรหัส: {notification_id}"
            )
        return {
            "notification_id": notification_id,
            "is_read": True,
            "message": "ทำเครื่องหมายว่าอ่านแล้วเรียบร้อย",
        }

    @staticmethod
    def mark_all_as_read(seller_id: str) -> Dict:
        """ทำเครื่องหมายแจ้งเตือนทั้งหมดว่าอ่านแล้ว พร้อมบันทึก Audit Log (P-05)"""
        count = supabase_store.mark_all_notifications_as_read(seller_id)

        supabase_store.add_audit_log(
            action="SELLER_CLEAR_NOTIFICATIONS",
            entity_id=seller_id,
            actor_id=seller_id,
            details={"cleared_count": count}
        )

        return {
            "seller_id": seller_id,
            "cleared_count": count,
            "message": f"ทำเครื่องหมายว่าอ่านแล้วทั้งหมด {count} รายการ",
        }


# -----------------------------------------------------------------------------
# 4. Knowledge Base Service: Guides & FAQs (AC-S08-02, AC-S08-03, P-02, P-03)
# -----------------------------------------------------------------------------
class KnowledgeBaseService:
    @staticmethod
    def get_sorting_guides() -> Dict:
        """ดึงคู่มือแนะนำการคัดแยกขยะเพื่อเพิ่มมูลค่า 4 หมวดหลัก (AC-S08-02)"""
        return {"guides": DEFAULT_SORTING_GUIDES}

    @staticmethod
    def get_faqs(query: Optional[str] = None) -> Dict:
        """ดึงคำถามที่พบบ่อย 3 หมวดหมู่ พร้อมกรองคำค้นหา (AC-S08-03)"""
        if not query:
            total = sum(len(c["faqs"]) for c in DEFAULT_FAQS)
            return {"categories": DEFAULT_FAQS, "total_faqs": total}

        q = query.strip().lower()
        filtered_categories = []
        total = 0

        for cat in DEFAULT_FAQS:
            matching_faqs = [
                f for f in cat["faqs"]
                if q in f["question"].lower() or q in f["answer"].lower()
            ]
            if matching_faqs:
                filtered_categories.append({
                    "category_id": cat["category_id"],
                    "category_name": cat["category_name"],
                    "faqs": matching_faqs,
                })
                total += len(matching_faqs)

        return {"categories": filtered_categories, "total_faqs": total}


# -----------------------------------------------------------------------------
# 5. Support Ticket Service (AC-S08-04, UC-13, REQ-SEC-002, P-04, P-05)
# -----------------------------------------------------------------------------
class SupportTicketService:
    @staticmethod
    def create_ticket(
        seller_id: str,
        category: str,
        subject: str,
        description: str,
        contact_phone: str,
    ) -> Dict:
        """
        บันทึกคำร้องขอความช่วยเหลือจากผู้ขาย (AC-S08-04, P-04, Q-04)
        """
        # สร้างรหัสตั๋ว TCK-YYYYMMDD-XXXX
        today_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        rand_suffix = str(uuid.uuid4().hex[:4]).upper()
        ticket_no = f"TCK-{today_str}-{rand_suffix}"

        # ปกปิดเบอร์โทรศัพท์ (REQ-SEC-002)
        masked_phone = mask_phone(contact_phone)

        ticket_data = {
            "ticket_no": ticket_no,
            "seller_id": seller_id,
            "category": category,
            "subject": subject,
            "description": description,
            "contact_phone_masked": masked_phone,
            "status": "OPEN",
        }

        created = supabase_store.create_support_ticket(ticket_data)

        # บันทึก Audit Log (REQ-SEC-001, AC-S08-05)
        supabase_store.add_audit_log(
            action="SELLER_SUBMIT_SUPPORT_TICKET",
            entity_id=ticket_no,
            actor_id=seller_id,
            details={
                "category": category,
                "subject": subject,
                "ticket_id": created["id"],
                "contact_phone_masked": masked_phone,
            }
        )

        return created

    @staticmethod
    def get_contact_info() -> Dict:
        """ดึงข้อมูลติดต่อสายด่วน Call Center และ LINE Official"""
        return {
            "call_center_phone": "02-123-4567",
            "operating_hours": "ทุกวัน 08:00 - 18:00 น.",
            "line_official": "@saleng-help",
            "emergency_notice": "หากเกิดเหตุฉุกเฉินหรือมีข้อพิพาทหน้างาน สามารถกดปุ่มฉุกเฉินในแอปหรือโทรเข้าสายด่วนได้ทันที",
        }
