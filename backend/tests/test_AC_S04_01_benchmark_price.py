"""
Automated Test for AC-S04-01: Benchmark Price Table Daily Refresh
รองรับ REQ-DAT-001, AC-S04-01, P-04, D-04
"""

from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store
from backend.app.cron.daily_price_updater import run_daily_price_update

client = TestClient(app)


def test_AC_S04_01_benchmark_price_table_display():
    """
    AC-S04-01: แสดงตารางช่วงราคากลาง (ต่ำสุด–สูงสุด) จำแนกตามประเภทและเกรดวัสดุ พร้อมวันที่และเวลาอัปเดตล่าสุด
    รองรับ REQ-DAT-001, AC-S04-01
    """
    response = client.get("/api/v1/pricing/benchmark-prices")
    assert response.status_code == 200

    data = response.json()
    assert "prices" in data
    assert "last_updated_at" in data
    assert len(data["prices"]) >= 5

    # สร้าง Dictionary เพื่อง่ายต่อการตรวจสอบรายหมวดหมู่
    price_map = {item["category_code"]: item for item in data["prices"]}

    # 1. กระดาษลัง 3–4 บาท/กก. (ตาม spec.md ข้อ 1.1)
    assert "MAT-CARDBOARD" in price_map
    cardboard = price_map["MAT-CARDBOARD"]
    assert cardboard["unit"] == "kg"
    assert cardboard["min_price_per_unit"] == 3.0
    assert cardboard["max_price_per_unit"] == 4.0

    # 2. กระดาษขาวดำ 6–7 บาท/กก.
    assert "MAT-WHITE-PAPER" in price_map
    white_paper = price_map["MAT-WHITE-PAPER"]
    assert white_paper["unit"] == "kg"
    assert white_paper["min_price_per_unit"] == 6.0
    assert white_paper["max_price_per_unit"] == 7.0

    # 3. ขวดแก้ว 1–2 บาท/กก.
    assert "MAT-GLASS-BOTTLE" in price_map
    glass = price_map["MAT-GLASS-BOTTLE"]
    assert glass["unit"] == "kg"
    assert glass["min_price_per_unit"] == 1.0
    assert glass["max_price_per_unit"] == 2.0

    # 4. ขวดพลาสติก 5–8 บาท/กก.
    assert "MAT-PLASTIC-BOTTLE" in price_map
    plastic = price_map["MAT-PLASTIC-BOTTLE"]
    assert plastic["unit"] == "kg"
    assert plastic["min_price_per_unit"] == 5.0
    assert plastic["max_price_per_unit"] == 8.0

    # 5. ขวดแก้ว (กระสอบ) 40–60 บาท/กระสอบ (ตาม D-02, AC-S04-05)
    assert "MAT-GLASS-BOTTLE-BAG" in price_map
    glass_bag = price_map["MAT-GLASS-BOTTLE-BAG"]
    assert glass_bag["unit"] == "bag"
    assert glass_bag["min_price_per_unit"] == 40.0
    assert glass_bag["max_price_per_unit"] == 60.0

    # 6. ทุกรายการต้องมี min <= max เสมอ (ตาม BR-01)
    for p in data["prices"]:
        assert p["min_price_per_unit"] <= p["max_price_per_unit"]
        assert p["min_price_per_unit"] > 0


def test_AC_S04_01_daily_refresh_cron():
    """
    AC-S04-01 & D-04: ตรวจสอบการรัน Scheduled Refresh ราคากลางประจำวันเวลา 06:00 น.
    และบันทึกประวัติลง Audit Log (REQ-SEC-001)
    """
    test_date = "2026-11-03"
    result = run_daily_price_update(effective_date_str=test_date)
    assert result["status"] == "SUCCESS"
    assert result["effective_timestamp"] == "2026-11-03T06:00:00Z"
    assert result["categories_count"] >= 5

    # ตรวจสอบผ่าน API
    response = client.get("/api/v1/pricing/benchmark-prices")
    assert response.status_code == 200
    data = response.json()
    assert "2026-11-03T06:00:00Z" in data["last_updated_at"]

    # ตรวจสอบ Audit Log
    logs = [log for log in supabase_store.audit_logs if log["action"] == "BENCHMARK_PRICE_DAILY_REFRESH"]
    assert len(logs) >= 1
    latest_log = logs[-1]
    assert latest_log["details"]["scheduled_time"] == "06:00"
    assert latest_log["details"]["effective_timestamp"] == "2026-11-03T06:00:00Z"

