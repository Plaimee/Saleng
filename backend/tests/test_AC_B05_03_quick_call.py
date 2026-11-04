"""
Acceptance Tests for AC-B05-03: Native Quick Call Launch & Audit Logging
(Task T-04: UC-08, REQ-SEC-001, CC-01, D-B05-02)
"""

import pytest
from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_quick_call_environment():
    """เตรียมข้อมูลคำขอขายสถานะ S3 สำหรับทดสอบปุ่มโทรด่วน"""
    order_id = "order-call-01"
    supabase_store.orders[order_id] = {
        "order_id": order_id,
        "seller_id": "seller-call-01",
        "collector_id": "saleng-01",
        "assigned_saleng_id": "saleng-01",
        "status": "S3",
        "version": 2,
    }

    supabase_store.sellers["seller-call-01"] = {
        "seller_id": "seller-call-01",
        "display_name": "ป้าสมร",
        "phone": "089-111-2222",
    }

    orig_profile = dict(supabase_store.saleng_profiles.get("saleng-01", {}))
    supabase_store.saleng_profiles["saleng-01"].update({
        "verified": True,
        "kyc_status": "VERIFIED",
        "is_online": True,
    })

    yield

    supabase_store.orders.pop(order_id, None)
    supabase_store.sellers.pop("seller-call-01", None)
    supabase_store.saleng_profiles.pop("saleng-unverified", None)
    if orig_profile:
        supabase_store.saleng_profiles["saleng-01"] = orig_profile


def test_AC_B05_03_phone_unmasked_in_status_s3():
    """
    AC-B05-03: ในสถานะ S3..S6 ระบบเปิดเผยเบอร์โทรศัพท์จริงของผู้ขาย เพื่อให้โทรด่วนได้
    """
    order_id = "order-call-01"
    resp = client.get(f"/api/v1/collectors/chat/{order_id}/messages?saleng_id=saleng-01")
    assert resp.status_code == 200
    data = resp.json()
    assert data["order_status"] == "S3"
    assert data["seller_info"]["phone_masked"] is False
    assert data["seller_info"]["phone"] == "089-111-2222"


def test_AC_B05_03_log_call_audit():
    """
    AC-B05-03: เมื่อซาเล้งกดโทรด่วน ระบบบันทึกประวัติการโทรลง Audit Log ถูกต้อง (REQ-SEC-001)
    """
    order_id = "order-call-01"
    payload = {
        "saleng_id": "saleng-01",
        "dialed_phone": "089-111-2222",
    }

    resp = client.post(f"/api/v1/collectors/chat/{order_id}/call-log", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "logged"
    assert data["action"] == "COLLECTOR_INITIATED_CALL"
    assert data["order_id"] == order_id
    assert data["saleng_id"] == "saleng-01"

    # ตรวจสอบใน audit_logs
    latest_audit = supabase_store.audit_logs[-1]
    assert latest_audit["action"] == "COLLECTOR_INITIATED_CALL"
    assert latest_audit["actor_id"] == "saleng-01"
    assert latest_audit["details"]["dialed_phone"] == "089-111-2222"


def test_AC_B05_03_kyc_blocked_call():
    """
    AC-B05-03: ซาเล้งที่ยังไม่ผ่าน KYC ไม่สามารถโทรหาผู้ขายได้ (D-00-01)
    """
    order_id = "order-call-01"
    supabase_store.saleng_profiles["saleng-unverified"] = {
        "saleng_id": "saleng-unverified",
        "display_name": "ยังไม่ตรวจ",
        "phone": "089-000-0000",
        "verified": False,
        "kyc_status": "PENDING",
        "vehicle_type": "TRICYCLE",
        "current_lat": 13.7900,
        "current_lng": 100.5750,
        "is_online": True,
    }

    payload = {
        "saleng_id": "saleng-unverified",
        "dialed_phone": "089-111-2222",
    }
    resp = client.post(f"/api/v1/collectors/chat/{order_id}/call-log", json=payload)
    assert resp.status_code == 403
    assert "KYC" in resp.json()["detail"]
