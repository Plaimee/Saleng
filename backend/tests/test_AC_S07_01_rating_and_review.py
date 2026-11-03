"""
Automated Backend Tests สำหรับ AC-S07-01: Post-Job Rating & Review
รองรับ UC-10, SC-05, REQ-SEC-001, AC-S07-01, P-01, P-05, Q-01, Q-02
"""

from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


def setup_function():
    """เตรียมข้อมูลคำขอในสถานะต่างๆ สำหรับการทดสอบ"""
    # 1. คำขอที่จบงานแล้ว (S7)
    supabase_store.orders["ORDER-S7-01"] = {
        "order_id": "ORDER-S7-01",
        "seller_id": "SELLER-01",
        "collector_id": "COLLECTOR-SOMKID",
        "status": "S7",
        "total_settled_amount": 350.0,
    }

    # 2. คำขอที่ยังไม่จบงาน (S5: ชั่งของ / รอคอนเฟิร์ม)
    supabase_store.orders["ORDER-S5-01"] = {
        "order_id": "ORDER-S5-01",
        "seller_id": "SELLER-01",
        "collector_id": "COLLECTOR-SOMKID",
        "status": "S5",
    }


def test_submit_review_success():
    """
    AC-S07-01: ผู้ขายสามารถให้คะแนนดาว 1-5 ดาว และเขียนรีวิวหลังจบงาน (S7)
    และระบบบันทึก Audit Log SELLER_SUBMIT_REVIEW
    """
    order_id = "ORDER-S7-01"
    payload = {
        "seller_id": "SELLER-01",
        "rating": 5,
        "comment": "ซาเล้งตรงต่อเวลา สุภาพ ตาชั่งเที่ยงตรงมาก",
    }

    response = client.post(f"/api/v1/orders/{order_id}/review", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert data["order_id"] == order_id
    assert data["seller_id"] == "SELLER-01"
    assert data["collector_id"] == "COLLECTOR-SOMKID"
    assert data["rating"] == 5
    assert data["comment"] == "ซาเล้งตรงต่อเวลา สุภาพ ตาชั่งเที่ยงตรงมาก"

    # ตรวจสอบการดึงข้อมูลรีวิว
    get_resp = client.get(f"/api/v1/orders/{order_id}/review")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == data["id"]

    # ตรวจสอบ Audit Log (REQ-SEC-001, AC-S07-05)
    logs = [
        l for l in supabase_store.audit_logs
        if l["action"] == "SELLER_SUBMIT_REVIEW" and l["entity_id"] == order_id
    ]
    assert len(logs) >= 1
    assert logs[-1]["details"]["rating"] == 5


def test_submit_review_non_s7_rejected():
    """
    AC-S07-01 / MD-STM-04: บล็อกการส่งรีวิวหากคำขอยังไม่เข้าสู่สถานะ S7: Completed (400 Bad Request)
    """
    order_id = "ORDER-S5-01"
    payload = {
        "seller_id": "SELLER-01",
        "rating": 4,
        "comment": "ยังไม่จบงานแต่พยายามรีวิว",
    }

    response = client.post(f"/api/v1/orders/{order_id}/review", json=payload)
    assert response.status_code == 400
    assert "เฉพาะคำขอที่จบงานสมบูรณ์แล้ว" in response.json()["detail"]


def test_submit_review_forbidden_seller():
    """
    AC-S07-01: ผู้ใช้คนอื่นที่ไม่ใช่ผู้ขายของคำขอ ไม่สามารถส่งรีวิวได้ (403 Forbidden)
    """
    order_id = "ORDER-S7-01"
    payload = {
        "seller_id": "SELLER-OTHER",  # ไม่ใช่เจ้าของ
        "rating": 5,
    }

    response = client.post(f"/api/v1/orders/{order_id}/review", json=payload)
    assert response.status_code == 403
    assert "ไม่มีสิทธิ์ส่งรีวิว" in response.json()["detail"]


def test_submit_duplicate_review_blocked():
    """
    AC-S07-01 / P-01 / Q-02: ป้องกันการส่งรีวิวซ้ำในคำขอเดิม (409 Conflict)
    """
    # จำลองว่า ORDER-S7-01 มีรีวิวอยู่แล้วจาก test ก่อนหน้า หรือสร้างใหม่
    order_id = "ORDER-S7-DUP"
    supabase_store.orders[order_id] = {
        "order_id": order_id,
        "seller_id": "SELLER-01",
        "collector_id": "COLLECTOR-DUP",
        "status": "S7",
    }

    # ส่งรีวิวครั้งแรก ผ่าน
    resp1 = client.post(f"/api/v1/orders/{order_id}/review", json={"seller_id": "SELLER-01", "rating": 5})
    assert resp1.status_code == 201

    # ส่งรีวิวครั้งที่สอง ต้องถูกบล็อกด้วย 409 Conflict
    resp2 = client.post(f"/api/v1/orders/{order_id}/review", json={"seller_id": "SELLER-01", "rating": 3})
    assert resp2.status_code == 409
    assert "ได้รับการส่งรีวิวแล้ว" in resp2.json()["detail"]

