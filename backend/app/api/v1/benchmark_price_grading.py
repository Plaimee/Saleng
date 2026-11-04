"""
Admin Benchmark Price & Quality Grading Router
รองรับ REQ-DAT-001, REQ-FN-003, BR-01, D-A02-01..06, CC-03, CC-05
"""

from typing import List, Optional
from fastapi import APIRouter, Header, Query, HTTPException
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
from backend.app.services.benchmark_price_grading_service import (
    benchmark_price_grading_service,
)

router = APIRouter(prefix="/benchmark-prices", tags=["admin-benchmark-prices"])


@router.get("", response_model=List[BenchmarkPriceAdminItem])
def list_benchmark_prices(
    unit: Optional[str] = Query(None, description="กรองตามหน่วยนับ: all, kg, piece, bag"),
    q: Optional[str] = Query(None, description="ค้นหาตามรหัสหรือชื่อหมวดหมู่วัสดุ"),
    x_admin_role: Optional[str] = Header(None, alias="X-Admin-Role"),
):
    """
    ดึงรายการราคากลางอ้างอิงประจำวันทั้งหมดสำหรับแอดมิน
    รองรับ UC-03, REQ-DAT-001, AC-A02-01, D-A02-01, CC-03
    """
    return benchmark_price_grading_service.list_benchmark_prices(
        unit=unit,
        q=q,
        admin_role=x_admin_role,
    )


@router.put("/{category_code}", response_model=BenchmarkPriceResponse)
def update_benchmark_price(
    category_code: str,
    request: UpdateBenchmarkPriceRequest,
    x_admin_role: Optional[str] = Header(None, alias="X-Admin-Role"),
):
    """
    แก้ไขช่วงราคากลางรายวัน (Min-Max) ของหมวดหมู่วัสดุ
    รองรับ AC-A02-01, D-A02-02, BR-01, CC-03
    """
    return benchmark_price_grading_service.update_benchmark_price(
        category_code=category_code,
        request=request,
        admin_role=x_admin_role,
    )


@router.post("/batch-update", response_model=BatchUpdateResponse)
def batch_update_prices(
    request: BatchUpdateBenchmarkPricesRequest,
    x_admin_role: Optional[str] = Header(None, alias="X-Admin-Role"),
):
    """
    อัปเดตราคากลางแบบกลุ่มหลายรายการพร้อมกัน
    รองรับ UC-03, UC-05, REQ-DAT-001, AC-A02-03, D-A02-01..04
    """
    return benchmark_price_grading_service.batch_update_prices(
        request=request,
        admin_role=x_admin_role,
    )


@router.get("/grading/{category_code}", response_model=List[QualityGradingRuleItem])
def get_grading_rules(
    category_code: str,
    x_admin_role: Optional[str] = Header(None, alias="X-Admin-Role"),
):
    """
    ดึงเกณฑ์คุณภาพและการหักสิ่งปนเปื้อน 3 ระดับ (GRADE_A, GRADE_B, GRADE_C)
    รองรับ UC-03, REQ-FN-003, AC-A02-02, D-A02-03
    """
    return benchmark_price_grading_service.get_grading_rules(
        category_code=category_code,
        admin_role=x_admin_role,
    )


@router.put("/grading/{category_code}", response_model=GradingRulesResponse)
def update_grading_rules(
    category_code: str,
    request: UpdateGradingRulesRequest,
    x_admin_role: Optional[str] = Header(None, alias="X-Admin-Role"),
):
    """
    แก้ไขเกณฑ์คุณภาพ 3 ระดับและเปอร์เซ็นต์หักสิ่งปนเปื้อน
    รองรับ UC-03, REQ-FN-003, AC-A02-02, D-A02-03, REQ-SEC-001
    """
    return benchmark_price_grading_service.update_grading_rules(
        category_code=category_code,
        request=request,
        admin_role=x_admin_role,
    )


@router.get("/history/{category_code}", response_model=List[PriceHistoryLogItem])
def get_price_history(
    category_code: str,
    limit: int = Query(20, ge=1, le=100),
    x_admin_role: Optional[str] = Header(None, alias="X-Admin-Role"),
):
    """
    ดึงประวัติการปรับปรุงราคาของหมวดหมู่วัสดุ
    รองรับ AC-A02-05, REQ-SEC-001
    """
    return benchmark_price_grading_service.get_price_history(
        category_code=category_code,
        limit=limit,
        admin_role=x_admin_role,
    )

