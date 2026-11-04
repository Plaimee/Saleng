"""
Test Suite for AC-A03-02: Dispute Inspection Dossier Display (4 Dimensions)
รองรับ UC-13, REQ-FN-005, REQ-FN-004, D-A03-04, CC-03, CC-06
"""

import pytest
from datetime import datetime, timezone, timedelta
from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)
ADMIN_HEADER = {"X-Admin-Role": "ADMIN"}


@pytest.fixture(autouse=True)
def setup_teardown_dispute_dossier_data():
    """เตรียมข้อมูลและคืนค่าเดิมหลังทดสอบ"""
    created_disputes = []
    created_orders = []
    yield {"disputes": created_disputes, "orders": created_orders}
    for disp_id in created_disputes:
        supabase_store.dispute_reports.pop(disp_id, None)
    for oid in created_orders:
        supabase_store.orders.pop(oid, None)
        supabase_store.items.pop(f"item-{oid}", None)


def test_AC_A03_02_list_disputes_pending():
    """
    AC-A03-02: แอดมินเรียกดูรายการข้อพิพาทสถานะ PENDING_ADMIN
    - ต้องมีข้อมูลสรุป: dispute_id, order_id, seller_name, buyer_name, dispute_reason
    """
    resp = client.get("/api/v1/admin/disputes?status=PENDING_ADMIN", headers=ADMIN_HEADER)
    assert resp.status_code == 200
    disputes = resp.json()
    assert isinstance(disputes, list)
    assert len(disputes) >= 1

    seeded = next((d for d in disputes if d["dispute_id"] == "DISP-20261104-0001"), None)
    assert seeded is not None
    assert seeded["status"] == "PENDING_ADMIN"
    assert "หักสิ่งปนเปื้อนเกินจริง" in seeded["dispute_reason"]
    assert seeded["buyer_name"] is not None


def test_AC_A03_02_get_dispute_dossier_4_dimensions(setup_teardown_dispute_dossier_data):
    """
    AC-A03-02 / D-A03-04: ตรวจสอบสำนวนหลักฐาน 4 มิติครบถ้วน:
    มิติ 1: ข้อมูลคำขอเดิม & Price Snapshot
    มิติ 2: ข้อมูลหน้างานจากซาเล้ง (ภาพตาชั่ง scale_photo_url, actual_weights, re_quoted_price)
    มิติ 3: ข้อมูลข้อโต้แย้งจากผู้ขาย (dispute_reason, seller_photo_urls)
    มิติ 4: ข้อมูลคู่กรณี (parties_contact) พร้อม Masking เบอร์โทรศัพท์ (CC-06)
    """
    disp_id = "DISP-20261104-0001"
    resp = client.get(f"/api/v1/admin/disputes/{disp_id}", headers=ADMIN_HEADER)
    assert resp.status_code == 200
    dossier = resp.json()

    # ตรวจสอบภาพรวมสำนวน
    assert dossier["dispute_id"] == disp_id
    assert dossier["order_id"] == "order-dispute-01"
    assert dossier["status"] == "PENDING_ADMIN"

    # มิติ 1: Original Order & Price Snapshot
    orig = dossier["original_order"]
    assert orig["order_id"] == "order-dispute-01"
    assert "price_snapshot" in orig
    assert "MAT-PET-BOTTLE" in orig["price_snapshot"]
    assert orig["total_est_min_price"] == 300.0
    assert orig["total_est_max_price"] == 450.0

    # มิติ 2: Saleng Verification (REQ-FN-005)
    saleng_ver = dossier["saleng_verification"]
    assert saleng_ver["scale_photo_url"] is not None
    assert "scale_photo" in saleng_ver["scale_photo_url"]
    assert saleng_ver["re_quoted_price"] == 210.0
    assert saleng_ver["actual_weights"] is not None

    # มิติ 3: Seller Dispute
    seller_disp = dossier["seller_dispute"]
    assert "dispute_reason" in seller_disp
    assert len(seller_disp["dispute_reason"]) > 0
    assert "seller_photo_urls" in seller_disp

    # มิติ 4: Parties Contact & Masking (CC-06)
    parties = dossier["parties_contact"]
    assert "seller" in parties
    assert "buyer" in parties
    assert "08X-" in parties["seller"]["phone_masked"] or "X" in parties["seller"]["phone_masked"]
    assert "08X-" in parties["buyer"]["phone_masked"] or "X" in parties["buyer"]["phone_masked"]


def test_AC_A03_02_get_dispute_dossier_not_found():
    """
    AC-A03-02: ดึงสำนวนข้อพิพาทที่ไม่พบในระบบ ต้องส่งกลับ 404 Not Found
    """
    resp = client.get("/api/v1/admin/disputes/DISP-NON-EXISTENT", headers=ADMIN_HEADER)
    assert resp.status_code == 404
    assert "ไม่พบสำนวนข้อพิพาท" in resp.json()["detail"]

