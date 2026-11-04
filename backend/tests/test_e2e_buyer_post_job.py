"""
Integration E2E Test Suite for Buyer Post-Job Management System
(Task T-08: UC-10, UC-13, REQ-FN-005, REQ-FN-006, REQ-SEC-001, REQ-SEC-002, CC-01, CC-04, CC-06, D-B07-01..06)
"""

from datetime import datetime, timezone
import pytest
from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_e2e_post_job_environment():
    """เตรียมข้อมูลสำหรับการทดสอบ E2E ระบบหลังจบงานซาเล้ง"""
    order_completed = "order-b07-e2e-completed"
    order_disputed = "order-b07-e2e-enroute"

    now_iso = datetime.now(timezone.utc).isoformat()

    # 1. คำขอที่เสร็จสมบูรณ์แล้ว (S7: Completed)
    supabase_store.orders[order_completed] = {
        "order_id": order_completed,
        "seller_id": "seller-e2e-01",
        "saleng_id": "saleng-01",
        "buyer_id": "saleng-01",
        "status": "S7",
        "completed_at": now_iso,
        "total_settled_amount": 420.0,
        "seller_name": "คุณวิภาดา รักษ์โลก",
        "seller_phone": "0898765432",
        "payment_method": "PROMPTPAY",
        "receipt_id": "REC-20261104-E2E1",
        "items": [
            {
                "item_id": "it-e2e-1",
                "category_name": "กระดาษลัง",
                "actual_quantity": 60.0,
                "unit": "กก.",
            },
            {
                "item_id": "it-e2e-2",
                "category_name": "ขวดแก้วใส",
                "actual_quantity": 30.0,
                "unit": "กก.",
            },
        ],
    }

    # 2. คำขอที่กำลังเดินทางไปรับของ (S3: En Route)
    supabase_store.orders[order_disputed] = {
        "order_id": order_disputed,
        "seller_id": "seller-e2e-02",
        "saleng_id": "saleng-01",
        "buyer_id": "saleng-01",
        "status": "S3",
        "active_collector_lock": True,
    }

    orig_profile = dict(supabase_store.saleng_profiles.get("saleng-01", {}))
    supabase_store.saleng_profiles["saleng-01"].update({
        "name": "สมชาย ซาเล้งสุพรรณ",
        "phone": "0812345678",
        "verified": True,
        "kyc_status": "VERIFIED",
    })

    # ล้างรายการลูกค้าประจำของ saleng-01
    supabase_store.collector_favorite_sellers = [
        f for f in supabase_store.collector_favorite_sellers if f.get("collector_id") != "saleng-01"
    ]

    yield

    supabase_store.orders.pop(order_completed, None)
    supabase_store.orders.pop(order_disputed, None)
    supabase_store.collector_favorite_sellers = [
        f for f in supabase_store.collector_favorite_sellers if f.get("collector_id") != "saleng-01"
    ]
    if orig_profile:
        supabase_store.saleng_profiles["saleng-01"] = orig_profile


def test_e2e_buyer_post_job_lifecycle():
    """
    ทดสอบ Full Lifecycle ของระบบหลังจบงานฝั่งซาเล้ง:
    1. ดึงประวัติการรับซื้อสถานะ S7 พร้อมตรวจสอบสถิติสะสม 3 มิติ และ PII Masking
    2. ปักหมุดผู้ขายเป็นลูกค้าประจำ (Regular Customer) พร้อมบันทึกย่อช่วยจำ และตรวจสอบในรายการ
    3. ซาเล้งเดินทางไปหน้างานอีกใบงานหนึ่ง (S3) แล้วพบผู้ขาย No-show จึงส่งรายงานข้อพิพาทพร้อมภาพถ่าย
    4. ตรวจสอบว่าคำขอถูกเปลี่ยนเป็น S8: Disputed ส่งให้ Admin และปลดล็อกซาเล้งออกจากงาน
    5. ตรวจสอบ Audit Log ทุกขั้นตอนตามข้อกำหนดความปลอดภัย REQ-SEC-001
    """
    # -------------------------------------------------------------
    # Step 1: ดึงประวัติการรับซื้อและสถิติสะสม
    # -------------------------------------------------------------
    resp1 = client.get("/api/v1/collectors/post-job/history?saleng_id=saleng-01&period=all")
    assert resp1.status_code == 200
    history = resp1.json()
    assert history["period"] == "all"
    assert history["summary"]["total_expense_baht"] == 420.0
    assert history["summary"]["total_weight_kg"] == 90.0
    assert history["summary"]["total_completed_jobs"] == 1

    first_item = history["items"][0]
    assert first_item["order_id"] == "order-b07-e2e-completed"
    assert first_item["seller_phone_masked"] == "08X-XXX-5432"
    assert first_item["is_regular_customer"] is False

    # -------------------------------------------------------------
    # Step 2: ปักหมุดผู้ขายเป็นลูกค้าประจำ (Regular Customer Bookmark)
    # -------------------------------------------------------------
    payload_fav = {
        "saleng_id": "saleng-01",
        "seller_id": "seller-e2e-01",
        "notes": "บ้านรั้วสีฟ้า มีทองแดงและลังกระดาษบ่อย สะดวกเสาร์-อาทิตย์",
        "latitude": 13.7563,
        "longitude": 100.5018,
    }
    resp2 = client.post("/api/v1/collectors/post-job/regular-customers", json=payload_fav)
    assert resp2.status_code == 200
    fav_res = resp2.json()
    assert fav_res["status"] == "success"
    assert fav_res["is_favorite"] is True

    # ดึงรายชื่อลูกค้าประจำ
    resp3 = client.get("/api/v1/collectors/post-job/regular-customers?saleng_id=saleng-01")
    assert resp3.status_code == 200
    regular_list = resp3.json()
    assert len(regular_list) == 1
    assert regular_list[0]["seller_id"] == "seller-e2e-01"
    assert regular_list[0]["notes"] == payload_fav["notes"]

    # ตรวจสอบว่าในหน้าประวัติ ตอนนี้ is_regular_customer เป็น True แล้ว
    resp1_updated = client.get("/api/v1/collectors/post-job/history?saleng_id=saleng-01&period=all")
    assert resp1_updated.json()["items"][0]["is_regular_customer"] is True

    # -------------------------------------------------------------
    # Step 3: รายงานปัญหาหน้างานผู้ขาย No-show จากสถานะ S3
    # -------------------------------------------------------------
    order_dispute_id = "order-b07-e2e-enroute"
    payload_mismatch = {
        "saleng_id": "saleng-01",
        "order_id": order_dispute_id,
        "mismatch_reason": "SELLER_NO_SHOW",
        "evidence_photo_url": "https://storage.saleng.app/disputes/no-show-e2e.jpg",
        "notes": "เดินทางไปถึงหน้าบ้านตามเวลานัดแล้ว โทรติดต่อผู้ขาย 3 ครั้งไม่มีผู้รับสาย",
        "current_lat": 13.7563,
        "current_lng": 100.5018,
    }
    resp4 = client.post("/api/v1/collectors/post-job/report-mismatch", json=payload_mismatch)
    assert resp4.status_code == 200
    mismatch_res = resp4.json()
    assert mismatch_res["status"] == "success"
    assert mismatch_res["new_status"] == "S8"
    assert mismatch_res["dispute_id"].startswith("DISP-")

    # -------------------------------------------------------------
    # Step 4: ตรวจสอบสถานะคำขอใน Store ปลดล็อกซาเล้ง
    # -------------------------------------------------------------
    order_in_store = supabase_store.get_order(order_dispute_id)
    assert order_in_store["status"] == "S8"
    assert order_in_store["active_collector_lock"] is False
    assert order_in_store["dispute_id"] == mismatch_res["dispute_id"]

    # -------------------------------------------------------------
    # Step 5: ตรวจสอบ Audit Log ทุกขั้นตอน (REQ-SEC-001)
    # -------------------------------------------------------------
    fav_logs = [log for log in supabase_store.audit_logs if log.get("action") == "COLLECTOR_BOOKMARKED_CUSTOMER"]
    assert len(fav_logs) > 0
    assert fav_logs[-1]["entity_id"] == "seller-e2e-01"
    assert fav_logs[-1]["actor_id"] == "saleng-01"

    dispute_logs = [log for log in supabase_store.audit_logs if log.get("action") == "COLLECTOR_REPORTED_MISMATCH"]
    assert len(dispute_logs) > 0
    assert dispute_logs[-1]["entity_id"] == order_dispute_id
    assert dispute_logs[-1]["actor_id"] == "saleng-01"

