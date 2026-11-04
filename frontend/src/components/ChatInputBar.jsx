import React, { useState } from 'react';

/**
 * ChatInputBar Component
 * ช่องพิมพ์ข้อความอิสระและปุ่มส่งข้อความ (ทัชทาร์เก็ต >= 48px ตาม REQ-UX-001, CC-01)
 * ปิดการใช้งานอัตโนมัติเมื่อห้องแชตล็อกเป็น Read-only (S7/S8) หรือออฟไลน์ (AC-B05-01, AC-B05-05, AC-B05-06)
 */
export default function ChatInputBar({
  onSendMessage,
  disabled = false,
  isReadOnly = false,
  isOffline = false,
}) {
  const [text, setText] = useState('');

  const isDisabled = disabled || isReadOnly || isOffline;

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = text.trim();
    if (!trimmed || isDisabled) return;

    if (onSendMessage) {
      onSendMessage(trimmed);
      setText('');
    }
  };

  const getPlaceholder = () => {
    if (isReadOnly) return 'ห้องแชตถูกปิดเนื่องจากเสร็จสิ้นธุรกรรมแล้ว';
    if (isOffline) return 'โหมดออฟไลน์: ไม่สามารถส่งข้อความได้';
    return 'พิมพ์ข้อความถึงผู้ขาย...';
  };

  return (
    <form
      onSubmit={handleSubmit}
      data-testid="chat-input-bar"
      className="bg-white border-t border-slate-200 p-2.5 flex items-center gap-2"
    >
      <input
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        disabled={isDisabled}
        maxLength={500}
        placeholder={getPlaceholder()}
        data-testid="chat-input"
        className="flex-1 min-h-[48px] px-3.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 disabled:bg-slate-100 disabled:text-slate-400 disabled:cursor-not-allowed transition-all"
      />
      <button
        type="submit"
        disabled={isDisabled || !text.trim()}
        data-testid="send-message-btn"
        aria-label="ส่งข้อความ"
        className="min-h-[48px] min-w-[48px] px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-200 disabled:text-slate-400 disabled:cursor-not-allowed text-white font-semibold text-sm flex items-center justify-center shadow-sm active:scale-95 transition-all"
      >
        <span>ส่ง</span>
      </button>
    </form>
  );
}

