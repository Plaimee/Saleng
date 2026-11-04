"""
Full-Lifecycle Integration E2E Test Suite for Admin Benchmark Price & Quality Grading Management
รองรับ UC-03, UC-05, REQ-DAT-001, REQ-FN-003, REQ-BR-002, REQ-SEC-001, CC-01..06, D-00-02, D-A02-01..06, AC-A02-01..05
"""

import uuid
import pytest
from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_and_restore_state():
    """บันทึกและกู้คืนสถานะข้อมูลหลังการทดสอบ E2E เพื่อป้องกันผลข้างเคียงต่อชุดทดสอบอื่น"""
    orig_cardboard = dict(supabase_store.benchmark_prices.get("MAT-CARDBOARD", {}))
    orig_white = dict(supabase_store.benchmark_prices.get("MAT-WHITE-PAPER", {}))
    orig_fridge = dict(supabase_store.benchmark_prices.get("BULKY-FRIDGE", {}))
    orig_tv = dict(supabase_store.benchmark_prices.get("BULKY-TV", {}))
    test_orders = []

    yield test_orders

    if orig_cardboard:
        supabase_store.benchmark_prices["MAT-CARDBOARD"] = orig_cardboard
    if orig_white:
        supabase_store.benchmark_prices["MAT-WHITE-PAPER"] = orig_white
    if orig_fridge:
        supabase_store.benchmark_prices["BULKY-FRIDGE"] = orig_fridge
    if orig_tv:
        supabase_store.benchmark_prices["BULKY-TV"] = orig_tv
    for oid in test_orders:
        supabase_store.orders.pop(oid, None)


def test_e2e_admin_benchmark_price_and_grading_lifecycle(clean_and_restore_state):
    """
    ทดสอบวงจรชีวิตเต็มรูปแบบของฟีเจอร์ Admin 02:
    1. ตรวจสอบสิทธิ์ RBAC (บล็อกผู้ใช้ที่ไม่ใช่แอดมินด้วย HTTP 403)
    2. เรียกดูรายการราคากลางรายวันทั้งหมด พร้อมตรวจสอบ Validation ช่วงราคา
    3. แก้ไขราคากลางเดี่ยว (Min-Max) และทดสอบระบบเตือนราคาขยับเกิน 50%
    4. ตรวจสอบและปรับปรุงเกณฑ์คุณภาพ 3 ระดับ (GRADE_A: 0%, GRADE_B: 5%, GRADE_C: 10%)
    5. ตรวจสอบและอัปเดตราคาขยะชิ้นใหญ่เหมาจ่าย (หน่วย PIECE) และ Batch Update
    6. ทดสอบความถูกต้องของ Price Snapshot: ออเดอร์ S1/S2 อัปเดตราคาใหม่, ออเดอร์ S3..S7 ล็อกราคาเดิม
    7. ตรวจสอบความสมบูรณ์ของ Audit Log ทุกขั้นตอน
    """

    # -------------------------------------------------------------
    # ขั้นที่ 1: ตรวจสอบความปลอดภัย Admin RBAC (CC-03, D-A02-06, AC-A02-05)
    # -------------------------------------------------------------
    unauth_res = client.get("/api/v1/admin/benchmark-prices")
    assert unauth_res.status_code == 403

    wrong_role_res = client.put(
        "/api/v1/admin/benchmark-prices/MAT-CARDBOARD",
        json={"min_price_per_unit": 3.0, "max_price_per_unit": 4.0},
        headers={"X-Admin-Role": "SELLER"},
    )
    assert wrong_role_res.status_code == 403

    # -------------------------------------------------------------
    # ขั้นที่ 2: เรียกดูรายการราคากลางรายวันด้วยสิทธิ์แอดมิน (UC-03, REQ-DAT-001, AC-A02-01)
    # -------------------------------------------------------------
    list_res = client.get(
        "/api/v1/admin/benchmark-prices",
        headers={"X-Admin-Role": "ADMIN"},
    )
    assert list_res.status_code == 200
    all_prices = list_res.json()
    assert len(all_prices) >= 11
    for p in all_prices:
        assert p["min_price_per_unit"] > 0
        assert p["max_price_per_unit"] >= p["min_price_per_unit"]
        assert p["effective_date"] is not None

    # -------------------------------------------------------------
    # ขั้นที่ 3: แก้ไขราคากลางรายวัน และทดสอบระบบเตือนยืนยัน 50% (D-A02-02, BR-01)
    # -------------------------------------------------------------
    # 3.1 ลองเปลี่ยนราคาเกิน 50% โดยไม่ confirm -> ต้องถูกบล็อกด้วย HTTP 400
    excessive_shift = {
        "min_price_per_unit": 8.0,
        "max_price_per_unit": 10.0,
        "confirm_shift": False,
        "updated_by": "admin-01",
    }
    block_res = client.put(
        "/api/v1/admin/benchmark-prices/MAT-CARDBOARD",
        json=excessive_shift,
        headers={"X-Admin-Role": "ADMIN"},
    )
    assert block_res.status_code == 400
    assert "PRICE_SHIFT_EXCEEDS_50_PERCENT" in str(block_res.json())

    # 3.2 ปรับเปลี่ยนราคาตามปกติ (< 50%) -> สำเร็จ
    normal_update = {
        "min_price_per_unit": 3.20,
        "max_price_per_unit": 4.20,
        "grading_condition": "แห้ง สะอาด ไม่เปียกชื้น",
        "confirm_shift": False,
        "updated_by": "admin-01",
        "change_reason": "ปรับตามราคาอ้างอิงรายวัน",
    }
    ok_res = client.put(
        "/api/v1/admin/benchmark-prices/MAT-CARDBOARD",
        json=normal_update,
        headers={"X-Admin-Role": "ADMIN"},
    )
    assert ok_res.status_code == 200
    assert ok_res.json()["min_price_per_unit"] == 3.20
    assert ok_res.json()["max_price_per_unit"] == 4.20

    # -------------------------------------------------------------
    # ขั้นที่ 4: ตรวจสอบและปรับปรุงเกณฑ์คุณภาพ 3 ระดับ (UC-03, REQ-FN-003, AC-A02-02, D-A02-03)
    # -------------------------------------------------------------
    get_grading_res = client.get(
        "/api/v1/admin/benchmark-prices/grading/MAT-CARDBOARD",
        headers={"X-Admin-Role": "ADMIN"},
    )
    assert get_grading_res.status_code == 200
    grading_rules = get_grading_res.json()
    assert len(grading_rules) == 3

    # ตรวจสอบเปอร์เซ็นต์หักสิ่งปนเปื้อน 0%, 5%, 10%
    grades_map = {r["grade_level"]: r for r in grading_rules}
    assert grades_map["GRADE_A"]["contamination_deduction_percent"] == 0.0
    assert grades_map["GRADE_B"]["contamination_deduction_percent"] == 5.0
    assert grades_map["GRADE_C"]["contamination_deduction_percent"] == 10.0

    # ปรับปรุงคำอธิบายเกณฑ์
    grading_rules[0]["description"] = "แห้งสนิท ลังใหม่ ไม่โดนน้ำ"
    update_grading_res = client.put(
        "/api/v1/admin/benchmark-prices/grading/MAT-CARDBOARD",
        json={"rules": grading_rules, "updated_by": "admin-01"},
        headers={"X-Admin-Role": "ADMIN"},
    )
    assert update_grading_res.status_code == 200
    assert update_grading_res.json()["rules"][0]["description"] == "แห้งสนิท ลังใหม่ ไม่โดนน้ำ"

    # -------------------------------------------------------------
    # ขั้นที่ 5: จัดการราคาขยะชิ้นใหญ่เหมาจ่าย (UC-05, REQ-FN-003, AC-A02-03, D-A02-04)
    # -------------------------------------------------------------
    bulky_res = client.get(
        "/api/v1/admin/benchmark-prices?unit=piece",
        headers={"X-Admin-Role": "ADMIN"},
    )
    assert bulky_res.status_code == 200
    bulky_list = bulky_res.json()
    assert len(bulky_list) >= 5
    bulky_codes = [b["category_code"] for b in bulky_list]
    assert "BULKY-FRIDGE" in bulky_codes
    assert "BULKY-WASHING-MACHINE" in bulky_codes
    assert "BULKY-AIR-CONDITIONER" in bulky_codes
    assert "BULKY-TV" in bulky_codes
    assert "BULKY-FURNITURE" in bulky_codes

    # ทำ Batch Update ขยะชิ้นใหญ่
    batch_payload = {
        "items": [
            {
                "category_code": "BULKY-FRIDGE",
                "min_price_per_unit": 220.0,
                "max_price_per_unit": 320.0,
                "confirm_shift": False,
            },
            {
                "category_code": "BULKY-TV",
                "min_price_per_unit": 55.0,
                "max_price_per_unit": 155.0,
                "confirm_shift": False,
            },
        ],
        "effective_date": "2026-11-05",
        "updated_by": "admin-01",
    }
    batch_res = client.post(
        "/api/v1/admin/benchmark-prices/batch-update",
        json=batch_payload,
        headers={"X-Admin-Role": "ADMIN"},
    )
    assert batch_res.status_code == 200
    assert batch_res.json()["updated_count"] == 2

    # -------------------------------------------------------------
    # ขั้นที่ 6: ทดสอบความถูกต้องของ Price Snapshot (REQ-BR-002, D-00-02, D-A02-05, AC-A02-04)
    # -------------------------------------------------------------
    # สร้างออเดอร์ S2
    oid_s2 = f"e2e-order-s2-{uuid.uuid4().hex[:6]}"
    iid_s2 = f"e2e-item-s2-{uuid.uuid4().hex[:6]}"
    clean_and_restore_state.append(oid_s2)
    supabase_store.orders[oid_s2] = {
        "order_id": oid_s2,
        "seller_id": "seller-01",
        "status": "S2",
        "total_est_min_price": 320.0,
        "total_est_max_price": 420.0,
        "items": [
            {
                "item_id": iid_s2,
                "order_id": oid_s2,
                "category_code": "MAT-CARDBOARD",
                "quantity": 100.0,
                "unit": "kg",
                "est_min_price": 320.0,
                "est_max_price": 420.0,
            }
        ],
    }
    supabase_store.items[iid_s2] = supabase_store.orders[oid_s2]["items"][0]

    # สร้างออเดอร์ S3 (ล็อก Price Snapshot 3.20 บาท)
    oid_s3 = f"e2e-order-s3-{uuid.uuid4().hex[:6]}"
    iid_s3 = f"e2e-item-s3-{uuid.uuid4().hex[:6]}"
    clean_and_restore_state.append(oid_s3)
    supabase_store.orders[oid_s3] = {
        "order_id": oid_s3,
        "seller_id": "seller-02",
        "buyer_id": "saleng-01",
        "status": "S3",
        "total_est_min_price": 320.0,
        "total_est_max_price": 420.0,
        "items": [
            {
                "item_id": iid_s3,
                "order_id": oid_s3,
                "category_code": "MAT-CARDBOARD",
                "quantity": 100.0,
                "unit": "kg",
                "est_min_price": 320.0,
                "est_max_price": 420.0,
                "locked_unit_price": 3.20,
            }
        ],
    }
    supabase_store.items[iid_s3] = supabase_store.orders[oid_s3]["items"][0]

    # แอดมินปรับราคากลาง MAT-CARDBOARD อีกครั้งเป็น 3.80 - 4.80 บาท/กก.
    client.put(
        "/api/v1/admin/benchmark-prices/MAT-CARDBOARD",
        json={"min_price_per_unit": 3.80, "max_price_per_unit": 4.80, "confirm_shift": False},
        headers={"X-Admin-Role": "ADMIN"},
    )

    # ออเดอร์ S2: ต้องได้รับการคำนวณใหม่ตามเรต 3.80 - 4.80 (380 - 480 บาท)
    check_s2 = supabase_store.get_order(oid_s2)
    assert check_s2["total_est_min_price"] == 380.0
    assert check_s2["total_est_max_price"] == 480.0

    # ออเดอร์ S3: ต้องยังคงล็อกราคาเดิมตาม Price Snapshot (320 - 420 บาท)
    check_s3 = supabase_store.get_order(oid_s3)
    assert check_s3["total_est_min_price"] == 320.0
    assert check_s3["total_est_max_price"] == 420.0
    assert check_s3["items"][0]["locked_unit_price"] == 3.20

    # -------------------------------------------------------------
    # ขั้นที่ 7: ตรวจสอบความสมบูรณ์ของ Audit Logs (REQ-SEC-001, AC-A02-05)
    # -------------------------------------------------------------
    price_audits = [a for a in supabase_store.audit_logs if a["action"] == "ADMIN_UPDATED_BENCHMARK_PRICE"]
    grading_audits = [a for a in supabase_store.audit_logs if a["action"] == "ADMIN_UPDATED_GRADING_RULES"]
    assert len(price_audits) >= 1
    assert len(grading_audits) >= 1
    assert price_audits[-1]["actor_id"] == "admin-01"
    assert grading_audits[-1]["actor_id"] == "admin-01"

