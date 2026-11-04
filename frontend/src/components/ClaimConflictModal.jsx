/**
 * โมดอลแจ้งเตือนกรณีมีผู้รับงานตัดหน้า (ClaimConflictModal)
 * แสดงเมื่อเกิด HTTP 409 Conflict จากระบบ Optimistic Concurrency Control
 * รองรับ BR-02, REQ-BR-002, CC-04, REQ-UX-001, AC-B04-01, D-B04-01
 */

import React from 'react';

export default function ClaimConflictModal({
  isOpen,
  message = 'มีผู้รับงานนี้แล้ว',
  onAcknowledge,
}) {
  if (!isOpen) return null;

  return (
    <div
      data-testid="claim-conflict-modal"
      data-req="REQ-BR-002"
      data-br="BR-02"
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-xs"
    >
      <div className="w-full max-w-sm bg-white rounded-3xl shadow-2xl border border-slate-100 p-6 text-center space-y-4 animate-in fade-in zoom-in-95 duration-200">
        <div className="w-16 h-16 mx-auto bg-amber-100 text-amber-600 rounded-full flex items-center justify-center text-3xl shadow-inner">
          ⏳
        </div>

        <div className="space-y-1">
          <h3 className="text-lg font-bold text-slate-800">
            ขออภัย! งานนี้ถูกรับไปแล้ว
          </h3>
          <p
            data-testid="conflict-message-text"
            className="text-sm text-slate-600"
          >
            {message}
          </p>
          <p className="text-xs text-slate-400">
            ระบบทำงานแบบ Single Collector Atomic Claim จึงให้สิทธิ์แก่ผู้ที่กดยืนยันก่อน
          </p>
        </div>

        <button
          type="button"
          data-testid="acknowledge-conflict-btn"
          onClick={onAcknowledge}
          className="w-full min-h-[48px] px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-sm rounded-xl transition-colors shadow-sm"
        >
          รับทราบและดูงานอื่น
        </button>
      </div>
    </div>
  );
}

