"""
Acceptance Tests for AC-B04-04: Active Queue & Route Ordering
(Task T-04: UC-04, BR-03, REQ-CON-003, AC-B04-04, D-B04-02)
"""

import pytest
from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_active_jobs_queue():
    """เตรียมงาน 2 งานในคิวของ saleng-01 ในสถานะ S3"""
    orig_o1_status = supabase_store.orders["order-s2-01"].get("status")
    orig_o1_col = supabase_store.orders["order-s2-01"].get("collector_id")
    orig_o2_status = supabase_store.orders["order-s2-02"].get("status")
    orig_o2_col = supabase_store.orders["order-s2-02"].get("collector_id")

    supabase_store.orders["order-s2-01"]["status"] = "S3"
    supabase_store.orders["order-s2-01"]["collector_id"] = "saleng-01"
    supabase_store.orders["order-s2-01"]["assigned_saleng_id"] = "saleng-01"

    supabase_store.orders["order-s2-02"]["status"] = "S3"
    supabase_store.orders["order-s2-02"]["collector_id"] = "saleng-01"
    supabase_store.orders["order-s2-02"]["assigned_saleng_id"] = "saleng-01"

    yield

    supabase_store.orders["order-s2-01"]["status"] = orig_o1_status
    supabase_store.orders["order-s2-01"]["collector_id"] = orig_o1_col
    supabase_store.orders["order-s2-01"]["assigned_saleng_id"] = orig_o1_col

    supabase_store.orders["order-s2-02"]["status"] = orig_o2_status
    supabase_store.orders["order-s2-02"]["collector_id"] = orig_o2_col
    supabase_store.orders["order-s2-02"]["assigned_saleng_id"] = orig_o2_col


def test_AC_B04_04_get_active_queue_and_route_ordering():
    """
    Given: ซาเล้ง saleng-01 รับงานไว้ในคิว 2 งาน (order-s2-01 น้ำหนัก 25 กก. และ order-s2-02 น้ำหนัก 60 กก.)
    When: เรียกดูรายการคิวงานและเส้นทาง GET /api/v1/collectors/saleng-01/active-jobs
    Then: ระบบแสดงรายการงานในคิวครบ 2 งาน (total_active_jobs = 2)
    And: คำนวณน้ำหนักสะสมรวมถูกต้อง (25 + 60 = 85.0 กก.) เทียบกับความจุสูงสุด 200 กก. (BR-03)
    And: จัดลำดับจุดแวะรับตาม Route Optimization (sequence_order = 1, 2)
    And: แสดงระยะทางถนนจริงและเวลาถึงโดยประมาณ (ETA) ของแต่ละจุดแวะ
    """
    res = client.get("/api/v1/collectors/saleng-01/active-jobs")
    assert res.status_code == 200
    data = res.json()

    assert data["saleng_id"] == "saleng-01"
    assert data["total_active_jobs"] == 2
    assert data["current_load_kg"] == 85.0
    assert data["max_capacity_kg"] == 200.0
    assert data["remaining_capacity_kg"] == 115.0
    assert data["capacity_percentage"] == 42.5
    assert data["total_route_distance_km"] > 0.0

    jobs = data["jobs"]
    assert len(jobs) == 2
    assert jobs[0]["sequence_order"] == 1
    assert jobs[1]["sequence_order"] == 2
    assert jobs[0]["road_distance_km"] > 0.0
    assert jobs[0]["estimated_arrival_minutes"] >= 5
    assert "https://www.google.com/maps/dir/?api=1" in jobs[0]["navigation_url"]

