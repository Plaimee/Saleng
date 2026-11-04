"""
Acceptance Tests for AC-B07-01: Purchase History Log & Aggregated Stats
(Task T-02: UC-10, REQ-FN-005, REQ-SEC-002, D-B07-05)
"""

from datetime import datetime, timezone
import pytest
from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_history_test_environment():
    """เตรียมข้อมูลคำขอขายสถานะ S7 และโปรไฟล์ซาเล้งสำหรับการทดสอบประวัติการรับซื้อ"""
    order1 = "order-b07-ac01-1"
    order2 = "order-b07-ac01-2"
    order_old = "order-b07-ac01-old"

    now_iso = datetime.now(timezone.utc).isoformat()

    supabase_store.orders[order1] = {
        "order_id": order1,
        "seller_id": "seller-01",
        "saleng_id": "saleng-01",
        "buyer_id": "saleng-01",
        "status": "S7",
        "completed_at": now_iso,
        "total_settled_amount": 350.0,
        "seller_name": "คุณวิภาดา รักษ์โลก",
        "seller_phone": "0891234567",
        "payment_method": "PROMPTPAY",
        "receipt_id": "REC-20261104-0001",
        "items": [
            {
                "item_id": "it-1",
                "category_name": "กระดาษลัง",
                "actual_quantity": 50.0,
                "unit": "กก.",
            },
            {
                "item_id": "it-2",
                "category_name": "ขวดแก้วใส",
                "actual_quantity": 20.0,
                "unit": "กก.",
            },
        ],
    }

    supabase_store.orders[order2] = {
        "order_id": order2,
        "seller_id": "seller-02",
        "saleng_id": "saleng-01",
        "buyer_id": "saleng-01",
        "status": "S7",
        "completed_at": now_iso,
        "total_settled_amount": 200.0,
        "seller_name": "ลุงสมหมาย",
        "seller_phone": "0867654321",
        "payment_method": "CASH",
        "receipt_id": "REC-20261104-0002",
        "items": [
            {
                "item_id": "it-3",
                "category_name": "พลาสติกรวม",
                "actual_quantity": 40.0,
                "unit": "กก.",
            }
        ],
    }

    # คำขอเก่าเมื่อ 2 เดือนก่อน
    supabase_store.orders[order_old] = {
        "order_id": order_old,
        "seller_id": "seller-03",
        "saleng_id": "saleng-01",
        "buyer_id": "saleng-01",
        "status": "S7",
        "completed_at": "2026-08-15T09:00:00Z",
        "total_settled_amount": 500.0,
        "seller_name": "ป้าสมใจ",
        "seller_phone": "0855554433",
        "payment_method": "CASH",
        "items": [],
    }

    orig_profile = dict(supabase_store.saleng_profiles.get("saleng-01", {}))
    supabase_store.saleng_profiles["saleng-01"].update({
        "verified": True,
        "kyc_status": "VERIFIED",
    })

    yield

    supabase_store.orders.pop(order1, None)
    supabase_store.orders.pop(order2, None)
    supabase_store.orders.pop(order_old, None)
    if orig_profile:
        supabase_store.saleng_profiles["saleng-01"] = orig_profile


def test_AC_B07_01_get_purchase_history_all():
    """ซาเล้งสามารถดึงประวัติการรับซื้อทั้งหมด พร้อมสถิติสะสม 3 มิติและ PII Masking"""
    resp = client.get("/api/v1/collectors/post-job/history?saleng_id=saleng-01&period=all")
    assert resp.status_code == 200
    data = resp.json()
    assert data["period"] == "all"

    summary = data["summary"]
    # 350 + 200 + 500 = 1050.0 บาท
    assert summary["total_expense_baht"] == 1050.0
    # 70 + 40 + 0 = 110.0 กก.
    assert summary["total_weight_kg"] == 110.0
    assert summary["total_completed_jobs"] == 3

    assert len(data["items"]) == 3
    first_item = data["items"][0]
    # ตรวจสอบ PII Masking (0891234567 -> 08X-XXX-4567)
    assert first_item["seller_phone_masked"] in ["08X-XXX-4567", "08X-XXX-4321"]
    assert first_item["status"] == "S7"


def test_AC_B07_01_filter_by_today():
    """ซาเล้งสามารถกรองประวัติเฉพาะวันนี้ (Today) ได้"""
    resp = client.get("/api/v1/collectors/post-job/history?saleng_id=saleng-01&period=today")
    assert resp.status_code == 200
    data = resp.json()
    assert data["period"] == "today"

    summary = data["summary"]
    # เฉพาะ order1 และ order2 ของวันนี้: 350 + 200 = 550.0 บาท
    assert summary["total_expense_baht"] == 550.0
    assert summary["total_weight_kg"] == 110.0
    assert summary["total_completed_jobs"] == 2
    assert len(data["items"]) == 2


def test_AC_B07_01_unverified_saleng_blocked():
    """ซาเล้งที่ยังไม่ผ่าน KYC ถูกปฏิเสธไม่ให้เข้าถึงประวัติ (HTTP 403)"""
    supabase_store.saleng_profiles["saleng-unverified"] = {
        "id": "saleng-unverified",
        "verified": False,
        "kyc_status": "PENDING",
    }
    resp = client.get("/api/v1/collectors/post-job/history?saleng_id=saleng-unverified")
    assert resp.status_code == 403
    del supabase_store.saleng_profiles["saleng-unverified"]

