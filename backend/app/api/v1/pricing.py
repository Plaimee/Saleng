"""
Pricing API Endpoints
รองรับ REQ-DAT-001, AC-S04-01, P-04, D-04
"""

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from backend.app.models.pricing_models import (
    BenchmarkPriceListResponse,
    CalculationEstimateRequest,
    CalculationEstimateResponse,
    OrderSubmissionInput,
    OrderSubmissionResponse,
)
from backend.app.services.pricing_service import pricing_service
from backend.app.services.order_submission_service import (
    order_submission_service,
    MinimumThresholdError,
)

pricing_router = APIRouter(prefix="/api/v1/pricing", tags=["pricing"])
orders_router = APIRouter(prefix="/api/v1/orders", tags=["orders"])


@pricing_router.get("/benchmark-prices", response_model=BenchmarkPriceListResponse)
def get_benchmark_prices():
    """
    ดึงตารางเรตราคากลางรับซื้อรายวัน (แยกตามหมวดหมู่)
    รองรับ REQ-DAT-001, AC-S04-01, D-04
    - แสดงช่วงราคารับซื้ออ้างอิงตามประเภทและเกรดวัสดุ (ต่ำสุด–สูงสุด)
    - แสดงวันที่และเวลาอัปเดตข้อมูลราคาล่าสุด (รอบเวลา 06:00 น.)
    """
    return pricing_service.get_all_benchmark_prices()


@pricing_router.post("/calculate-estimate", response_model=CalculationEstimateResponse)
def calculate_estimate(request: CalculationEstimateRequest):
    """
    คำนวณช่วงราคาประเมินเบื้องต้นจากปริมาณที่ระบุ
    รองรับ Card 01, BR-01, AC-S04-02, AC-S04-04, AC-S04-05, P-01, P-02, D-02, D-06
    - คำนวณช่วงราคาประเมิน (ต่ำสุด–สูงสุด) ภายใน 3 วินาที
    - รองรับหน่วย กก. และ กระสอบ (ราคาเหมาต่อกระสอบ)
    - รองรับตะกร้าหลายรายการ (Multi-Item Basket) พร้อมยอดรวม Min-Max
    - บล็อกเมื่อปริมาณ <= 0 (HTTP 422)
    - กำกับด้วยข้อความ "ราคาจริงขึ้นกับสภาพของหน้างาน"
    """
    try:
        return pricing_service.calculate_estimate(request.items)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@orders_router.post("/validate-and-submit", response_model=OrderSubmissionResponse, status_code=201)
def validate_and_submit_order(submission: OrderSubmissionInput):
    """
    ตรวจสอบเกณฑ์มูลค่าขั้นต่ำและส่งคำขอนัดหมาย
    รองรับ REQ-FN-001, REQ-FN-006, AC-S04-03, P-03, D-01, D-03
    - ผ่าน: มูลค่ารวม min_price >= 500 บาท หรือขวดแก้ว/พลาสติก >= 2 กระสอบ (HTTP 201)
    - บล็อก & เสนอทางเลือก: หากไม่ถึงเกณฑ์ขั้นต่ำ ปฏิเสธนัดหมายเดี่ยว (HTTP 400) พร้อมตัวเลือกฝากรวมทางผ่าน/จุดรับรวมอาคาร
    - รองรับการส่งคำขอแบบฝากรวมจุดรับทางผ่าน (isRouteDropIn = true -> S2)
    - รองรับการส่งคำขอแบบจุดรับรวมประจำอาคาร (isBuildingGroupDrop = true)
    """
    try:
        return order_submission_service.submit_order(submission)
    except MinimumThresholdError as e:
        return JSONResponse(
            status_code=400,
            content={
                "error": "MINIMUM_THRESHOLD_NOT_MET",
                "message": e.message,
                "total_est_min_price": e.total_est_min_price,
                "total_bags": e.total_bags,
                "allowed_alternatives": e.allowed_alternatives,
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@orders_router.post("/{order_id}/accept", status_code=200)
def accept_order(order_id: str, buyer_id: str = "USR-BUYER-01"):
    """
    ซาเล้งกดรับนัดหมาย (S2 -> S3) พร้อมล็อกราคากลาง Snapshot ในฐานข้อมูล
    รองรับ REQ-BR-002, D-04, REQ-SEC-001
    """
    try:
        return order_submission_service.accept_order_and_lock_price(order_id, buyer_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


from backend.app.api.v1.payment import payment_router, receipt_router
from backend.app.api.v1.post_transaction import post_transaction_router
from backend.app.api.v1.notifications_help import notifications_help_router
from backend.app.api.v1.safety import safety_router
from backend.app.api.v1.account import account_router
from backend.app.api.v1.scrap_posting import scrap_posting_router
from backend.app.api.v1.buyer_search import router as buyer_search_router
from backend.app.api.v1.booking_tracking import router as booking_tracking_router
from backend.app.api.v1.collector_account import router as collector_account_router
from backend.app.api.v1.job_search import router as job_search_router
from backend.app.api.v1.job_evaluation import router as job_evaluation_router
from backend.app.api.v1.job_route import router as job_route_router
from backend.app.api.v1.communication import router as communication_router
from backend.app.api.v1.billing import router as billing_router
from backend.app.api.v1.post_job import router as post_job_router
from backend.app.api.v1.user_verification_penalty import router as admin_user_router
from backend.app.api.v1.benchmark_price_grading import router as admin_benchmark_router
from backend.app.api.v1.dispatch_dispute import router as admin_dispatch_dispute_router
from backend.app.api.v1.security_compliance import router as admin_security_compliance_router

# Application instance สำหรับทดสอบและเชื่อมต่อ Server
app = FastAPI(
    title="Saleng Pricing & Decision API",
    description="API ระบบราคาและการตัดสินใจ ฝั่งผู้ขาย ผู้ซื้อ และผู้ดูแลระบบ (Seller 01..09, Buyer 01..07, Admin 01, Admin 02)",
    version="1.0.0"
)
app.include_router(pricing_router)
app.include_router(orders_router)
app.include_router(payment_router)
app.include_router(receipt_router)
app.include_router(post_transaction_router)
app.include_router(notifications_help_router)
app.include_router(safety_router)
app.include_router(account_router, prefix="/api/v1")
app.include_router(scrap_posting_router, prefix="/api/v1")
app.include_router(buyer_search_router, prefix="/api/v1")
app.include_router(booking_tracking_router, prefix="/api/v1")
app.include_router(collector_account_router, prefix="/api/v1")
app.include_router(job_search_router, prefix="/api/v1")
app.include_router(job_evaluation_router, prefix="/api/v1")
app.include_router(job_route_router, prefix="/api/v1/collectors")
app.include_router(communication_router, prefix="/api/v1/collectors")
app.include_router(billing_router, prefix="/api/v1/collectors")
app.include_router(post_job_router, prefix="/api/v1/collectors")
app.include_router(admin_user_router, prefix="/api/v1/admin")
app.include_router(admin_benchmark_router, prefix="/api/v1/admin")
app.include_router(admin_dispatch_dispute_router, prefix="/api/v1/admin")
app.include_router(admin_security_compliance_router, prefix="/api/v1/admin/compliance")

