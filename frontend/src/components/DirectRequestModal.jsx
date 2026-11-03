/**
 * ป๊อปอัปยืนยันการส่งคำขอนัดหมายเจาะจงบุคคล (DirectRequestModal)
 * รองรับ UC-03, REQ-SEC-001, MD-STM-04, AC-S03-05, P-05, Q-01
 */

import React, { useState } from 'react';

export default function DirectRequestModal({
  collector,
  isOpen,
  onClose,
  onConfirm,
  loading = false,
}) {
  const [notes, setNotes] = useState('');

  if (!isOpen || !collector) return null;

  const handleConfirm = () => {
    onConfirm(collector.saleng_id, notes);
  };

  return (
    <div
      data-req="UC-03"
      data-testid="direct-request-modal"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs animate-fade-in"
    >
      <div className="bg-white rounded-3xl max-w-sm w-full p-5 space-y-4 shadow-xl border border-gray-100">
        <div className="text-center space-y-1">
          <div className="w-14 h-14 rounded-full bg-emerald-100 mx-auto flex items-center justify-center text-2xl border-2 border-emerald-300">
            {collector.avatar_url ? (
              <img
                src={collector.avatar_url}
                alt={collector.display_name}
                className="w-full h-full object-cover rounded-full"
              />
            ) : (
              '👨‍🔧'
            )}
          </div>
          <h3 className="text-sm font-bold text-gray-800 pt-1">
            นัดหมาย {collector.display_name}
          </h3>
          <p className="text-[11px] text-gray-500">
            ★ {collector.rating.toFixed(1)} • {collector.vehicle_type === 'PICKUP_TRUCK' ? 'รถกระบะ' : 'ซาเล้ง'} • ห่าง {collector.distance_km.toFixed(1)} กม.
          </p>
        </div>

        {/* แถบแจ้งเตือนเงื่อนไข 15 นาที */}
        <div className="p-3 bg-amber-50 border border-amber-200 rounded-2xl text-[11px] text-amber-900 space-y-1">
          <div className="font-bold flex items-center gap-1">
            <span>⏱️</span>
            <span>เวลารอตอบรับ 15 นาที</span>
          </div>
          <p className="text-[10px] text-amber-700 leading-relaxed">
            ระบบจะส่งคำขอไปยังซาเล้งท่านนี้โดยตรง หากซาเล้งไม่ตอบรับภายใน 15 นาที คุณสามารถเลือกซาเล้งท่านใหม่ หรือเปิดประกาศงานทั่วไปได้
          </p>
        </div>

        {/* ช่องระบุข้อความเพิ่มเติม */}
        <div>
          <label className="block text-[11px] font-semibold text-gray-700 mb-1">
            ข้อความหรือเวลาที่สะดวก (ถ้ามี):
          </label>
          <textarea
            rows={2}
            data-testid="direct-request-notes"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="เช่น สะดวกช่วง 14:00 - 15:00 น. ครับ"
            className="w-full px-3 py-2 text-xs rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-emerald-500"
          />
        </div>

        {/* ปุ่มกดยืนยัน / ยกเลิก */}
        <div className="flex space-x-2 pt-1">
          <button
            type="button"
            data-testid="modal-cancel-btn"
            onClick={onClose}
            disabled={loading}
            className="flex-1 min-h-[44px] py-2 border border-gray-200 rounded-xl text-xs font-semibold text-gray-600 hover:bg-gray-50 transition-colors"
          >
            ยกเลิก
          </button>
          <button
            type="button"
            data-testid="modal-confirm-btn"
            onClick={handleConfirm}
            disabled={loading}
            className="flex-1 min-h-[44px] py-2 bg-emerald-600 text-white rounded-xl text-xs font-bold hover:bg-emerald-700 shadow-xs transition-all flex items-center justify-center gap-1"
          >
            {loading ? 'กำลังส่ง...' : 'ยืนยันเลือกซาเล้ง'}
          </button>
        </div>
      </div>
    </div>
  );
}

