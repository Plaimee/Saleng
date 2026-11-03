"""
Unit Tests สำหรับ Data Models และ Schema ของระบบบัญชีซาเล้ง (Task T-01)
รองรับ UC-01, MD-DOM-04, REQ-SEC-002, CC-04, P-01..P-03
"""

import pytest
from pydantic import ValidationError
from backend.app.models.collector_account_models import (
    CollectorOtpRequest,
    CollectorOtpVerifyRequest,
    CollectorAuthResponse,
    CollectorProfileUpdateRequest,
    VehicleProfileUpdateRequest,
    KycSubmissionRequest,
    KycStatusResponse,
    JobClaimGateCheckResponse,
    mask_phone_number,
    validate_thai_id,
)
from backend.app.core.supabase import SupabaseStore


def test_mask_phone_number():
    """ทดสอบการแปลงเบอร์โทรศัพท์เป็น 08X-XXX-XXXX ตาม REQ-SEC-002"""
    assert mask_phone_number("0812345678") == "08X-XXX-5678"
    assert mask_phone_number("089-876-5432") == "08X-XXX-5432"
    assert mask_phone_number("021234567") == "02X-XXX-4567"
    assert mask_phone_number("") == "08X-XXX-XXXX"


def test_validate_thai_id():
    """ทดสอบการตรวจสอบ Checksum เลขบัตรประชาชน 13 หลัก"""
    # 1100701234561 (ตัวอย่างเลขบัตรที่มี checksum ถูกต้อง: total % 11)
    # คำนวณ check digit สำหรับ '110070123456'
    digits = [1, 1, 0, 0, 7, 0, 1, 2, 3, 4, 5, 6]
    total = sum(d * (13 - i) for i, d in enumerate(digits))
    valid_cd = (11 - (total % 11)) % 10
    valid_id = "110070123456" + str(valid_cd)

    assert validate_thai_id(valid_id) is True
    assert validate_thai_id("1234567890123") is False
    assert validate_thai_id("123") is False


def test_collector_otp_request_valid():
    """ทดสอบการสร้างคำขอ OTP ซาเล้งด้วยเบอร์ที่ถูกต้อง (AC-B01-01)"""
    req = CollectorOtpRequest(phone="0812345678")
    assert req.phone == "0812345678"


def test_collector_otp_request_invalid():
    """ทดสอบการปฏิเสธเบอร์โทรศัพท์ที่ไม่ถูกต้อง"""
    with pytest.raises(ValidationError):
        CollectorOtpRequest(phone="12345")
    with pytest.raises(ValidationError):
        CollectorOtpRequest(phone="9812345678")  # ไม่ได้ขึ้นต้นด้วย 0


def test_vehicle_profile_update_validation():
    """ทดสอบการตรวจสอบค่ายานพาหนะและความจุ (REQ-FN-001, MD-DOM-04, BR-03)"""
    # ค่าถูกต้อง
    v_req = VehicleProfileUpdateRequest(
        vehicle_type="TRICYCLE",
        license_plate="1กข-1234",
        max_capacity_kg=150.0
    )
    assert v_req.vehicle_type == "TRICYCLE"
    assert v_req.max_capacity_kg == 150.0

    # ความจุ <= 0 ต้อง Error
    with pytest.raises(ValidationError):
        VehicleProfileUpdateRequest(
            vehicle_type="SIDE_CAR_MOTORCYCLE",
            max_capacity_kg=0.0
        )

    # ประเภทรถนอกเหนือจากที่กำหนดต้อง Error
    with pytest.raises(ValidationError):
        VehicleProfileUpdateRequest(
            vehicle_type="AIRPLANE",  # type: ignore
            max_capacity_kg=500.0
        )


def test_kyc_submission_validation():
    """ทดสอบการส่งเอกสาร KYC (AC-B01-03, Q-02)"""
    digits = [1, 1, 0, 0, 7, 0, 1, 2, 3, 4, 5, 6]
    total = sum(d * (13 - i) for i, d in enumerate(digits))
    valid_cd = (11 - (total % 11)) % 10
    valid_id = "110070123456" + str(valid_cd)

    kyc_req = KycSubmissionRequest(
        id_card_no=valid_id,
        full_name="สมชาย สายรีไซเคิล",
        id_card_photo_url="/uploads/id_card.jpg",
        selfie_photo_url="/uploads/selfie.jpg",
        vehicle_photo_url="/uploads/vehicle.jpg"
    )
    assert kyc_req.id_card_no == valid_id
    assert kyc_req.full_name == "สมชาย สายรีไซเคิล"

    # ผิด Checksum เลข ปชช.
    with pytest.raises(ValidationError):
        KycSubmissionRequest(
            id_card_no="1234567890123",
            full_name="ทดสอบ ผิดเลข",
            id_card_photo_url="/uploads/id.jpg",
            selfie_photo_url="/uploads/selfie.jpg"
        )


def test_supabase_store_collector_operations():
    """ทดสอบ SupabaseStore สำหรับ collector OTP, Session, KYC และ Profile"""
    store = SupabaseStore()

    # 1. OTP creation & verification
    otp = store.create_collector_otp("0812345678", "123456")
    assert otp["otp_code"] == "123456"
    latest_otp = store.get_latest_collector_otp("0812345678")
    assert latest_otp is not None
    assert latest_otp["otp_code"] == "123456"
    store.mark_collector_otp_used(otp["id"])
    assert store.get_latest_collector_otp("0812345678") is None

    # 2. Collector profile creation
    profile = store.create_collector_profile("0899998888", "ลุงชัย พ่วงข้าง")
    assert profile["saleng_id"].startswith("saleng-")
    assert profile["verified"] is False
    assert profile["kyc_status"] == "UNVERIFIED"

    # 3. Session creation & retrieval
    session = store.create_collector_session(profile["saleng_id"])
    token = session["token"]
    assert store.get_collector_session(token) is not None
    store.delete_collector_session(token)
    assert store.get_collector_session(token) is None

    # 4. KYC submission & review
    kyc_data = {
        "id_card_no": "1100701234561",
        "full_name": "ลุงชัย พ่วงข้าง",
        "id_card_photo_url": "/id.png",
        "selfie_photo_url": "/selfie.png",
        "vehicle_photo_url": "/veh.png",
    }
    sub = store.submit_collector_kyc(profile["saleng_id"], kyc_data)
    assert sub["status"] == "PENDING_REVIEW"
    assert profile["kyc_status"] == "PENDING_REVIEW"

    # Mock approval
    updated_profile = store.update_collector_kyc_status(profile["saleng_id"], "VERIFIED")
    assert updated_profile is not None
    assert updated_profile["verified"] is True
    assert updated_profile["kyc_status"] == "VERIFIED"
