"""
Main FastAPI Application Entrypoint for Saleng Platform (กลุ่ม 2 — 517 511 RE)
รวม Router ทั้ง 3 พอร์ทัล (Seller, Collector/Buyer, Admin) พร้อม CORS สำหรับ Frontend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.v1.account import account_router
from backend.app.api.v1.scrap_posting import scrap_posting_router
from backend.app.api.v1.buyer_search import router as buyer_search_router
from backend.app.api.v1.booking_tracking import router as booking_tracking_router
from backend.app.api.v1.pricing import pricing_router, orders_router
from backend.app.api.v1.payment import payment_router, receipt_router
from backend.app.api.v1.post_transaction import post_transaction_router
from backend.app.api.v1.notifications_help import notifications_help_router
from backend.app.api.v1.safety import safety_router

from backend.app.api.v1.collector_account import router as collector_account_router
from backend.app.api.v1.job_search import router as job_search_router
from backend.app.api.v1.job_evaluation import router as job_evaluation_router
from backend.app.api.v1.job_route import router as job_route_router
from backend.app.api.v1.communication import router as communication_router
from backend.app.api.v1.billing import router as billing_router
from backend.app.api.v1.post_job import router as post_job_router

from backend.app.api.v1.user_verification_penalty import router as admin_user_router
from backend.app.api.v1.benchmark_price_grading import router as admin_benchmark_router
from backend.app.api.v1.dispatch_dispute import router as admin_dispatch_router
from backend.app.api.v1.security_compliance import router as admin_compliance_router

app = FastAPI(
    title="Saleng Digital Scrap Platform API",
    description="API กลางสำหรับแพลตฟอร์มรับซื้อของเก่าดิจิทัล Saleng (Seller, Collector, Admin)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Seller Portal Routers
app.include_router(account_router, prefix="/api/v1")
app.include_router(scrap_posting_router, prefix="/api/v1")
app.include_router(buyer_search_router, prefix="/api/v1")
app.include_router(booking_tracking_router, prefix="/api/v1")
app.include_router(pricing_router)
app.include_router(orders_router)
app.include_router(payment_router)
app.include_router(receipt_router)
app.include_router(post_transaction_router)
app.include_router(notifications_help_router)
app.include_router(safety_router)

# Collector (Buyer) Portal Routers
app.include_router(collector_account_router, prefix="/api/v1")
app.include_router(job_search_router, prefix="/api/v1")
app.include_router(job_evaluation_router, prefix="/api/v1")
app.include_router(job_route_router, prefix="/api/v1/collectors")
app.include_router(communication_router, prefix="/api/v1/collectors")
app.include_router(billing_router, prefix="/api/v1/collectors")
app.include_router(post_job_router, prefix="/api/v1/collectors")

# Admin Portal Routers
app.include_router(admin_user_router, prefix="/api/v1/admin")
app.include_router(admin_benchmark_router, prefix="/api/v1/admin")
app.include_router(admin_dispatch_router, prefix="/api/v1/admin")
app.include_router(admin_compliance_router, prefix="/api/v1/admin/compliance")


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "saleng-backend"}
