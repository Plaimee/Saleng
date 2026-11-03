"""
Unit tests สำหรับ T-01: Post-Transaction Models & Supabase Store
รองรับ UC-10, SC-05, REQ-FN-005, REQ-SEC-002, CC-04, P-01..P-03
"""

import pytest
from pydantic import ValidationError
from backend.app.models.post_transaction_models import (
    ReviewCreateRequest,
    ReviewResponse,
    FavoriteCollectorRequest,
    FavoriteCollectorResponse,
    SalesSummaryResponse,
    SalesHistoryResponse,
)
from backend.app.core.supabase import supabase_store


def test_review_create_request_validation():
    """ตรวจสอบการตรวจสอบข้อมูลคำขอส่งรีวิว (1-5 ดาว, ข้อความ <= 500 ตัวอักษร)"""
    # กรณีถูกต้อง
    valid_req = ReviewCreateRequest(
        seller_id="SELLER-001",
        rating=5,
        comment="บริการดีมาก ตรงต่อเวลา ตาชั่งได้มาตรฐาน",
    )
    assert valid_req.rating == 5
    assert valid_req.seller_id == "SELLER-001"

    # กรณีดาวต่ำกว่า 1
    with pytest.raises(ValidationError):
        ReviewCreateRequest(seller_id="SELLER-001", rating=0)

    # กรณีดาวเกิน 5
    with pytest.raises(ValidationError):
        ReviewCreateRequest(seller_id="SELLER-001", rating=6)

    # กรณีคอมเมนต์เกิน 500 ตัวอักษร
    with pytest.raises(ValidationError):
        ReviewCreateRequest(seller_id="SELLER-001", rating=4, comment="A" * 501)


def test_supabase_store_review_lifecycle():
    """ตรวจสอบการบันทึกรีวิว และคำนวณคะแนนเฉลี่ยซาเล้ง (P-01, Q-02)"""
    collector_id = "COLLECTOR-TEST-01"
    order_id_1 = "ORDER-REV-01"
    order_id_2 = "ORDER-REV-02"

    # บันทึกรีวิวที่ 1
    rev1 = supabase_store.create_review({
        "order_id": order_id_1,
        "seller_id": "SELLER-01",
        "collector_id": collector_id,
        "rating": 5,
        "comment": "ยอดเยี่ยมมาก",
    })
    assert rev1["id"] is not None
    assert rev1["rating"] == 5

    # บันทึกรีวิวที่ 2
    rev2 = supabase_store.create_review({
        "order_id": order_id_2,
        "seller_id": "SELLER-02",
        "collector_id": collector_id,
        "rating": 4,
        "comment": "บริการรวดเร็ว",
    })
    assert rev2["rating"] == 4

    # ตรวจสอบการคำนวณคะแนนเฉลี่ย (5 + 4) / 2 = 4.5
    summary = supabase_store.get_collector_rating_summary(collector_id)
    assert summary["average_rating"] == 4.5
    assert summary["total_reviews"] == 2

    # ตรวจสอบการบล็อกรีวิวซ้ำในคำขอเดิม (P-01, Q-02)
    with pytest.raises(ValueError, match="ได้รับการส่งรีวิวแล้ว"):
        supabase_store.create_review({
            "order_id": order_id_1,
            "seller_id": "SELLER-01",
            "collector_id": collector_id,
            "rating": 3,
        })


def test_supabase_store_favorite_collector():
    """ตรวจสอบการบันทึกและยกเลิกผู้รับซื้อประจำ (Toggle Bookmark - P-02, Q-03)"""
    seller_id = "SELLER-FAV-TEST"
    collector_id = "COLLECTOR-FAV-01"

    # เริ่มต้นต้องยังไม่เป็นผู้รับซื้อประจำ
    assert not supabase_store.is_favorite(seller_id, collector_id)

    # เพิ่มเป็นผู้รับซื้อประจำ
    fav = supabase_store.add_favorite(seller_id, collector_id)
    assert fav["seller_id"] == seller_id
    assert fav["collector_id"] == collector_id
    assert supabase_store.is_favorite(seller_id, collector_id)

    # เพิ่มซ้ำต้องไม่เกิด duplicate
    fav_again = supabase_store.add_favorite(seller_id, collector_id)
    assert fav_again["id"] == fav["id"]
    favorites = supabase_store.get_seller_favorites(seller_id)
    assert favorites == [collector_id]

    # ยกเลิกผู้รับซื้อประจำ
    removed = supabase_store.remove_favorite(seller_id, collector_id)
    assert removed is True
    assert not supabase_store.is_favorite(seller_id, collector_id)
    assert supabase_store.get_seller_favorites(seller_id) == []

