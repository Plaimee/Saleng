"""
Integration E2E Test Suite: Buyer Job and Route Management Lifecycle
(Task T-08: UC-04, UC-09, UC-12, BR-02, BR-03, CC-01, CC-04, CC-05, REQ-BR-002, REQ-SEC-002, REQ-CON-003, AC-B04-01..07)

ทดสอบครบวงจรระบบจัดการงานและเส้นทางของซาเล้ง:
1. Single Collector Atomic Claim (OCC) ป้องกันแย่งงานและตอบกลับ HTTP 409 Conflict (AC-B04-01)
2. การข้ามงาน (Skip Job) คงสถานะ S2 ให้ซาเล้งอื่นรับต่อได้ (AC-B04-02)
3. การเปิดเผยบ้านเลขที่จริงและพิกัดจริงเฉพาะผู้รับงาน พร้อมลิงก์ Google Maps (AC-B04-03)
4. การจัดการคิวงานสะสม การคำนวณน้ำหนักเทียบความจุรถ 200 กก. และการจัดลำดับเส้นทาง (AC-B04-04)
5. การเริ่มออกเดินทาง S3 -> S4 และการล็อกปุ่มยกเลิกผู้ขาย (AC-B04-05)
6. การสละสิทธิ์ยกเลิกงานและคืนสถานะคำขอกลับเป็น S2 อัตโนมัติ (AC-B04-06)
"""

import pytest
from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_environment_state():
    """รีเซ็ตและคืนค่าข้อมูลคำขอและประวัติซาเล้งก่อนและหลังการทดสอบ"""
    # สำรองข้อมูล orders
    orig_orders = {k: dict(v) for k, v in supabase_store.orders.items()}
    orig_saleng = {k: dict(v) for k, v in supabase_store.saleng_profiles.items()}

    # ล้างงานคงค้างของ saleng-01 / saleng-02 จาก test suite อื่นที่รันก่อนหน้า
    for o in supabase_store.orders.values():
        if o.get("collector_id") in ("saleng-01", "saleng-02") or o.get("assigned_saleng_id") in ("saleng-01", "saleng-02"):
            o["collector_id"] = None
            o["assigned_saleng_id"] = None
            if o.get("status") in ("S3", "S4"):
                o["status"] = "S2"

    # ตรวจสอบให้มั่นใจว่า saleng-01 และ saleng-02 ผ่าน KYC และออนไลน์
    supabase_store.saleng_profiles["saleng-01"]["verified"] = True
    supabase_store.saleng_profiles["saleng-01"]["is_online"] = True
    supabase_store.saleng_profiles["saleng-01"]["current_load_kg"] = 0.0

    if "saleng-02" in supabase_store.saleng_profiles:
        supabase_store.saleng_profiles["saleng-02"]["verified"] = True
        supabase_store.saleng_profiles["saleng-02"]["is_online"] = True
        supabase_store.saleng_profiles["saleng-02"]["current_load_kg"] = 0.0

    yield

    # คืนค่าเดิม
    supabase_store.orders = orig_orders
    supabase_store.saleng_profiles = orig_saleng


def test_e2e_atomic_claim_and_conflict_handling():
    """
    E2E ขั้นตอนที่ 1: ทดสอบ Single Collector Atomic Claim และป้องกันรับงานซ้ำ (AC-B04-01, BR-02, CC-04)
    - ซาเล้งคนที่ 1 (saleng-01) กดรับงานสำเร็จ -> สถานะเปลี่ยนเป็น S3, version เพิ่มขึ้น
    - ซาเล้งคนที่ 2 (saleng-02) พยายามกดรับงานเดียวกัน -> ตอบกลับ HTTP 409 Conflict พร้อมข้อความ "มีผู้รับงานนี้แล้ว"
    """
    order_id = "order-s2-01"
    initial_version = supabase_store.orders[order_id]["version"]

    # 1. ซาเล้ง 01 กดรับงาน
    res1 = client.post(
        f"/api/v1/collectors/jobs/{order_id}/claim",
        json={"saleng_id": "saleng-01", "expected_version": initial_version},
    )
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["status"] == "S3"
    assert data1["collector_id"] == "saleng-01"
    assert data1["version"] == initial_version + 1

    # 2. ซาเล้ง 02 กดรับงานเดียวกัน (ส่ง expected_version เดิมหรือใหม่ก็ต้องชน)
    res2 = client.post(
        f"/api/v1/collectors/jobs/{order_id}/claim",
        json={"saleng_id": "saleng-02", "expected_version": initial_version},
    )
    assert res2.status_code == 409
    assert res2.json()["detail"] == "มีผู้รับงานนี้แล้ว"

    # 3. ตรวจสอบ Audit Log การกดรับงาน
    claim_logs = [l for l in supabase_store.audit_logs if l["action"] == "COLLECTOR_CLAIMED_JOB"]
    assert len(claim_logs) >= 1
    assert claim_logs[-1]["actor_id"] == "saleng-01"
    assert claim_logs[-1]["entity_id"] == order_id


def test_e2e_address_unmasking_and_gps_url():
    """
    E2E ขั้นตอนที่ 2: ตรวจสอบการเปิดเผยบ้านเลขที่จริง พิกัดจริง และการสร้างลิงก์ Google Maps (AC-B04-03, REQ-SEC-002, UC-09)
    """
    order_id = "order-s2-01"
    current_ver = supabase_store.orders[order_id]["version"]

    res = client.post(
        f"/api/v1/collectors/jobs/{order_id}/claim",
        json={"saleng_id": "saleng-01", "expected_version": current_ver},
    )
    assert res.status_code == 200
    data = res.json()

    # ตรวจสอบการเปิดเผยที่อยู่จริงและเบอร์โทร
    assert "123/45" in data["address_text"]
    assert data["dest_lat"] == 13.7930
    assert data["dest_lng"] == 100.5780
    assert data["seller_phone"] == "081-234-5678"

    # ตรวจสอบลิงก์ Google Maps Navigation Deep Link
    assert "https://www.google.com/maps/dir/?api=1" in data["navigation_url"]
    assert "destination=13.793000,100.578000" in data["navigation_url"]
    assert "travelmode=driving" in data["navigation_url"]


def test_e2e_skip_job_lifecycle():
    """
    E2E ขั้นตอนที่ 3: ตรวจสอบการข้ามงาน (Skip Job) โดยคงสถานะ S2 ให้ผู้อื่นรับต่อได้ (AC-B04-02, Extension A2)
    """
    order_id = "order-s2-02"
    assert supabase_store.orders[order_id]["status"] == "S2"

    res = client.post(
        f"/api/v1/collectors/jobs/{order_id}/skip",
        params={"saleng_id": "saleng-01"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "S2"
    assert data["skipped"] is True
    assert "ข้ามงานเรียบร้อย" in data["message"]

    # ตรวจสอบใน Store ว่ายังคงเป็น S2 และยังไม่มีผู้รับงาน
    in_db = supabase_store.orders[order_id]
    assert in_db["status"] == "S2"
    assert in_db.get("collector_id") is None


def test_e2e_active_queue_route_ordering_and_capacity():
    """
    E2E ขั้นตอนที่ 4: ตรวจสอบการคำนวณคิวงานสะสม การจำกัดน้ำหนัก 200 กก. และการเรียงลำดับเส้นทาง (AC-B04-04, BR-03)
    """
    # ซาเล้ง 01 รับงาน 2 งาน (order-s2-01 = 25 กก., order-s2-02 = 60 กก.)
    v1 = supabase_store.orders["order-s2-01"]["version"]
    v2 = supabase_store.orders["order-s2-02"]["version"]

    client.post(
        "/api/v1/collectors/jobs/order-s2-01/claim",
        json={"saleng_id": "saleng-01", "expected_version": v1},
    )
    client.post(
        "/api/v1/collectors/jobs/order-s2-02/claim",
        json={"saleng_id": "saleng-01", "expected_version": v2},
    )

    # เรียกดูคิวงานและเส้นทาง
    res = client.get(
        "/api/v1/collectors/saleng-01/active-jobs",
        params={"saleng_lat": 13.7900, "saleng_lng": 100.5750},
    )
    assert res.status_code == 200
    data = res.json()

    assert data["saleng_id"] == "saleng-01"
    assert data["total_active_jobs"] == 2
    assert data["max_capacity_kg"] == 200.0
    assert data["current_load_kg"] == 85.0  # 25 + 60
    assert data["remaining_capacity_kg"] == 115.0
    assert data["total_route_distance_km"] > 0.0

    # ลำดับจุดแวะรับ sequence_order ต้องเรียง 1 และ 2
    jobs = data["jobs"]
    assert jobs[0]["sequence_order"] == 1
    assert jobs[1]["sequence_order"] == 2


def test_e2e_start_transit_and_seller_lock():
    """
    E2E ขั้นตอนที่ 5: ตรวจสอบการเปลี่ยนสถานะเป็น S4 และการล็อกปุ่มยกเลิกฝั่งผู้ขาย (AC-B04-05, BR-03, UC-09)
    """
    order_id = "order-s2-01"
    ver = supabase_store.orders[order_id]["version"]

    client.post(
        f"/api/v1/collectors/jobs/{order_id}/claim",
        json={"saleng_id": "saleng-01", "expected_version": ver},
    )

    # ยืนยันออกเดินทาง
    res = client.post(
        f"/api/v1/collectors/jobs/{order_id}/start-transit",
        json={"saleng_id": "saleng-01", "current_lat": 13.7900, "current_lng": 100.5750},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "S4"
    assert data["seller_cancel_locked"] is True

    # ตรวจสอบใน Store
    order_in_db = supabase_store.orders[order_id]
    assert order_in_db["status"] == "S4"

    # ตรวจสอบ Audit Log
    logs = [l for l in supabase_store.audit_logs if l["action"] == "COLLECTOR_STARTED_TRANSIT"]
    assert len(logs) >= 1
    assert logs[-1]["details"]["status"] == "S4"


def test_e2e_collector_cancellation_and_auto_revert():
    """
    E2E ขั้นตอนที่ 6: ตรวจสอบการสละสิทธิ์ยกเลิกงานในสถานะ S3 และการคืนสถานะคำขอกลับเป็น S2 (AC-B04-06, MD-STM-04)
    """
    order_id = "order-s2-01"
    ver = supabase_store.orders[order_id]["version"]

    # 1. รับงาน
    client.post(
        f"/api/v1/collectors/jobs/{order_id}/claim",
        json={"saleng_id": "saleng-01", "expected_version": ver},
    )
    assert supabase_store.orders[order_id]["status"] == "S3"

    # 2. กดยกเลิกงานระบุเหตุผล VEHICLE_BREAKDOWN
    res_cancel = client.post(
        f"/api/v1/collectors/jobs/{order_id}/cancel",
        json={
            "saleng_id": "saleng-01",
            "reason": "VEHICLE_BREAKDOWN",
            "note": "ยางหน้ารั่ว ซอยรัชดาภิเษก 18",
        },
    )
    assert res_cancel.status_code == 200
    cancel_data = res_cancel.json()
    assert cancel_data["status"] == "S2"
    assert cancel_data["reverted_to_pending"] is True

    # 3. คำขอใน Store คืนกลับเป็น S2 และ collector_id กลายเป็น None
    reverted_order = supabase_store.orders[order_id]
    assert reverted_order["status"] == "S2"
    assert reverted_order["collector_id"] is None

    # 4. ตรวจสอบ Audit Log การยกเลิก
    cancel_logs = [l for l in supabase_store.audit_logs if l["action"] == "COLLECTOR_CANCELLED_JOB"]
    assert len(cancel_logs) >= 1
    assert cancel_logs[-1]["details"]["reason"] == "VEHICLE_BREAKDOWN"

    # 5. ซาเล้งอีกคน (saleng-02) สามารถรับงานนี้ต่อได้ทันที!
    res_reclaim = client.post(
        f"/api/v1/collectors/jobs/{order_id}/claim",
        json={"saleng_id": "saleng-02", "expected_version": reverted_order["version"]},
    )
    assert res_reclaim.status_code == 200
    assert res_reclaim.json()["status"] == "S3"
    assert res_reclaim.json()["collector_id"] == "saleng-02"
