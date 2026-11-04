"""
Acceptance Tests for AC-B07-03: Seller Mismatch & No-Show Dispute Reporting
(Task T-04: UC-13, REQ-FN-006, REQ-SEC-001, D-B07-01, D-B07-02)
"""

import pytest
from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_mismatch_environment():
    """เตรียมข้อมูลคำขอขายสำหรับการทดสอบรายงานข้อพิพาทหน้างาน"""
    order_s3 = "order-b07-ac03-s3"
    order_s4 = "order-b07-ac03-s4"
    order_s7 = "order-b07-ac03-s7"

    supabase_store.orders[order_s3] = {
        "order_id": order_s3,
        "seller_id": "seller-01",
        "saleng_id": "saleng-01",
        "buyer_id": "saleng-01",
        "status": "S3",
        "active_collector_lock": True,
    }

    supabase_store.orders[order_s4] = {
        "order_id": order_s4,
        "seller_id": "seller-02",
        "saleng_id": "saleng-01",
        "buyer_id": "saleng-01",
        "status": "S4",
        "active_collector_lock": True,
    }

    supabase_store.orders[order_s7] = {
        "order_id": order_s7,
        "seller_id": "seller-03",
        "saleng_id": "saleng-01",
        "buyer_id": "saleng-01",
        "status": "S7",
        "active_collector_lock": False,
    }

    orig_profile = dict(supabase_store.saleng_profiles.get("saleng-01", {}))
    supabase_store.saleng_profiles["saleng-01"].update({
        "verified": True,
        "kyc_status": "VERIFIED",
    })

    yield

    supabase_store.orders.pop(order_s3, None)
    supabase_store.orders.pop(order_s4, None)
    supabase_store.orders.pop(order_s7, None)
    if orig_profile:
        supabase_store.saleng_profiles["saleng-01"] = orig_profile


def test_AC_B07_03_report_no_show_from_s3():
    """รายงานกรณีผู้ขายไม่อยู่บ้าน (No-show) ในสถานะ S3 เปลี่ยนเป็น S8 และปลดล็อกซาเล้ง (D-B07-01, D-B07-02)"""
    order_id = "order-b07-ac03-s3"
    payload = {
        "saleng_id": "saleng-01",
        "order_id": order_id,
        "mismatch_reason": "SELLER_NO_SHOW",
        "evidence_photo_url": "https://storage.saleng.app/disputes/no-show-s3.jpg",
        "notes": "เดินทางไปถึงหน้าบ้านตามเวลานัดแล้ว โทรติดต่อผู้ขาย 3 ครั้งไม่มีผู้รับสาย",
        "current_lat": 13.7563,
        "current_lng": 100.5018,
    }
    resp = client.post("/api/v1/collectors/post-job/report-mismatch", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["new_status"] == "S8"
    assert data["dispute_id"].startswith("DISP-")

    # ตรวจสอบสถานะคำขอใน Database
    order = supabase_store.get_order(order_id)
    assert order["status"] == "S8"
    assert order["active_collector_lock"] is False
    assert order["dispute_id"] == data["dispute_id"]

    # ตรวจสอบ Audit Log
    logs = [log for log in supabase_store.audit_logs if log.get("action") == "COLLECTOR_REPORTED_MISMATCH"]
    assert len(logs) > 0
    assert logs[-1]["entity_id"] == order_id


def test_AC_B07_03_report_contaminated_scrap_from_s4():
    """รายงานกรณีของปนเปื้อนอันตราย/ไม่ตรงสเปกในสถานะ S4 เปลี่ยนเป็น S8 (REQ-FN-006)"""
    order_id = "order-b07-ac03-s4"
    payload = {
        "saleng_id": "saleng-01",
        "order_id": order_id,
        "mismatch_reason": "CONTAMINATED_WASTE",
        "evidence_photo_url": "https://storage.saleng.app/disputes/contaminated.jpg",
        "notes": "พบสารเคมีอันตรายและเศษแก้วแตกปนเปื้อนในกองกระดาษ",
    }
    resp = client.post("/api/v1/collectors/post-job/report-mismatch", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["new_status"] == "S8"

    order = supabase_store.get_order(order_id)
    assert order["status"] == "S8"


def test_AC_B07_03_reject_reporting_from_completed_order():
    """ปฏิเสธการรายงานข้อพิพาทหากคำขอปิดงานไปแล้ว (S7)"""
    order_id = "order-b07-ac03-s7"
    payload = {
        "saleng_id": "saleng-01",
        "order_id": order_id,
        "mismatch_reason": "OTHER",
        "evidence_photo_url": "https://storage.saleng.app/disputes/disp.jpg",
    }
    resp = client.post("/api/v1/collectors/post-job/report-mismatch", json=payload)
    assert resp.status_code == 400
    assert "S7" in resp.json()["detail"]


def test_AC_B07_03_reject_without_evidence_photo():
    """ปฏิเสธหากไม่มีภาพถ่ายหน้างานเป็นหลักฐาน (REQ-FN-006)"""
    order_id = "order-b07-ac03-s3"
    payload = {
        "saleng_id": "saleng-01",
        "order_id": order_id,
        "mismatch_reason": "SELLER_NO_SHOW",
        "evidence_photo_url": "",  # Empty photo
    }
    resp = client.post("/api/v1/collectors/post-job/report-mismatch", json=payload)
    assert resp.status_code == 422

