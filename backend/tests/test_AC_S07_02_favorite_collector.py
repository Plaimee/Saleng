"""
Automated Backend Tests สำหรับ AC-S07-02: Favorite Collector Bookmark
รองรับ UC-10, SC-05, REQ-SEC-001, AC-S07-02, P-02, P-05, Q-03
"""

from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


def test_favorite_collector_flow():
    """
    AC-S07-02: ทดสอบการบันทึกและยกเลิกซาเล้งเป็นผู้รับซื้อประจำ (Toggle Bookmark)
    พร้อมตรวจสอบ Audit Log SELLER_ADD_FAVORITE และ SELLER_REMOVE_FAVORITE
    """
    seller_id = "SELLER-FAV-01"
    collector_id = "COLLECTOR-MANAS"

    # 1. ตรวจสอบเริ่มต้น รายการผู้รับซื้อประจำต้องว่าง
    resp_init = client.get(f"/api/v1/sellers/{seller_id}/favorites")
    assert resp_init.status_code == 200
    assert collector_id not in resp_init.json()

    # 2. กดบันทึกเป็นผู้รับซื้อประจำ (POST)
    resp_add = client.post(f"/api/v1/sellers/{seller_id}/favorites/{collector_id}")
    assert resp_add.status_code == 200
    data_add = resp_add.json()
    assert data_add["seller_id"] == seller_id
    assert data_add["collector_id"] == collector_id
    assert data_add["is_favorite"] is True
    assert "บันทึกเป็นผู้รับซื้อประจำเรียบร้อยแล้ว" in data_add["message"]

    # ตรวจสอบว่ามี collector_id อยู่ในรายการแล้ว
    resp_check = client.get(f"/api/v1/sellers/{seller_id}/favorites")
    assert collector_id in resp_check.json()

    # ตรวจสอบ Audit Log ADD (REQ-SEC-001, AC-S07-05)
    add_logs = [
        l for l in supabase_store.audit_logs
        if l["action"] == "SELLER_ADD_FAVORITE" and l["entity_id"] == collector_id
    ]
    assert len(add_logs) >= 1
    assert add_logs[-1]["details"]["is_favorite"] is True

    # 3. กดยกเลิกผู้รับซื้อประจำ (DELETE หรือ Toggle POST ซ้ำ)
    resp_del = client.delete(f"/api/v1/sellers/{seller_id}/favorites/{collector_id}")
    assert resp_del.status_code == 200
    data_del = resp_del.json()
    assert data_del["is_favorite"] is False
    assert "ยกเลิกผู้รับซื้อประจำ" in data_del["message"]

    # ตรวจสอบว่าไม่มี collector_id ในรายการแล้ว
    resp_empty = client.get(f"/api/v1/sellers/{seller_id}/favorites")
    assert collector_id not in resp_empty.json()

    # ตรวจสอบ Audit Log REMOVE (REQ-SEC-001, AC-S07-05)
    remove_logs = [
        l for l in supabase_store.audit_logs
        if l["action"] == "SELLER_REMOVE_FAVORITE" and l["entity_id"] == collector_id
    ]
    assert len(remove_logs) >= 1
    assert remove_logs[-1]["details"]["is_favorite"] is False

