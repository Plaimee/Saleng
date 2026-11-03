"""
Unit tests สำหรับ T-01: Data Models และ Supabase Store ของระบบค้นหาและเลือกผู้รับซื้อ
รองรับ UC-03, MD-DOM-04, REQ-QA-001, CC-04, P-01, D-00-01
"""

import pytest
from backend.app.models.buyer_search_models import (
    SalengProfileResponse,
    CollectorSearchQuery,
    CollectorListResponse,
    DirectAppointmentRequest,
    DirectAppointmentResponse,
    FavoriteToggleResponse,
)
from backend.app.core.supabase import supabase_store


def test_T01_saleng_profile_response_model():
    """ทดสอบการสร้างและตรวจสอบ Schema ของ SalengProfileResponse"""
    data = {
        "saleng_id": "saleng-01",
        "display_name": "ลุงสมชาย ซาเล้งสุทธิสาร",
        "phone": "081-234-5678",
        "avatar_url": "https://example.com/avatar.jpg",
        "verified": True,
        "rating": 4.9,
        "completed_jobs_count": 142,
        "vehicle_type": "TRICYCLE",
        "max_capacity_kg": 200.0,
        "current_lat": 13.7900,
        "current_lng": 100.5750,
        "distance_km": 1.25,
        "is_favorite": True,
        "is_online": True,
        "accepted_categories": ["MAT-CARDBOARD", "MAT-WHITE-PAPER"],
    }
    model = SalengProfileResponse(**data)
    assert model.saleng_id == "saleng-01"
    assert model.display_name == "ลุงสมชาย ซาเล้งสุทธิสาร"
    assert model.verified is True
    assert model.rating == 4.9
    assert model.distance_km == 1.25
    assert model.is_favorite is True


def test_T01_collector_search_query_and_response_models():
    """ทดสอบ CollectorSearchQuery และ CollectorListResponse"""
    query = CollectorSearchQuery(radius_km=3.0, vehicle_type="PICKUP_TRUCK")
    assert query.radius_km == 3.0
    assert query.vehicle_type == "PICKUP_TRUCK"

    profile = SalengProfileResponse(
        saleng_id="saleng-02",
        display_name="พี่วิชัย รถกระบะรีไซเคิล",
        phone="089-876-5432",
        verified=True,
        rating=4.8,
        completed_jobs_count=215,
        vehicle_type="PICKUP_TRUCK",
        max_capacity_kg=1000.0,
        current_lat=13.7920,
        current_lng=100.5770,
        distance_km=0.85,
        is_favorite=False,
        is_online=True,
    )
    list_resp = CollectorListResponse(
        collectors=[profile],
        total_count=1,
        has_bulky_items=True,
        bulky_warning_message="คำขอมีของชิ้นใหญ่ แนะนำรถกระบะ",
    )
    assert list_resp.total_count == 1
    assert list_resp.has_bulky_items is True
    assert list_resp.collectors[0].vehicle_type == "PICKUP_TRUCK"


def test_T01_supabase_saleng_profiles_seeding():
    """ทดสอบว่า Supabase store มีข้อมูลซาเล้งตั้งต้นครบถ้วนและถูกต้องตามเงื่อนไข KYC / Online"""
    profiles = supabase_store.get_all_saleng_profiles()
    assert len(profiles) >= 5

    saleng_01 = supabase_store.get_saleng_profile("saleng-01")
    assert saleng_01 is not None
    assert saleng_01["verified"] is True
    assert saleng_01["is_online"] is True
    assert saleng_01["vehicle_type"] == "TRICYCLE"

    saleng_02 = supabase_store.get_saleng_profile("saleng-02")
    assert saleng_02 is not None
    assert saleng_02["vehicle_type"] == "PICKUP_TRUCK"

    saleng_05 = supabase_store.get_saleng_profile("saleng-05")
    assert saleng_05 is not None
    assert saleng_05["verified"] is False  # unverified KYC

