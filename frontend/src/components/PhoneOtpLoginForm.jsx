/**
 * คอมโพเนนต์เข้าสู่ระบบด้วยเบอร์โทรศัพท์และ OTP สำหรับผู้ขาย (PhoneOtpLoginForm)
 * รองรับ UC-01, REQ-UX-001, REQ-UX-002, REQ-QA-001, CC-01, AC-S01-01
 */

import React, { useState, useEffect } from 'react';
import { accountApi } from '../services/accountApi';

export default function PhoneOtpLoginForm({ onLoginSuccess }) {
  const [step, setStep] = useState('PHONE'); // 'PHONE' | 'OTP'
  const [phone, setPhone] = useState('');
  const [otpCode, setOtpCode] = useState('');
  const [cooldown, setCooldown] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [phoneMasked, setPhoneMasked] = useState('');

  useEffect(() => {
    let timer;
    if (cooldown > 0) {
      timer = setInterval(() => setCooldown((prev) => prev - 1), 1000);
    }
    return () => clearInterval(timer);
  }, [cooldown]);

  const handleRequestOtp = async (e) => {
    if (e) e.preventDefault();
    setError('');
    const cleanPhone = phone.replace(/\D/g, '');
    if (cleanPhone.length !== 10 || !cleanPhone.startsWith('0')) {
      setError('กรุณากรอกเบอร์โทรศัพท์ 10 หลักที่ถูกต้อง (เช่น 0812345678)');
      return;
    }

    setLoading(true);
    try {
      const res = await accountApi.requestOtp(cleanPhone);
      setPhoneMasked(res.phone_masked);
      setCooldown(res.cooldown_seconds || 60);
      setStep('OTP');
      // อำนวยความสะดวกในโหมดทดสอบ
      if (res.mock_otp) {
        setOtpCode(res.mock_otp);
      }
    } catch (err) {
      setError(err.message || 'ขอรับรหัส OTP ไม่สำเร็จ');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async (e) => {
    if (e) e.preventDefault();
    setError('');
    if (otpCode.length !== 6) {
      setError('กรุณากรอกรหัส OTP 6 หลัก');
      return;
    }

    setLoading(true);
    try {
      const cleanPhone = phone.replace(/\D/g, '');
      const auth = await accountApi.verifyOtp(cleanPhone, otpCode);
      if (onLoginSuccess) {
        onLoginSuccess(auth);
      }
    } catch (err) {
      setError(err.message || 'รหัส OTP ไม่ถูกต้อง');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      data-req="UC-01"
      className="bg-white rounded-2xl shadow-sm border border-emerald-100 p-5 max-w-md mx-auto"
    >
      <div className="flex items-center space-x-3 mb-4">
        <div className="w-10 h-10 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-700 text-xl font-bold">
          📱
        </div>
        <div>
          <h2 className="text-lg font-bold text-gray-900">เข้าสู่ระบบผู้ขาย</h2>
          <p className="text-xs text-gray-500">สะดวกรวดเร็วด้วยเบอร์โทรศัพท์และ OTP</p>
        </div>
      </div>

      {error && (
        <div
          data-testid="error-message"
          className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl"
        >
          {error}
        </div>
      )}

      {step === 'PHONE' ? (
        <form onSubmit={handleRequestOtp} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">
              เบอร์โทรศัพท์มือถือ
            </label>
            <input
              type="tel"
              data-testid="phone-input"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="08X-XXX-XXXX"
              maxLength={12}
              className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm"
            />
          </div>

          <button
            type="submit"
            data-testid="request-otp-btn"
            disabled={loading}
            className="w-full py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-medium rounded-xl text-sm transition-colors shadow-sm disabled:opacity-50 min-h-[48px]"
          >
            {loading ? 'กำลังส่งรหัส OTP...' : 'ขอรับรหัส OTP'}
          </button>
        </form>
      ) : (
        <form onSubmit={handleVerifyOtp} className="space-y-4">
          <div className="p-3 bg-emerald-50 rounded-xl border border-emerald-100 text-xs text-emerald-800">
            รหัส OTP ส่งไปยังเบอร์ <span className="font-bold">{phoneMasked}</span>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">
              รหัส OTP (6 หลัก)
            </label>
            <input
              type="text"
              data-testid="otp-input"
              value={otpCode}
              onChange={(e) => setOtpCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
              placeholder="123456"
              maxLength={6}
              className="w-full px-4 py-3 text-center tracking-widest text-lg font-bold rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>

          <button
            type="submit"
            data-testid="verify-otp-btn"
            disabled={loading || otpCode.length !== 6}
            className="w-full py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-medium rounded-xl text-sm transition-colors shadow-sm disabled:opacity-50 min-h-[48px]"
          >
            {loading ? 'กำลังตรวจสอบ...' : 'ยืนยันเข้าสู่ระบบ'}
          </button>

          <div className="flex items-center justify-between text-xs text-gray-500 pt-2">
            <button
              type="button"
              data-testid="change-phone-btn"
              onClick={() => setStep('PHONE')}
              className="text-gray-600 hover:underline"
            >
              ← เปลี่ยนเบอร์โทรศัพท์
            </button>

            {cooldown > 0 ? (
              <span data-testid="cooldown-timer">ขอรหัสใหม่ได้ใน {cooldown} วิ</span>
            ) : (
              <button
                type="button"
                data-testid="resend-otp-btn"
                onClick={handleRequestOtp}
                className="text-emerald-600 font-semibold hover:underline"
              >
                ขอรหัส OTP อีกครั้ง
              </button>
            )}
          </div>
        </form>
      )}
    </div>
  );
}

