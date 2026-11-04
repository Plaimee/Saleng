"""
Test Suite for AC-A03-04: Dispute Resolution to Cancel (RESOLVE_CANCEL -> S9)
รองรับ UC-13, D-A03-01, D-A03-05, REQ-SEC-001, CC-03
"""

import pytest
from datetime import datetime, timezone
from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)
ADMIN_HEADER = {"X-Admin-Role": "ADMIN"}


@pytest.fixture(autouse=True)
def setup_teardown_resolve_cancel_data():
    """เตรียมข้อมูลและคืนค่าเดิมหลังทดสอบ"""
    created_disputes = []
    created_orders = []
    yield {"disputes": created_disputes, "orders": created_orders}
    for disp_id in created_disputes:
        supabase_store.dispute_reports.pop(disp_id, None)
    for oid in created_orders:
        supabase_store.orders.pop(oid, None)


def test_AC_A03_04_resolve_dispute_cancel_success(setup_teardown_resolve_cancel_data):
    """
    AC-A03-04: แอดมินตัดสินสั่งยกเลิกคำขอ (RESOLVE_CANCEL)
    - คำขอเปลี่ยนจาก S8 เป็น S9 (Cancelled)
    - ไม่มีการออกใบเสร็จหรือชำระเงิน
    - บันทึกเหตุผลการยกเลิกใน cancellation_reason
    - บันทึก Audit Log ADMIN_CANCELLED_DISPUTE
    """
    disp_id = "DISP-RESOLVE-CANCEL-01"
    order_id = "order-resolve-cancel-01"
    setup_teardown_resolve_cancel_data["disputes"].append(disp_id)
    setup_teardown_resolve_cancel_data["orders"].append(order_id)

    now_iso = datetime.now(timezone.utc).isoformat()
    supabase_store.orders[order_id] = {
        "order_id": order_id,
        "seller_id": "seller-03",
        "status": "S8",
        "assigned_saleng_id": "saleng-01",
        "buyer_id": "saleng-01",
        "created_at": now_iso,
        "version": 2,
    }
    supabase_store.dispute_reports[disp_id] = {
        "dispute_id": disp_id,
        "order_id": order_id,
        "seller_id": "seller-03",
        "buyer_id": "saleng-01",
        "dispute_reason": "ขยะปนเปื้อนสารเคมีอันตราย ซาเล้งไม่สามารถรับซื้อได้",
        "status": "PENDING_ADMIN",
        "created_at": now_iso,
    }

    payload = {
        "action": "RESOLVE_CANCEL",
        "arbitration_note": "ขยะไม่ตรงตามเกณฑ์และมีความอันตราย สั่งยกเลิกคำขอ",
        "admin_id": "admin-01",
    }
    resp = client.post(f"/api/v1/admin/disputes/{disp_id}/resolve", json=payload, headers=ADMIN_HEADER)
    assert resp.status_code == 200
    res_data = resp.json()

    assert res_data["success"] is True
    assert res_data["dispute_id"] == disp_id
    assert res_data["order_status"] == "S9"
    assert res_data["dispute_status"] == "RESOLVED_CANCELLED"
    assert res_data["receipt"] is None

    # ตรวจสอบ Order ใน Store เปลี่ยนเป็น S9
    stored_order = supabase_store.orders[order_id]
    assert stored_order["status"] == "S9"
    assert "ขยะไม่ตรงตามเกณฑ์" in stored_order.get("cancelled_reason", "")

    # ตรวจสอบ Dispute ใน Store
    stored_disp = supabase_store.dispute_reports[disp_id]
    assert stored_disp["status"] == "RESOLVED_CANCELLED"
    assert stored_disp["arbitrated_by"] == "admin-01"

    # ตรวจสอบ Audit Log
    audit = next((a for a in supabase_store.audit_logs if a.get("action") == "ADMIN_CANCELLED_DISPUTE" and a.get("entity_id") == disp_id), None)
    assert audit is not None
    assert "ขยะไม่ตรงตามเกณฑ์" in audit["details"]["cancellation_reason"]


def test_AC_A03_04_resolve_cancel_missing_note(setup_teardown_resolve_cancel_data):
    """
    AC-A03-04: การสั่งยกเลิกโดยไม่ระบุเหตุผล ต้องถูกปฏิเสธ (422 Unprocessable Entity)
    """
    disp_id = "DISP-CANCEL-NO-NOTE"
    setup_teardown_resolve_cancel_data["disputes"].append(disp_id)

    payload = {
        "action": "RESOLVE_CANCEL",
        "arbitration_note": "",
    }
    resp = client.post(f"/api/v1/admin/disputes/{disp_id}/resolve", json=payload, headers=ADMIN_HEADER)
    assert resp.status_code == 422

