"""
End-to-End Integration Test สำหรับ Seller Feature 07: ระบบหลังทำธุรกรรม (Post-Transaction)
รองรับ Use Case UC-10, SC-05, REQ-FN-005, REQ-SEC-001, REQ-SEC-002, AC-S07-01..05, P-01..P-06
"""

import uuid
from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


def test_e2e_post_transaction_lifecycle():
    """
    ทดสอบครบวงจรระบบหลังทำธุรกรรม (End-to-End):
    1. จำลองใบงานที่ปิดงานสมบูรณ์แล้ว (S7) พร้อมใบเสร็จดิจิทัล
    2. ผู้ขายส่งคะแนนดาว 5 ดาวและรีวิว -> คะแนนเฉลี่ยซาเล้งถูกอัปเดต (AC-S07-01)
    3. ตรวจสอบการบล็อกส่งรีวิวซ้ำ (409 Conflict) (P-01, Q-02)
    4. ผู้ขายบันทึกซาเล้งเป็น "ผู้รับซื้อประจำ" (AC-S07-02, Q-03)
    5. ผู้ขายดึงข้อมูลประวัติการขายย้อนหลัง -> สรุปสถิติ 3 ด้าน และ PII Masking (AC-S07-03, REQ-SEC-002)
    6. ผู้ขายเปิดดูใบเสร็จดิจิทัลของใบงานเดิม -> รายละเอียดครบถ้วน (AC-S07-04, REQ-FN-005)
    7. ตรวจสอบความสมบูรณ์ของ Audit Logs ทุกการกระทำ (AC-S07-05, REQ-SEC-001)
    """
    seller_id = "SELLER-E2E-07"
    collector_id = "COLLECTOR-E2E-SOMCHAI"
    order_id = "ORDER-E2E-S07-FULL"

    # -------------------------------------------------------------------------
    # 1. จัดเตรียมคำขอในสถานะ S7 พร้อมรายการและใบเสร็จดิจิทัล
    # -------------------------------------------------------------------------
    supabase_store.orders[order_id] = {
        "order_id": order_id,
        "seller_id": seller_id,
        "seller_name": "คุณสมศรี มีของเก่า",
        "seller_phone": "0811223344",
        "collector_id": collector_id,
        "collector_name": "นายสมชาย ใจซื่อ",
        "buyer_phone": "0899887766",
        "status": "S7",
        "payment_method": "PROMPTPAY",
        "total_settled_amount": 450.0,
        "payment_confirmed_at": "2026-11-03T14:30:00Z",
    }

    supabase_store.items[str(uuid.uuid4())] = {
        "order_id": order_id,
        "category_code": "MAT-CARDBOARD",
        "category_name": "กระดาษลัง",
        "actual_quantity": 45.0,
        "unit": "kg",
        "locked_unit_price": 10.0,
        "settled_item_price": 450.0,
    }

    receipt_no = "REC-20261103-E2E7"
    supabase_store.create_digital_receipt({
        "receipt_no": receipt_no,
        "order_id": order_id,
        "seller_id": seller_id,
        "seller_name": "คุณสมศรี มีของเก่า",
        "seller_phone_masked": "08X-XXX-3344",
        "buyer_id": collector_id,
        "buyer_name": "นายสมชาย ใจซื่อ",
        "buyer_phone_masked": "08X-XXX-7766",
        "total_amount": 450.0,
        "payment_method": "PROMPTPAY",
        "items": [
            {
                "category_code": "MAT-CARDBOARD",
                "category_name": "กระดาษลัง",
                "actual_quantity": 45.0,
                "unit": "kg",
                "locked_unit_price": 10.0,
                "settled_item_price": 450.0,
            }
        ],
        "issued_at": "2026-11-03T14:30:00Z",
    })

    # -------------------------------------------------------------------------
    # 2. ผู้ขายส่งคะแนนดาว 5 ดาวและรีวิว (AC-S07-01, UC-10)
    # -------------------------------------------------------------------------
    review_payload = {
        "seller_id": seller_id,
        "rating": 5,
        "comment": "บริการรวดเร็วมาก มาตรงเวลา ตาชั่งดิจิทัลเที่ยงตรง",
    }
    resp_review = client.post(f"/api/v1/orders/{order_id}/review", json=review_payload)
    assert resp_review.status_code == 201
    review_data = resp_review.json()
    assert review_data["rating"] == 5
    assert review_data["comment"] == "บริการรวดเร็วมาก มาตรงเวลา ตาชั่งดิจิทัลเที่ยงตรง"

    # ตรวจสอบการอัปเดตคะแนนเฉลี่ยซาเล้ง
    summary_rating = supabase_store.get_collector_rating_summary(collector_id)
    assert summary_rating["average_rating"] >= 4.0
    assert summary_rating["total_reviews"] >= 1

    # -------------------------------------------------------------------------
    # 3. ตรวจสอบการบล็อกส่งรีวิวซ้ำ (409 Conflict - P-01, Q-02)
    # -------------------------------------------------------------------------
    resp_dup = client.post(f"/api/v1/orders/{order_id}/review", json={"seller_id": seller_id, "rating": 4})
    assert resp_dup.status_code == 409
    assert "ได้รับการส่งรีวิวแล้ว" in resp_dup.json()["detail"]

    # -------------------------------------------------------------------------
    # 4. ผู้ขายบันทึกซาเล้งเป็น "ผู้รับซื้อประจำ" (AC-S07-02, Q-03)
    # -------------------------------------------------------------------------
    resp_fav = client.post(f"/api/v1/sellers/{seller_id}/favorites/{collector_id}")
    assert resp_fav.status_code == 200
    assert resp_fav.json()["is_favorite"] is True

    # ดึงรายชื่อผู้รับซื้อประจำ ตรวจสอบว่ามี collector_id อยู่
    resp_fav_list = client.get(f"/api/v1/sellers/{seller_id}/favorites")
    assert resp_fav_list.status_code == 200
    assert collector_id in resp_fav_list.json()

    # -------------------------------------------------------------------------
    # 5. ผู้ขายดึงข้อมูลประวัติการขายย้อนหลัง (AC-S07-03, REQ-SEC-002)
    # -------------------------------------------------------------------------
    resp_history = client.get(f"/api/v1/sellers/{seller_id}/sales-history")
    assert resp_history.status_code == 200
    hist_data = resp_history.json()

    # สถิติสรุปสะสม
    assert hist_data["summary"]["total_sales_amount"] == 450.0
    assert hist_data["summary"]["total_weight_kg"] == 45.0
    assert hist_data["summary"]["total_completed_orders"] >= 1

    # ตรวจสอบรายการใบงาน
    order_in_hist = next(o for o in hist_data["orders"] if o["order_id"] == order_id)
    assert order_in_hist["is_favorite_collector"] is True
    assert order_in_hist["has_reviewed"] is True

    # REQ-SEC-002: ตรวจสอบ PII Masking
    assert order_in_hist["collector_phone_masked"] == "08X-XXX-7766"
    assert "0899887766" not in resp_history.text

    # -------------------------------------------------------------------------
    # 6. ผู้ขายเปิดดูใบเสร็จดิจิทัล (AC-S07-04, REQ-FN-005)
    # -------------------------------------------------------------------------
    resp_rcpt = client.get(f"/api/v1/receipts/{order_id}")
    assert resp_rcpt.status_code == 200
    receipt_obj = resp_rcpt.json()
    assert receipt_obj["receipt_no"] == receipt_no
    assert receipt_obj["total_amount"] == 450.0

    # -------------------------------------------------------------------------
    # 7. ตรวจสอบ Audit Log ของทุกการกระทำ (AC-S07-05, REQ-SEC-001)
    # -------------------------------------------------------------------------
    seller_logs = [l for l in supabase_store.audit_logs if l.get("actor_id") == seller_id]
    actions = [l["action"] for l in seller_logs]
    assert "SELLER_SUBMIT_REVIEW" in actions
    assert "SELLER_ADD_FAVORITE" in actions

