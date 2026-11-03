"""
Unit tests สำหรับ Data Models และ Schema ระบบบัญชีและที่อยู่นัดหมาย (T-01)
รองรับ UC-01, MD-DOM-04, REQ-SEC-002, CC-04, P-01..P-04
"""

import pytest
from pydantic import ValidationError
from backend.app.models.account_models import (
    OtpRequest,
    OtpVerifyRequest,
    SellerProfileUpdateRequest,
    PickupLocationCreateRequest,
    PickupLocationUpdateRequest,
    GeoPoint,
    mask_phone_number,
)
from backend.app.core.supabase import supabase_store


def test_mask_phone_number():
    """ทดสอบฟังก์ชันแปลงเบอร์โทรศัพท์เป็น PDPA Masking 08X-XXX-XXXX (REQ-SEC-002)"""
    assert mask_phone_number("0812345678") == "08X-XXX-5678"
    assert mask_phone_number("0987654321") == "09X-XXX-4321"
    assert mask_phone_number("02-123-4567") == "02X-XXX-4567"
    assert mask_phone_number("") == "08X-XXX-XXXX"


def test_otp_request_validation():
    """ทดสอบ Pydantic Validation สำหรับ OtpRequest (AC-S01-01)"""
    # เบอร์โทร 10 หลักขึ้นต้นด้วย 0
    req = OtpRequest(phone="0812345678")
    assert req.phone == "0812345678"

    # มีขีดคั่นก็คลีนให้
    req_dash = OtpRequest(phone="081-234-5678")
    assert req_dash.phone == "0812345678"

    # เบอร์ไม่ครบ 10 หลัก
    with pytest.raises(ValidationError):
        OtpRequest(phone="0812345")

    # เบอร์ไม่ขึ้นต้นด้วย 0
    with pytest.raises(ValidationError):
        OtpRequest(phone="1812345678")


def test_otp_verify_validation():
    """ทดสอบ Pydantic Validation สำหรับ OtpVerifyRequest (AC-S01-01)"""
    req = OtpVerifyRequest(phone="0812345678", otp_code="123456")
    assert req.otp_code == "123456"

    # OTP ไม่ใช่ตัวเลข
    with pytest.raises(ValidationError):
        OtpVerifyRequest(phone="0812345678", otp_code="12345A")

    # OTP ไม่ครบ 6 หลัก
    with pytest.raises(ValidationError):
        OtpVerifyRequest(phone="0812345678", otp_code="12345")


def test_pickup_location_models_and_store():
    """ทดสอบ Data Models และ Supabase Store สำหรับที่อยู่นัดหมาย (AC-S01-02, MD-DOM-04)"""
    geo = GeoPoint(lat=13.7563, lng=100.5018)
    loc_req = PickupLocationCreateRequest(
        label="บ้านพักอาศัย",
        sub_district="บางซื่อ",
        address_text="123/45 ซอย 5 ถนนวงศ์สว่าง",
        geo_point=geo,
        is_default=True,
    )
    assert loc_req.sub_district == "บางซื่อ"
    assert loc_req.is_default is True

    # ทดสอบ Supabase store CRUD
    seller = supabase_store.create_seller({
        "phone": "0899999999",
        "display_name": "ทดสอบ ผู้ขาย",
    })
    seller_id = seller["seller_id"]

    loc_data = {
        "seller_id": seller_id,
        "label": loc_req.label,
        "sub_district": loc_req.sub_district,
        "address_text": loc_req.address_text,
        "geo_point": loc_req.geo_point.model_dump(),
        "is_default": loc_req.is_default,
    }
    created_loc = supabase_store.create_pickup_location(loc_data)
    assert created_loc["location_id"].startswith("LOC-")
    assert created_loc["sub_district"] == "บางซื่อ"
    assert created_loc["is_default"] is True

    # สร้างที่อยู่อันที่ 2 พร้อมตั้งเป็น default -> อันแรกต้องกลายเป็น false
    loc_data2 = {
        "seller_id": seller_id,
        "label": "ที่ทำงาน",
        "sub_district": "จตุจักร",
        "address_text": "999 อาคารสำนักงาน ชั้น 12",
        "geo_point": {"lat": 13.8000, "lng": 100.5500},
        "is_default": True,
    }
    created_loc2 = supabase_store.create_pickup_location(loc_data2)
    assert created_loc2["is_default"] is True

    # ตรวจสอบอันแรกว่าถูกปลด default หรือไม่
    loc1_updated = supabase_store.get_pickup_location(created_loc["location_id"])
    assert loc1_updated["is_default"] is False

    # ตรวจสอบรายการทั้งหมดของผู้ขาย
    locs = supabase_store.get_pickup_locations_by_seller(seller_id)
    assert len(locs) == 2
    # default ต้องอยู่อันแรก
    assert locs[0]["location_id"] == created_loc2["location_id"]

    # ตรวจสอบการดึง default location
    default_loc = supabase_store.get_default_pickup_location(seller_id)
    assert default_loc["location_id"] == created_loc2["location_id"]

