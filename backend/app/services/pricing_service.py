"""
Pricing Service
รองรับ REQ-DAT-001, AC-S04-01, P-04, D-04
"""

from datetime import datetime, timezone
import time
from typing import List, Optional
from backend.app.core.supabase import supabase_store
from backend.app.models.pricing_models import (
    BenchmarkPrice,
    BenchmarkPriceListResponse,
    WasteItemEstimateInput,
    WasteItemEstimateOutput,
    CalculationEstimateResponse,
)


class PricingService:
    def __init__(self, store=supabase_store):
        self.store = store

    def get_all_benchmark_prices(self) -> BenchmarkPriceListResponse:
        """
        ดึงตารางราคากลางอ้างอิงรายวันทั้งหมด
        รองรับ REQ-DAT-001, AC-S04-01
        """
        raw_prices = self.store.get_benchmark_prices()
        prices = [BenchmarkPrice(**p) for p in raw_prices]

        # หาเวลาอัปเดตล่าสุด
        if prices:
            last_updated = max(p.updated_at for p in prices)
        else:
            last_updated = datetime.now(timezone.utc).isoformat()

        return BenchmarkPriceListResponse(
            prices=prices,
            last_updated_at=last_updated
        )

    def get_price_by_category(self, category_code: str) -> Optional[BenchmarkPrice]:
        """
        ดึงราคากลางของหมวดหมู่วัสดุที่ระบุ
        """
        raw = self.store.get_price_by_category(category_code)
        if raw:
            return BenchmarkPrice(**raw)
        return None

    def calculate_estimate(self, items: List[WasteItemEstimateInput]) -> CalculationEstimateResponse:
        """
        คำนวณช่วงราคาประเมินเบื้องต้น (Min-Max) รองรับรายการเดี่ยวและตะกร้าหลายรายการ
        รองรับ Card 01, BR-01, AC-S04-02, AC-S04-05, P-01, P-02, D-02, D-06
        """
        start_time = time.perf_counter()
        item_outputs: List[WasteItemEstimateOutput] = []

        for item in items:
            resolved_code = item.category_code
            # รองรับการแปลงหมวดหมู่สำหรับหน่วยกระสอบ (D-02, AC-S04-05)
            if item.unit == "bag" and not resolved_code.endswith("-BAG"):
                bag_code = f"{resolved_code}-BAG"
                if self.store.get_price_by_category(bag_code):
                    resolved_code = bag_code
            elif item.unit == "kg" and resolved_code.endswith("-BAG"):
                base_code = resolved_code[:-4]
                if self.store.get_price_by_category(base_code):
                    resolved_code = base_code

            benchmark = self.get_price_by_category(resolved_code)
            if not benchmark:
                raise ValueError(f"ไม่พบข้อมูลราคากลางสำหรับหมวดหมู่: {item.category_code}")

            est_min = round(item.quantity * benchmark.min_price_per_unit, 2)
            est_max = round(item.quantity * benchmark.max_price_per_unit, 2)

            item_outputs.append(
                WasteItemEstimateOutput(
                    category_code=resolved_code,
                    category_name=benchmark.category_name,
                    unit=item.unit,
                    quantity=item.quantity,
                    unit_min_price=benchmark.min_price_per_unit,
                    unit_max_price=benchmark.max_price_per_unit,
                    est_min_price=est_min,
                    est_max_price=est_max,
                )
            )

        total_min = round(sum(o.est_min_price for o in item_outputs), 2)
        total_max = round(sum(o.est_max_price for o in item_outputs), 2)
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return CalculationEstimateResponse(
            items=item_outputs,
            total_est_min_price=total_min,
            total_est_max_price=total_max,
            disclaimer="ราคาจริงขึ้นกับสภาพของหน้างาน",
            calculation_time_ms=elapsed_ms,
        )

    def refresh_daily_prices(
        self,
        new_price_list: Optional[List[dict]] = None,
        effective_time_str: Optional[str] = None
    ) -> BenchmarkPriceListResponse:
        """
        อัปเดตราคากลางประจำวันตามกำหนดเวลา 06:00 น.
        รองรับ P-04, D-04
        """
        now = datetime.now(timezone.utc)
        if effective_time_str:
            update_timestamp = effective_time_str
        else:
            update_timestamp = now.strftime("%Y-%m-%d") + "T06:00:00Z"

        if new_price_list:
            for item in new_price_list:
                item["updated_at"] = update_timestamp
                self.store.upsert_benchmark_price(item)
        else:
            # อัปเดต timestamp ราคากลางที่มีอยู่
            current_prices = self.store.get_benchmark_prices()
            for p in current_prices:
                p["updated_at"] = update_timestamp
                self.store.upsert_benchmark_price(p)

        return self.get_all_benchmark_prices()


pricing_service = PricingService()

