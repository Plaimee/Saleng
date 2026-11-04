"""
FastAPI Router for Admin Security, Audit Trail & PDPA Compliance
รองรับ UC-13, REQ-SEC-001, REQ-SEC-002, CT-01, P-07, D-A04-01..06, CC-03, CC-04, CC-05, CC-06
"""

from typing import Optional
from fastapi import APIRouter, Header, Query, Response
from backend.app.models.security_compliance_models import (
    AuditLogQueryFilter,
    AuditLogListResponse,
    VerifyIntegrityResponse,
    CommunityWasteReportResponse,
    DataRetentionStatusResponse,
    PurgeExpiredDataRequest,
    PurgeExpiredDataResponse,
)
from backend.app.services.security_compliance_service import security_compliance_service

router = APIRouter(tags=["Admin - Security & Compliance"])


@router.get(
    "/audit-logs",
    response_model=AuditLogListResponse,
    summary="สืบค้นประวัติ Audit Trail กรองตามเงื่อนไข (Append-only Log)",
)
def get_audit_logs(
    action: Optional[str] = Query(None, description="ชื่อการกระทำที่ต้องการกรอง"),
    actor_role: Optional[str] = Query(None, description="บทบาทผู้กระทำ (ADMIN, COLLECTOR, SELLER, SYSTEM)"),
    actor_id: Optional[str] = Query(None, description="รหัสผู้กระทำ"),
    start_date: Optional[str] = Query(None, description="วันเริ่มต้น (ISO8601)"),
    end_date: Optional[str] = Query(None, description="วันสิ้นสุด (ISO8601)"),
    limit: int = Query(50, ge=1, le=500, description="จำนวนระเบียนต่อหน้า"),
    offset: int = Query(0, ge=0, description="ตำแหน่งเริ่มต้น"),
    x_admin_role: Optional[str] = Header(None, alias="X-Admin-Role"),
):
    """
    ดึงรายการบันทึก Audit Trail พร้อมการจัดหน้าและตัวกรอง
    รองรับ D-A04-01, REQ-SEC-001, AC-A04-01, CC-03
    """
    filter_params = AuditLogQueryFilter(
        action=action,
        actor_role=actor_role,
        actor_id=actor_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )
    return security_compliance_service.list_audit_logs(
        filter_params=filter_params,
        admin_role=x_admin_role,
    )


@router.get(
    "/audit-logs/export",
    summary="ส่งออกบันทึก Audit Trail ในรูปแบบ CSV หรือ JSON",
)
def export_audit_logs(
    format: str = Query("csv", description="รูปแบบไฟล์ (csv หรือ json)"),
    action: Optional[str] = Query(None),
    actor_role: Optional[str] = Query(None),
    actor_id: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    x_admin_role: Optional[str] = Header(None, alias="X-Admin-Role"),
):
    """
    ส่งออก Audit Log รองรับการดาวน์โหลด CSV หรือ JSON
    รองรับ D-A04-01, AC-A04-01, CC-03
    """
    filter_params = AuditLogQueryFilter(
        action=action,
        actor_role=actor_role,
        actor_id=actor_id,
        start_date=start_date,
        end_date=end_date,
        limit=10000,
        offset=0,
    )
    content, media_type = security_compliance_service.export_audit_logs(
        filter_params=filter_params,
        export_format=format,
        admin_role=x_admin_role,
    )
    filename = f"audit_trail_export.{format.lower()}"
    headers = {"Content-Disposition": f"attachment; filename={filename}"}
    return Response(content=content, media_type=media_type, headers=headers)


@router.post(
    "/audit-logs/verify-integrity",
    response_model=VerifyIntegrityResponse,
    summary="ตรวจสอบความถูกต้องสมบูรณ์ของ Audit Trail ด้วย SHA-256",
)
def verify_audit_integrity(
    x_admin_role: Optional[str] = Header(None, alias="X-Admin-Role"),
):
    """
    คำนวณแฮชย้อนหลังเทียบกับ log_hash ของทุกระเบียนเพื่อตรวจจับการปลอมแปลง (Tamper-evident)
    รองรับ REQ-SEC-001, P-07, D-A04-05, AC-A04-02, CC-03
    """
    return security_compliance_service.verify_audit_integrity(admin_role=x_admin_role)


@router.get(
    "/reports/community-waste",
    response_model=CommunityWasteReportResponse,
    summary="รายงานสถิติปริมาณขยะรีไซเคิลชุมชนรายเขต/แขวง แบบ No PII",
)
def get_community_waste_report(
    period: Optional[str] = Query(None, description="ช่วงเวลา (YYYY-MM เช่น 2026-11)"),
    district: Optional[str] = Query(None, description="กรองเฉพาะชื่อเขต"),
    x_admin_role: Optional[str] = Header(None, alias="X-Admin-Role"),
):
    """
    ดึงรายงานสถิติปริมาณขยะรีไซเคิลชุมชน โดยตัดข้อมูลส่วนบุคคล (PII) ออกทั้งหมด 100%
    รองรับ D-A04-03, REQ-SEC-002, AC-A04-05, CC-03
    """
    return security_compliance_service.get_community_waste_report(
        period=period,
        district=district,
        admin_role=x_admin_role,
    )


@router.get(
    "/reports/community-waste/export",
    summary="ส่งออกรายงานขยะชุมชนรายเขตเป็นไฟล์ CSV",
)
def export_community_waste_csv(
    period: Optional[str] = Query(None, description="ช่วงเวลา (YYYY-MM)"),
    district: Optional[str] = Query(None, description="กรองเฉพาะชื่อเขต"),
    x_admin_role: Optional[str] = Header(None, alias="X-Admin-Role"),
):
    """
    ส่งออกรายงานขยะชุมชนเป็น CSV สำหรับหน่วยงานภายนอก (กทม./เทศบาล)
    รองรับ D-A04-03, AC-A04-05
    """
    csv_content = security_compliance_service.export_community_waste_csv(
        period=period,
        district=district,
        admin_role=x_admin_role,
    )
    headers = {"Content-Disposition": "attachment; filename=community_waste_report.csv"}
    return Response(content=csv_content, media_type="text/csv", headers=headers)


@router.get(
    "/retention-status",
    response_model=DataRetentionStatusResponse,
    summary="ตรวจสอบสถานะการเก็บรักษาข้อมูลและรายการหมดอายุตามนโยบาย PDPA",
)
def get_pdpa_retention_status(
    x_admin_role: Optional[str] = Header(None, alias="X-Admin-Role"),
):
    """
    ตรวจสอบจำนวนพิกัด GPS ซาเล้งที่เกิน 90 วัน และรายการคำขอที่จบงานเกิน 24 ชม. ที่รอ Mask ที่อยู่
    รองรับ D-A04-04, REQ-SEC-002, CT-01, AC-A04-04, CC-03
    """
    return security_compliance_service.get_pdpa_retention_status(admin_role=x_admin_role)


@router.post(
    "/purge-expired",
    response_model=PurgeExpiredDataResponse,
    summary="ดำเนินการล้างข้อมูลหมดอายุตามนโยบาย PDPA (GPS 90 วัน, Mask Address)",
)
def purge_expired_pdpa_data(
    request: PurgeExpiredDataRequest,
    x_admin_role: Optional[str] = Header(None, alias="X-Admin-Role"),
):
    """
    สั่ง Purge พิกัด GPS ซาเล้งที่เกิน 90 วัน และ Mask ที่อยู่ผู้ขายในงานที่จบเกิน 24 ชม. ถาวร
    รองรับ D-A04-04, REQ-SEC-002, CT-01, AC-A04-04, CC-03
    """
    return security_compliance_service.purge_expired_pdpa_data(
        request=request,
        admin_role=x_admin_role,
    )

