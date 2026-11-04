"""
Acceptance Tests for AC-B04-06: Collector Cancellation with State Reversion
(Task T-05: UC-12, MD-STM-04, REQ-SEC-001, AC-B04-06, D-B04-04)
"""

import pytest
from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_order_state():
    orig_status = supabase_store.orders["order-s2-01"].get("status")
    orig_collector = supabase_store.orders["order-s2-01"].get("collector_id")
    orig_assigned = supabase_store.orders["order-s2-01"].get("assigned_saleng_id")
    orig_version = supabase_store.orders["order-s2-01"].get("version", 1)

    supabase_store.orders["order-s2-01"]["status"] = "S3"
    supabase_store.orders["order-s2-01"]["collector_id"] = "saleng-01"
    supabase_store.orders["order-s2-01"]["assigned_saleng_id"] = "saleng-01"

    yield

    supabase_store.orders["order-s2-01"]["status"] = orig_status
    supabase_store.orders["order-s2-01"]["collector_id"] = orig_collector
    supabase_store.orders["order-s2-01"]["assigned_saleng_id"] = orig_assigned
    supabase_store.orders["order-s2-01"]["version"] = orig_version


def test_AC_B04_06_collector_cancel_reverts_order_to_s2():
    """
    Given: ซาเล้ง saleng-01 รับงาน order-s2-01 ไว้ในสถานะ S3
    When: เกิดเหตุสุดวิสัย (เช่น รถเสีย) ซาเล้งกดยกเลิกงานพร้อมระบุเหตุผล VEHICLE_BREAKDOWN
    Then: ระบบคืนสถานะคำขอขายกลับเป็น S2: รอผู้รับงาน เพื่อให้ซาเล้งอื่นรับต่อได้ทันที (D-B04-04)
    And: เคลียร์ collector_id เป็น None
    And: บันทึกเหตุผลลงใน audit_logs (REQ-SEC-001)
    """
    res = client.post(
        "/api/v1/collectors/jobs/order-s2-01/cancel",
        json={
            "saleng_id": "saleng-01",
            "reason": "VEHICLE_BREAKDOWN",
            "note": "ยางหน้าระเบิด ไม่สามารถเดินทางต่อได้",
        },
    )
    assert res.status_code == 200
    data = res.json()

    assert data["order_id"] == "order-s2-01"
    assert data["status"] == "S2"
    assert data["reverted_to_pending"] is True
    assert "สละสิทธิ์งานสำเร็จ" in data["message"]

    # ตรวจสอบว่าใน Store กลับไปเป็น S2 และไม่มีผู้รับงาน
    order_db = supabase_store.orders.get("order-s2-01")
    assert order_db["status"] == "S2"
    assert order_db["collector_id"] is None
    assert order_db["assigned_saleng_id"] is None
    assert order_db["cancel_reason"] == "VEHICLE_BREAKDOWN"


def test_AC_B04_06_unauthorized_collector_cannot_cancel():
    """ซาเล้งคนอื่นที่ไม่ได้รับงานนี้ ไม่สามารถกดยกเลิกงานได้"""
    res = client.post(
        "/api/v1/collectors/jobs/order-s2-01/cancel",
        json={"saleng_id": "saleng-99", "reason": "OTHER"},
    )
    assert res.status_code == 403

