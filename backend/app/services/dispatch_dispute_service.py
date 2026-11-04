"""
Service Layer for Admin Dispatch & Dispute Management
รองรับ UC-13, REQ-FN-005, REQ-FN-004, REQ-BR-002, REQ-SEC-001, CC-03, CC-04, CC-05, D-A03-01..06
"""

from typing import List, Optional, Dict, Any
from fastapi import HTTPException
from backend.app.core.supabase import supabase_store, SupabaseStore
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
    DisputeActionEnum,
)


class DispatchDisputeService:
    """
    ตรรกะธุรกิจศูนย์ควบคุมการจับคู่งานและข้อพิพาทสำหรับผู้ดูแลระบบ
    """

    def __init__(self, store: Optional[SupabaseStore] = None):
        self.store = store or supabase_store

    def _verify_admin_role(self, admin_role: Optional[str]) -> None:
        """
        ตรวจสอบสิทธิ์การเข้าถึงของผู้ดูแลระบบ (CC-03, D-A03-06, AC-A03-05)
        """
        if not admin_role or admin_role.strip().upper() != "ADMIN":
            raise HTTPException(
                status_code=403,
                detail="สิทธิ์ไม่ถูกต้อง: เฉพาะผู้ดูแลระบบ (ADMIN) เท่านั้นที่สามารถเข้าถึงศูนย์ควบคุมได้"
            )

    def list_stalled_orders(
        self,
        min_wait_minutes: float = 30.0,
        admin_role: Optional[str] = None,
    ) -> List[StalledOrderItem]:
        """
        ดึงรายการคำขอนัดหมายสถานะ S2 (Pending) ที่ตกค้างเกินเกณฑ์เวลา (UC-13, D-A03-02, AC-A03-01)
        """
        self._verify_admin_role(admin_role)
        raw_items = self.store.get_stalled_orders(min_wait_minutes=min_wait_minutes)
        return [StalledOrderItem(**item) for item in raw_items]

    def assign_order_manually(
        self,
        request: ManualDispatchAssignRequest,
        admin_role: Optional[str] = None,
    ) -> ManualDispatchResponse:
        """
        แอดมินมอบหมายงานตรงให้ซาเล้งเฉพาะราย (Direct Assign -> S3) (UC-13, D-A03-03, D-00-01, AC-A03-01)
        """
        self._verify_admin_role(admin_role)
        ok, res_order, msg = self.store.manual_dispatch_order(
            order_id=request.order_id,
            saleng_id=request.saleng_id,
            admin_id=request.admin_id,
            notes=request.notes,
        )
        if not ok:
            if "ไม่พบ" in msg:
                raise HTTPException(status_code=404, detail=msg)
            elif "ไม่ได้อยู่ในสถานะรอผู้รับงาน" in msg:
                raise HTTPException(status_code=409, detail=msg)
            else:
                raise HTTPException(status_code=400, detail=msg)

        saleng = self.store.saleng_profiles.get(request.saleng_id, {})
        return ManualDispatchResponse(
            success=True,
            order_id=request.order_id,
            status="S3",
            assigned_saleng_id=request.saleng_id,
            assigned_saleng_name=saleng.get("display_name"),
            message="มอบหมายงานสำเร็จ",
            dispatched_at=res_order.get("dispatched_at"),
        )

    def expand_search_radius(
        self,
        request: ExpandDispatchRadiusRequest,
        admin_role: Optional[str] = None,
    ) -> ExpandRadiusResponse:
        """
        แอดมินขยายรัศมีการค้นหาของคำขอเป็น 10.0 กม. (Expand Radius Broadcast) (UC-13, D-A03-03, AC-A03-01)
        """
        self._verify_admin_role(admin_role)
        ok, res_data, msg = self.store.expand_order_search_radius(
            order_id=request.order_id,
            new_radius_km=request.new_radius_km,
            admin_id=request.admin_id,
        )
        if not ok:
            if "ไม่พบ" in msg:
                raise HTTPException(status_code=404, detail=msg)
            else:
                raise HTTPException(status_code=400, detail=msg)

        return ExpandRadiusResponse(
            success=True,
            order_id=request.order_id,
            old_radius_km=res_data["old_radius_km"],
            new_radius_km=res_data["new_radius_km"],
            message="ขยายรัศมีการค้นหาสำเร็จ",
        )

    def list_disputes(
        self,
        status: Optional[str] = "PENDING_ADMIN",
        admin_role: Optional[str] = None,
    ) -> List[DisputeSummaryItem]:
        """
        ดึงรายการข้อพิพาทสถานะ PENDING_ADMIN หรือตามสถานะที่กำหนด (UC-13, D-A03-01, AC-A03-02)
        """
        self._verify_admin_role(admin_role)
        raw_disputes = self.store.get_disputes(status_filter=status)
        return [DisputeSummaryItem(**disp) for disp in raw_disputes]

    def get_dispute_dossier(
        self,
        dispute_id: str,
        admin_role: Optional[str] = None,
    ) -> DisputeDossierResponse:
        """
        ดึงสำนวนหลักฐานข้อพิพาท 4 มิติฉบับสมบูรณ์ (UC-13, REQ-FN-005, REQ-FN-004, D-A03-04, AC-A03-02)
        """
        self._verify_admin_role(admin_role)
        dossier = self.store.get_dispute_dossier(dispute_id)
        if not dossier:
            raise HTTPException(
                status_code=404,
                detail=f"ไม่พบสำนวนข้อพิพาทรหัส {dispute_id}"
            )
        return DisputeDossierResponse(**dossier)

    def resolve_dispute(
        self,
        dispute_id: str,
        request: ResolveDisputeRequest,
        admin_role: Optional[str] = None,
    ) -> ResolveDisputeResponse:
        """
        แอดมินตัดสินชี้ขาดข้อพิพาท (จบงาน -> S7 หรือ ยกเลิก -> S9) (UC-13, D-A03-01, D-A03-05, AC-A03-03, AC-A03-04)
        """
        self._verify_admin_role(admin_role)
        action_str = request.action.value if hasattr(request.action, "value") else str(request.action)
        ok, res_data, msg = self.store.resolve_dispute(
            dispute_id=dispute_id,
            action=action_str,
            arbitrated_amount=request.arbitrated_amount,
            arbitration_note=request.arbitration_note,
            admin_id=request.admin_id,
        )
        if not ok:
            if "ไม่พบ" in msg:
                raise HTTPException(status_code=404, detail=msg)
            elif "ได้รับการตัดสินแล้ว" in msg:
                raise HTTPException(status_code=409, detail=msg)
            else:
                raise HTTPException(status_code=400, detail=msg)

        disp = res_data["dispute"]
        return ResolveDisputeResponse(
            success=True,
            dispute_id=dispute_id,
            order_id=disp.get("order_id"),
            dispute_status=disp.get("status"),
            order_status=res_data.get("order_status"),
            action_taken=action_str,
            arbitrated_amount=res_data.get("arbitrated_amount"),
            arbitration_note=request.arbitration_note,
            receipt=res_data.get("receipt"),
            message=msg,
        )


dispatch_dispute_service = DispatchDisputeService()

