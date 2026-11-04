"""
Test Suite for AC-A03-03: Dispute Resolution to Complete (RESOLVE_COMPLETE -> S7)
รองรับ UC-13, D-A03-01, D-A03-05, REQ-SEC-001, CC-03, CC-04
"""

import pytest
from datetime import datetime, timezone
from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)
ADMIN_HEADER = {"X-Admin-Role": "ADMIN"}


@pytest.fixture(autouse=True)
def setup_teardown_resolve_complete_data():
    """เตรียมข้อมูลและคืนค่าเดิมหลังทดสอบ"""
    created_disputes = []
    created_orders = []
    created_receipts = []
    yield {
        "disputes": created_disputes,
        "orders": created_orders,
        "receipts": created_receipts,
    }
    for disp_id in created_disputes:
        supabase_store.dispute_reports.pop(disp_id, None)
    for oid in created_orders:
        supabase_store.orders.pop(oid, None)
    for rid in created_receipts:
        supabase_store.receipts.pop(rid, None)


def test_AC_A03_03_resolve_dispute_complete_success(setup_teardown_resolve_complete_data):
    """
    AC-A03-03: แอดมินตัดสินชี้ขาดให้จบงาน (RESOLVE_COMPLETE)
    - คำขอเปลี่ยนจาก S8 เป็น S7 (Completed)
    - ระบุยอดเงินชี้ขาดสุทธิ Arbitrated Amount = 230 บาท
    - ระบบออกใบเสร็จดิจิทัลตามยอดเงินชี้ขาด
    - บันทึก Audit Log ADMIN_RESOLVED_DISPUTE
    """
    disp_id = "DISP-RESOLVE-COMP-01"
    order_id = "order-resolve-comp-01"
    setup_teardown_resolve_complete_data["disputes"].append(disp_id)
    setup_teardown_resolve_complete_data["orders"].append(order_id)
    setup_teardown_resolve_complete_data["receipts"].append(f"REC-DISP-{disp_id}")

    now_iso = datetime.now(timezone.utc).isoformat()
    supabase_store.orders[order_id] = {
        "order_id": order_id,
        "seller_id": "seller-02",
        "status": "S8",
        "assigned_saleng_id": "saleng-01",
        "buyer_id": "saleng-01",
        "total_est_min_price": 200.0,
        "total_est_max_price": 300.0,
        "created_at": now_iso,
        "version": 2,
    }
    supabase_store.dispute_reports[disp_id] = {
        "dispute_id": disp_id,
        "order_id": order_id,
        "seller_id": "seller-02",
        "buyer_id": "saleng-01",
        "dispute_reason": "ผู้ขายไม่เห็นด้วยกับการหักค่าความชื้น 15%",
        "status": "PENDING_ADMIN",
        "re_quoted_price": 210.0,
        "created_at": now_iso,
    }

    payload = {
        "action": "RESOLVE_COMPLETE",
        "arbitrated_amount": 230.0,
        "arbitration_note": "แอดมินพิจารณาให้ประนีประนอมที่ยอด 230 บาท",
        "admin_id": "admin-01",
    }
    resp = client.post(f"/api/v1/admin/disputes/{disp_id}/resolve", json=payload, headers=ADMIN_HEADER)
    assert resp.status_code == 200
    res_data = resp.json()

    assert res_data["success"] is True
    assert res_data["dispute_id"] == disp_id
    assert res_data["order_status"] == "S7"
    assert res_data["dispute_status"] == "RESOLVED_COMPLETED"
    assert res_data["arbitrated_amount"] == 230.0
    assert "receipt" in res_data
    assert res_data["receipt"]["total_amount"] == 230.0
    assert res_data["receipt"]["status"] == "ISSUED"

    # ตรวจสอบ Order ใน Store เปลี่ยนเป็น S7
    stored_order = supabase_store.orders[order_id]
    assert stored_order["status"] == "S7"
    assert stored_order["final_price"] == 230.0

    # ตรวจสอบ Dispute ใน Store
    stored_disp = supabase_store.dispute_reports[disp_id]
    assert stored_disp["status"] == "RESOLVED_COMPLETED"
    assert stored_disp["arbitrated_amount"] == 230.0
    assert stored_disp["arbitrated_by"] == "admin-01"

    # ตรวจสอบ Audit Log
    audit = next((a for a in supabase_store.audit_logs if a.get("action") == "ADMIN_RESOLVED_DISPUTE" and a.get("entity_id") == disp_id), None)
    assert audit is not None
    assert audit["details"]["arbitrated_amount"] == 230.0


def test_AC_A03_03_resolve_complete_missing_or_negative_amount(setup_teardown_resolve_complete_data):
    """
    AC-A03-03: การตัดสินให้จบงานโดยไม่ระบุยอดเงิน หรือระบุยอดเงิน <= 0 ต้องถูกปฏิเสธ (422 Unprocessable Entity)
    """
    disp_id = "DISP-RESOLVE-INVALID-01"
    order_id = "order-resolve-invalid-01"
    setup_teardown_resolve_complete_data["disputes"].append(disp_id)
    setup_teardown_resolve_complete_data["orders"].append(order_id)

    now_iso = datetime.now(timezone.utc).isoformat()
    supabase_store.orders[order_id] = {"order_id": order_id, "status": "S8"}
    supabase_store.dispute_reports[disp_id] = {
        "dispute_id": disp_id,
        "order_id": order_id,
        "status": "PENDING_ADMIN",
    }

    # กรณีไม่มี arbitrated_amount
    resp_no_amt = client.post(
        f"/api/v1/admin/disputes/{disp_id}/resolve",
        json={"action": "RESOLVE_COMPLETE"},
        headers=ADMIN_HEADER,
    )
    assert resp_no_amt.status_code == 422

    # กรณี arbitrated_amount <= 0
    resp_neg_amt = client.post(
        f"/api/v1/admin/disputes/{disp_id}/resolve",
        json={"action": "RESOLVE_COMPLETE", "arbitrated_amount": 0.0},
        headers=ADMIN_HEADER,
    )
    assert resp_neg_amt.status_code == 422


def test_AC_A03_03_resolve_already_resolved_dispute(setup_teardown_resolve_complete_data):
    """
    AC-A03-03: ข้อพิพาทที่ได้รับการตัดสินไปแล้ว จะไม่สามารถตัดสินซ้ำได้ (409 Conflict)
    """
    disp_id = "DISP-ALREADY-RESOLVED-01"
    order_id = "order-already-resolved-01"
    setup_teardown_resolve_complete_data["disputes"].append(disp_id)
    setup_teardown_resolve_complete_data["orders"].append(order_id)

    supabase_store.orders[order_id] = {"order_id": order_id, "status": "S7"}
    supabase_store.dispute_reports[disp_id] = {
        "dispute_id": disp_id,
        "order_id": order_id,
        "status": "RESOLVED_COMPLETED",
        "arbitrated_amount": 200.0,
    }

    payload = {
        "action": "RESOLVE_COMPLETE",
        "arbitrated_amount": 250.0,
        "arbitration_note": "พยายามตัดสินซ้ำ",
    }
    resp = client.post(f"/api/v1/admin/disputes/{disp_id}/resolve", json=payload, headers=ADMIN_HEADER)
    assert resp.status_code == 409
    assert "ได้รับการตัดสินแล้ว" in resp.json()["detail"]

