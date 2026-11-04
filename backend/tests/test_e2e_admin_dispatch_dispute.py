"""
Integration E2E Test Suite for Admin Dispatch & Dispute Management (Admin Feature 03)
รองรับ UC-13, REQ-FN-005, REQ-FN-004, REQ-BR-002, REQ-SEC-001, CC-01..06, D-00-01, D-00-02, D-A03-01..06
"""

import time
import pytest
from datetime import datetime, timezone, timedelta
from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)
ADMIN_HEADER = {"X-Admin-Role": "ADMIN"}


@pytest.fixture(autouse=True)
def clean_e2e_state():
    """เตรียมข้อมูลและคืนค่าเดิมหลังทดสอบ"""
    created_orders = []
    created_disputes = []
    created_receipts = []
    yield {
        "orders": created_orders,
        "disputes": created_disputes,
        "receipts": created_receipts,
    }
    for oid in created_orders:
        supabase_store.orders.pop(oid, None)
        supabase_store.items.pop(f"item-{oid}", None)
        supabase_store.pickup_locations.pop(f"loc-{oid}", None)
    for disp_id in created_disputes:
        supabase_store.dispute_reports.pop(disp_id, None)
    for rid in created_receipts:
        supabase_store.receipts.pop(rid, None)


def test_e2e_admin_dispatch_and_dispute_complete_lifecycle(clean_e2e_state):
    """
    E2E ทดสอบครบวงจรศูนย์ควบคุมการจับคู่งานและข้อพิพาท:
    1. คัดกรองงานตกค้าง S2 > 30 นาที (AC-A03-01)
    2. ขยายรัศมีการค้นหาจาก 5.0 กม. เป็น 10.0 กม. (AC-A03-01)
    3. มอบหมายงานตรงให้ซาเล้ง (Direct Assign -> S3) (AC-A03-01, D-00-01)
    4. ตรวจสอบคิวข้อพิพาท S8 และสำนวนหลักฐาน 4 มิติ (AC-A03-02, D-A03-04)
    5. ตัดสินชี้ขาดให้จบงาน (RESOLVE_COMPLETE -> S7) พร้อมยอดเงินชี้ขาดและใบเสร็จ (AC-A03-03, D-A03-05)
    6. ตัดสินสั่งยกเลิกคำขอข้อพิพาท (RESOLVE_CANCEL -> S9) (AC-A03-04, D-A03-05)
    7. ตรวจสอบการปฏิเสธคำขอที่ไม่มีสิทธิ์แอดมิน (403 Forbidden) (AC-A03-05, CC-03)
    8. ตรวจสอบ Audit Log ครบถ้วนทั้ง 4 แอ็กชัน (AC-A03-05, REQ-SEC-001)
    """
    now = datetime.now(timezone.utc)
    stalled_order_id = "e2e-order-stalled-01"
    clean_e2e_state["orders"].append(stalled_order_id)
    t_stalled = (now - timedelta(minutes=40)).isoformat()

    supabase_store.pickup_locations[f"loc-{stalled_order_id}"] = {
        "location_id": f"loc-{stalled_order_id}",
        "seller_id": "seller-01",
        "subdistrict": "แขวงห้วยขวาง",
        "district": "เขตห้วยขวาง",
        "province": "กรุงเทพมหานคร",
        "lat": 13.7780,
        "lng": 100.5740,
    }
    supabase_store.orders[stalled_order_id] = {
        "order_id": stalled_order_id,
        "seller_id": "seller-01",
        "location_id": f"loc-{stalled_order_id}",
        "status": "S2",
        "total_est_min_price": 200.0,
        "total_est_max_price": 320.0,
        "total_est_weight_kg": 30.0,
        "search_radius_km": 5.0,
        "created_at": t_stalled,
        "version": 1,
    }

    # ========================================================
    # ขั้นที่ 1: คัดกรองงานตกค้าง S2 > 30 นาที (AC-A03-01)
    # ========================================================
    start_time = time.time()
    resp_stalled = client.get("/api/v1/admin/dispatch/stalled-orders?min_wait_minutes=30", headers=ADMIN_HEADER)
    latency = time.time() - start_time
    assert latency < 2.0, "Latency exceeds 2.0s SLO"
    assert resp_stalled.status_code == 200
    stalled_list = resp_stalled.json()
    assert any(o["order_id"] == stalled_order_id for o in stalled_list)

    # ========================================================
    # ขั้นที่ 2: ขยายรัศมีการค้นหาเป็น 10.0 กม. (AC-A03-01, D-A03-03)
    # ========================================================
    resp_expand = client.post(
        "/api/v1/admin/dispatch/expand-radius",
        json={"order_id": stalled_order_id, "new_radius_km": 10.0},
        headers=ADMIN_HEADER,
    )
    assert resp_expand.status_code == 200
    assert resp_expand.json()["new_radius_km"] == 10.0
    assert supabase_store.orders[stalled_order_id]["search_radius_km"] == 10.0

    # ========================================================
    # ขั้นที่ 3: มอบหมายงานตรงให้ซาเล้ง (Direct Assign -> S3) (AC-A03-01, D-00-01)
    # ========================================================
    resp_assign = client.post(
        "/api/v1/admin/dispatch/assign",
        json={"order_id": stalled_order_id, "saleng_id": "saleng-01"},
        headers=ADMIN_HEADER,
    )
    assert resp_assign.status_code == 200
    assert resp_assign.json()["status"] == "S3"
    assert supabase_store.orders[stalled_order_id]["status"] == "S3"
    assert supabase_store.orders[stalled_order_id]["assigned_saleng_id"] == "saleng-01"

    # ========================================================
    # ขั้นที่ 4: เกิดข้อพิพาทหน้างาน (S8) และแอดมินเปิดสำนวนหลักฐาน (AC-A03-02, D-A03-04)
    # ========================================================
    dispute_id_1 = "DISP-E2E-001"
    clean_e2e_state["disputes"].append(dispute_id_1)
    clean_e2e_state["receipts"].append(f"REC-DISP-{dispute_id_1}")

    # อัปเดตคำขอเป็น S8 (Disputed)
    supabase_store.orders[stalled_order_id]["status"] = "S8"
    supabase_store.orders[stalled_order_id]["scale_photo_url"] = "https://storage.saleng.app/disputes/scale_photo_e2e.jpg"
    supabase_store.orders[stalled_order_id]["re_quoted_price"] = 230.0

    supabase_store.dispute_reports[dispute_id_1] = {
        "dispute_id": dispute_id_1,
        "order_id": stalled_order_id,
        "seller_id": "seller-01",
        "buyer_id": "saleng-01",
        "dispute_reason": "ผู้ขายไม่ยอมรับการหักสิ่งปนเปื้อน 10% จากกระดาษลังเปียกน้ำ",
        "status": "PENDING_ADMIN",
        "re_quoted_price": 230.0,
        "scale_photo_url": "https://storage.saleng.app/disputes/scale_photo_e2e.jpg",
        "created_at": now.isoformat(),
    }

    # ตรวจสอบคิวข้อพิพาท
    resp_disp_list = client.get("/api/v1/admin/disputes", headers=ADMIN_HEADER)
    assert resp_disp_list.status_code == 200
    assert any(d["dispute_id"] == dispute_id_1 for d in resp_disp_list.json())

    # เปิดดูสำนวน 4 มิติ
    resp_dossier = client.get(f"/api/v1/admin/disputes/{dispute_id_1}", headers=ADMIN_HEADER)
    assert resp_dossier.status_code == 200
    dossier = resp_dossier.json()
    assert dossier["dispute_id"] == dispute_id_1
    assert "original_order" in dossier
    assert "saleng_verification" in dossier
    assert "seller_dispute" in dossier
    assert "parties_contact" in dossier
    assert "scale_photo" in dossier["saleng_verification"]["scale_photo_url"]

    # ========================================================
    # ขั้นที่ 5: ตัดสินชี้ขาดให้จบงาน (RESOLVE_COMPLETE -> S7) (AC-A03-03, D-A03-05)
    # ========================================================
    resp_resolve_complete = client.post(
        f"/api/v1/admin/disputes/{dispute_id_1}/resolve",
        json={
            "action": "RESOLVE_COMPLETE",
            "arbitrated_amount": 250.0,
            "arbitration_note": "แอดมินตัดสินชี้ขาดประนีประนอมที่ยอด 250 บาท",
        },
        headers=ADMIN_HEADER,
    )
    assert resp_resolve_complete.status_code == 200
    res_comp = resp_resolve_complete.json()
    assert res_comp["order_status"] == "S7"
    assert res_comp["arbitrated_amount"] == 250.0
    assert "receipt" in res_comp
    assert res_comp["receipt"]["total_amount"] == 250.0

    # ยืนยันสถานะใน Store
    assert supabase_store.orders[stalled_order_id]["status"] == "S7"
    assert supabase_store.orders[stalled_order_id]["final_price"] == 250.0
    assert supabase_store.dispute_reports[dispute_id_1]["status"] == "RESOLVED_COMPLETED"

    # ========================================================
    # ขั้นที่ 6: ตัดสินสั่งยกเลิกคำขอข้อพิพาท (RESOLVE_CANCEL -> S9) (AC-A03-04, D-A03-05)
    # ========================================================
    dispute_id_2 = "DISP-E2E-CANCEL-02"
    order_cancel_id = "e2e-order-cancel-02"
    clean_e2e_state["disputes"].append(dispute_id_2)
    clean_e2e_state["orders"].append(order_cancel_id)

    supabase_store.orders[order_cancel_id] = {
        "order_id": order_cancel_id,
        "seller_id": "seller-02",
        "status": "S8",
        "version": 1,
    }
    supabase_store.dispute_reports[dispute_id_2] = {
        "dispute_id": dispute_id_2,
        "order_id": order_cancel_id,
        "seller_id": "seller-02",
        "buyer_id": "saleng-01",
        "dispute_reason": "ขยะไม่ตรงประเภทและมีขยะติดเชื้อปนเปื้อน",
        "status": "PENDING_ADMIN",
        "created_at": now.isoformat(),
    }

    resp_resolve_cancel = client.post(
        f"/api/v1/admin/disputes/{dispute_id_2}/resolve",
        json={
            "action": "RESOLVE_CANCEL",
            "arbitration_note": "ขยะติดเชื้ออันตราย สั่งยกเลิกคำขอทันที",
        },
        headers=ADMIN_HEADER,
    )
    assert resp_resolve_cancel.status_code == 200
    assert resp_resolve_cancel.json()["order_status"] == "S9"
    assert supabase_store.orders[order_cancel_id]["status"] == "S9"
    assert supabase_store.dispute_reports[dispute_id_2]["status"] == "RESOLVED_CANCELLED"

    # ========================================================
    # ขั้นที่ 7: ตรวจสอบการบล็อกผู้ใช้ที่ไม่มีสิทธิ์แอดมิน (403 Forbidden) (AC-A03-05, CC-03)
    # ========================================================
    resp_forbidden = client.get("/api/v1/admin/dispatch/stalled-orders", headers={"X-Admin-Role": "BUYER"})
    assert resp_forbidden.status_code == 403

    # ========================================================
    # ขั้นที่ 8: ตรวจสอบ Audit Log ครบทั้ง 4 แอ็กชัน (AC-A03-05, REQ-SEC-001)
    # ========================================================
    actions_logged = [a["action"] for a in supabase_store.audit_logs]
    assert "ADMIN_MANUAL_DISPATCH" in actions_logged
    assert "ADMIN_EXPAND_DISPATCH_RADIUS" in actions_logged
    assert "ADMIN_RESOLVED_DISPUTE" in actions_logged
    assert "ADMIN_CANCELLED_DISPUTE" in actions_logged

