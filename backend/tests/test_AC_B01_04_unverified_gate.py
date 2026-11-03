"""
Automated Tests สำหรับ AC-B01-04: Unverified Collector Job Claim Block Gate
รองรับ D-00-01, REQ-SEC-001, CC-01, P-05, Q-05
"""

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store
from backend.app.services.collector_account_service import CollectorKycService

client = TestClient(app)


def test_AC_B01_04_gate_blocks_unverified_collector():
    """
    ทดสอบกฎเหล็ก D-00-01: ซาเล้งที่ยังไม่ผ่าน KYC (UNVERIFIED) ต้องถูกบล็อกด้วย HTTP 403 Forbidden
    """
    # saleng-05 ถูก seed มาโดย verified = False, kyc_status = UNVERIFIED
    res = client.get("/api/v1/collectors/saleng-05/job-claim-gate")
    assert res.status_code == 403
    assert "ยังไม่ได้ยื่นเอกสารยืนยันตัวตน (KYC)" in res.json()["detail"]

    # ทดสอบฟังก์ชันระดับ Service โดยตรง
    with pytest.raises(HTTPException) as excinfo:
        CollectorKycService.assert_can_claim_job("saleng-05")
    assert excinfo.value.status_code == 403


def test_AC_B01_04_gate_blocks_pending_review_collector():
    """
    ทดสอบกรณีเอกสารอยู่ระหว่างตรวจสอบ (PENDING_REVIEW) ต้องถูกบล็อกด้วย HTTP 403 พร้อมข้อความแจ้งเวลา
    """
    saleng_id = "saleng-05"
    # อัปเดตสถานะเป็น PENDING_REVIEW
    supabase_store.update_saleng_profile(saleng_id, {"kyc_status": "PENDING_REVIEW", "verified": False})

    res = client.get(f"/api/v1/collectors/{saleng_id}/job-claim-gate")
    assert res.status_code == 403
    assert "อยู่ระหว่างการตรวจสอบ" in res.json()["detail"]


def test_AC_B01_04_gate_blocks_rejected_collector():
    """
    ทดสอบกรณีเอกสารถูกปฏิเสธ (REJECTED) ต้องถูกบล็อกด้วย HTTP 403 พร้อมเหตุผล
    """
    saleng_id = "saleng-05"
    supabase_store.update_saleng_profile(
        saleng_id,
        {"kyc_status": "REJECTED", "verified": False, "rejection_reason": "รูปภาพไม่ชัดเจน"}
    )

    res = client.get(f"/api/v1/collectors/{saleng_id}/job-claim-gate")
    assert res.status_code == 403
    assert "ไม่ผ่านการอนุมัติ: รูปภาพไม่ชัดเจน" in res.json()["detail"]

    # คืนค่าเดิม
    supabase_store.update_saleng_profile(
        saleng_id,
        {"kyc_status": "UNVERIFIED", "verified": False, "rejection_reason": None}
    )


def test_AC_B01_04_gate_permits_verified_collector():
    """
    ทดสอบกรณีซาเล้งผ่าน KYC เรียบร้อย (VERIFIED, verified = True) สามารถกดรับงานได้ (200 OK)
    """
    # saleng-01 ผ่าน KYC เรียบร้อย (verified = True)
    res = client.get("/api/v1/collectors/saleng-01/job-claim-gate")
    assert res.status_code == 200
    data = res.json()
    assert data["can_claim_job"] is True
    assert data["verified"] is True
    assert data["kyc_status"] == "VERIFIED"
    assert "สามารถกดรับงานได้" in data["reason"]

    # ทดสอบฟังก์ชันระดับ Service โดยตรง
    service_result = CollectorKycService.assert_can_claim_job("saleng-01")
    assert service_result.can_claim_job is True
