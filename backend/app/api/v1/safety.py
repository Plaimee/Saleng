"""
API Endpoints สำหรับระบบความปลอดภัยขณะทำธุรกรรม (Transaction Safety & SOS API)
รองรับ UC-09, UC-13, REQ-SEC-001, REQ-SEC-002, REQ-QA-001, REQ-UX-001, REQ-FN-006, AC-S09-01..05, P-01..P-05
"""

from typing import Optional
from fastapi import APIRouter, status, Query
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
from backend.app.services.safety_service import (
    MediaEvidenceService,
    EmergencySosService,
    EmergencyContactService,
    EvidenceLockService,
)

safety_router = APIRouter(prefix="/api/v1", tags=["transaction-safety"])


# -----------------------------------------------------------------------------
# 1. Media Evidence Endpoints (AC-S09-01, P-01, Q-01)
# -----------------------------------------------------------------------------
@safety_router.post(
    "/orders/{order_id}/safety/evidence",
    response_model=EvidenceItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="บันทึก/อัปโหลดไฟล์หลักฐานเสียงหรือวิดีโอหน้างาน (AC-S09-01, UC-09)"
)
def upload_safety_evidence(
    order_id: str,
    payload: EvidenceUploadRequest,
    seller_id: Optional[str] = Query(None, description="รหัสผู้ขาย"),
):
    """
    ผู้ขายบันทึกหรืออัปโหลดหลักฐานเสียงหรือคลิปวิดีโอหน้างานในสถานะ S4, S5, S6
    """
    # ถ้าไม่มี seller_id ใน query ให้ดึงจาก order
    from backend.app.core.supabase import supabase_store
    order = supabase_store.orders.get(order_id)
    resolved_seller_id = seller_id or (order.get("seller_id") if order else "")
    return MediaEvidenceService.upload_evidence(
        order_id=order_id,
        seller_id=resolved_seller_id,
        payload=payload,
    )


@safety_router.get(
    "/orders/{order_id}/safety/evidence",
    response_model=EvidenceListResponse,
    summary="ดึงรายการหลักฐานทั้งหมดของคำขอ (AC-S09-01, AC-S09-04)"
)
def get_safety_evidences(
    order_id: str,
    seller_id: Optional[str] = Query(None, description="รหัสผู้ขาย"),
):
    """ดึงรายการหลักฐานทั้งหมดที่แนบไว้กับคำขอ"""
    from backend.app.core.supabase import supabase_store
    order = supabase_store.orders.get(order_id)
    resolved_seller_id = seller_id or (order.get("seller_id") if order else "")
    return MediaEvidenceService.get_evidences(
        order_id=order_id,
        seller_id=resolved_seller_id,
    )


# -----------------------------------------------------------------------------
# 2. Emergency SOS Endpoints (AC-S09-02, P-02, Q-02)
# -----------------------------------------------------------------------------
@safety_router.post(
    "/orders/{order_id}/safety/sos",
    response_model=SosAlertResponse,
    status_code=status.HTTP_200_OK,
    summary="ส่งสัญญาณฉุกเฉิน SOS One-Tap Trigger (AC-S09-02, REQ-QA-001)"
)
def trigger_sos(
    order_id: str,
    payload: SosTriggerRequest,
    seller_id: Optional[str] = Query(None, description="รหัสผู้ขาย"),
):
    """
    ผู้ขายกดปุ่ม SOS ฉุกเฉินเพื่อส่งพิกัดและข้อมูลซาเล้งไปยังศูนย์ Admin ภายใน 2 วินาที (REQ-QA-001)
    """
    from backend.app.core.supabase import supabase_store
    order = supabase_store.orders.get(order_id)
    resolved_seller_id = seller_id or (order.get("seller_id") if order else "")
    return EmergencySosService.trigger_sos(
        order_id=order_id,
        seller_id=resolved_seller_id,
        payload=payload,
    )


# -----------------------------------------------------------------------------
# 3. Trusted Emergency Contact Endpoints (AC-S09-03, P-03, Q-03)
# -----------------------------------------------------------------------------
@safety_router.get(
    "/sellers/{seller_id}/safety/emergency-contact",
    response_model=EmergencyContactResponse,
    summary="ดึงข้อมูลผู้ติดต่อฉุกเฉินที่ไว้ใจได้ (AC-S09-03, REQ-SEC-002)"
)
def get_emergency_contact(seller_id: str):
    """ดึงข้อมูลผู้ติดต่อฉุกเฉินของผู้ขาย พร้อม PDPA Masking 08X-XXX-XXXX"""
    return EmergencyContactService.get_contact(seller_id=seller_id)


@safety_router.put(
    "/sellers/{seller_id}/safety/emergency-contact",
    response_model=EmergencyContactResponse,
    summary="บันทึกหรือแก้ไขผู้ติดต่อฉุกเฉินที่ไว้ใจได้ (AC-S09-03, REQ-SEC-002)"
)
def update_emergency_contact(seller_id: str, payload: EmergencyContactUpdateRequest):
    """บันทึกหรือแก้ไขข้อมูลผู้ติดต่อฉุกเฉิน พร้อม Audit Log"""
    return EmergencyContactService.update_contact(
        seller_id=seller_id,
        payload=payload,
    )


# -----------------------------------------------------------------------------
# 4. Evidence Lock Endpoint (AC-S09-04, P-04, Q-04)
# -----------------------------------------------------------------------------
@safety_router.patch(
    "/orders/{order_id}/safety/lock-evidence",
    response_model=LockEvidenceResponse,
    summary="ล็อกหลักฐานของคำขอเป็น Read-only เมื่อมีข้อพิพาท/SOS (AC-S09-04, REQ-FN-006)"
)
def lock_order_evidence(
    order_id: str,
    actor_id: Optional[str] = Query(None, description="รหัสผู้สั่งล็อก"),
):
    """ล็อกหลักฐานเสียง/วิดีโอทั้งหมดของคำขอเป็น Read-only ป้องกันการลบหรือแก้ไข"""
    from backend.app.core.supabase import supabase_store
    order = supabase_store.orders.get(order_id)
    resolved_actor_id = actor_id or (order.get("seller_id") if order else "SYSTEM")
    return EvidenceLockService.lock_evidences_for_order(
        order_id=order_id,
        actor_id=resolved_actor_id,
    )

