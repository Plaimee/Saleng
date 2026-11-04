"""
Test Suite for T-01: Dispatch & Dispute Data Models, Pydantic Validation, and Store Methods
รองรับ UC-13, REQ-DAT-001, CC-04, D-A03-01..06
"""

import pytest
from pydantic import ValidationError
from datetime import datetime, timezone, timedelta
from backend.app.models.dispatch_dispute_models import (
    StalledOrderItem,
    ManualDispatchAssignRequest,
    ManualDispatchResponse,
    ExpandDispatchRadiusRequest,
    ExpandRadiusResponse,
    DisputeSummaryItem,
    DisputeDossierResponse,
    ResolveDisputeAction,
    ResolveDisputeRequest,
    ResolveDisputeResponse,
)
from backend.app.core.supabase import supabase_store


def test_stalled_order_item_model():
    """ทดสอบ Schema ของ StalledOrderItem"""
    item = StalledOrderItem(
        order_id="order-s2-stalled-01",
        seller_id="seller-01",
        status="S2",
        created_at=datetime.now(timezone.utc).isoformat(),
        waiting_minutes=45.2,
        subdistrict="แขวงห้วยขวาง",
        district="เขตห้วยขวาง",
        total_est_min_price=200.0,
        total_est_max_price=350.0,
        total_est_weight_kg=40.0,
        search_radius_km=5.0,
        is_manual_dispatched=False,
    )
    assert item.order_id == "order-s2-stalled-01"
    assert item.waiting_minutes == 45.2
    assert item.search_radius_km == 5.0
    assert item.is_manual_dispatched is False


def test_manual_dispatch_assign_request_validation():
    """ทดสอบ Validation ของ ManualDispatchAssignRequest"""
    req = ManualDispatchAssignRequest(
        order_id="order-s2-01",
        saleng_id="saleng-01",
        admin_id="admin-01",
        notes="มอบหมายงานกรณีพิเศษ",
    )
    assert req.order_id == "order-s2-01"
    assert req.saleng_id == "saleng-01"

    # ห้ามค่าว่าง
    with pytest.raises(ValidationError):
        ManualDispatchAssignRequest(order_id="", saleng_id="saleng-01")
    with pytest.raises(ValidationError):
        ManualDispatchAssignRequest(order_id="order-01", saleng_id="   ")


def test_expand_dispatch_radius_request_validation():
    """ทดสอบ Validation ของ ExpandDispatchRadiusRequest (ต้อง > 5.0 กม.)"""
    req = ExpandDispatchRadiusRequest(
        order_id="order-s2-01",
        new_radius_km=10.0,
    )
    assert req.new_radius_km == 10.0

    # ถ้ารัศมี <= 5.0 ต้องเกิด ValidationError
    with pytest.raises(ValidationError):
        ExpandDispatchRadiusRequest(order_id="order-s2-01", new_radius_km=5.0)
    with pytest.raises(ValidationError):
        ExpandDispatchRadiusRequest(order_id="order-s2-01", new_radius_km=3.0)


def test_resolve_dispute_request_validation():
    """ทดสอบ Validation ของ ResolveDisputeRequest ตามเงื่อนไขของ Action"""
    # 1. RESOLVE_COMPLETE ต้องระบุ arbitrated_amount > 0
    req_complete = ResolveDisputeRequest(
        action=ResolveDisputeAction.RESOLVE_COMPLETE,
        arbitrated_amount=250.0,
        arbitration_note="ยอมรับราคาชั่งจริง 250 บาท",
    )
    assert req_complete.action == ResolveDisputeAction.RESOLVE_COMPLETE
    assert req_complete.arbitrated_amount == 250.0

    # RESOLVE_COMPLETE ขาด arbitrated_amount หรือ <= 0 ต้อง Error
    with pytest.raises(ValidationError):
        ResolveDisputeRequest(
            action=ResolveDisputeAction.RESOLVE_COMPLETE,
            arbitrated_amount=None,
        )
    with pytest.raises(ValidationError):
        ResolveDisputeRequest(
            action=ResolveDisputeAction.RESOLVE_COMPLETE,
            arbitrated_amount=-10.0,
        )

    # 2. RESOLVE_CANCEL ต้องมี arbitration_note ระบุเหตุผล
    req_cancel = ResolveDisputeRequest(
        action=ResolveDisputeAction.RESOLVE_CANCEL,
        arbitration_note="คู่กรณีตกลงยกเลิกการซื้อขาย",
    )
    assert req_cancel.action == ResolveDisputeAction.RESOLVE_CANCEL

    with pytest.raises(ValidationError):
        ResolveDisputeRequest(
            action=ResolveDisputeAction.RESOLVE_CANCEL,
            arbitration_note="",
        )


def test_store_get_stalled_orders():
    """ทดสอบเมธอด get_stalled_orders ใน SupabaseStore"""
    stalled = supabase_store.get_stalled_orders(min_wait_minutes=30.0)
    assert isinstance(stalled, list)
    # ควรพบ order-s2-stalled-01 ที่ seed ไว้ 45 นาที
    stalled_ids = [s["order_id"] for s in stalled]
    assert "order-s2-stalled-01" in stalled_ids

    # ตรวจสอบฟิลด์ที่ส่งกลับ
    stalled_item = next(s for s in stalled if s["order_id"] == "order-s2-stalled-01")
    assert stalled_item["status"] == "S2"
    assert stalled_item["waiting_minutes"] >= 30.0
    assert stalled_item["subdistrict"] == "แขวงห้วยขวาง"


def test_store_manual_dispatch_and_expand_radius():
    """ทดสอบเมธอด manual_dispatch_order และ expand_order_search_radius"""
    # สร้าง Order S2 ชั่วคราว
    test_order_id = "test-order-dispatch-01"
    now_iso = (datetime.now(timezone.utc) - timedelta(minutes=40)).isoformat()
    supabase_store.orders[test_order_id] = {
        "order_id": test_order_id,
        "seller_id": "seller-01",
        "location_id": "loc-s2-stalled-01",
        "status": "S2",
        "total_est_min_price": 100.0,
        "total_est_max_price": 150.0,
        "search_radius_km": 5.0,
        "created_at": now_iso,
        "version": 1,
    }

    try:
        # 1. ทดสอบขยายรัศมีเป็น 10.0 กม.
        ok_exp, res_exp, msg_exp = supabase_store.expand_order_search_radius(
            order_id=test_order_id,
            new_radius_km=10.0,
            admin_id="admin-01",
        )
        assert ok_exp is True
        assert res_exp["new_radius_km"] == 10.0
        assert supabase_store.orders[test_order_id]["search_radius_km"] == 10.0

        # 2. ทดสอบมอบหมายงานตรงให้ saleng-01
        ok_disp, res_disp, msg_disp = supabase_store.manual_dispatch_order(
            order_id=test_order_id,
            saleng_id="saleng-01",
            admin_id="admin-01",
            notes="ทดสอบมอบหมายงานตรง",
        )
        assert ok_disp is True
        assert res_disp["status"] == "S3"
        assert res_disp["assigned_saleng_id"] == "saleng-01"
        assert res_disp["is_manual_dispatched"] is True

        # ทดสอบ Concurrency / Status check (เมื่อเป็น S3 แล้วจะมอบหมายซ้ำไม่ได้)
        ok_dup, _, msg_dup = supabase_store.manual_dispatch_order(
            order_id=test_order_id,
            saleng_id="saleng-01",
        )
        assert ok_dup is False
        assert "ไม่ได้อยู่ในสถานะรอผู้รับงาน (S2)" in msg_dup

    finally:
        supabase_store.orders.pop(test_order_id, None)


def test_store_dispute_dossier_and_resolution():
    """ทดสอบเมธอด get_disputes, get_dispute_dossier, และ resolve_dispute"""
    # ตรวจสอบ dispute ที่ seed ไว้
    disputes = supabase_store.get_disputes(status_filter="PENDING_ADMIN")
    assert len(disputes) >= 1
    disp_id = disputes[0]["dispute_id"]

    # 1. ตรวจสอบสำนวนหลักฐาน 4 มิติ
    dossier = supabase_store.get_dispute_dossier(disp_id)
    assert dossier is not None
    assert dossier["dispute_id"] == disp_id
    assert "original_order" in dossier
    assert "saleng_verification" in dossier
    assert "seller_dispute" in dossier
    assert "parties_contact" in dossier
    assert dossier["original_order"]["price_snapshot"] is not None

    # สร้าง Dispute ชั่วคราวสำหรับการตัดสิน
    temp_disp_id = "DISP-TEST-TEMP-001"
    temp_order_id = "order-test-disp-001"
    now_iso = datetime.now(timezone.utc).isoformat()
    supabase_store.orders[temp_order_id] = {
        "order_id": temp_order_id,
        "seller_id": "seller-02",
        "location_id": "loc-s2-02",
        "status": "S8",
        "assigned_saleng_id": "saleng-01",
        "buyer_id": "saleng-01",
        "total_est_min_price": 200.0,
        "total_est_max_price": 300.0,
        "version": 1,
    }
    supabase_store.dispute_reports[temp_disp_id] = {
        "dispute_id": temp_disp_id,
        "order_id": temp_order_id,
        "seller_id": "seller-02",
        "buyer_id": "saleng-01",
        "dispute_reason": "ทดสอบข้อพิพาท",
        "status": "PENDING_ADMIN",
        "re_quoted_price": 180.0,
        "created_at": now_iso,
    }

    try:
        # ตัดสินชี้ขาดให้จบงาน (RESOLVE_COMPLETE -> S7)
        ok_res, res_data, msg_res = supabase_store.resolve_dispute(
            dispute_id=temp_disp_id,
            action="RESOLVE_COMPLETE",
            arbitrated_amount=190.0,
            arbitration_note="ตัดสินให้จบงานที่ยอด 190 บาท",
            admin_id="admin-01",
        )
        assert ok_res is True
        assert res_data["order_status"] == "S7"
        assert res_data["arbitrated_amount"] == 190.0
        assert supabase_store.orders[temp_order_id]["status"] == "S7"
        assert supabase_store.orders[temp_order_id]["final_price"] == 190.0

        # ตรวจสอบการออกใบเสร็จ
        assert "receipt" in res_data
        assert res_data["receipt"]["total_amount"] == 190.0
        assert res_data["receipt"]["status"] == "ISSUED"

        # ตรวจสอบ Audit Log
        audit = next((a for a in supabase_store.audit_logs if a.get("action") == "ADMIN_RESOLVED_DISPUTE" and a.get("entity_id") == temp_disp_id), None)
        assert audit is not None
        assert audit["details"]["arbitrated_amount"] == 190.0
    finally:
        supabase_store.dispute_reports.pop(temp_disp_id, None)
        supabase_store.orders.pop(temp_order_id, None)
        receipt_id = f"REC-DISP-{temp_disp_id}"
        supabase_store.receipts.pop(receipt_id, None)

