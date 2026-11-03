/**
 * ป๊อปอัปให้ผู้ขายเลือกเหตุผลและกดยืนยันการยกเลิกนัดหมาย (CancelBookingModal)
 * รองรับ UC-04, BR-03, REQ-FN-003, REQ-SEC-001, AC-S05-03, AC-S05-05, P-03
 */

import React, { useState } from 'react';

const PRESET_REASONS = [
  'ติดธุระด่วน ไม่สะดวกอยู่บ้านในเวลาดังกล่าว',
  'ต้องการเปลี่ยนวันหรือช่วงเวลาใหม่',
  'ขายหรือจัดการขยะรีไซเคิลไปแล้ว',
  'ระบุข้อมูลประเภท/ปริมาณของเก่าผิดพลาด',
];

export default function CancelBookingModal({
  isOpen = false,
  onClose = () => {},
  onConfirmCancel = () => {},
  loading = false,
}) {
  const [selectedReason, setSelectedReason] = useState(PRESET_REASONS[0]);
  const [customReason, setCustomReason] = useState('');
  const [useCustom, setUseCustom] = useState(false);

  if (!isOpen) return null;

  const finalReason = useCustom ? customReason.trim() : selectedReason;

  const handleConfirm = () => {
    if (!finalReason) return;
    onConfirmCancel(finalReason);
  };

  return (
    <div
      data-req="UC-04"
      data-testid="cancel-modal"
      className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4 animate-in fade-in"
    >
      <div className="bg-white rounded-3xl max-w-sm w-full p-5 space-y-4 shadow-xl border border-gray-100">
        <div className="flex items-center justify-between pb-2 border-b border-gray-100">
          <div className="flex items-center gap-2">
            <span className="text-xl">⚠️</span>
            <h3 className="text-sm font-bold text-gray-900">ยืนยันการยกเลิกนัดหมาย</h3>
          </div>
          <button
            type="button"
            data-testid="btn-close-cancel-modal"
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-sm p-1"
          >
            ✕
          </button>
        </div>

        <p className="text-xs text-gray-600">
          กรุณาระบุเหตุผลการยกเลิก เพื่อให้ระบบบันทึก Audit Log และแจ้งให้ซาเล้งทราบ
        </p>

        {/* ตัวเลือกเหตุผลสำเร็จรูป */}
        <div className="space-y-2">
          {PRESET_REASONS.map((r, idx) => (
            <label
              key={idx}
              className={`flex items-start gap-2.5 p-2.5 rounded-xl border text-xs cursor-pointer transition-colors ${
                !useCustom && selectedReason === r
                  ? 'border-red-500 bg-red-50/50 text-red-900 font-medium'
                  : 'border-gray-200 hover:bg-gray-50 text-gray-700'
              }`}
            >
              <input
                type="radio"
                name="cancellation_reason"
                checked={!useCustom && selectedReason === r}
                onChange={() => {
                  setSelectedReason(r);
                  setUseCustom(false);
                }}
                className="mt-0.5 accent-red-600"
              />
              <span>{r}</span>
            </label>
          ))}

          <label
            className={`flex items-start gap-2.5 p-2.5 rounded-xl border text-xs cursor-pointer transition-colors ${
              useCustom
                ? 'border-red-500 bg-red-50/50 text-red-900 font-medium'
                : 'border-gray-200 hover:bg-gray-50 text-gray-700'
            }`}
          >
            <input
              type="radio"
              name="cancellation_reason"
              checked={useCustom}
              onChange={() => setUseCustom(true)}
              className="mt-0.5 accent-red-600"
            />
            <span>ระบุเหตุผลอื่นๆ</span>
          </label>
        </div>

        {useCustom && (
          <textarea
            data-testid="cancel-reason-input"
            rows={2}
            value={customReason}
            onChange={(e) => setCustomReason(e.target.value)}
            placeholder="พิมพ์เหตุผลที่ต้องการยกเลิก..."
            className="w-full text-xs p-2.5 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-400"
          />
        )}

        <div className="flex gap-2 pt-2">
          <button
            type="button"
            onClick={onClose}
            className="flex-1 py-2 rounded-xl text-xs font-semibold text-gray-600 bg-gray-100 hover:bg-gray-200 transition-colors"
          >
            ย้อนกลับ
          </button>
          <button
            type="button"
            data-testid="confirm-cancel-btn"
            disabled={loading || !finalReason}
            onClick={handleConfirm}
            className="flex-1 py-2 rounded-xl text-xs font-bold text-white bg-red-600 hover:bg-red-700 disabled:opacity-50 transition-colors"
          >
            {loading ? 'กำลังยกเลิก...' : 'ยืนยันยกเลิก'}
          </button>
        </div>
      </div>
    </div>
  );
}

