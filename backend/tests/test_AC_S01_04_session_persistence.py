"""
Automated Test สำหรับ AC-S01-04: Session Token Validation & Persistence
รองรับ CC-05, REQ-OP-001, P-04
- เซสชันโทเคนต้องมีอายุ 30 วัน
- ฟังก์ชัน verify_seller_session ต้องตรวจสอบความถูกต้องของ Token
- หาก Token หมดอายุหรือไม่พบในระบบ ต้องคืนค่า None หรือถูกปฏิเสธ
"""

from datetime import datetime, timezone, timedelta
import pytest
from backend.app.core.supabase import supabase_store
from backend.app.services.account_service import verify_seller_session, SellerAuthService
from backend.app.models.account_models import OtpRequest, OtpVerifyRequest


def test_AC_S01_04_session_token_lifecycle():
    """ทดสอบวงจรชีวิตของเซสชันโทเคน (AC-S01-04)"""
    phone = "0884443322"
    # ขอ OTP และยืนยัน
    SellerAuthService.request_otp(OtpRequest(phone=phone))
    auth = SellerAuthService.verify_otp(OtpVerifyRequest(phone=phone, otp_code="123456"))
    token = auth.session_token

    # 1. ตรวจสอบ session token
    sess = verify_seller_session(token)
    assert sess is not None
    assert sess["seller_id"] == auth.seller_id
    assert sess["phone"] == phone

    # 2. ตรวจสอบวันหมดอายุ (ต้องอยู่ในอนาคต ~30 วัน)
    exp = datetime.fromisoformat(sess["expires_at"])
    now = datetime.now(timezone.utc)
    diff_days = (exp - now).days
    assert 28 <= diff_days <= 31

    # 3. ทดสอบกรณี token ปลอม
    assert verify_seller_session("fake-token-1234") is None

    # 4. ทดสอบกรณี token หมดอายุ
    expired_token = "expired-token-xyz"
    supabase_store.create_seller_session({
        "session_token": expired_token,
        "seller_id": auth.seller_id,
        "phone": phone,
        "expires_at": (now - timedelta(days=1)).isoformat(),
    })
    # เมื่อ verify token ที่หมดอายุ ต้องคืน None และลบออกจาก store
    assert verify_seller_session(expired_token) is None
    assert supabase_store.get_seller_session(expired_token) is None

