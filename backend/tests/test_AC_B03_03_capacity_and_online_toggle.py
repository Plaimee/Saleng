"""
Acceptance Tests for AC-B03-03: Online/Offline Toggle & Capacity Guard
(Task T-04: UC-04, BR-03, REQ-CON-003, CC-02, D-B03-03, D-B03-04, D-B03-05)
"""

from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


def test_AC_B03_03_capacity_guard_within_and_exceeded():
    """
    ทดสอบการตรวจสอบความจุรถซาเล้ง (BR-03, REQ-CON-003, D-B03-03, D-B03-04):
    - เมื่อน้ำหนักสะสมไม่เกินความจุ (<= 200 กก.): can_claim_job = True, is_capacity_exceeded = False
    - เมื่อน้ำหนักสะสมเกินความจุ (> 200 กก.): can_claim_job = False, is_capacity_exceeded = True, block_reason = 'CAPACITY_EXCEEDED'
    """
    saleng_id = "saleng-01"
    # order-s2-01 มีน้ำหนัก 25 กก.
    try:
        # 1. กรณีรถว่าง (current_load = 0 กก.) -> น้ำหนักรวม 25 กก. <= 200 กก.
        supabase_store.set_saleng_current_load(saleng_id, 0.0)
        resp_ok = client.get(f"/api/v1/collectors/jobs/order-s2-01/evaluate?saleng_id={saleng_id}")
        assert resp_ok.status_code == 200
        data_ok = resp_ok.json()
        assert data_ok["collector_current_load_kg"] == 0.0
        assert data_ok["total_est_weight_kg"] == 25.0
        assert data_ok["projected_total_load_kg"] == 25.0
        assert data_ok["is_capacity_exceeded"] is False
        assert data_ok["remaining_capacity_kg"] == 200.0
        assert data_ok["can_claim_job"] is True
        assert data_ok["claim_block_reason"] is None

        # 2. กรณีมีของในรถแล้ว 185 กก. -> น้ำหนักรวม 185 + 25 = 210 กก. > 200 กก. (เกินความจุ)
        supabase_store.set_saleng_current_load(saleng_id, 185.0)
        resp_over = client.get(f"/api/v1/collectors/jobs/order-s2-01/evaluate?saleng_id={saleng_id}")
        assert resp_over.status_code == 200
        data_over = resp_over.json()
        assert data_over["collector_current_load_kg"] == 185.0
        assert data_over["projected_total_load_kg"] == 210.0
        assert data_over["is_capacity_exceeded"] is True
        assert data_over["can_claim_job"] is False
        assert data_over["claim_block_reason"] == "CAPACITY_EXCEEDED"
    finally:
        # คืนค่า current load
        supabase_store.set_saleng_current_load(saleng_id, 0.0)


def test_AC_B03_03_online_offline_status_toggle():
    """
    ทดสอบการสลับสถานะ Online / Offline (CC-02, D-B03-05):
    - เมื่อ Offline: can_claim_job = False, claim_block_reason = 'OFFLINE'
    - เมื่อ Online: can_claim_job = True
    """
    saleng_id = "saleng-01"

    try:
        # 1. สลับเป็น Offline
        resp_off = client.patch(
            f"/api/v1/collectors/{saleng_id}/status",
            json={"saleng_id": saleng_id, "is_online": False},
        )
        assert resp_off.status_code == 200
        assert resp_off.json()["profile"]["is_online"] is False

        # เปิดดูรายละเอียดงาน -> ต้องล็อกปุ่มรับงานด้วยเหตุผล OFFLINE
        resp_eval_off = client.get(f"/api/v1/collectors/jobs/order-s2-01/evaluate?saleng_id={saleng_id}")
        assert resp_eval_off.status_code == 200
        data_eval_off = resp_eval_off.json()
        assert data_eval_off["collector_is_online"] is False
        assert data_eval_off["can_claim_job"] is False
        assert data_eval_off["claim_block_reason"] == "OFFLINE"

        # 2. สลับกลับเป็น Online
        resp_on = client.patch(
            f"/api/v1/collectors/{saleng_id}/status",
            json={"saleng_id": saleng_id, "is_online": True, "current_lat": 13.7900, "current_lng": 100.5750},
        )
        assert resp_on.status_code == 200
        assert resp_on.json()["profile"]["is_online"] is True

        resp_eval_on = client.get(f"/api/v1/collectors/jobs/order-s2-01/evaluate?saleng_id={saleng_id}")
        assert resp_eval_on.status_code == 200
        data_eval_on = resp_eval_on.json()
        assert data_eval_on["collector_is_online"] is True
        assert data_eval_on["can_claim_job"] is True
    finally:
        supabase_store.update_saleng_online_status(saleng_id, True)


def test_AC_B03_03_get_collector_capacity_endpoint():
    """
    ทดสอบ Endpoint GET /api/v1/collectors/{saleng_id}/capacity
    """
    saleng_id = "saleng-01"
    supabase_store.set_saleng_current_load(saleng_id, 40.0)

    try:
        resp = client.get(f"/api/v1/collectors/{saleng_id}/capacity")
        assert resp.status_code == 200
        data = resp.json()
        assert data["saleng_id"] == saleng_id
        assert data["current_load_kg"] == 40.0
        assert data["max_capacity_kg"] == 200.0
        assert data["remaining_capacity_kg"] == 160.0
        assert data["load_percentage"] == 20.0
    finally:
        supabase_store.set_saleng_current_load(saleng_id, 0.0)

