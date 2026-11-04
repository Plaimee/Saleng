"""
Test Suite for AC-A03-05: Admin RBAC & Dispute Audit Trail
รองรับ REQ-SEC-001, CC-03, CC-05, D-A03-06
"""

import pytest
from datetime import datetime, timezone
from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)
ADMIN_HEADER = {"X-Admin-Role": "ADMIN"}
INVALID_HEADERS = [
    {},
    {"X-Admin-Role": "SELLER"},
    {"X-Admin-Role": "BUYER"},
    {"X-Admin-Role": "GUEST"},
    {"X-Admin-Role": ""},
]


def test_AC_A03_05_rbac_forbidden_on_all_endpoints():
    """
    AC-A03-05 / CC-03: ปฏิเสธคำขอที่ไม่มี Header X-Admin-Role: ADMIN ด้วย HTTP 403 Forbidden
    """
    endpoints = [
        ("GET", "/api/v1/admin/dispatch/stalled-orders"),
        ("POST", "/api/v1/admin/dispatch/assign", {"order_id": "ord-1", "saleng_id": "sal-1"}),
        ("POST", "/api/v1/admin/dispatch/expand-radius", {"order_id": "ord-1", "new_radius_km": 10.0}),
        ("GET", "/api/v1/admin/disputes"),
        ("GET", "/api/v1/admin/disputes/DISP-1"),
        ("POST", "/api/v1/admin/disputes/DISP-1/resolve", {"action": "RESOLVE_COMPLETE", "arbitrated_amount": 100.0}),
    ]

    for method, url, *payload in endpoints:
        data = payload[0] if payload else None
        for invalid_h in INVALID_HEADERS:
            if method == "GET":
                resp = client.get(url, headers=invalid_h)
            else:
                resp = client.post(url, json=data, headers=invalid_h)
            assert resp.status_code == 403, f"Endpoint {method} {url} with header {invalid_h} returned {resp.status_code}, expected 403"
            assert "สิทธิ์ไม่ถูกต้อง" in resp.json()["detail"]


def test_AC_A03_05_audit_logs_append_only_integrity():
    """
    AC-A03-05 / REQ-SEC-001: ตรวจสอบว่าทุกแอ็กชันบันทึกลง audit_logs แบบครบถ้วนทั้ง 4 แอ็กชัน
    1. ADMIN_MANUAL_DISPATCH
    2. ADMIN_EXPAND_DISPATCH_RADIUS
    3. ADMIN_RESOLVED_DISPUTE
    4. ADMIN_CANCELLED_DISPUTE
    """
    initial_log_count = len(supabase_store.audit_logs)

    # 1. ทดสอบบันทึก ADMIN_MANUAL_DISPATCH
    order_id = "test-audit-ord-01"
    now_iso = datetime.now(timezone.utc).isoformat()
    supabase_store.orders[order_id] = {
        "order_id": order_id,
        "seller_id": "seller-01",
        "status": "S2",
        "created_at": now_iso,
        "version": 1,
    }
    client.post(
        "/api/v1/admin/dispatch/assign",
        json={"order_id": order_id, "saleng_id": "saleng-01"},
        headers=ADMIN_HEADER,
    )

    # 2. ทดสอบบันทึก ADMIN_EXPAND_DISPATCH_RADIUS
    order_id_2 = "test-audit-ord-02"
    supabase_store.orders[order_id_2] = {
        "order_id": order_id_2,
        "seller_id": "seller-01",
        "status": "S2",
        "created_at": now_iso,
        "version": 1,
    }
    client.post(
        "/api/v1/admin/dispatch/expand-radius",
        json={"order_id": order_id_2, "new_radius_km": 10.0},
        headers=ADMIN_HEADER,
    )

    # 3. ทดสอบบันทึก ADMIN_RESOLVED_DISPUTE
    disp_1 = "DISP-AUDIT-01"
    supabase_store.orders[order_id] = {"order_id": order_id, "status": "S8"}
    supabase_store.dispute_reports[disp_1] = {
        "dispute_id": disp_1,
        "order_id": order_id,
        "seller_id": "seller-01",
        "buyer_id": "saleng-01",
        "status": "PENDING_ADMIN",
    }
    client.post(
        f"/api/v1/admin/disputes/{disp_1}/resolve",
        json={"action": "RESOLVE_COMPLETE", "arbitrated_amount": 150.0, "arbitration_note": "ปิดงาน"},
        headers=ADMIN_HEADER,
    )

    # 4. ทดสอบบันทึก ADMIN_CANCELLED_DISPUTE
    disp_2 = "DISP-AUDIT-02"
    supabase_store.orders[order_id_2] = {"order_id": order_id_2, "status": "S8"}
    supabase_store.dispute_reports[disp_2] = {
        "dispute_id": disp_2,
        "order_id": order_id_2,
        "seller_id": "seller-01",
        "buyer_id": "saleng-01",
        "status": "PENDING_ADMIN",
    }
    client.post(
        f"/api/v1/admin/disputes/{disp_2}/resolve",
        json={"action": "RESOLVE_CANCEL", "arbitration_note": "ยกเลิกงาน"},
        headers=ADMIN_HEADER,
    )

    # ตรวจสอบว่ามีบันทึกเพิ่มขึ้น 4 รายการ
    assert len(supabase_store.audit_logs) >= initial_log_count + 4

    actions = [log.get("action") for log in supabase_store.audit_logs]
    assert "ADMIN_MANUAL_DISPATCH" in actions
    assert "ADMIN_EXPAND_DISPATCH_RADIUS" in actions
    assert "ADMIN_RESOLVED_DISPUTE" in actions
    assert "ADMIN_CANCELLED_DISPUTE" in actions

    # คลีนอัพ
    supabase_store.orders.pop(order_id, None)
    supabase_store.orders.pop(order_id_2, None)
    supabase_store.dispute_reports.pop(disp_1, None)
    supabase_store.dispute_reports.pop(disp_2, None)

