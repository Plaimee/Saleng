"""
Acceptance Tests for AC-B02-02: No Jobs in Radius & 10.0 km Expansion
(Task T-03: UC-04, REQ-FN-002, AC-04-04, P-06, Q-06)
"""

from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


def test_AC_B02_02_no_jobs_in_5km_shows_empty_and_expansion_hint():
    """
    Given: ซาเล้งอยู่ที่พิกัดห่างไกล (13.8200, 100.6500 - ย่านบางกะปิ) ซึ่งไม่มีงานในรัศมี 5.0 กม.
           แต่มีงานในรัศมี 10.0 กม.
    When: ซาเล้งค้นหางานด้วยรัศมีเริ่มต้น 5.0 กม.
    Then: ระบบตอบกลับรายการว่าง (0 รายการ)
    And: แสดงข้อความ 'ยังไม่มีงานในเส้นทาง'
    And: มี Flag can_expand_radius = True
    """
    lat, lng = 13.8200, 100.6500

    resp = client.get(
        "/api/v1/collectors/jobs/nearby",
        params={
            "saleng_lat": lat,
            "saleng_lng": lng,
            "radius_km": 5.0,
        },
    )
    assert resp.status_code == 200
    data = resp.json()

    assert data["total_count"] == 0
    assert len(data["jobs"]) == 0
    assert data["message"] == "ยังไม่มีงานในเส้นทาง"
    assert data["can_expand_radius"] is True


def test_AC_B02_02_expand_to_10km_retrieves_jobs():
    """
    Given: ซาเล้งอยู่ที่พิกัดห่างไกล (13.8200, 100.6500) และเคยกดขยายรัศมี
    When: ส่งคำขอด้วย radius_km = 10.0
    Then: ระบบค้นพบและแสดงรายการงานที่อยู่ในรัศมี 10.0 กม. ทันที
    And: can_expand_radius = False (เนื่องจากถึงขอบเขต 10 กม. แล้ว)
    """
    lat, lng = 13.8200, 100.6500

    resp = client.get(
        "/api/v1/collectors/jobs/nearby",
        params={
            "saleng_lat": lat,
            "saleng_lng": lng,
            "radius_km": 10.0,
        },
    )
    assert resp.status_code == 200
    data = resp.json()

    assert data["total_count"] > 0
    assert len(data["jobs"]) > 0
    assert data["radius_km"] == 10.0
    for job in data["jobs"]:
        assert job["road_distance_km"] <= 10.0

    # ตรวจสอบ Audit Log ว่ามีการบันทึกการค้นหารัศมี 10.0 กม. (REQ-SEC-001)
    logs = supabase_store.get_audit_logs("JOB_SEARCH_QUERY")
    expansion_logs = [l for l in logs if l.get("details", {}).get("radius_km") == 10.0]
    assert len(expansion_logs) > 0


def test_AC_B02_02_include_order_at_7km_when_expanded():
    """
    ตรวจสอบว่าคำขอขาย order-s2-04 (อยู่ห่าง ~ 7.5 กม. จากสุทธิสาร 13.7900, 100.5750)
    ไม่ปรากฏในการค้นหา 5.0 กม. แต่ปรากฏทันทีเมื่อขยายเป็น 10.0 กม.
    """
    sutthisan_lat, sutthisan_lng = 13.7900, 100.5750

    # 1. ค้นหา 5.0 กม. -> ไม่มี order-s2-04
    resp_5km = client.get(
        "/api/v1/collectors/jobs/nearby",
        params={"saleng_lat": sutthisan_lat, "saleng_lng": sutthisan_lng, "radius_km": 5.0},
    )
    assert resp_5km.status_code == 200
    ids_5km = [j["order_id"] for j in resp_5km.json()["jobs"]]
    assert "order-s2-04" not in ids_5km

    # 2. ค้นหา 10.0 กม. -> มี order-s2-04
    resp_10km = client.get(
        "/api/v1/collectors/jobs/nearby",
        params={"saleng_lat": sutthisan_lat, "saleng_lng": sutthisan_lng, "radius_km": 10.0},
    )
    assert resp_10km.status_code == 200
    ids_10km = [j["order_id"] for j in resp_10km.json()["jobs"]]
    assert "order-s2-04" in ids_10km

