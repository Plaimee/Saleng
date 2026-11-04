"""
ชุดทดสอบ AC-A01-01: Driver KYC Queue & Inspection (UC-11, REQ-QA-001, REQ-SEC-002, CC-06, D-00-01)
"""

import time
import pytest
from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_kyc_test_data():
    """เตรียมข้อมูลคำขอ KYC และกู้คืนสถานะหลังทดสอบ"""
    orig_submissions = dict(supabase_store.collector_kyc_submissions)
    # รับประกันว่ามีคำขอสถานะ PENDING_REVIEW อย่างน้อย 1 รายการ
    supabase_store.collector_kyc_submissions["test-sub-pending"] = {
        "id": "test-sub-pending",
        "saleng_id": "saleng-05",
        "id_card_no": "1100200112233",
        "full_name": "นายสมศักดิ์ ทดสอบ",
        "id_card_photo_url": "https://storage.saleng.app/kyc/id_cards/test.jpg",
        "selfie_photo_url": "https://storage.saleng.app/kyc/selfies/test.jpg",
        "vehicle_photo_url": "https://storage.saleng.app/kyc/vehicles/test.jpg",
        "status": "PENDING_REVIEW",
        "rejection_reason": None,
        "submitted_at": "2026-11-04T10:00:00Z",
        "reviewed_at": None,
        "reviewed_by": None,
    }
    yield
    supabase_store.collector_kyc_submissions = orig_submissions


def test_AC_A01_01_get_pending_kyc_queue_success():
    """
    ทดสอบ AC-A01-01: แอดมินสามารถเรียกดูคิวคำขอ KYC ซาเล้ง พร้อมตรวจภาพถ่าย และ Masking เลขบัตรประชาชน
    """
    start_time = time.time()
    response = client.get(
        "/api/v1/admin/kyc/submissions?status=PENDING_REVIEW",
        headers={"X-Admin-Role": "ADMIN", "X-Admin-Id": "admin-01"},
    )
    elapsed = time.time() - start_time

    assert response.status_code == 200
    assert elapsed < 2.0  # REQ-QA-001: ตอบสนองภายใน < 2.0s

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    item = next(sub for sub in data if sub["id"] == "test-sub-pending")
    assert item["saleng_id"] == "saleng-05"
    assert item["status"] == "PENDING_REVIEW"
    # ตรวจสอบ PII Masking หมายเลขบัตรประชาชนตาม REQ-SEC-002, CC-06
    assert item["id_card_no_masked"] == "1-1002-XXXXX-XX-3"
    assert "1100200112233" not in str(item)  # ห้ามหลุดเลขบัตรประชาชนจริงแบบ Unmasked
    assert item["id_card_photo_url"] != ""
    assert item["selfie_photo_url"] != ""
    assert item["vehicle_photo_url"] != ""


def test_AC_A01_01_reject_unauthorized_access():
    """
    ทดสอบ AC-A01-01 / CC-03: การเรียกดูคิวคำขอ KYC โดยไม่มี Header สิทธิ์แอดมิน ต้องถูกปฏิเสธด้วย 403 Forbidden
    """
    # 1. ไม่มี Header
    resp1 = client.get("/api/v1/admin/kyc/submissions")
    assert resp1.status_code == 403
    assert "เฉพาะผู้ดูแลระบบ" in resp1.json()["detail"]

    # 2. Header บทบาทไม่ใช่ ADMIN
    resp2 = client.get(
        "/api/v1/admin/kyc/submissions",
        headers={"X-Admin-Role": "USER"},
    )
    assert resp2.status_code == 403
    assert "เฉพาะผู้ดูแลระบบ" in resp2.json()["detail"]

