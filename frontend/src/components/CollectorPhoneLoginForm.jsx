/**
 * คอมโพเนนต์เข้าสู่ระบบด้วยเบอร์โทรศัพท์และ Phone OTP สำหรับซาเล้ง (CollectorPhoneLoginForm)
 * รองรับ UC-01, REQ-UX-001, REQ-SEC-002, REQ-QA-001, CC-01, AC-B01-01, Q-01
 */

import React, { useState, useEffect } from 'react';
import { collectorAccountApi } from '../services/collectorAccountApi';

export default function CollectorPhoneLoginForm({ onLoginSuccess }) {
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
      const res = await collectorAccountApi.requestOtp(cleanPhone);
      setPhoneMasked(res.phone_masked);
      setCooldown(res.cooldown_seconds || 60);
      setStep('OTP');
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
      const authData = await collectorAccountApi.verifyOtp(cleanPhone, otpCode);
      if (onLoginSuccess) {
        onLoginSuccess(authData);
      }
    } catch (err) {
      setError(err.message || 'ยืนยันรหัส OTP ไม่สำเร็จ');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      data-req="UC-01"
      className="w-full max-w-md mx-auto bg-white rounded-2xl shadow-lg border border-emerald-100 p-6 my-4"
    >
      <div className="flex items-center space-x-3 mb-6">
        <div className="w-12 h-12 bg-emerald-600 rounded-xl flex items-center justify-center text-white shadow-md">
          <span className="text-2xl font-bold">🚛</span>
        </div>
        <div>
          <h2 className="text-xl font-bold text-gray-900">เข้าสู่ระบบซาเล้ง</h2>
          <p className="text-sm text-gray-500">แพลตฟอร์มรับซื้อของเก่าและจัดการเส้นทาง</p>
        </div>
      </div>

      {error && (
        <div
          data-testid="login-error-alert"
          className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 text-sm rounded-xl flex items-center"
        >
          <span className="mr-2">⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {step === 'PHONE' ? (
        <form onSubmit={handleRequestOtp} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              เบอร์โทรศัพท์มือถือ (10 หลัก)
            </label>
            <input
              type="tel"
              data-testid="phone-input"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="0812345678"
              maxLength={10}
              className="w-full h-12 px-4 rounded-xl border border-gray-300 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-lg tracking-wider"
              disabled={loading}
              autoFocus
            />
          </div>

          <button
            type="submit"
            data-testid="request-otp-btn"
            disabled={loading || phone.length < 10}
            className="w-full min-h-[48px] bg-emerald-600 hover:bg-emerald-700 text-white font-medium rounded-xl shadow-md transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center text-base"
          >
            {loading ? 'กำลังส่งรหัส...' : 'ขอรับรหัส OTP'}
          </button>
        </form>
      ) : (
        <form onSubmit={handleVerifyOtp} className="space-y-4">
          <div className="bg-emerald-50 p-3 rounded-xl flex justify-between items-center text-sm">
            <div>
              <span className="text-gray-600">ส่งรหัสไปยังเบอร์: </span>
              <strong className="text-emerald-900">{phoneMasked}</strong>
            </div>
            <button
              type="button"
              onClick={() => {
                setStep('PHONE');
                setOtpCode('');
                setError('');
              }}
              className="text-emerald-700 hover:underline font-medium text-xs min-h-[32px] px-2 py-1"
            >
              เปลี่ยนเบอร์
            </button>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              รหัส OTP (6 หลัก)
            </label>
            <input
              type="text"
              data-testid="otp-input"
              value={otpCode}
              onChange={(e) => setOtpCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
              placeholder="123456"
              maxLength={6}
              className="w-full h-12 px-4 rounded-xl border border-gray-300 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-2xl tracking-widest text-center font-mono font-bold"
              disabled={loading}
              autoFocus
            />
          </div>

          <button
            type="submit"
            data-testid="verify-otp-btn"
            disabled={loading || otpCode.length !== 6}
            className="w-full min-h-[48px] bg-emerald-600 hover:bg-emerald-700 text-white font-medium rounded-xl shadow-md transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center text-base"
          >
            {loading ? 'กำลังตรวจสอบ...' : 'ยืนยันและเข้าสู่ระบบ'}
          </button>

          <div className="text-center pt-2">
            {cooldown > 0 ? (
              <p className="text-xs text-gray-500">
                ขอรหัสใหม่ได้ในอีก <span className="font-semibold text-emerald-600">{cooldown}</span> วินาที
              </p>
            ) : (
              <button
                type="button"
                data-testid="resend-otp-btn"
                onClick={handleRequestOtp}
                className="text-xs text-emerald-700 hover:underline font-medium min-h-[40px] px-3 py-1"
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

