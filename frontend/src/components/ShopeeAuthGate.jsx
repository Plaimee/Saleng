/**
 * Shopee-Style Authentication Gate (เข้าสู่ระบบ / สมัครสมาชิก)
 * เป็นหน้าแรกบังคับของทั้ง 3 พอร์ทัล: ผู้ขาย (Seller), ซาเล้ง (Buyer/Collector), แอดมิน (Admin)
 * รองรับ UC-01, UC-11, AC-S01-01, AC-B01-01, AC-A01-05
 */

import React, { useState, useEffect } from 'react';
import { accountApi } from '../services/accountApi';
import { collectorAccountApi } from '../services/collectorAccountApi';

const PORTAL_META = {
  seller: {
    id: 'seller',
    shortName: 'ผู้ขาย (Seller)',
    badge: 'Seller Centre',
    icon: '🛒',
    heroTitle: 'ขายของเก่าได้ราคาดี',
    heroSubtitle: 'เช็กราคากลางประจำวัน นัดซาเล้งรับถึงหน้าบ้าน โปร่งใสทุกขั้นตอน',
    highlights: [
      { icon: '💰', text: 'ราคากลางอัปเดตทุกวัน ไม่โดนกดราคา' },
      { icon: '📍', text: 'ปักหมุดนัดรับถึงหน้าบ้าน ติดตามเรียลไทม์' },
      { icon: '🧾', text: 'ใบเสร็จดิจิทัลพร้อมภาพชั่งน้ำหนักตรวจสอบได้' },
    ],
    demoHint: 'โหมดทดสอบ: กรอกเบอร์ 10 หลัก (เช่น 0812345678) แล้วใช้ OTP 123456',
  },
  collector: {
    id: 'collector',
    shortName: 'ซาเล้ง (Buyer)',
    badge: 'Collector Hub',
    icon: '🛺',
    heroTitle: 'รับงานคุ้มค่า วิ่งรถไม่เสียเที่ยว',
    heroSubtitle: 'ค้นหางานใกล้ตัว ประเมินค่าน้ำมันและน้ำหนักบรรทุกก่อนกดรับงาน',
    highlights: [
      { icon: '📡', text: 'เรดาร์หางานใกล้คุณ พร้อมแผนที่วางเส้นทาง' },
      { icon: '⛽', text: 'คำนวณจุดคุ้มทุนและค่าน้ำมันก่อนตัดสินใจ' },
      { icon: '🪪', text: 'ระบบยืนยันตัวตน KYC สร้างความมั่นใจให้ผู้ขาย' },
    ],
    demoHint: 'โหมดทดสอบ: กรอกเบอร์ 10 หลัก (เช่น 0899999999) แล้วใช้ OTP 123456',
  },
  admin: {
    id: 'admin',
    shortName: 'แอดมิน (Admin)',
    badge: 'Admin Portal',
    icon: '🛡️',
    heroTitle: 'ศูนย์ควบคุมและกำกับดูแลระบบ',
    heroSubtitle: 'อนุมัติ KYC คุมราคากลาง ระงับข้อพิพาท และตรวจสอบความปลอดภัยตาม PDPA',
    highlights: [
      { icon: '⚖️', text: 'ตรวจสอบเอกสาร KYC และจัดการบทลงโทษ' },
      { icon: '📊', text: 'ประกาศราคากลางและเกณฑ์คัดแยกวัสดุ' },
      { icon: '🔒', text: 'บันทึก Audit Trail และกำกับดูแล PDPA' },
    ],
    demoHint: 'บัญชีทดสอบแอดมิน: admin / admin123',
  },
};

function maskPhone(cleanPhone) {
  if (cleanPhone.length !== 10) return cleanPhone;
  return `${cleanPhone.slice(0, 3)}-XXX-${cleanPhone.slice(6)}`;
}

function getRegisteredAdmins() {
  try {
    const raw = window.localStorage.getItem('saleng_registered_admins');
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export default function ShopeeAuthGate({ activeRole, onSwitchRole, onAuthenticated }) {
  const [mode, setMode] = useState('login'); // 'login' | 'register'
  const [step, setStep] = useState('INPUT'); // 'INPUT' | 'OTP' (for seller & collector)

  // Shared / Phone OTP fields
  const [displayName, setDisplayName] = useState('');
  const [phone, setPhone] = useState('');
  const [otpCode, setOtpCode] = useState('');
  const [phoneMasked, setPhoneMasked] = useState('');
  const [cooldown, setCooldown] = useState(0);
  const [vehicleType, setVehicleType] = useState('รถสามล้อซาเล้ง');

  // Admin fields
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  // Status
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [infoMsg, setInfoMsg] = useState('');

  const meta = PORTAL_META[activeRole] || PORTAL_META.seller;

  // Reset form when switching portal or tab
  useEffect(() => {
    if (activeRole === 'admin' && mode !== 'login') {
      setMode('login');
    }
    setStep('INPUT');
    setError('');
    setInfoMsg('');
    setOtpCode('');
    setCooldown(0);
  }, [activeRole, mode]);

  useEffect(() => {
    if (cooldown <= 0) return undefined;
    const timer = setInterval(() => setCooldown((prev) => prev - 1), 1000);
    return () => clearInterval(timer);
  }, [cooldown]);

  // --- Phone OTP Request (Seller / Collector) ---
  const handleRequestOtp = async (e) => {
    if (e) e.preventDefault();
    setError('');
    setInfoMsg('');

    const cleanPhone = phone.replace(/\D/g, '');
    if (mode === 'register' && displayName.trim().length < 2) {
      setError('กรุณากรอกชื่อ-นามสกุล หรือชื่อร้านอย่างน้อย 2 ตัวอักษร');
      return;
    }
    if (cleanPhone.length !== 10 || !cleanPhone.startsWith('0')) {
      setError('กรุณากรอกเบอร์โทรศัพท์มือถือ 10 หลักให้ถูกต้อง (เช่น 0812345678)');
      return;
    }

    setLoading(true);
    try {
      const api = activeRole === 'collector' ? collectorAccountApi : accountApi;
      const res = await api.requestOtp(cleanPhone);
      setPhoneMasked(res.phone_masked || maskPhone(cleanPhone));
      setCooldown(res.cooldown_seconds || 60);
      setStep('OTP');
      if (res.mock_otp) {
        setOtpCode(res.mock_otp);
      }
    } catch {
      // Fallback สำหรับโหมดพรีวิวเมื่อ Backend ยังไม่ได้รัน
      setPhoneMasked(maskPhone(cleanPhone));
      setCooldown(60);
      setOtpCode('123456');
      setStep('OTP');
      setInfoMsg('โหมดทดสอบ: ระบบกรอกรหัส OTP จำลอง (123456) ให้เรียบร้อยแล้ว');
    } finally {
      setLoading(false);
    }
  };

  // --- Phone OTP Verify (Seller / Collector) ---
  const handleVerifyOtp = async (e) => {
    if (e) e.preventDefault();
    setError('');

    if (otpCode.length !== 6) {
      setError('กรุณากรอกรหัส OTP ให้ครบ 6 หลัก');
      return;
    }

    const cleanPhone = phone.replace(/\D/g, '');
    setLoading(true);
    try {
      const api = activeRole === 'collector' ? collectorAccountApi : accountApi;
      const authData = await api.verifyOtp(cleanPhone, otpCode);
      if (mode === 'register' && displayName.trim()) {
        authData.display_name = displayName.trim();
        if (activeRole === 'collector' && authData.saleng_id) {
          try {
            await collectorAccountApi.updateProfile(authData.saleng_id, displayName.trim());
          } catch {
            // ignore optional profile sync failure
          }
          const storedProfile = JSON.parse(
            window.localStorage.getItem('saleng_collector_profile') || '{}'
          );
          window.localStorage.setItem(
            'saleng_collector_profile',
            JSON.stringify({ ...storedProfile, display_name: displayName.trim() })
          );
        }
      }
      onAuthenticated(activeRole, authData);
    } catch {
      // Fallback สำหรับโหมดพรีวิวเมื่อ Backend ยังไม่ได้รัน
      if (otpCode !== '123456') {
        setError('รหัส OTP ไม่ถูกต้อง (ในโหมดทดสอบกรุณาใช้รหัส 123456)');
        setLoading(false);
        return;
      }

      const masked = maskPhone(cleanPhone);
      if (activeRole === 'seller') {
        const sellerData = {
          session_token: `demo-seller-${Date.now()}`,
          seller_id: `SEL-${cleanPhone.slice(-4)}`,
          phone_masked: masked,
          display_name:
            displayName.trim() || `ผู้ขาย ${cleanPhone.slice(-4)}`,
        };
        window.localStorage.setItem('saleng_seller_token', sellerData.session_token);
        window.localStorage.setItem(
          'saleng_seller_profile',
          JSON.stringify({
            seller_id: sellerData.seller_id,
            phone_masked: sellerData.phone_masked,
            display_name: sellerData.display_name,
          })
        );
        onAuthenticated('seller', sellerData);
      } else {
        const collectorData = {
          session_token: `demo-collector-${Date.now()}`,
          saleng_id: 'saleng-01',
          display_name:
            displayName.trim() || 'ลุงสมชาย ซาเล้งสุทธิสาร',
          phone_masked: masked,
          verified: true,
          kyc_status: 'VERIFIED',
          vehicle_type: vehicleType,
          max_capacity_kg: vehicleType === 'รถกระบะ' ? 800 : 300,
        };
        window.localStorage.setItem('saleng_collector_session', collectorData.session_token);
        window.localStorage.setItem(
          'saleng_collector_profile',
          JSON.stringify({
            saleng_id: collectorData.saleng_id,
            display_name: collectorData.display_name,
            phone_masked: collectorData.phone_masked,
            verified: collectorData.verified,
            kyc_status: collectorData.kyc_status,
            vehicle_type: collectorData.vehicle_type,
            max_capacity_kg: collectorData.max_capacity_kg,
          })
        );
        onAuthenticated('collector', collectorData);
      }
    } finally {
      setLoading(false);
    }
  };

  // --- Admin Login Only ---
  const handleAdminSubmit = (e) => {
    e.preventDefault();
    setError('');
    setInfoMsg('');

    const cleanUser = username.trim();
    if (!cleanUser || !password) {
      setError('กรุณากรอกชื่อผู้ใช้และรหัสผ่านให้ครบถ้วน');
      return;
    }

    const existing = getRegisteredAdmins();
    const matched = existing.find(
      (a) => a.username === cleanUser && a.password === password
    );

    if ((cleanUser === 'admin' && password === 'admin123') || matched) {
      const profile = matched
        ? { username: matched.username, display_name: matched.display_name }
        : { username: 'admin', display_name: 'ผู้ดูแลระบบหลัก (Admin)' };

      window.localStorage.setItem('saleng_admin_session', 'authenticated');
      window.localStorage.setItem('saleng_admin_profile', JSON.stringify(profile));
      onAuthenticated('admin', profile);
      return;
    }

    setError('ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง (ทดสอบ: admin / admin123)');
  };

  return (
    <div className="min-h-screen flex flex-col sp-page-bg">
      {/* Top Auth Header: Black & Yellow Accent */}
      <header className="bg-black text-white border-b-2 border-yellow-400 shadow-sm sticky top-0 z-30">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-3 flex flex-wrap items-center justify-between gap-3">
          {/* Brand + Page Title */}
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <span className="w-9 h-9 rounded-lg bg-yellow-400 flex items-center justify-center text-2xl">
                🛺
              </span>
              <span className="text-2xl font-bold text-yellow-400 tracking-tight">
                Saleng
              </span>
            </div>
            <span className="text-gray-600 text-xl font-light">|</span>
            <span className="text-base sm:text-lg font-medium text-white">
              {activeRole === 'admin' || mode === 'login' ? 'เข้าสู่ระบบ' : 'สมัครสมาชิก'}
            </span>
            <span className="hidden sm:inline-block text-xs font-bold px-2.5 py-0.5 rounded-full bg-yellow-400 text-black">
              {meta.badge}
            </span>
          </div>

          {/* 3-Portal Switcher */}
          <div className="flex items-center gap-1.5 bg-zinc-900 p-1 rounded-lg border border-zinc-700">
            {Object.values(PORTAL_META).map((portal) => {
              const isActive = activeRole === portal.id;
              return (
                <button
                  key={portal.id}
                  type="button"
                  onClick={() => onSwitchRole(portal.id)}
                  className={`px-3 py-1.5 rounded-md text-xs sm:text-sm font-bold transition flex items-center gap-1 ${
                    isActive
                      ? 'bg-yellow-400 text-black shadow-sm'
                      : 'text-gray-300 hover:text-white'
                  }`}
                >
                  <span>{portal.icon}</span>
                  <span>{portal.shortName}</span>
                </button>
              );
            })}
          </div>
        </div>
      </header>

      {/* 70% Yellow Hero Section with Centered White Auth Card */}
      <main className="flex-1 sp-auth-hero flex items-center py-10 px-4 sm:px-6">
        <div className="max-w-5xl w-full mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8 items-center relative z-10">
          {/* Left Branding Column (Black Text on Yellow Hero) */}
          <div className="lg:col-span-7 text-gray-900 text-center lg:text-left space-y-5">
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full sp-badge-dark text-xs font-bold shadow">
              <span>{meta.icon}</span>
              <span className="text-yellow-400">พอร์ทัล {meta.shortName}</span>
            </div>

            <div className="flex flex-col lg:flex-row items-center lg:items-start gap-4">
              <div className="w-20 h-20 rounded-2xl bg-black border-4 border-white shadow-xl flex items-center justify-center text-5xl flex-shrink-0">
                🛺
              </div>
              <div>
                <h1 className="text-2xl sm:text-3xl font-extrabold leading-tight">
                  <span className="sp-hero-stamp">{meta.heroTitle}</span>
                </h1>
                <p className="mt-3 text-sm sm:text-base text-black font-semibold max-w-lg mx-auto lg:mx-0">
                  {meta.heroSubtitle}
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5 pt-2">
              {meta.highlights.map((item, idx) => (
                <div
                  key={idx}
                  className="sp-hero-card rounded-xl p-3.5 text-left"
                >
                  <div className="text-2xl mb-1.5">{item.icon}</div>
                  <p className="text-xs sm:text-sm font-bold text-black leading-snug">
                    {item.text}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Right Auth Card (Sleek Modern Elevated Card) */}
          <div className="lg:col-span-5">
            <div className="sp-auth-card overflow-hidden max-w-md mx-auto p-6 sm:p-8">
              {/* Card Brand Header */}
              <div className="flex items-center gap-3.5 mb-6">
                <div className="w-12 h-12 rounded-2xl bg-yellow-400 flex items-center justify-center text-2xl shadow-sm flex-shrink-0">
                  {meta.icon}
                </div>
                <div>
                  <span className="inline-block text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-black text-yellow-400 mb-1">
                    {meta.badge}
                  </span>
                  <h2 className="text-xl font-extrabold text-black leading-tight">
                    {activeRole === 'admin'
                      ? 'เข้าสู่ระบบผู้ดูแลระบบ'
                      : mode === 'login'
                      ? `เข้าสู่ระบบ${meta.shortName.split(' ')[0]}`
                      : `สมัครสมาชิก${meta.shortName.split(' ')[0]}`}
                  </h2>
                </div>
              </div>

              {/* Segmented Pill Tabs (ซ่อนสำหรับแอดมิน) */}
              {activeRole !== 'admin' && (
                <div className="sp-segmented mb-6">
                  <button
                    type="button"
                    data-testid="auth-tab-login"
                    onClick={() => setMode('login')}
                    className={`sp-auth-tab ${mode === 'login' ? 'sp-auth-tab-active' : ''}`}
                  >
                    เข้าสู่ระบบ
                  </button>
                  <button
                    type="button"
                    data-testid="auth-tab-register"
                    onClick={() => setMode('register')}
                    className={`sp-auth-tab ${mode === 'register' ? 'sp-auth-tab-active' : ''}`}
                  >
                    สมัครสมาชิก
                  </button>
                </div>
              )}

              <div>
                {error && (
                  <div
                    role="alert"
                    className="mb-4 p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs font-medium"
                  >
                    ⚠️ {error}
                  </div>
                )}

                {infoMsg && (
                  <div className="mb-4 p-3 rounded-xl bg-yellow-50 border border-yellow-300 text-black text-xs font-medium">
                    ℹ️ {infoMsg}
                  </div>
                )}

                {/* Seller & Collector Auth Form (Phone + OTP) */}
                {activeRole !== 'admin' ? (
                  step === 'INPUT' ? (
                    <form onSubmit={handleRequestOtp} className="space-y-4">
                      {mode === 'register' && (
                        <div>
                          <label className="block text-xs font-semibold text-gray-700 mb-1">
                            {activeRole === 'collector'
                              ? 'ชื่อ-นามสกุลผู้ขับซาเล้ง'
                              : 'ชื่อผู้ขาย / ชื่อบ้านหรือร้าน'}
                          </label>
                          <input
                            type="text"
                            value={displayName}
                            onChange={(e) => setDisplayName(e.target.value)}
                            placeholder={
                              activeRole === 'collector'
                                ? 'เช่น สมชาย ซาเล้งใจดี'
                                : 'เช่น บ้านคุณสมหญิง'
                            }
                            className="sp-input"
                          />
                        </div>
                      )}

                      <div>
                        <label className="block text-xs font-semibold text-gray-700 mb-1">
                          เบอร์โทรศัพท์มือถือ (10 หลัก)
                        </label>
                        <input
                          type="tel"
                          value={phone}
                          onChange={(e) => setPhone(e.target.value)}
                          placeholder="0812345678"
                          maxLength={12}
                          className="sp-input"
                        />
                      </div>

                      {mode === 'register' && activeRole === 'collector' && (
                        <div>
                          <label className="block text-xs font-semibold text-gray-700 mb-1">
                            ประเภทยานพาหนะรับซื้อ
                          </label>
                          <select
                            value={vehicleType}
                            onChange={(e) => setVehicleType(e.target.value)}
                            className="sp-input"
                          >
                            <option value="รถสามล้อซาเล้ง">รถสามล้อซาเล้ง (ความจุ ~300 กก.)</option>
                            <option value="รถกระบะ">รถกระบะ (ความจุ ~800 กก.)</option>
                            <option value="รถบรรทุกเล็ก">รถบรรทุกเล็ก (ความจุ ~1,500 กก.)</option>
                          </select>
                        </div>
                      )}

                      <button
                        type="submit"
                        disabled={loading}
                        className="w-full sp-btn-primary text-sm"
                      >
                        {loading
                          ? 'กำลังส่งรหัส OTP...'
                          : mode === 'login'
                          ? 'ถัดไป (รับรหัส OTP)'
                          : 'สมัครสมาชิกด้วย OTP'}
                      </button>
                    </form>
                  ) : (
                    <form onSubmit={handleVerifyOtp} className="space-y-4">
                      <div className="p-3 rounded bg-yellow-100 border border-yellow-400 text-xs text-black flex items-center justify-between">
                        <span>
                          ส่งรหัส OTP ไปยัง <strong>{phoneMasked}</strong>
                        </span>
                        <button
                          type="button"
                          onClick={() => setStep('INPUT')}
                          className="text-black font-bold underline"
                        >
                          เปลี่ยนเบอร์
                        </button>
                      </div>

                      <div>
                        <label className="block text-xs font-semibold text-gray-700 mb-1">
                          กรอกรหัสยืนยัน OTP (6 หลัก)
                        </label>
                        <input
                          type="text"
                          value={otpCode}
                          onChange={(e) =>
                            setOtpCode(e.target.value.replace(/\D/g, '').slice(0, 6))
                          }
                          placeholder="123456"
                          maxLength={6}
                          className="sp-input text-center text-xl font-bold tracking-widest"
                        />
                      </div>

                      <button
                        type="submit"
                        disabled={loading || otpCode.length !== 6}
                        className="w-full sp-btn-primary text-sm"
                      >
                        {loading
                          ? 'กำลังตรวจสอบ...'
                          : mode === 'login'
                          ? 'ยืนยันเข้าสู่ระบบ'
                          : 'ยืนยันสมัครสมาชิกและเข้าใช้งาน'}
                      </button>

                      <div className="text-center text-xs text-gray-500">
                        {cooldown > 0 ? (
                          <span>ขอรหัสใหม่ได้ในอีก {cooldown} วินาที</span>
                        ) : (
                          <button
                            type="button"
                            onClick={handleRequestOtp}
                            className="text-black font-bold underline"
                          >
                            ส่งรหัส OTP อีกครั้ง
                          </button>
                        )}
                      </div>
                    </form>
                  )
                ) : (
                  /* Admin Auth Form (Login Only: Username + Password) */
                  <form onSubmit={handleAdminSubmit} className="space-y-3.5">
                    <div>
                      <label className="block text-xs font-semibold text-gray-700 mb-1">
                        ชื่อผู้ใช้ (Username)
                      </label>
                      <input
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        placeholder="admin"
                        autoComplete="username"
                        className="sp-input"
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-gray-700 mb-1">
                        รหัสผ่าน (Password)
                      </label>
                      <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="••••••••"
                        autoComplete="current-password"
                        className="sp-input"
                      />
                    </div>

                    <button type="submit" className="w-full sp-btn-primary text-sm">
                      เข้าสู่ระบบแอดมิน
                    </button>
                  </form>
                )}

                {/* Subtle Demo Helper & Switch Mode Link */}
                <div className="mt-6 pt-4 border-t border-zinc-100 text-xs text-zinc-500 space-y-3">
                  <div className="flex items-start gap-2 rounded-xl bg-zinc-50 px-3.5 py-2.5 text-zinc-600">
                    <span className="text-sm leading-none mt-0.5">💡</span>
                    <span className="leading-relaxed">{meta.demoHint}</span>
                  </div>
                  {activeRole !== 'admin' && (
                    <div className="text-center">
                      {mode === 'login' ? (
                        <span>
                          ยังไม่มีบัญชี Saleng?{' '}
                          <button
                            type="button"
                            onClick={() => setMode('register')}
                            className="text-black font-bold underline decoration-yellow-400 decoration-2 underline-offset-4 hover:text-zinc-700"
                          >
                            สมัครสมาชิกเลย
                          </button>
                        </span>
                      ) : (
                        <span>
                          มีบัญชีอยู่แล้ว?{' '}
                          <button
                            type="button"
                            onClick={() => setMode('login')}
                            className="text-black font-bold underline decoration-yellow-400 decoration-2 underline-offset-4 hover:text-zinc-700"
                          >
                            เข้าสู่ระบบ
                          </button>
                        </span>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-black border-t-2 border-yellow-400 py-5 text-center text-xs text-yellow-300">
        Saleng Digital Scrap Platform &copy; 2026 รายวิชา 517 511 Requirements Engineering (กลุ่ม 2)
      </footer>
    </div>
  );
}
