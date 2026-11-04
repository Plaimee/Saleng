"""
Acceptance Tests for AC-B04-02: Skip Job Option
(Task T-03: UC-04, Extension A2, CC-06, AC-B04-02)
"""

from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


def test_AC_B04_02_skip_job_preserves_status_s2():
    """
    Given: คำขอขาย order-s2-02 อยู่ในสถานะ S2: รอผู้รับงาน
    When: ซาเล้ง saleng-01 กดปุ่ม "ข้ามงานนี้"
    Then: ระบบตอบกลับสำเร็จ (skipped = True)
    And: คำขอขายยังคงอยู่ในสถานะ S2: รอผู้รับงาน เพื่อให้ซาเล้งคนอื่นในพื้นที่มองเห็นและรับต่อได้ (Extension A2)
    And: บันทึก Audit Log การข้ามงาน (REQ-SEC-001)
    """
    res = client.post(
        "/api/v1/collectors/jobs/order-s2-02/skip",
        params={"saleng_id": "saleng-01"},
    )
    assert res.status_code == 200
    data = res.json()

    assert data["order_id"] == "order-s2-02"
    assert data["status"] == "S2"
    assert data["skipped"] is True
    assert "ข้ามงานเรียบร้อย" in data["message"]

    # ตรวจสอบสถานะจริงใน Store ยังคงเป็น S2
    order_in_db = supabase_store.orders.get("order-s2-02")
    assert order_in_db is not None
    assert order_in_db["status"] == "S2"
    assert order_in_db.get("collector_id") is None
