"""
FastAPI Router for Admin Dispatch & Dispute Management
รองรับ UC-13, REQ-FN-005, REQ-FN-004, REQ-BR-002, REQ-SEC-001, CC-03, CC-04, CC-05, D-A03-01..06
"""

from typing import List, Optional
from fastapi import APIRouter, Header, Query, Path
from backend.app.models.dispatch_dispute_models import (
    StalledOrderItem,
    ManualDispatchAssignRequest,
    ManualDispatchResponse,
    ExpandDispatchRadiusRequest,
    ExpandRadiusResponse,
    DisputeSummaryItem,
    DisputeDossierResponse,
    ResolveDisputeRequest,
    ResolveDisputeResponse,
)
from backend.app.services.dispatch_dispute_service import dispatch_dispute_service

router = APIRouter(tags=["Admin - Dispatch & Dispute"])


@router.get(
    "/dispatch/stalled-orders",
    response_model=List[StalledOrderItem],
    summary="คัดกรองคำขอนัดหมายสถานะ S2 ที่ตกค้างเกิน 30 นาที",
)
def get_stalled_orders(
    min_wait_minutes: float = Query(30.0, description="เกณฑ์เวลาตกค้างขั้นต่ำ (นาที)"),
    x_admin_role: Optional[str] = Header(None, alias="X-Admin-Role"),
):
    """
    ดึงรายการคำขอขายสถานะ S2 (Pending) ที่ไม่มีซาเล้งกดรับเกิน 30 นาที
    รองรับ UC-13, D-A03-02, AC-A03-01, CC-03, CC-06
    """
    return dispatch_dispute_service.list_stalled_orders(
        min_wait_minutes=min_wait_minutes,
        admin_role=x_admin_role,
    )


@router.post(
    "/dispatch/assign",
    response_model=ManualDispatchResponse,
    summary="แอดมินมอบหมายงานตรงให้ซาเล้งเฉพาะราย (Direct Assign)",
)
def assign_order_manually(
    request: ManualDispatchAssignRequest,
    x_admin_role: Optional[str] = Header(None, alias="X-Admin-Role"),
):
    """
    แอดมินเลือกมอบหมายงานให้ซาเล้งที่ผ่าน KYC และออนไลน์ในพื้นที่โดยตรง (S2 -> S3)
    รองรับ UC-13, D-A03-03, D-00-01, AC-A03-01, CC-03, REQ-SEC-001
    """
    return dispatch_dispute_service.assign_order_manually(
        request=request,
        admin_role=x_admin_role,
    )


@router.post(
    "/dispatch/expand-radius",
    response_model=ExpandRadiusResponse,
    summary="ขยายรัศมีการค้นหาของคำขอเป็น 10.0 กม. (Expand Radius Broadcast)",
)
def expand_search_radius(
    request: ExpandDispatchRadiusRequest,
    x_admin_role: Optional[str] = Header(None, alias="X-Admin-Role"),
):
    """
    แอดมินกดขยายรัศมีการค้นหาจาก 5.0 กม. เป็น 10.0 กม. เพื่อบรอดคาสต์หาซาเล้งวงนอก
    รองรับ UC-13, D-A03-03, AC-A03-01, CC-03, REQ-SEC-001
    """
    return dispatch_dispute_service.expand_search_radius(
        request=request,
        admin_role=x_admin_role,
    )


@router.get(
    "/disputes",
    response_model=List[DisputeSummaryItem],
    summary="ดึงรายการข้อพิพาทหน้างานรอดำเนินการ (S8 / PENDING_ADMIN)",
)
def get_disputes(
    status: Optional[str] = Query("PENDING_ADMIN", description="สถานะข้อพิพาท"),
    x_admin_role: Optional[str] = Header(None, alias="X-Admin-Role"),
):
    """
    ดึงรายการข้อพิพาทสำหรับแสดงในศูนย์ระงับข้อพิพาทของแอดมิน
    รองรับ UC-13, D-A03-01, AC-A03-02, CC-03
    """
    return dispatch_dispute_service.list_disputes(
        status=status,
        admin_role=x_admin_role,
    )


@router.get(
    "/disputes/{dispute_id}",
    response_model=DisputeDossierResponse,
    summary="ดึงชุดสำนวนหลักฐานข้อพิพาท 4 มิติ",
)
def get_dispute_dossier(
    dispute_id: str = Path(..., description="รหัสข้อพิพาท"),
    x_admin_role: Optional[str] = Header(None, alias="X-Admin-Role"),
):
    """
    ดึงสำนวนหลักฐาน 4 มิติ: คำขอเดิม & Price Snapshot, ภาพตาชั่งซาเล้ง, ข้อโต้แย้งผู้ขาย, ข้อมูลติดต่อ
    รองรับ UC-13, REQ-FN-005, REQ-FN-004, D-A03-04, AC-A03-02, CC-03
    """
    return dispatch_dispute_service.get_dispute_dossier(
        dispute_id=dispute_id,
        admin_role=x_admin_role,
    )


@router.post(
    "/disputes/{dispute_id}/resolve",
    response_model=ResolveDisputeResponse,
    summary="แอดมินตัดสินชี้ขาดข้อพิพาท (จบงาน S7 หรือ ยกเลิก S9)",
)
def resolve_dispute(
    dispute_id: str = Path(..., description="รหัสข้อพิพาท"),
    request: ResolveDisputeRequest = ...,
    x_admin_role: Optional[str] = Header(None, alias="X-Admin-Role"),
):
    """
    แอดมินชี้ขาดข้อพิพาท:
    1. RESOLVE_COMPLETE: ตัดสินให้ปิดงาน (S7) พร้อมยอดเงินชี้ขาดสุทธิ และออกใบเสร็จ
    2. RESOLVE_CANCEL: ตัดสินสั่งยกเลิกคำขอ (S9) ไม่มีการชำระเงิน
    รองรับ UC-13, D-A03-01, D-A03-05, AC-A03-03, AC-A03-04, CC-03, REQ-SEC-001
    """
    return dispatch_dispute_service.resolve_dispute(
        dispute_id=dispute_id,
        request=request,
        admin_role=x_admin_role,
    )

