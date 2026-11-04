"""
Unit Tests for Task T-01: Post-Job Models & Supabase Store
รองรับ UC-10, UC-13, REQ-FN-005, REQ-FN-006, REQ-SEC-002, CC-04, D-B07-01..06
"""

import pytest
from pydantic import ValidationError
from backend.app.models.post_job_models import (
    PurchaseHistorySummary,
    PurchaseHistoryItem,
    PurchaseHistoryResponse,
    RegularCustomerItem,
    ToggleRegularCustomerRequest,
    ToggleRegularCustomerResponse,
    ReportSellerMismatchRequest,
    ReportSellerMismatchResponse,
)
from backend.app.core.supabase import supabase_store


def test_purchase_history_summary_validation():
    """สรุปสถิติต้องมียอดเงิน น้ำหนัก และจำนวนงาน >= 0"""
    summary = PurchaseHistorySummary(
        total_expense_baht=1500.0,
        total_weight_kg=350.0,
        total_completed_jobs=5,
    )
    assert summary.total_expense_baht == 1500.0
    assert summary.total_weight_kg == 350.0
    assert summary.total_completed_jobs == 5

    with pytest.raises(ValidationError):
        PurchaseHistorySummary(
            total_expense_baht=-10.0,
            total_weight_kg=10.0,
            total_completed_jobs=1,
        )


def test_toggle_regular_customer_request_validation():
    """ทดสอบ ToggleRegularCustomerRequest validation และ notes <= 200 ตัวอักษร"""
    valid = ToggleRegularCustomerRequest(
        saleng_id="saleng-01",
        seller_id="seller-01",
        notes="บ้านรั้วสีฟ้า สะดวกเสาร์-อาทิตย์",
        latitude=13.7563,
        longitude=100.5018,
    )
    assert valid.saleng_id == "saleng-01"
    assert valid.notes == "บ้านรั้วสีฟ้า สะดวกเสาร์-อาทิตย์"

    # Notes over 200 characters should raise ValidationError
    with pytest.raises(ValidationError):
        ToggleRegularCustomerRequest(
            saleng_id="saleng-01",
            seller_id="seller-01",
            notes="A" * 201,
        )


def test_report_seller_mismatch_request_validation():
    """รายงานข้อพิพาทต้องมี evidence_photo_url บังคับตาม REQ-FN-006"""
    valid = ReportSellerMismatchRequest(
        saleng_id="saleng-01",
        order_id="order-101",
        mismatch_reason="SELLER_NO_SHOW",
        evidence_photo_url="https://storage.saleng.app/disputes/no-show-101.jpg",
        notes="ผู้ขายไม่อยู่บ้าน",
        current_lat=13.7563,
        current_lng=100.5018,
    )
    assert valid.evidence_photo_url == "https://storage.saleng.app/disputes/no-show-101.jpg"

    # Photo URL empty or too short
    with pytest.raises(ValidationError):
        ReportSellerMismatchRequest(
            saleng_id="saleng-01",
            order_id="order-101",
            mismatch_reason="SELLER_NO_SHOW",
            evidence_photo_url="",
        )


def test_supabase_store_post_job_methods():
    """ทดสอบ Store methods สำหรับลูกค้าประจำและข้อพิพาท"""
    collector_id = "saleng-t01-test"
    seller_id = "seller-t01-test"

    # 1. ปักหมุดลูกค้าประจำ (Toggle ON)
    is_fav1, fav_data1 = supabase_store.toggle_collector_favorite_seller(
        collector_id=collector_id,
        seller_id=seller_id,
        notes="ลูกค้านิสัยดี มีลังกระดาษเยอะ",
        lat=13.75,
        lng=100.50,
        seller_name="ป้าสมศรี",
        seller_phone_masked="08X-XXX-4567",
    )
    assert is_fav1 is True
    assert fav_data1["seller_id"] == seller_id
    assert fav_data1["seller_name"] == "ป้าสมศรี"

    # ตรวจสอบ get_collector_favorite_sellers
    favs = supabase_store.get_collector_favorite_sellers(collector_id)
    assert len(favs) == 1
    assert favs[0]["notes"] == "ลูกค้านิสัยดี มีลังกระดาษเยอะ"

    # 2. ปักหมุดซ้ำ (Toggle OFF)
    is_fav2, removed = supabase_store.toggle_collector_favorite_seller(
        collector_id=collector_id,
        seller_id=seller_id,
    )
    assert is_fav2 is False
    assert removed["seller_id"] == seller_id
    assert len(supabase_store.get_collector_favorite_sellers(collector_id)) == 0

    # 3. สร้างรายงานข้อพิพาท create_dispute_report
    dispute = supabase_store.create_dispute_report({
        "order_id": "order-t01-test",
        "reporter_id": collector_id,
        "mismatch_reason": "CONTAMINATED_WASTE",
        "evidence_photo_url": "https://storage.saleng.app/disp1.jpg",
        "notes": "ขยะปนเปื้อนสารเคมีอันตราย",
    })
    assert dispute["dispute_id"].startswith("DISP-")
    assert dispute["status"] == "PENDING_ADMIN"
    assert dispute["order_id"] == "order-t01-test"
    assert dispute["dispute_id"] in supabase_store.dispute_reports

    # Cleanup
    supabase_store.dispute_reports.pop(dispute["dispute_id"], None)

