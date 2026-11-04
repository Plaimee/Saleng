import React from 'react';

/**
 * QuickRepliesBar Component
 * แถบปุ่มลัดข้อความด่วน 4 ข้อความมาตรฐาน (เลื่อนแนวนอน)
 * รองรับ Digital Literacy ของซาเล้งผู้สูงอายุ ขับขี่ปลอดภัย
 * ขนาดปุ่มทัชทาร์เก็ต >= 48px ตาม REQ-UX-001, CC-01, AC-B05-02, D-B05-03
 */
export default function QuickRepliesBar({
  quickReplies = [],
  onSelectQuickReply,
  disabled = false,
}) {
  if (!quickReplies || quickReplies.length === 0) return null;

  return (
    <div
      data-testid="quick-replies-bar"
      className="bg-white border-t border-slate-100 px-3 py-2 overflow-x-auto scrollbar-none flex items-center gap-2"
    >
      <span className="text-xs font-semibold text-slate-400 whitespace-nowrap pl-1">
        ด่วน:
      </span>
      {quickReplies.map((qr) => (
        <button
          key={qr.id}
          type="button"
          disabled={disabled}
          onClick={() => onSelectQuickReply && onSelectQuickReply(qr.text)}
          data-testid="quick-reply-btn"
          data-qr-id={qr.id}
          className={`min-h-[48px] px-3.5 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap flex items-center gap-1.5 border transition-all ${
            disabled
              ? 'bg-slate-100 text-slate-400 border-slate-200 cursor-not-allowed opacity-60'
              : 'bg-emerald-50 text-emerald-800 border-emerald-200 hover:bg-emerald-100 active:scale-95 shadow-sm'
          }`}
        >
          <span className="text-sm">{qr.emoji}</span>
          <span>{qr.text}</span>
        </button>
      ))}
    </div>
  );
}

