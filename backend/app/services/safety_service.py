"""
Service Layer สำหรับระบบความปลอดภัยขณะทำธุรกรรม (Transaction Safety & SOS Service)
รองรับ UC-09, UC-13, REQ-SEC-001, REQ-SEC-002, REQ-QA-001, REQ-UX-001, REQ-FN-006, AC-S09-01..05, P-01..P-05
"""

import time
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from fastapi import HTTPException, status
from backend.app.core.supabase import supabase_store
from backend.app.services.payment_service import mask_phone
from backend.app.models.safety_models import (
    EvidenceUploadRequest,
    EvidenceItemResponse,
    EvidenceListResponse,
    EmergencyContactUpdateRequest,
    EmergencyContactResponse,
    SosTriggerRequest,
    SosAlertResponse,
    LockEvidenceResponse,
)

DEFAULT_HOTLINE_PHONE = "02-123-4567"
DEFAULT_HOTLINE_NAME = "ศูนย์ช่วยเหลือและสายด่วน Saleng Hotline"


# -----------------------------------------------------------------------------
# 1. Media Evidence Service: การบันทึกเสียงและวิดีโอหลักฐานหน้างาน (AC-S09-01, P-01, Q-01)
# -----------------------------------------------------------------------------
class MediaEvidenceService:
    @staticmethod
    def upload_evidence(order_id: str, seller_id: str, payload: EvidenceUploadRequest) -> EvidenceItemResponse:
        """
        บันทึกไฟล์หลักฐานเสียงหรือคลิปวิดีโอหน้างานในสถานะ S4..S6 (AC-S09-01, P-01)
        """
        order = supabase_store.orders.get(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ไม่พบคำขอรหัส: {order_id}"
            )

        if order.get("seller_id") != seller_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="ไม่มีสิทธิ์บันทึกหลักฐานสำหรับคำขอนี้"
            )

        order_status = order.get("status")
        # อนุญาตเฉพาะสถานะหน้างาน S4 (ถึงหน้างาน), S5 (ชั่งของ), S6 (รอชำระเงิน)
        if order_status not in ["S4", "S5", "S6"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"สามารถบันทึกหลักฐานได้เฉพาะขณะซาเล้งปฏิบัติงานหน้างาน (สถานะ S4, S5, S6) สถานะปัจจุบันคือ: {order_status}"
            )

        # ตรวจสอบขนาดไฟล์ไม่เกิน 25 MB (CC-01)
        max_bytes = 25 * 1024 * 1024
        if payload.file_size_bytes > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ขนาดไฟล์หลักฐานต้องไม่เกิน 25 MB ตามข้อกำหนด CC-01"
            )

        today_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        rand_suffix = str(uuid.uuid4().hex[:4]).upper()
        evidence_id = f"EVD-{today_str}-{rand_suffix}"

        file_url = payload.file_url or f"https://storage.saleng.app/evidences/{order_id}/{evidence_id}.webm"

        evidence_data = {
            "evidence_id": evidence_id,
            "order_id": order_id,
            "seller_id": seller_id,
            "media_type": payload.media_type.upper(),
            "file_url": file_url,
            "file_size_bytes": payload.file_size_bytes,
            "duration_seconds": payload.duration_seconds,
            "is_locked": False,
        }

        created = supabase_store.add_safety_evidence(evidence_data)

        # บันทึก Audit Log (REQ-SEC-001, AC-S09-05)
        supabase_store.add_audit_log(
            action="SELLER_STOP_EVIDENCE_RECORDING",
            entity_id=evidence_id,
            actor_id=seller_id,
            details={
                "order_id": order_id,
                "media_type": payload.media_type,
                "duration_seconds": payload.duration_seconds,
                "file_size_bytes": payload.file_size_bytes,
            }
        )

        return EvidenceItemResponse(**created)

    @staticmethod
    def get_evidences(order_id: str, seller_id: str) -> EvidenceListResponse:
        """ดึงรายการหลักฐานทั้งหมดของคำขอ"""
        order = supabase_store.orders.get(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ไม่พบคำขอรหัส: {order_id}"
            )

        if order.get("seller_id") != seller_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="ไม่มีสิทธิ์ดูหลักฐานของคำขอนี้"
            )

        raw_evidences = supabase_store.get_safety_evidences_by_order(order_id)
        evidences = [EvidenceItemResponse(**e) for e in raw_evidences]

        return EvidenceListResponse(
            order_id=order_id,
            total_evidences=len(evidences),
            evidences=evidences,
        )


# -----------------------------------------------------------------------------
# 2. Emergency SOS Service: การส่งสัญญาณฉุกเฉิน SOS (AC-S09-02, P-02, Q-02)
# -----------------------------------------------------------------------------
class EmergencySosService:
    @staticmethod
    def trigger_sos(order_id: str, seller_id: str, payload: SosTriggerRequest) -> SosAlertResponse:
        """
        ส่งสัญญาณฉุกเฉิน SOS One-Tap Dispatch ไปยัง Admin ภายใน 2.0 วินาที (REQ-QA-001, AC-S09-02)
        """
        start_time = time.perf_counter()

        order = supabase_store.orders.get(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ไม่พบคำขอรหัส: {order_id}"
            )

        if order.get("seller_id") != seller_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="ไม่มีสิทธิ์ส่งสัญญาณฉุกเฉินสำหรับคำขอนี้"
            )

        order_status = order.get("status")
        # ใช้งานได้ในสถานะ S3 (เดินทางมา), S4 (ถึงหน้างาน), S5 (ชั่งของ), S6 (ชำระเงิน)
        if order_status not in ["S3", "S4", "S5", "S6"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"สามารถกดปุ่ม SOS ฉุกเฉินได้ในสถานะ S3, S4, S5, S6 เท่านั้น สถานะปัจจุบันคือ: {order_status}"
            )

        today_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        rand_suffix = str(uuid.uuid4().hex[:4]).upper()
        sos_id = f"SOS-{today_str}-{rand_suffix}"

        # รวบรวมพิกัด
        lat = payload.current_lat if payload.current_lat is not None else 13.7563
        lng = payload.current_lng if payload.current_lng is not None else 100.5018
        geo_point = {"lat": lat, "lng": lng}

        saleng_id = order.get("collector_id") or "SALENG-ASSIGNED"

        # ดึงเบอร์ผู้ติดต่อฉุกเฉินเพื่อส่งให้หน้าจอต่อสายตรง
        contact = supabase_store.get_emergency_contact(seller_id)
        if contact and contact.get("contact_phone"):
            emergency_phone = contact["contact_phone"]
            contact_name = contact.get("contact_name", "ผู้ติดต่อฉุกเฉิน")
        else:
            emergency_phone = DEFAULT_HOTLINE_PHONE
            contact_name = DEFAULT_HOTLINE_NAME

        sos_data = {
            "sos_id": sos_id,
            "order_id": order_id,
            "seller_id": seller_id,
            "saleng_id": saleng_id,
            "geo_point": geo_point,
            "status": "TRIGGERED",
        }
        created = supabase_store.create_sos_alert(sos_data)

        # ล็อกหลักฐานอัตโนมัติเพื่อป้องกันการสูญหาย (P-04, REQ-FN-006)
        supabase_store.lock_safety_evidences_for_order(order_id)

        # บันทึก Audit Log (REQ-SEC-001, AC-S09-05)
        supabase_store.add_audit_log(
            action="SELLER_TRIGGER_SOS",
            entity_id=sos_id,
            actor_id=seller_id,
            details={
                "order_id": order_id,
                "saleng_id": saleng_id,
                "geo_point": geo_point,
                "called_phone": emergency_phone,
            }
        )

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return SosAlertResponse(
            id=created["id"],
            sos_id=sos_id,
            order_id=order_id,
            seller_id=seller_id,
            saleng_id=saleng_id,
            geo_point=geo_point,
            status="TRIGGERED",
            emergency_phone_to_call=emergency_phone,
            emergency_contact_name=contact_name,
            created_at=created["created_at"],
            response_time_ms=round(elapsed_ms, 2),
            message="ระบบได้ส่งสัญญาณแจ้งเหตุฉุกเฉินและพิกัดไปยังศูนย์ดูแลระบบเรียบร้อยแล้ว",
        )


# -----------------------------------------------------------------------------
# 3. Emergency Contact Service: การจัดการเบอร์ผู้ติดต่อฉุกเฉิน (AC-S09-03, P-03, Q-03)
# -----------------------------------------------------------------------------
class EmergencyContactService:
    @staticmethod
    def get_contact(seller_id: str) -> EmergencyContactResponse:
        """ดึงข้อมูลผู้ติดต่อฉุกเฉินที่ไว้ใจได้ พร้อม PDPA Masking (AC-S09-03, REQ-SEC-002)"""
        contact = supabase_store.get_emergency_contact(seller_id)
        if not contact:
            # Fallback เป็นสายด่วน Saleng Hotline
            return EmergencyContactResponse(
                seller_id=seller_id,
                contact_name=DEFAULT_HOTLINE_NAME,
                relationship="ศูนย์ดูแลระบบส่วนกลาง",
                contact_phone_masked=DEFAULT_HOTLINE_PHONE,
                is_default=True,
                updated_at=datetime.now(timezone.utc).isoformat(),
            )

        raw_phone = contact.get("contact_phone", "")
        masked = mask_phone(raw_phone)

        return EmergencyContactResponse(
            seller_id=seller_id,
            contact_name=contact["contact_name"],
            relationship=contact["relationship"],
            contact_phone_masked=masked,
            is_default=False,
            updated_at=contact.get("updated_at", ""),
        )

    @staticmethod
    def update_contact(seller_id: str, payload: EmergencyContactUpdateRequest) -> EmergencyContactResponse:
        """บันทึกหรือแก้ไขผู้ติดต่อฉุกเฉิน พร้อม Audit Log (AC-S09-03, P-03, P-05)"""
        data = {
            "seller_id": seller_id,
            "contact_name": payload.contact_name,
            "relationship": payload.relationship,
            "contact_phone": payload.contact_phone,
        }
        saved = supabase_store.upsert_emergency_contact(data)
        masked = mask_phone(payload.contact_phone)

        # บันทึก Audit Log (REQ-SEC-001, AC-S09-05)
        supabase_store.add_audit_log(
            action="SELLER_UPDATE_EMERGENCY_CONTACT",
            entity_id=seller_id,
            actor_id=seller_id,
            details={
                "contact_name": payload.contact_name,
                "relationship": payload.relationship,
                "masked_phone": masked,
            }
        )

        return EmergencyContactResponse(
            seller_id=seller_id,
            contact_name=saved["contact_name"],
            relationship=saved["relationship"],
            contact_phone_masked=masked,
            is_default=False,
            updated_at=saved["updated_at"],
        )


# -----------------------------------------------------------------------------
# 4. Evidence Lock Service: ล็อกหลักฐานห้ามแก้ไขเมื่อมีข้อพิพาท (AC-S09-04, P-04, Q-04)
# -----------------------------------------------------------------------------
class EvidenceLockService:
    @staticmethod
    def lock_evidences_for_order(order_id: str, actor_id: str) -> LockEvidenceResponse:
        """
        ล็อกหลักฐานทั้งหมดของคำขอเป็น Read-only เมื่อเกิดข้อพิพาท S8 หรือกด SOS (REQ-FN-006, AC-S09-04)
        """
        order = supabase_store.orders.get(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ไม่พบคำขอรหัส: {order_id}"
            )

        count = supabase_store.lock_safety_evidences_for_order(order_id)

        # บันทึก Audit Log
        supabase_store.add_audit_log(
            action="SYSTEM_LOCK_EVIDENCE",
            entity_id=order_id,
            actor_id=actor_id,
            details={"locked_count": count}
        )

        return LockEvidenceResponse(
            order_id=order_id,
            locked_count=count,
            is_locked=True,
            message=f"ทำการล็อกหลักฐานของคำขอ {order_id} จำนวน {count} รายการ เรียบร้อยแล้ว (Read-only ตาม REQ-FN-006)",
        )

