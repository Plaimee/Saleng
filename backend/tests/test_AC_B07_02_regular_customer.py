"""
Acceptance Tests for AC-B07-02: Regular Customer Bookmark & Notes
(Task T-03: UC-10, REQ-SEC-001, REQ-SEC-002, D-B07-03)
"""

import pytest
from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_regular_customer_environment():
    """เตรียมข้อมูลสำหรับการทดสอบลูกค้าประจำ"""
    orig_profile = dict(supabase_store.saleng_profiles.get("saleng-01", {}))
    supabase_store.saleng_profiles["saleng-01"].update({
        "verified": True,
        "kyc_status": "VERIFIED",
    })

    supabase_store.sellers["seller-ac02"] = {
        "id": "seller-ac02",
        "display_name": "คุณวิภาดา ซอยอารีย์",
        "phone": "0812345678",
        "latitude": 13.7563,
        "longitude": 100.5018,
    }

    # ล้างรายการลูกค้าประจำของ saleng-01
    supabase_store.collector_favorite_sellers = [
        f for f in supabase_store.collector_favorite_sellers if f.get("collector_id") != "saleng-01"
    ]

    yield

    supabase_store.sellers.pop("seller-ac02", None)
    supabase_store.collector_favorite_sellers = [
        f for f in supabase_store.collector_favorite_sellers if f.get("collector_id") != "saleng-01"
    ]
    if orig_profile:
        supabase_store.saleng_profiles["saleng-01"] = orig_profile


def test_AC_B07_02_toggle_bookmark_and_retrieve():
    """ซาเล้งสามารถปักหมุดลูกค้าประจำพร้อมบันทึกย่อ และดึงรายชื่อลูกค้าประจำได้"""
    payload = {
        "saleng_id": "saleng-01",
        "seller_id": "seller-ac02",
        "notes": "บ้านรั้วสีฟ้า มีทองแดงและแบตเตอรี่บ่อย สะดวกเสาร์-อาทิตย์",
        "latitude": 13.7563,
        "longitude": 100.5018,
    }

    # 1. กดปักหมุดลูกค้าประจำ (Toggle ON)
    resp1 = client.post("/api/v1/collectors/post-job/regular-customers", json=payload)
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert data1["status"] == "success"
    assert data1["is_favorite"] is True

    # 2. ดึงรายชื่อลูกค้าประจำ
    resp2 = client.get("/api/v1/collectors/post-job/regular-customers?saleng_id=saleng-01")
    assert resp2.status_code == 200
    list_data = resp2.json()
    assert len(list_data) == 1
    fav = list_data[0]
    assert fav["seller_id"] == "seller-ac02"
    assert fav["notes"] == payload["notes"]
    assert fav["latitude"] == 13.7563
    assert fav["longitude"] == 100.5018
    assert fav["seller_phone_masked"] == "08X-XXX-5678"

    # ตรวจสอบ Audit Log (REQ-SEC-001)
    logs = [log for log in supabase_store.audit_logs if log.get("action") == "COLLECTOR_BOOKMARKED_CUSTOMER"]
    assert len(logs) > 0
    assert logs[-1]["entity_id"] == "seller-ac02"
    assert logs[-1]["actor_id"] == "saleng-01"

    # 3. กดซ้ำเพื่อยกเลิกการปักหมุด (Toggle OFF)
    resp3 = client.post("/api/v1/collectors/post-job/regular-customers", json=payload)
    assert resp3.status_code == 200
    data3 = resp3.json()
    assert data3["is_favorite"] is False

    # ตรวจสอบว่ารายชื่อลดลงเหลือ 0
    resp4 = client.get("/api/v1/collectors/post-job/regular-customers?saleng_id=saleng-01")
    assert resp4.status_code == 200
    assert len(resp4.json()) == 0


def test_AC_B07_02_notes_length_validation():
    """บันทึกย่อช่วยจำมีความยาวเกิน 200 ตัวอักษรไม่ได้"""
    payload = {
        "saleng_id": "saleng-01",
        "seller_id": "seller-ac02",
        "notes": "A" * 201,
    }
    resp = client.post("/api/v1/collectors/post-job/regular-customers", json=payload)
    assert resp.status_code == 422

