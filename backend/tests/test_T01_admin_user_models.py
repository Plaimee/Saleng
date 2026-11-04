"""
ชุดทดสอบ T-01: Data Models และ Store Methods สำหรับ Admin KYC & Penalty (AC-A01-01..05)
"""

import pytest
from pydantic import ValidationError
from backend.app.models.user_verification_penalty_models import (
    mask_thai_id_card,
    KYCSubmissionItem,
    KYCReviewRequest,
    KYCReviewResponse,
    UserAccountItem,
    UserPenaltyRequest,
    UserPenaltyResponse,
    UserReactivateRequest,
    UserReactivateResponse,
)
from backend.app.core.supabase import supabase_store


@pytest.fixture(autouse=True)
def restore_store_after_test():
    """กู้คืนสถานะข้อมูลใน Store หลังทดสอบ ป้องกัน Side-effect ต่อชุดทดสอบอื่น"""
    orig_profiles = {k: dict(v) for k, v in supabase_store.saleng_profiles.items()}
    orig_submissions = {k: dict(v) for k, v in supabase_store.collector_kyc_submissions.items()}
    orig_sellers = {k: dict(v) for k, v in supabase_store.sellers.items()}
    orig_audit = list(supabase_store.audit_logs)
    yield
    supabase_store.saleng_profiles = orig_profiles
    supabase_store.collector_kyc_submissions = orig_submissions
    supabase_store.sellers = orig_sellers
    supabase_store.audit_logs = orig_audit


def test_mask_thai_id_card():
    """ทดสอบฟังก์ชัน Masking เลขบัตรประชาชน 13 หลักตาม PDPA (REQ-SEC-002, CC-06)"""
    assert mask_thai_id_card("1100200112233") == "1-1002-XXXXX-XX-3"
    assert mask_thai_id_card("1-1002-00112-23-3") == "1-1002-XXXXX-XX-3"
    assert mask_thai_id_card("invalid") == "1-1002-XXXXX-XX-X"


def test_kyc_models_validation():
    """ทดสอบ Pydantic Validation ของ KYC Models"""
    # 1. KYCReviewRequest: เมื่อ action = REJECT ต้องมี rejection_reason
    with pytest.raises(ValidationError):
        KYCReviewRequest(
            submission_id="sub-01",
            action="REJECT",
            rejection_reason="",
        )

    req_reject = KYCReviewRequest(
        submission_id="sub-01",
        action="REJECT",
        rejection_reason="ภาพถ่ายไม่ชัดเจน",
    )
    assert req_reject.action == "REJECT"
    assert req_reject.rejection_reason == "ภาพถ่ายไม่ชัดเจน"

    req_approve = KYCReviewRequest(
        submission_id="sub-01",
        action="APPROVE",
    )
    assert req_approve.action == "APPROVE"
    assert req_approve.rejection_reason is None


def test_user_penalty_models_validation():
    """ทดสอบ Pydantic Validation ของ User Penalty Models"""
    # 1. UserPenaltyRequest: penalty_reason ต้องมีความยาวอย่างน้อย 3 ตัวอักษร
    with pytest.raises(ValidationError):
        UserPenaltyRequest(
            user_id="saleng-01",
            role="COLLECTOR",
            action="BAN",
            penalty_reason="โก",  # น้อยกว่า 3 ตัวอักษร
        )

    req = UserPenaltyRequest(
        user_id="saleng-01",
        role="COLLECTOR",
        action="SUSPEND_TEMPORARY",
        penalty_reason="ตรวจสอบพบข้อพิพาทโกงตาชั่ง",
        duration_days=7,
    )
    assert req.user_id == "saleng-01"
    assert req.role == "COLLECTOR"
    assert req.action == "SUSPEND_TEMPORARY"
    assert req.duration_days == 7


def test_supabase_store_admin_methods():
    """ทดสอบเมธอดของ Store สำหรับแอดมิน (AC-A01-01..04)"""
    # 1. ดึงคิวคำขอ KYC
    submissions = supabase_store.get_collector_kyc_submissions("PENDING_REVIEW")
    assert isinstance(submissions, list)
    assert len(submissions) >= 1

    sub_id = submissions[0]["id"]
    sub = supabase_store.get_collector_kyc_submission(sub_id)
    assert sub is not None
    assert sub["id"] == sub_id

    # 2. พิจารณาอนุมัติ KYC
    reviewed_sub, reviewed_profile = supabase_store.review_collector_kyc(
        submission_id=sub_id,
        action="APPROVE",
        reviewed_by="admin-test",
    )
    assert reviewed_sub["status"] == "VERIFIED"
    assert reviewed_profile["verified"] is True
    assert reviewed_profile["kyc_status"] == "VERIFIED"

    # 3. ดึงรายชื่อผู้ใช้ทั้งหมด
    users = supabase_store.get_admin_users()
    assert len(users) >= 2
    assert any(u["role"] == "COLLECTOR" for u in users)
    assert any(u["role"] == "SELLER" for u in users)

    # 4. สั่งระงับสิทธิ์ผู้ใช้ (Suspend)
    saleng_user = next(u for u in users if u["role"] == "COLLECTOR")
    penalized = supabase_store.penalize_user_account(
        user_id=saleng_user["user_id"],
        role="COLLECTOR",
        action="SUSPEND_TEMPORARY",
        penalty_reason="โกงตาชั่งซ้ำซาก",
    )
    assert penalized["account_status"] == "SUSPENDED_TEMPORARY"
    assert penalized["penalty_reason"] == "โกงตาชั่งซ้ำซาก"

    # 5. ปลดระงับสิทธิ์ผู้ใช้ (Reactivate)
    reactivated = supabase_store.reactivate_user_account(
        user_id=saleng_user["user_id"],
        role="COLLECTOR",
    )
    assert reactivated["account_status"] == "ACTIVE"
    assert reactivated["penalty_reason"] is None
