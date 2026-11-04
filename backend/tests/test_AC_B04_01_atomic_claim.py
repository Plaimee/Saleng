"""
Acceptance Tests for AC-B04-01: Single Collector Atomic Claim
(Task T-02: UC-04, BR-02, REQ-BR-002, CC-04, AC-04-05, D-B04-01, D-B04-05)
"""

import pytest
from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_environment_state():
    """ทำความสะอาดและคืนค่าสถานะซาเล้งและคำขอขายก่อนและหลังการทดสอบ"""
    orig_order = supabase_store.orders.get("order-s2-01")
    orig_status = orig_order.get("status") if orig_order else "S2"
    orig_version = orig_order.get("version") if orig_order else 1
    orig_collector = orig_order.get("collector_id") if orig_order else None
    orig_assigned = orig_order.get("assigned_saleng_id") if orig_order else None

    # รีเซ็ตให้อยู่ในสถานะ S2 รอรับงาน
    if "order-s2-01" in supabase_store.orders:
        supabase_store.orders["order-s2-01"]["status"] = "S2"
        supabase_store.orders["order-s2-01"]["version"] = 1
        supabase_store.orders["order-s2-01"]["collector_id"] = None
        supabase_store.orders["order-s2-01"]["assigned_saleng_id"] = None

    orig_profile = supabase_store.saleng_profiles.get("saleng-01")
    orig_verified = orig_profile.get("verified", True) if orig_profile else True
    orig_kyc = orig_profile.get("kyc_status", "VERIFIED") if orig_profile else "VERIFIED"
    orig_online = orig_profile.get("is_online", True) if orig_profile else True
    supabase_store.set_saleng_current_load("saleng-01", 0.0)

    yield

    if "order-s2-01" in supabase_store.orders:
        supabase_store.orders["order-s2-01"]["status"] = orig_status
        supabase_store.orders["order-s2-01"]["version"] = orig_version
        supabase_store.orders["order-s2-01"]["collector_id"] = orig_collector
        supabase_store.orders["order-s2-01"]["assigned_saleng_id"] = orig_assigned

    if "saleng-01" in supabase_store.saleng_profiles:
        supabase_store.saleng_profiles["saleng-01"]["verified"] = orig_verified
        supabase_store.saleng_profiles["saleng-01"]["kyc_status"] = orig_kyc
        supabase_store.saleng_profiles["saleng-01"]["is_online"] = orig_online
    supabase_store.set_saleng_current_load("saleng-01", 0.0)


def test_AC_B04_01_atomic_claim_success():
    """
    Given: คำขอขาย order-s2-01 อยู่ในสถานะ S2 (version = 1)
    When: ซาเล้ง saleng-01 (ผ่าน KYC, สถานะ Online, น้ำหนักไม่เกิน) กดรับงาน
    Then: สถานะคำขอเปลี่ยนเป็น S3, version กลายเป็น 2, ผูกกับ saleng-01
    And: ระบบเปิดเผยบ้านเลขที่จริง, พิกัดจริง, และเบอร์โทรผู้ขาย (REQ-SEC-002, D-00-02)
    And: ระบบส่งคืน navigation_url สำหรับเปิด Google Maps (D-B04-03)
    """
    res = client.post(
        "/api/v1/collectors/jobs/order-s2-01/claim",
        json={"saleng_id": "saleng-01", "expected_version": 1},
    )
    assert res.status_code == 200, f"Got error: {res.text}"
    data = res.json()

    assert data["order_id"] == "order-s2-01"
    assert data["status"] == "S3"
    assert data["collector_id"] == "saleng-01"
    assert data["version"] == 2
    assert "123/45" in data["address_text"]
    assert data["dest_lat"] == 13.7930
    assert data["dest_lng"] == 100.5780
    assert data["seller_phone"] != ""
    assert "https://www.google.com/maps/dir/?api=1" in data["navigation_url"]


def test_AC_B04_01_atomic_claim_conflict_raises_409():
    """
    Given: ซาเล้ง saleng-01 กดรับงาน order-s2-01 ไปแล้ว (สถานะเปลี่ยนเป็น S3, version = 2)
    When: ซาเล้งคนที่สอง saleng-02 กดรับงานคำขอเดียวกันด้วย expected_version = 1
    Then: ระบบป้องกันการรับงานซ้ำซ้อนด้วย Optimistic Concurrency Control (OCC)
    And: ตอบกลับ HTTP 409 Conflict พร้อมข้อความ "มีผู้รับงานนี้แล้ว" (AC-04-05, BR-02)
    """
    # ซาเล้งคนแรกรับงานสำเร็จ
    res1 = client.post(
        "/api/v1/collectors/jobs/order-s2-01/claim",
        json={"saleng_id": "saleng-01", "expected_version": 1},
    )
    assert res1.status_code == 200

    # ซาเล้งคนที่สองกดรับงานเดียวกัน
    res2 = client.post(
        "/api/v1/collectors/jobs/order-s2-01/claim",
        json={"saleng_id": "saleng-02", "expected_version": 1},
    )
    assert res2.status_code == 409
    data2 = res2.json()
    assert data2["detail"] == "มีผู้รับงานนี้แล้ว"


def test_AC_B04_01_unverified_and_offline_collector_cannot_claim():
    """
    ทดสอบการบล็อกการกดรับงานสำหรับซาเล้งที่ยังไม่ผ่าน KYC หรือปิดสถานะ Offline (D-00-01, CC-02)
    """
    # 1. ทดสอบซาเล้งยังไม่ผ่าน KYC -> 403 Forbidden
    supabase_store.saleng_profiles["saleng-01"]["verified"] = False
    supabase_store.saleng_profiles["saleng-01"]["kyc_status"] = "UNVERIFIED"

    res_kyc = client.post(
        "/api/v1/collectors/jobs/order-s2-01/claim",
        json={"saleng_id": "saleng-01", "expected_version": 1},
    )
    assert res_kyc.status_code == 403
    assert "KYC" in res_kyc.json()["detail"]

    # คืนค่า KYC
    supabase_store.saleng_profiles["saleng-01"]["verified"] = True
    supabase_store.saleng_profiles["saleng-01"]["kyc_status"] = "VERIFIED"

    # 2. ทดสอบซาเล้งสถานะ Offline -> 400 Bad Request
    supabase_store.saleng_profiles["saleng-01"]["is_online"] = False

    res_offline = client.post(
        "/api/v1/collectors/jobs/order-s2-01/claim",
        json={"saleng_id": "saleng-01", "expected_version": 1},
    )
    assert res_offline.status_code == 400
    assert "ออนไลน์" in res_offline.json()["detail"]
