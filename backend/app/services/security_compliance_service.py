"""
Service Layer for Admin Security, Audit Trail & PDPA Compliance
รองรับ UC-13, REQ-SEC-001, REQ-SEC-002, CT-01, P-07, D-A04-01..05, CC-03, CC-04, CC-05, CC-06
"""

from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, timezone
import csv
import io
import json
from fastapi import HTTPException

from backend.app.core.supabase import supabase_store
from backend.app.models.security_compliance_models import (
    compute_audit_log_hash,
    AuditLogQueryFilter,
    AuditLogItem,
    AuditLogListResponse,
    AuditLogExportResponse,
    VerifyIntegrityResponse,
    CommunityWasteSummaryItem,
    CommunityWasteReportResponse,
    DataRetentionStatusResponse,
    PurgeExpiredDataRequest,
    PurgeExpiredDataResponse,
)


class SecurityComplianceService:
    """
    บริการจัดการระบบความปลอดภัย ประวัติร่องรอยตรวจสอบ และการปฏิบัติตาม PDPA
    """

    ALLOWED_AUDIT_ROLES = {"ADMIN", "AUDITOR"}
    ALLOWED_REPORT_ROLES = {"ADMIN", "AUDITOR", "DPO"}
    ALLOWED_PDPA_ROLES = {"ADMIN", "DPO"}

    def verify_role(self, admin_role: Optional[str], allowed_roles: set) -> str:
        """
        ตรวจสอบสิทธิ์การเข้าถึง (RBAC) ผ่าน X-Admin-Role Header
        รองรับ D-A04-02, CC-03
        """
        if not admin_role:
            raise HTTPException(
                status_code=403,
                detail="สิทธิ์การเข้าถึงไม่เพียงพอ: ต้องระบุบทบาทผ่าน X-Admin-Role",
            )
        normalized_role = admin_role.strip().upper()
        if normalized_role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"สิทธิ์การเข้าถึงไม่เพียงพอ: บทบาท {admin_role} ไม่ได้รับอนุญาตให้ดำเนินการนี้",
            )
        return normalized_role

    def list_audit_logs(
        self,
        filter_params: AuditLogQueryFilter,
        admin_role: Optional[str],
    ) -> AuditLogListResponse:
        """
        สืบค้นประวัติ Audit Trail กรองตามเงื่อนไข
        รองรับ D-A04-01, REQ-SEC-001
        """
        self.verify_role(admin_role, self.ALLOWED_AUDIT_ROLES)

        total, raw_logs = supabase_store.query_audit_logs(
            action=filter_params.action,
            actor_role=filter_params.actor_role,
            actor_id=filter_params.actor_id,
            start_date=filter_params.start_date,
            end_date=filter_params.end_date,
            limit=filter_params.limit,
            offset=filter_params.offset,
        )

        logs = [
            AuditLogItem(
                log_id=item.get("log_id", ""),
                timestamp=item.get("timestamp", ""),
                actor_id=item.get("actor_id", ""),
                actor_role=item.get("actor_role", "SYSTEM"),
                action=item.get("action", ""),
                entity_id=item.get("entity_id", ""),
                details=item.get("details", {}),
                log_hash=item.get("log_hash", ""),
            )
            for item in raw_logs
        ]

        return AuditLogListResponse(
            total_records=total,
            limit=filter_params.limit,
            offset=filter_params.offset,
            logs=logs,
        )

    def export_audit_logs(
        self,
        filter_params: AuditLogQueryFilter,
        export_format: str,
        admin_role: Optional[str],
    ) -> Tuple[str, str]:
        """
        ส่งออกบันทึก Audit Trail ในรูปแบบ CSV หรือ JSON
        รองรับ D-A04-01, AC-A04-01
        Returns: (content_string, media_type)
        """
        self.verify_role(admin_role, self.ALLOWED_AUDIT_ROLES)

        fmt = export_format.lower().strip()
        if fmt not in ("csv", "json"):
            raise HTTPException(
                status_code=400,
                detail=f"รูปแบบการส่งออกไม่ถูกต้อง: {export_format} (รองรับเฉพาะ 'csv' หรือ 'json')",
            )

        _, raw_logs = supabase_store.query_audit_logs(
            action=filter_params.action,
            actor_role=filter_params.actor_role,
            actor_id=filter_params.actor_id,
            start_date=filter_params.start_date,
            end_date=filter_params.end_date,
            limit=10000,
            offset=0,
        )

        if fmt == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["log_id", "timestamp", "actor_id", "actor_role", "action", "entity_id", "log_hash", "details"])
            for l in raw_logs:
                writer.writerow([
                    l.get("log_id", ""),
                    l.get("timestamp", ""),
                    l.get("actor_id", ""),
                    l.get("actor_role", ""),
                    l.get("action", ""),
                    l.get("entity_id", ""),
                    l.get("log_hash", ""),
                    json.dumps(l.get("details", {}), ensure_ascii=False),
                ])
            return output.getvalue(), "text/csv"
        else:
            return json.dumps(raw_logs, ensure_ascii=False, indent=2), "application/json"

    def verify_audit_integrity(self, admin_role: Optional[str]) -> VerifyIntegrityResponse:
        """
        ตรวจสอบความสมบูรณ์ของ Audit Trail ด้วย SHA-256
        รองรับ REQ-SEC-001, P-07, D-A04-05, AC-A04-02
        """
        self.verify_role(admin_role, self.ALLOWED_AUDIT_ROLES)

        total_checked, is_valid, corrupted_ids = supabase_store.verify_audit_logs_integrity()
        now_iso = datetime.now(timezone.utc).isoformat()
        status_msg = "Audit Trail Verified - 100% Integrity Intact" if is_valid else f"Tampering Detected: {len(corrupted_ids)} corrupted log(s)"

        return VerifyIntegrityResponse(
            total_checked=total_checked,
            is_valid=is_valid,
            corrupted_log_ids=corrupted_ids,
            verified_at=now_iso,
            message=status_msg,
        )

    def get_community_waste_report(
        self,
        period: Optional[str],
        district: Optional[str],
        admin_role: Optional[str],
    ) -> CommunityWasteReportResponse:
        """
        สรุปสถิติปริมาณขยะรีไซเคิลชุมชนรายเขต/แขวง แบบ No PII
        รองรับ D-A04-03, REQ-SEC-002, AC-A04-05
        """
        self.verify_role(admin_role, self.ALLOWED_REPORT_ROLES)

        raw_items = supabase_store.get_community_waste_report(
            period=period,
            district_filter=district,
        )

        summary_items = [
            CommunityWasteSummaryItem(
                subdistrict=item.get("subdistrict", "ไม่ระบุ"),
                district=item.get("district", "ไม่ระบุ"),
                category_code=item.get("category_code", "MAT-GEN"),
                category_name=item.get("category_name", "ขยะรีไซเคิล"),
                total_weight_kg=float(item.get("total_weight_kg", 0.0)),
                total_amount_thb=float(item.get("total_amount_baht", item.get("total_amount_thb", 0.0))),
                completed_trips_count=int(item.get("total_transactions", item.get("completed_trips_count", 1))),
                period_month=item.get("period", item.get("period_month", "2026-11")),
            )
            for item in raw_items
        ]

        grand_total_weight = round(sum(i.total_weight_kg for i in summary_items), 2)
        grand_total_amount = round(sum(i.total_amount_thb for i in summary_items), 2)
        total_trips = sum(i.completed_trips_count for i in summary_items)

        return CommunityWasteReportResponse(
            period=period or "2026-11",
            district=district,
            summary_items=summary_items,
            grand_total_weight_kg=grand_total_weight,
            grand_total_amount_thb=grand_total_amount,
            total_completed_trips=total_trips,
            exported_at=datetime.now(timezone.utc).isoformat(),
            is_anonymized=True,
        )

    def export_community_waste_csv(
        self,
        period: Optional[str],
        district: Optional[str],
        admin_role: Optional[str],
    ) -> str:
        """
        ส่งออกรายงานขยะชุมชนรายเขตเป็นไฟล์ CSV สำหรับส่งต่อ กทม. / เทศบาล
        รองรับ D-A04-03, AC-A04-05
        """
        self.verify_role(admin_role, self.ALLOWED_REPORT_ROLES)

        report = self.get_community_waste_report(period=period, district=district, admin_role=admin_role)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["district", "subdistrict", "category_code", "category_name", "total_weight_kg", "total_amount_thb", "completed_trips_count", "period_month"])
        for item in report.summary_items:
            writer.writerow([
                item.district,
                item.subdistrict,
                item.category_code,
                item.category_name,
                item.total_weight_kg,
                item.total_amount_thb,
                item.completed_trips_count,
                item.period_month,
            ])
        return output.getvalue()

    def get_pdpa_retention_status(self, admin_role: Optional[str]) -> DataRetentionStatusResponse:
        """
        ตรวจสอบสถานะการเก็บรักษาข้อมูลตามเงื่อนไข PDPA
        รองรับ D-A04-04, REQ-SEC-002, CT-01, AC-A04-04
        """
        self.verify_role(admin_role, self.ALLOWED_PDPA_ROLES)
        raw_status = supabase_store.get_pdpa_retention_status()
        return DataRetentionStatusResponse(
            gps_retention_days=raw_status.get("retention_policy_gps_days", 90),
            expired_gps_coordinates_count=raw_status.get("expired_gps_records", 0),
            unmasked_completed_orders_count=raw_status.get("unmasked_completed_orders_gt_24h", 0),
            total_audit_logs_count=len(supabase_store.audit_logs),
            checked_at=raw_status.get("last_checked_at", datetime.now(timezone.utc).isoformat()),
        )

    def purge_expired_pdpa_data(
        self,
        request: PurgeExpiredDataRequest,
        admin_role: Optional[str],
    ) -> PurgeExpiredDataResponse:
        """
        ล้างพิกัด GPS ซาเล้งเกิน 90 วัน และ Mask ข้อมูลที่อยู่ผู้ขายหลังจบงานเกิน 24 ชม.
        รองรับ D-A04-04, REQ-SEC-002, CT-01, AC-A04-04
        """
        self.verify_role(admin_role, self.ALLOWED_PDPA_ROLES)

        purged_gps, masked_orders = supabase_store.purge_expired_pdpa_data(admin_id=request.admin_id)
        return PurgeExpiredDataResponse(
            success=True,
            purged_gps_points_count=purged_gps,
            masked_orders_count=masked_orders,
            purged_at=datetime.now(timezone.utc).isoformat(),
            purged_by=request.admin_id,
            message=f"Purge completed successfully: {purged_gps} GPS records purged, {masked_orders} orders masked.",
        )


security_compliance_service = SecurityComplianceService()
