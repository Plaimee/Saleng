"""
Unit Tests for Task T-01: Job Route Models & Concurrency Store Methods
(UC-04, UC-09, UC-12, BR-02, BR-03, CC-04, D-B04-01..06)
"""

import pytest
from backend.app.models.job_route_models import (
    ClaimJobRequest,
    ClaimJobResponse,
    ActiveJobSummary,
    ActiveQueueResponse,
    StartTransitRequest,
    StartTransitResponse,
    CollectorCancelJobRequest,
    CollectorCancelJobResponse,
    build_google_maps_navigation_url,
)
from backend.app.core.supabase import supabase_store


@pytest.fixture(autouse=True)
def reset_test_orders():
    """คืนค่าสถานะ orders ก่อนและหลังการทดสอบ"""
    order1 = supabase_store.orders.get("order-s2-01")
    orig_status = order1.get("status") if order1 else "S2"
    orig_version = order1.get("version") if order1 else 1
    orig_collector = order1.get("collector_id") if order1 else None
    orig_assigned = order1.get("assigned_saleng_id") if order1 else None

    yield

    if "order-s2-01" in supabase_store.orders:
        supabase_store.orders["order-s2-01"]["status"] = orig_status
        supabase_store.orders["order-s2-01"]["version"] = orig_version
        supabase_store.orders["order-s2-01"]["collector_id"] = orig_collector
        supabase_store.orders["order-s2-01"]["assigned_saleng_id"] = orig_assigned


def test_T01_job_route_pydantic_schemas():
    """ตรวจสอบ Pydantic Models Validation และ Navigation URL Builder"""
    nav_url = build_google_maps_navigation_url(13.7950, 100.5810)
    assert "https://www.google.com/maps/dir/?api=1" in nav_url
    assert "destination=13.795000,100.581000" in nav_url

    # ตรวจสอบ ClaimJobRequest
    claim_req = ClaimJobRequest(saleng_id="saleng-01", expected_version=1)
    assert claim_req.saleng_id == "saleng-01"
    assert claim_req.expected_version == 1

    # ตรวจสอบ ClaimJobResponse
    claim_res = ClaimJobResponse(
        order_id="order-s2-01",
        status="S3",
        collector_id="saleng-01",
        address_text="123/45 ซอยประชาราษฎร์บำเพ็ญ 24",
        dest_lat=13.7950,
        dest_lng=100.5810,
        seller_phone="081-234-5678",
        seller_name="คุณวิภาดา",
        subdistrict_name="แขวงสามเสนนอก",
        district_name="เขตห้วยขวาง",
        total_est_weight_kg=25.0,
        total_est_price_min=150.0,
        total_est_price_max=220.0,
        claimed_at="2026-11-04T12:00:00Z",
        version=2,
        navigation_url=nav_url,
    )
    assert claim_res.order_id == "order-s2-01"
    assert claim_res.version == 2

    # ตรวจสอบ ActiveJobSummary & ActiveQueueResponse
    job_summary = ActiveJobSummary(
        order_id="order-s2-01",
        status="S3",
        pickup_slot_time="09:00 - 11:00",
        address_text="123/45 ซอยประชาราษฎร์บำเพ็ญ 24",
        dest_lat=13.7950,
        dest_lng=100.5810,
        seller_name="คุณวิภาดา",
        seller_phone="081-234-5678",
        total_est_weight_kg=25.0,
        total_est_price_min=150.0,
        total_est_price_max=220.0,
        road_distance_km=1.2,
        estimated_arrival_minutes=15,
        sequence_order=1,
        need_lifting_help=False,
        navigation_url=nav_url,
    )
    queue_res = ActiveQueueResponse(
        saleng_id="saleng-01",
        total_active_jobs=1,
        current_load_kg=25.0,
        max_capacity_kg=200.0,
        remaining_capacity_kg=175.0,
        capacity_percentage=12.5,
        total_route_distance_km=1.2,
        jobs=[job_summary],
    )
    assert queue_res.total_active_jobs == 1
    assert queue_res.remaining_capacity_kg == 175.0

    # ตรวจสอบ StartTransitResponse
    transit_res = StartTransitResponse(
        order_id="order-s2-01",
        status="S4",
        started_at="2026-11-04T12:05:00Z",
        seller_notified=True,
        seller_cancel_locked=True,
        navigation_url=nav_url,
    )
    assert transit_res.status == "S4"

    # ตรวจสอบ CollectorCancelJobResponse
    cancel_res = CollectorCancelJobResponse(
        order_id="order-s2-01",
        status="S2",
        message="ยกเลิกและคืนสถานะสำเร็จ",
        cancelled_at="2026-11-04T12:10:00Z",
        reverted_to_pending=True,
    )
    assert cancel_res.status == "S2"
    assert cancel_res.reverted_to_pending is True


def test_T01_supabase_store_claim_order_occ():
    """ทดสอบ Atomic Claim ด้วย Optimistic Concurrency Control (OCC) ใน Store"""
    order_id = "order-s2-01"
    saleng_id = "saleng-01"

    # รีเซ็ตสถานะเป็น S2, version = 1
    supabase_store.orders[order_id]["status"] = "S2"
    supabase_store.orders[order_id]["version"] = 1
    supabase_store.orders[order_id]["collector_id"] = None
    supabase_store.orders[order_id]["assigned_saleng_id"] = None

    # 1. กดรับงานสำเร็จครั้งแรก (version 1 -> 2)
    claimed = supabase_store.claim_order_occ(order_id, saleng_id, expected_version=1)
    assert claimed["status"] == "S3"
    assert claimed["collector_id"] == saleng_id
    assert claimed["version"] == 2

    # 2. จำลองซาเล้งคนที่สองกดรับงานเดียวกัน (version 1 ชนกับ version 2 ปัจจุบัน)
    with pytest.raises(ValueError, match="มีผู้รับงานนี้แล้ว"):
        supabase_store.claim_order_occ(order_id, "saleng-02", expected_version=1)

    # 3. ทดสอบการดึง active jobs
    active_jobs = supabase_store.get_collector_active_jobs(saleng_id)
    assert len(active_jobs) >= 1
    assert any(j["order_id"] == order_id for j in active_jobs)


def test_T01_supabase_store_revert_order_to_pending():
    """ทดสอบการคืนสถานะคำขอกลับเป็น S2 เมื่อซาเล้งกดยกเลิกงาน (D-B04-04)"""
    order_id = "order-s2-01"
    saleng_id = "saleng-01"

    # ตั้งค่าให้ order อยู่ในสถานะ S3 ผูกกับ saleng-01
    supabase_store.orders[order_id]["status"] = "S3"
    supabase_store.orders[order_id]["collector_id"] = saleng_id
    supabase_store.orders[order_id]["assigned_saleng_id"] = saleng_id
    supabase_store.orders[order_id]["version"] = 2

    # ซาเล้งกดยกเลิกงาน
    reverted = supabase_store.revert_order_to_pending(
        order_id=order_id,
        saleng_id=saleng_id,
        reason="VEHICLE_BREAKDOWN",
        note="ยางแตกกะทันหัน",
    )

    assert reverted["status"] == "S2"
    assert reverted["collector_id"] is None
    assert reverted["assigned_saleng_id"] is None
    assert reverted["cancel_reason"] == "VEHICLE_BREAKDOWN"
    assert reverted["version"] == 3

    # ซาเล้งคนอื่นไม่สามารถกดยกเลิกงานที่ไม่ใช่ของตนเองได้
    with pytest.raises(ValueError, match="คุณไม่ใช่ผู้รับผิดชอบ"):
        supabase_store.revert_order_to_pending(order_id, "saleng-99", "OTHER")

