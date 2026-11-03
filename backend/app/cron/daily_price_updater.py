"""
Daily Benchmark Price Scheduled Updater
รองรับ REQ-DAT-001, AC-S04-01, P-04, D-04
"""

from datetime import datetime, timezone
from typing import Optional
from backend.app.core.config import settings
from backend.app.core.supabase import supabase_store
from backend.app.services.pricing_service import pricing_service


def run_daily_price_update(effective_date_str: Optional[str] = None):
    """
    Worker อัปเดตราคากลางทุกวันเวลา 06:00 น. ตาม D-04
    และบันทึกประวัติการอัปเดตลง Audit Log
    """
    now = datetime.now(timezone.utc)
    if effective_date_str:
        timestamp_str = f"{effective_date_str}T{settings.BENCHMARK_PRICE_REFRESH_TIME}:00Z"
    else:
        timestamp_str = f"{now.strftime('%Y-%m-%d')}T{settings.BENCHMARK_PRICE_REFRESH_TIME}:00Z"

    # รีเฟรชราคากลาง
    updated_result = pricing_service.refresh_daily_prices(effective_time_str=timestamp_str)

    # บันทึก Audit Log (REQ-SEC-001)
    supabase_store.add_audit_log(
        action="BENCHMARK_PRICE_DAILY_REFRESH",
        entity_id="benchmark_prices",
        actor_id="SYSTEM_CRON",
        details={
            "scheduled_time": settings.BENCHMARK_PRICE_REFRESH_TIME,
            "effective_timestamp": timestamp_str,
            "total_categories_updated": len(updated_result.prices),
        }
    )

    return {
        "status": "SUCCESS",
        "effective_timestamp": timestamp_str,
        "categories_count": len(updated_result.prices),
        "last_updated_at": updated_result.last_updated_at,
    }

