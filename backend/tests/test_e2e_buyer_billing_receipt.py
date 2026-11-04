"""
End-to-End Integration Test for Buyer Billing & Receipt System
(Task T-08: UC-05, UC-06, UC-07, REQ-FN-002, REQ-FN-004, REQ-FN-005, REQ-BR-002, REQ-SEC-001, REQ-SEC-002, CC-01, CC-04, CC-06, D-B06-01..06)
"""

import pytest
from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_e2e_test_environment():
    """เตรียมข้อมูลคำขอขายและโปรไฟล์สำหรับการทดสอบ E2E เต็มวงรอบ"""
    order_id = "order-b06-e2e"
    item_1 = "item-b06-e2e-1"
    item_2 = "item-b06-e2e-2"

    supabase_store.orders[order_id] = {
        "order_id": order_id,
        "seller_id": "seller-01",
        "saleng_id": "saleng-01",
        "buyer_id": "saleng-01",
        "status": "S4",
        "seller_name": "คุณวิภาดา รักษ์โลก",
        "seller_phone": "0898765432",
        "seller_confirmed_weight": False,
        "items": [
            {
                "item_id": item_1,
                "order_id": order_id,
                "category_code": "PAPER_BOX",
                "category_name": "กระดาษลัง",
                "estimated_quantity": 40.0,
                "locked_unit_price": 4.5,
                "unit": "กก.",
            },
            {
                "item_id": item_2,
                "order_id": order_id,
                "category_code": "GLASS_CLEAR",
                "category_name": "ขวดแก้วใส",
                "estimated_quantity": 20.0,
                "locked_unit_price": 2.5,
                "unit": "กก.",
            },
        ],
    }

    supabase_store.items[item_1] = dict(supabase_store.orders[order_id]["items"][0])
    supabase_store.items[item_2] = dict(supabase_store.orders[order_id]["items"][1])

    orig_profile = dict(supabase_store.saleng_profiles.get("saleng-01", {}))
    supabase_store.saleng_profiles["saleng-01"].update({
        "name": "สมชาย ซาเล้งสุพรรณ",
        "phone": "0812345678",
        "verified": True,
        "kyc_status": "VERIFIED",
    })

    yield

    supabase_store.orders.pop(order_id, None)
    supabase_store.items.pop(item_1, None)
    supabase_store.items.pop(item_2, None)
    if orig_profile:
        supabase_store.saleng_profiles["saleng-01"] = orig_profile


def test_e2e_buyer_billing_and_receipt_full_cycle():
    """
    ทดสอบ Full Lifecycle ของระบบคิดเงินและออกใบเสร็จ (S4 -> S5 -> S6 -> S7):
    1. ดึงใบชั่งน้ำหนักหน้างาน (Weighing Sheet)
    2. บันทึกผลชั่งจริงหน้างานพร้อมรูปถ่ายตาชั่ง (S4 -> S5)
    3. ตรวจสอบ 100% Confirmation Gate: ซาเล้งถูกบล็อกไม่ให้เลือกชำระเงินจนกว่าผู้ขายจะยืนยัน
    4. ผู้ขายตรวจสอบและกดยืนยันน้ำหนัก (S5 -> S6)
    5. ซาเล้งเลือกช่องทางการชำระเงิน (PROMPTPAY)
    6. ตรวจสอบ Gate ก่อนออกใบเสร็จ: ซาเล้งไม่สามารถออกใบเสร็จได้ก่อนผู้ขายยืนยันเงิน
    7. ผู้ขายกดยืนยันรับเงิน (S6 -> S7)
    8. ซาเล้งดึงใบเสร็จสรุปรายการดิจิทัล พร้อมตรวจสอบ Masking เบอร์โทรศัพท์สองฝ่าย
    """
    order_id = "order-b06-e2e"

    # Step 1: ดึงใบชั่งน้ำหนัก
    resp1 = client.get(f"/api/v1/collectors/billing/{order_id}/weighing-sheet?saleng_id=saleng-01")
    assert resp1.status_code == 200
    sheet = resp1.json()
    assert sheet["order_id"] == order_id
    assert sheet["order_status"] == "S4"
    assert len(sheet["items"]) == 2
    assert sheet["seller_phone_masked"] == "08X-XXX-5432"

    # Step 2: บันทึกผลชั่งจริงหน้างาน (item1 = 42 kg, item2 = 18 kg)
    # total_actual = 60 kg vs total_est = 60 kg (diff 0%, is_re_quote = False)
    # total_settled = (42 * 4.5) + (18 * 2.5) = 189.0 + 45.0 = 234.0
    payload_weighing = {
        "saleng_id": "saleng-01",
        "scale_photo_url": "https://storage.saleng.app/scales/e2e-scale.jpg",
        "items": [
            {"item_id": "item-b06-e2e-1", "actual_quantity": 42.0},
            {"item_id": "item-b06-e2e-2", "actual_quantity": 18.0},
        ],
    }
    resp2 = client.post(f"/api/v1/collectors/billing/{order_id}/weighing", json=payload_weighing)
    assert resp2.status_code == 200
    weighing_result = resp2.json()
    assert weighing_result["status"] == "success"
    assert weighing_result["new_status"] == "S5"
    assert weighing_result["total_settled_amount"] == 234.0
    assert weighing_result["seller_confirmed_weight"] is False

    # Step 3: ตรวจสอบ 100% Confirmation Gate (ซาเล้งถูกบล็อกไม่ให้เลือกวิธีจ่ายเงิน)
    resp3 = client.post(
        f"/api/v1/collectors/billing/{order_id}/payment-method",
        json={"saleng_id": "saleng-01", "payment_method": "PROMPTPAY"}
    )
    assert resp3.status_code == 403
    assert "ผู้ขายยังไม่ได้ยืนยันผลการชั่งน้ำหนัก" in resp3.json()["detail"]

    # Step 4: ผู้ขายตรวจสอบและกดยืนยันน้ำหนักบนหน้าจอของตนเอง (S5 -> S6)
    resp4 = client.post(
        f"/api/v1/orders/{order_id}/confirm-weights",
        json={"seller_id": "seller-01"}
    )
    assert resp4.status_code == 200
    confirm_data = resp4.json()
    assert confirm_data["status"] == "S6"
    assert confirm_data["seller_confirmed_weight_at"] is not None

    # Step 5: ซาเล้งเลือกช่องทางการชำระเงิน (PROMPTPAY)
    resp5 = client.post(
        f"/api/v1/collectors/billing/{order_id}/payment-method",
        json={"saleng_id": "saleng-01", "payment_method": "PROMPTPAY"}
    )
    assert resp5.status_code == 200
    pm_data = resp5.json()
    assert pm_data["status"] == "success"
    assert pm_data["payment_method"] == "PROMPTPAY"

    # Step 6: ตรวจสอบ Gate ก่อนออกใบเสร็จ (คำขอยังอยู่ S6 รอยืนยันเงิน จึงยังดึงใบเสร็จไม่ได้)
    resp6 = client.get(f"/api/v1/collectors/billing/{order_id}/receipt?saleng_id=saleng-01")
    assert resp6.status_code == 400
    assert "S7" in resp6.json()["detail"]

    # Step 7: ผู้ขายกดยืนยันรับเงินบนหน้าจอของตนเอง (S6 -> S7)
    resp7 = client.post(
        f"/api/v1/orders/{order_id}/confirm-payment",
        json={"seller_id": "seller-01", "payment_method": "PROMPTPAY"}
    )
    assert resp7.status_code == 200
    payment_confirm_data = resp7.json()
    assert payment_confirm_data["status"] == "S7"

    # Step 8: ซาเล้งดึงใบเสร็จสรุปรายการดิจิทัลเมื่อเสร็จสมบูรณ์
    resp8 = client.get(f"/api/v1/collectors/billing/{order_id}/receipt?saleng_id=saleng-01")
    assert resp8.status_code == 200
    receipt = resp8.json()
    assert receipt["order_id"] == order_id
    assert receipt["seller_name"] == "คุณวิภาดา รักษ์โลก"
    assert receipt["seller_phone_masked"] == "08X-XXX-5432"
    assert receipt["collector_name"] == "สมชาย ซาเล้งสุพรรณ"
    assert receipt["collector_phone_masked"] == "08X-XXX-5678"
    assert receipt["payment_method"] == "PROMPTPAY"
    assert receipt["total_settled_amount"] == 234.0
    assert len(receipt["items"]) == 2
