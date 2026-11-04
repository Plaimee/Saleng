/**
 * โมดอลสละสิทธิ์/ยกเลิกงานสำหรับซาเล้ง (CollectorCancelModal)
 * ให้เลือกเหตุผล (รถเสีย/อุบัติเหตุ/ฉุกเฉิน) และคืนสถานะคำขอกลับเป็น S2 (Pending)
 * รองรับ UC-12, MD-STM-04, REQ-UX-001, CC-01, AC-B04-06, D-B04-04
 */

import React, { useState } from 'react';

const CANCEL_REASONS = [
  { id: 'VEHICLE_BREAKDOWN', label: '🛠️ รถเสีย / ยางรั่ว / เครื่องยนต์ขัดข้อง' },
  { id: 'ACCIDENT', label: '🚨 เกิดอุบัติเหตุระหว่างทาง' },
  { id: 'PERSONAL_EMERGENCY', label: '🏥 เหตุฉุกเฉินส่วนตัว / สุขภาพกะทันหัน' },
  { id: 'OTHER', label: '📝 อื่นๆ (โปรดระบุรายละเอียด)' },
];

export default function CollectorCancelModal({
  isOpen,
  job,
  onClose,
  onConfirm,
  isSubmitting = false,
}) {
  const [selectedReason, setSelectedReason] = useState('VEHICLE_BREAKDOWN');
  const [note, setNote] = useState('');

  if (!isOpen || !job) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (onConfirm) {
      onConfirm(job.order_id, { reason: selectedReason, note });
    }
  };

  return (
    <div
      data-testid="collector-cancel-modal"
      data-req="UC-12"
      data-stm="MD-STM-04"
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-xs"
    >
      <div className="w-full max-w-md bg-white rounded-3xl shadow-2xl border border-slate-100 overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="bg-rose-50 border-b border-rose-100 p-4">
          <div className="flex items-center space-x-2 text-rose-800">
            <span className="text-xl">⚠️</span>
            <h3 className="font-bold text-base">สละสิทธิ์ / ยกเลิกการรับงาน</h3>
          </div>
          <p className="text-xs text-rose-700 mt-1">
            คำขอนี้จะถูกคืนกลับเป็น <strong>"รอผู้รับงาน (S2)"</strong> อัตโนมัติเพื่อให้ซาเล้งท่านอื่นรับต่อ
          </p>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          <div>
            <div className="text-xs font-semibold text-slate-700 mb-2">
              โปรดระบุสาเหตุที่ต้องสละสิทธิ์งานนี้:
            </div>
            <div className="space-y-2">
              {CANCEL_REASONS.map((r) => (
                <label
                  key={r.id}
                  className={`flex items-center space-x-3 p-3 rounded-xl border cursor-pointer min-h-[48px] transition-colors ${
                    selectedReason === r.id
                      ? 'bg-rose-50/60 border-rose-300 text-rose-950 font-medium'
                      : 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100'
                  }`}
                >
                  <input
                    type="radio"
                    name="cancel_reason"
                    value={r.id}
                    checked={selectedReason === r.id}
                    onChange={(e) => setSelectedReason(e.target.value)}
                    className="w-4 h-4 text-rose-600 focus:ring-rose-500"
                  />
                  <span className="text-sm">{r.label}</span>
                </label>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              หมายเหตุเพิ่มเติม (ถ้ามี):
            </label>
            <textarea
              rows={2}
              value={note}
              onChange={(e) => setNote(e.target.value)}
              placeholder="เช่น ยางหลังรั่วบริเวณถนนรัชดาภิเษก ไม่สามารถเดินทางต่อได้"
              className="w-full text-sm p-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-rose-400"
            />
          </div>

          {/* Action Buttons (REQ-UX-001: Touch target >= 48px) */}
          <div className="flex gap-2 pt-2 border-t border-slate-100">
            <button
              type="button"
              data-testid="close-cancel-modal-btn"
              onClick={onClose}
              disabled={isSubmitting}
              className="flex-1 min-h-[48px] px-4 py-2.5 rounded-xl border border-slate-300 text-slate-700 font-semibold text-sm hover:bg-slate-50 transition-colors"
            >
              ย้อนกลับ
            </button>
            <button
              type="submit"
              data-testid="confirm-cancel-job-btn"
              disabled={isSubmitting}
              className="flex-1 min-h-[48px] px-4 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-semibold text-sm transition-colors shadow-sm"
            >
              {isSubmitting ? 'กำลังยกเลิก...' : 'ยืนยันสละสิทธิ์'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

