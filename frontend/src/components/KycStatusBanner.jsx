/**
 * คอมโพเนนต์แถบสถานะการยืนยันตัวตน KYC (KycStatusBanner)
 * รองรับ SC-04, D-00-01, REQ-UX-001, CC-01, AC-B01-03..04, Q-03, Q-05, P-03..P-05
 */

import React from 'react';

export default function KycStatusBanner({ profile, onOpenKycModal }) {
  if (!profile) return null;

  const kycStatus = profile.kyc_status || 'UNVERIFIED';

  if (kycStatus === 'VERIFIED') {
    return (
      <div
        data-req="D-00-01"
        data-testid="kyc-banner-verified"
        className="w-full max-w-md mx-auto bg-green-50 border border-green-200 rounded-2xl p-4 my-3 flex items-center space-x-3 shadow-sm"
      >
        <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center text-green-700 text-xl font-bold flex-shrink-0">
          ✓
        </div>
        <div>
          <h4 className="text-sm font-bold text-green-900">ผ่านการยืนยันตัวตนแล้ว (KYC Verified)</h4>
          <p className="text-xs text-green-700">คุณมีสิทธิ์กดรับงานในเส้นทางและระบบซื้อขายได้ตามปกติ</p>
        </div>
      </div>
    );
  }

  if (kycStatus === 'PENDING_REVIEW') {
    return (
      <div
        data-req="D-00-01"
        data-testid="kyc-banner-pending"
        className="w-full max-w-md mx-auto bg-amber-50 border border-amber-200 rounded-2xl p-4 my-3 shadow-sm"
      >
        <div className="flex items-start space-x-3">
          <div className="w-10 h-10 rounded-full bg-amber-100 flex items-center justify-center text-amber-700 text-xl font-bold flex-shrink-0">
            ⏳
          </div>
          <div className="flex-1">
            <h4 className="text-sm font-bold text-amber-900">เอกสารอยู่ระหว่างการตรวจสอบ (Pending Review)</h4>
            <p className="text-xs text-amber-700 mt-0.5">
              เจ้าหน้าที่จะตรวจสอบข้อมูลบัตรประชาชนและอนุมัติภายใน 24 ชม. ในระหว่างนี้คุณสามารถดูแผนที่ได้ แต่ยังไม่สามารถกดรับงานได้
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (kycStatus === 'REJECTED') {
    return (
      <div
        data-req="D-00-01"
        data-testid="kyc-banner-rejected"
        className="w-full max-w-md mx-auto bg-red-50 border border-red-200 rounded-2xl p-4 my-3 shadow-sm"
      >
        <div className="flex items-start space-x-3">
          <div className="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center text-red-700 text-xl font-bold flex-shrink-0">
            ✕
          </div>
          <div className="flex-1">
            <h4 className="text-sm font-bold text-red-900">เอกสารไม่ผ่านการอนุมัติ (KYC Rejected)</h4>
            <p className="text-xs text-red-700 mt-1">
              <strong>เหตุผล: </strong>
              {profile.rejection_reason || 'รูปถ่ายเอกสารไม่ชัดเจนหรือไม่ตรงตามเงื่อนไข'}
            </p>
            <button
              type="button"
              data-testid="retry-kyc-btn"
              onClick={onOpenKycModal}
              className="mt-3 w-full min-h-[48px] bg-red-600 hover:bg-red-700 text-white font-medium rounded-xl text-sm transition flex items-center justify-center space-x-1.5 shadow-sm"
            >
              <span>📷</span>
              <span>แก้ไขและส่งเอกสารใหม่อีกครั้ง</span>
            </button>
          </div>
        </div>
      </div>
    );
  }

  // สถานะเริ่มต้น: UNVERIFIED
  return (
    <div
      data-req="D-00-01"
      data-testid="kyc-banner-unverified"
      className="w-full max-w-md mx-auto bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 rounded-2xl p-4 my-3 shadow-sm"
    >
      <div className="flex items-start space-x-3">
        <div className="w-10 h-10 rounded-full bg-amber-100 flex items-center justify-center text-amber-800 text-xl font-bold flex-shrink-0">
          ⚠️
        </div>
        <div className="flex-1">
          <h4 className="text-sm font-bold text-amber-900">ยังไม่ได้ยืนยันตัวตน (Unverified)</h4>
          <p className="text-xs text-amber-800 mt-1">
            ตามกฎความปลอดภัย <strong>D-00-01</strong> ซาเล้งต้องผ่านการยืนยันตัวตนด้วยบัตรประชาชนก่อน จึงจะสามารถกดรับงานจากผู้ขายได้
          </p>
          <button
            type="button"
            data-testid="start-kyc-btn"
            onClick={onOpenKycModal}
            className="mt-3 w-full min-h-[48px] bg-emerald-600 hover:bg-emerald-700 text-white font-medium rounded-xl text-sm transition flex items-center justify-center space-x-1.5 shadow-sm"
          >
            <span>🪪</span>
            <span>ยืนยันตัวตนด้วยบัตรประชาชนทันที</span>
          </button>
        </div>
      </div>
    </div>
  );
}

