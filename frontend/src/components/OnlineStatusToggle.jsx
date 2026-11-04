/**
 * คอมโพเนนต์สลับสถานะ Online / Offline ของซาเล้ง (OnlineStatusToggle)
 * ปุ่มกดขนาดใหญ่ไม่น้อยกว่า 48px ตาม REQ-UX-001 และ CC-01
 * รองรับ CC-02, AC-B03-03, D-B03-05
 */

import React from 'react';

export default function OnlineStatusToggle({
  isOnline = true,
  onToggle,
  isLoading = false,
}) {
  return (
    <div
      data-testid="online-status-container"
      data-req="CC-02"
      className="flex flex-col gap-1.5"
    >
      <div className="flex items-center justify-between">
        <span
          data-testid="online-status-label"
          className="text-xs font-semibold text-slate-700 flex items-center gap-1.5"
        >
          <span
            className={`w-2.5 h-2.5 rounded-full inline-block ${
              isOnline ? 'bg-emerald-500 animate-pulse' : 'bg-slate-400'
            }`}
          />
          {isOnline ? 'สถานะ: พร้อมรับงาน (Online)' : 'สถานะ: พักรับงาน (Offline)'}
        </span>

        {/* ปุ่มสวิตช์ขนาด touch target >= 48px */}
        <button
          type="button"
          role="switch"
          aria-checked={isOnline}
          data-testid="online-status-toggle"
          data-req="REQ-UX-001"
          disabled={isLoading}
          onClick={() => onToggle && onToggle(!isOnline)}
          style={{ minHeight: '48px', minWidth: '48px' }}
          className={`flex items-center px-4 py-2 rounded-full font-medium text-xs transition-colors shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 ${
            isOnline
              ? 'bg-emerald-600 text-white hover:bg-emerald-700 focus:ring-emerald-500'
              : 'bg-slate-200 text-slate-700 hover:bg-slate-300 focus:ring-slate-400'
          }`}
        >
          {isLoading ? (
            <span className="text-xs">กำลังบันทึก...</span>
          ) : isOnline ? (
            <span>🟢 ออนไลน์อยู่ (แตะเพื่อพัก)</span>
          ) : (
            <span>⚪ ออฟไลน์ (แตะเพื่อออนไลน์)</span>
          )}
        </button>
      </div>

      {/* ป้ายแจ้งเตือนเมื่ออยู่ในสถานะ Offline */}
      {!isOnline && (
        <div
          data-testid="offline-warning-badge"
          className="p-2 bg-amber-50 border border-amber-300 rounded-lg text-[11px] text-amber-800 flex items-center gap-1.5"
        >
          <span>⚠️</span>
          <span>ขณะนี้คุณปิดสถานะ Offline อยู่ จะไม่สามารถกดรับงานได้จนกว่าจะเปิดออนไลน์</span>
        </div>
      )}
    </div>
  );
}

