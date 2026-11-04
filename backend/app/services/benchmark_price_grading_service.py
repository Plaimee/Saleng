"""
Service Layer for Admin Benchmark Price & Grading Management
รองรับ REQ-DAT-001, REQ-FN-003, BR-01, D-A02-01..06, CC-03, CC-05
"""

from typing import List, Optional
from datetime import datetime, timezone
from fastapi import HTTPException
from backend.app.core.supabase import supabase_store, SupabaseStore
from backend.app.models.benchmark_price_grading_models import (
    BenchmarkPriceAdminItem,
    UpdateBenchmarkPriceRequest,
    BatchUpdateBenchmarkPricesRequest,
    QualityGradingRuleItem,
    UpdateGradingRulesRequest,
    PriceHistoryLogItem,
    BenchmarkPriceResponse,
    BatchUpdateResponse,
    GradingRulesResponse,
)


class BenchmarkPriceGradingService:
    """
    ตรรกะธุรกิจสำหรับการจัดการราคากลางและเกณฑ์คุณภาพฝั่งแอดมิน
    """

    def __init__(self, store: Optional[SupabaseStore] = None):
        self.store = store or supabase_store

    def _verify_admin_role(self, admin_role: Optional[str]) -> None:
        """
        ตรวจสอบสิทธิ์การเข้าถึงของผู้ดูแลระบบ (CC-03, D-A02-06, AC-A02-05)
        """
        if not admin_role or admin_role.strip().upper() != "ADMIN":
            raise HTTPException(
                status_code=403,
                detail="สิทธิ์ไม่ถูกต้อง: เฉพาะผู้ดูแลระบบ (ADMIN) เท่านั้นที่สามารถจัดการราคากลางได้"
            )

    def list_benchmark_prices(
        self,
        unit: Optional[str] = None,
        q: Optional[str] = None,
        admin_role: Optional[str] = None,
    ) -> List[BenchmarkPriceAdminItem]:
        """
        ดึงตารางราคากลางสำหรับแอดมิน (UC-03, REQ-DAT-001, AC-A02-01, D-A02-01)
        - รองรับการกรองตามหน่วย (kg, piece, bag) และคำค้น
        - รองรับกลไก Fallback ราคาวันก่อนหน้าอัตโนมัติหากไม่มีการตั้งราคาใหม่ก่อน 06:00 น.
        """
        self._verify_admin_role(admin_role)
        raw_prices = self.store.get_all_benchmark_prices_admin(unit=unit, q=q)
        return [BenchmarkPriceAdminItem(**p) for p in raw_prices]

    def update_benchmark_price(
        self,
        category_code: str,
        request: UpdateBenchmarkPriceRequest,
        admin_role: Optional[str] = None,
    ) -> BenchmarkPriceResponse:
        """
        แก้ไขช่วงราคากลางรายวัน (AC-A02-01, D-A02-02, BR-01)
        - ตรวจสอบความถูกต้องของช่วงราคา (min > 0, max >= min, ทศนิยม <= 2)
        - ตรวจสอบการแจ้งเตือนยืนยันเมื่อราคาเปลี่ยนเกิน 50% (confirm_shift)
        - คำนวณราคาประเมินใหม่ให้แก่ออเดอร์ S1/S2 และล็อกราคา S3..S7 (D-A02-05)
        - บันทึก Audit Log (REQ-SEC-001)
        """
        self._verify_admin_role(admin_role)

        existing = self.store.benchmark_prices.get(category_code)
        if not existing:
            raise HTTPException(
                status_code=404,
                detail=f"ไม่พบหมวดหมู่วัสดุรหัส: {category_code}"
            )

        old_min = float(existing.get("min_price_per_unit", 0.0))
        old_max = float(existing.get("max_price_per_unit", 0.0))
        old_mid = (old_min + old_max) / 2.0 if (old_min + old_max) > 0 else 1.0

        new_min = request.min_price_per_unit
        new_max = request.max_price_per_unit
        new_mid = (new_min + new_max) / 2.0

        # ตรวจสอบการเปลี่ยนราคาเกิน 50% ตาม D-A02-02
        shift_ratio = abs(new_mid - old_mid) / old_mid
        warning_msg = None
        if shift_ratio > 0.50:
            if not request.confirm_shift:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "PRICE_SHIFT_EXCEEDS_50_PERCENT",
                        "message": f"ราคาเฉลี่ยใหม่ ({new_mid:.2f}) เปลี่ยนแปลงเกิน 50% จากราคาเดิม ({old_mid:.2f}) กรุณายืนยันการเปลี่ยนแปลงด้วย confirm_shift=True",
                        "old_mid_price": old_mid,
                        "new_mid_price": new_mid,
                        "shift_percent": round(shift_ratio * 100, 1),
                    }
                )
            warning_msg = f"ราคาเปลี่ยนแปลง {round(shift_ratio * 100, 1)}% ได้รับการยืนยันแล้ว"

        updated = self.store.update_benchmark_price(
            category_code=category_code,
            min_price=new_min,
            max_price=new_max,
            grading_condition=request.grading_condition,
            updated_by=request.updated_by or "admin-01",
            change_reason=request.change_reason,
        )

        return BenchmarkPriceResponse(
            success=True,
            message="อัปเดตราคากลางเรียบร้อยแล้ว",
            category_code=category_code,
            min_price_per_unit=updated["min_price_per_unit"],
            max_price_per_unit=updated["max_price_per_unit"],
            updated_at=updated["updated_at"],
            warning=warning_msg,
        )

    def get_grading_rules(
        self,
        category_code: str,
        admin_role: Optional[str] = None,
    ) -> List[QualityGradingRuleItem]:
        """
        ดึงเกณฑ์คุณภาพ 3 ระดับและการหักสิ่งปนเปื้อน (AC-A02-02, D-A02-03)
        """
        self._verify_admin_role(admin_role)
        existing = self.store.benchmark_prices.get(category_code)
        if not existing:
            raise HTTPException(
                status_code=404,
                detail=f"ไม่พบหมวดหมู่วัสดุรหัส: {category_code}"
            )
        raw_rules = self.store.get_quality_grading_rules(category_code)
        return [QualityGradingRuleItem(**r) for r in raw_rules]

    def update_grading_rules(
        self,
        category_code: str,
        request: UpdateGradingRulesRequest,
        admin_role: Optional[str] = None,
    ) -> GradingRulesResponse:
        """
        ปรับปรุงเกณฑ์คุณภาพ 3 ระดับและการหักสิ่งปนเปื้อน (AC-A02-02, D-A02-03, REQ-SEC-001)
        """
        self._verify_admin_role(admin_role)
        existing = self.store.benchmark_prices.get(category_code)
        if not existing:
            raise HTTPException(
                status_code=404,
                detail=f"ไม่พบหมวดหมู่วัสดุรหัส: {category_code}"
            )

        rules_dict = [r.model_dump() for r in request.rules]
        updated_rules = self.store.update_quality_grading_rules(
            category_code=category_code,
            rules_data=rules_dict,
            updated_by=request.updated_by or "admin-01",
        )
        return GradingRulesResponse(
            success=True,
            category_code=category_code,
            rules=[QualityGradingRuleItem(**r) for r in updated_rules],
        )

    def batch_update_prices(
        self,
        request: BatchUpdateBenchmarkPricesRequest,
        admin_role: Optional[str] = None,
    ) -> BatchUpdateResponse:
        """
        อัปเดตราคากลางหลายหมวดหมู่พร้อมกัน (Batch Update — AC-A02-03, D-A02-01..04)
        """
        self._verify_admin_role(admin_role)
        items_dict = []
        for it in request.items:
            # ตรวจสอบว่าหมวดหมู่นี้มีอยู่จริง
            cat = self.store.benchmark_prices.get(it.category_code)
            if not cat:
                raise HTTPException(
                    status_code=404,
                    detail=f"ไม่พบหมวดหมู่วัสดุรหัส: {it.category_code}"
                )
            # ตรวจสอบ 50% shift
            old_mid = (float(cat["min_price_per_unit"]) + float(cat["max_price_per_unit"])) / 2.0
            new_mid = (it.min_price_per_unit + it.max_price_per_unit) / 2.0
            shift_ratio = abs(new_mid - old_mid) / old_mid if old_mid > 0 else 0
            if shift_ratio > 0.50 and not it.confirm_shift:
                raise HTTPException(
                    status_code=400,
                    detail=f"PRICE_SHIFT_EXCEEDS_50_PERCENT: หมวด {it.category_code} เปลี่ยนแปลงเกิน 50% กรุณายืนยันด้วย confirm_shift=True"
                )
            items_dict.append(it.model_dump())

        updated = self.store.batch_update_benchmark_prices(
            items_data=items_dict,
            effective_date=request.effective_date,
            updated_by=request.updated_by or "admin-01",
            change_reason=request.change_reason,
        )
        return BatchUpdateResponse(
            success=True,
            message=f"อัปเดตราคาแบบกลุ่มสำเร็จจำนวน {len(updated)} รายการ",
            updated_count=len(updated),
            items=[BenchmarkPriceAdminItem(**p) for p in updated],
        )

    def get_price_history(
        self,
        category_code: str,
        limit: int = 20,
        admin_role: Optional[str] = None,
    ) -> List[PriceHistoryLogItem]:
        """
        ดึงประวัติการปรับเปลี่ยนราคาย้อนหลัง (AC-A02-05)
        """
        self._verify_admin_role(admin_role)
        existing = self.store.benchmark_prices.get(category_code)
        if not existing:
            raise HTTPException(
                status_code=404,
                detail=f"ไม่พบหมวดหมู่วัสดุรหัส: {category_code}"
            )
        history = self.store.get_benchmark_price_history(category_code, limit=limit)
        return [PriceHistoryLogItem(**h) for h in history]


# Singleton instance
benchmark_price_grading_service = BenchmarkPriceGradingService()

