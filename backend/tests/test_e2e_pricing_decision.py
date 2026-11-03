"""
End-to-End & Performance Integration Tests: Pricing & Decision Flow
รองรับ REQ-QA-001, REQ-BR-002, REQ-FN-001, REQ-FN-006, REQ-SEC-001, AC-S04-01..05, D-01..D-06
"""

import time
import pytest
from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store


client = TestClient(app)


def test_e2e_pricing_and_decision_lifecycle():
    """
    ทดสอบ Flow รวมครบวงจร:
    1. เปิดหน้าราคากลางและตรวจสอบข้อมูลราคารายวัน (06:00 น.)
    2. คำนวณช่วงราคาประเมินและรวมตะกร้าหลายรายการ (Multi-Item Basket พร้อมหน่วยกระสอบ)
    3. ตรวจสอบ Threshold Guard บล็อกเมื่อยอดประเมิน < 500 บาท และ < 2 กระสอบ
    4. ส่งคำขอใหม่โดยเลือกทางเลือกฝากรวมทางผ่าน (isRouteDropIn = True -> สถานะ S2)
    5. ผู้ซื้อกดรับงาน (S2 -> S3) พร้อมล็อก Price Snapshot ในฐานข้อมูล
    6. อัปเดตราคากลางใหม่ในวันถัดไป แต่ Price Snapshot ของใบงานเดิมต้องไม่เปลี่ยน
    """
    # -------------------------------------------------------------------------
    # ขั้นตอนที่ 1: ดึงราคากลางประจำวัน (GET /api/v1/pricing/benchmark-prices)
    # -------------------------------------------------------------------------
    start_time = time.perf_counter()
    resp_bench = client.get("/api/v1/pricing/benchmark-prices")
    bench_latency = time.perf_counter() - start_time

    assert resp_bench.status_code == 200
    assert bench_latency <= 3.0, f"Latency เกินเกณฑ์ 3.0s (จริง: {bench_latency:.4f}s)"

    bench_data = resp_bench.json()
    assert len(bench_data["prices"]) >= 5
    assert "last_updated_at" in bench_data

    # -------------------------------------------------------------------------
    # ขั้นตอนที่ 2: คำนวณช่วงราคาประเมิน Multi-Item Basket (POST /api/v1/pricing/calculate-estimate)
    # ผู้ขายเลือก: กระดาษลัง 20 กก. (3-4 บ.) + ขวดแก้ว 1 กระสอบ (40-60 บ.)
    # -------------------------------------------------------------------------
    basket_payload = {
        "items": [
            {"category_code": "MAT-CARDBOARD", "unit": "kg", "quantity": 20.0},
            {"category_code": "MAT-GLASS-BOTTLE", "unit": "bag", "quantity": 1.0},
        ]
    }

    start_time = time.perf_counter()
    resp_estimate = client.post("/api/v1/pricing/calculate-estimate", json=basket_payload)
    estimate_latency = time.perf_counter() - start_time

    assert resp_estimate.status_code == 200
    assert estimate_latency <= 3.0, f"Latency เกินเกณฑ์ 3.0s (จริง: {estimate_latency:.4f}s)"

    est_data = resp_estimate.json()
    # ตรวจสอบยอดรวม: 20*3 + 1*40 = 100, 20*4 + 1*60 = 140
    assert est_data["total_est_min_price"] == 100.0
    assert est_data["total_est_max_price"] == 140.0
    assert "ราคาจริงขึ้นกับสภาพของหน้างาน" in est_data["disclaimer"]  # BR-01

    # -------------------------------------------------------------------------
    # ขั้นตอนที่ 3: ตรวจสอบ Threshold Guard บล็อกคำขอนัดหมายเดี่ยว (DIRECT)
    # ยอดรวมขั้นต่ำ 100 บาท (< 500 บาท) และขวด 1 กระสอบ (< 2 กระสอบ)
    # -------------------------------------------------------------------------
    submission_payload = {
        "seller_id": "usr-seller-e2e-01",
        "pickup_location_id": "loc-seller-01",
        "items": basket_payload["items"],
        "submission_type": "DIRECT",
    }

    resp_direct = client.post("/api/v1/orders/validate-and-submit", json=submission_payload)
    assert resp_direct.status_code == 400
    err_data = resp_direct.json()
    assert err_data["error"] == "MINIMUM_THRESHOLD_NOT_MET"
    assert "ROUTE_DROP_IN" in err_data["allowed_alternatives"]
    assert "BUILDING_GROUP" in err_data["allowed_alternatives"]

    # -------------------------------------------------------------------------
    # ขั้นตอนที่ 4: ผู้ขายเลือกทางเลือกฝากรวมทางผ่าน (ROUTE_DROP_IN)
    # -------------------------------------------------------------------------
    route_drop_payload = {
        **submission_payload,
        "submission_type": "ROUTE_DROP_IN",
    }

    resp_route = client.post("/api/v1/orders/validate-and-submit", json=route_drop_payload)
    assert resp_route.status_code == 201
    order_data = resp_route.json()

    order_id = order_data["order_id"]
    assert order_data["status"] == "S2"  # S2: Pending
    assert order_data["is_route_drop_in"] is True
    assert order_data["total_est_min_price"] == 100.0

    # ตรวจสอบ Audit Log ว่ามีการบันทึกสถานะ S2
    recent_audit = [log for log in supabase_store.audit_logs if log["entity_id"] == order_id]
    assert len(recent_audit) >= 1
    assert recent_audit[0]["details"]["status"] == "S2"

    # -------------------------------------------------------------------------
    # ขั้นตอนที่ 5: ซาเล้งกดรับนัดหมาย (S2 -> S3) พร้อมล็อก Price Snapshot (REQ-BR-002, D-04)
    # -------------------------------------------------------------------------
    resp_accept = client.post(f"/api/v1/orders/{order_id}/accept?buyer_id=usr-saleng-99")
    assert resp_accept.status_code == 200
    accepted_order = resp_accept.json()

    assert accepted_order["status"] == "S3"
    assert accepted_order["buyer_id"] == "usr-saleng-99"

    # ตรวจสอบว่าทุกรายการมี locked_unit_price (Price Snapshot)
    assert len(accepted_order["items"]) == 2
    for item in accepted_order["items"]:
        assert item["locked_unit_price"] is not None
        assert item["locked_unit_price"] > 0

    # ตรวจสอบรายการขวดแก้วกระสอบ: locked_unit_price ต้องเป็น 40.0
    glass_item = next(i for i in accepted_order["items"] if "GLASS" in i["category_code"])
    assert glass_item["locked_unit_price"] == 40.0

    # -------------------------------------------------------------------------
    # ขั้นตอนที่ 6: อัปเดตราคากลางใหม่ในวันถัดไป แต่ Price Snapshot ของคำขอต้องคงเดิม
    # -------------------------------------------------------------------------
    supabase_store.upsert_benchmark_price({
        "category_code": "MAT-GLASS-BOTTLE-BAG",
        "category_name": "ขวดแก้ว (กระสอบ)",
        "unit": "bag",
        "min_price_per_unit": 20.0,  # ลดราคาลงเหลือ 20 บาท
        "max_price_per_unit": 35.0,
        "grading_condition": "ราคาวันถัดไป",
    })

    # ตรวจสอบคำขอเดิมใน Database
    order_in_db = supabase_store.get_order(order_id)
    saved_glass = next(i for i in order_in_db["items"] if "GLASS" in i["category_code"])
    # ต้องยังคงเป็น 40.0 บาทตามที่ล็อกไว้ตอน S3 ป้องกันข้อพิพาท (REQ-BR-002, D-04)
    assert saved_glass["locked_unit_price"] == 40.0


def test_performance_latency_benchmark():
    """
    ทดสอบเกณฑ์ประสิทธิภาพ Response Time <= 3.0s (P95)
    รองรับ REQ-QA-001, AC-S04-02
    """
    basket_payload = {
        "items": [
            {"category_code": "MAT-CARDBOARD", "unit": "kg", "quantity": 100.0},
            {"category_code": "MAT-WHITE-PAPER", "unit": "kg", "quantity": 50.0},
            {"category_code": "MAT-GLASS-BOTTLE", "unit": "bag", "quantity": 3.0},
            {"category_code": "MAT-PLASTIC-BOTTLE", "unit": "bag", "quantity": 2.0},
        ]
    }

    latencies = []
    iterations = 20

    for _ in range(iterations):
        t0 = time.perf_counter()
        resp = client.post("/api/v1/pricing/calculate-estimate", json=basket_payload)
        t1 = time.perf_counter()
        assert resp.status_code == 200
        latencies.append(t1 - t0)

    latencies.sort()
    # คำนวณค่า P95 (ดัชนีที่ 95% ของ 20 ครั้ง = ตัวที่ 19)
    p95_index = int(iterations * 0.95) - 1
    p95_latency = latencies[p95_index]

    assert p95_latency < 3.0, f"P95 latency เกินเกณฑ์ 3.0s: {p95_latency:.4f}s"
    # ตรวจสอบว่าระบบทำงานเร็ว (โดยทั่วไป < 0.1s สำหรับ local compute)
    assert p95_latency < 0.5, f"ระบบช้าผิดปกติ: {p95_latency:.4f}s"

