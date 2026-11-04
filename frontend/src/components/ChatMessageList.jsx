import React, { useEffect, useRef } from 'react';

/**
 * ChatMessageList Component
 * รายการข้อความแชต แยกกล่องข้อความฝั่งซาเล้ง (ขวา เขียวมรกต) และผู้ขาย (ซ้าย เทาอ่อน)
 * รองรับ AC-B05-01, AC-B05-02, D-B05-04
 */
export default function ChatMessageList({ messages = [], currentUserId = 'saleng-01' }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    if (bottomRef.current && typeof bottomRef.current.scrollIntoView === 'function') {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const formatTime = (isoString) => {
    if (!isoString) return '';
    try {
      const date = new Date(isoString);
      return date.toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' });
    } catch {
      return '';
    }
  };

  if (!messages || messages.length === 0) {
    return (
      <div
        data-testid="chat-message-list-empty"
        className="flex-1 flex flex-col items-center justify-center p-6 text-slate-400 text-sm text-center"
      >
        <span className="text-4xl mb-2">💬</span>
        <p>ยังไม่มีข้อความสนทนา</p>
        <p className="text-xs text-slate-400 mt-1">เริ่มพิมพ์ข้อความหรือเลือกข้อความด่วนด้านล่างได้เลย</p>
      </div>
    );
  }

  return (
    <div
      data-testid="chat-message-list"
      className="flex-1 overflow-y-auto p-4 space-y-3 bg-slate-50"
    >
      {messages.map((msg, idx) => {
        const isMe = msg.sender_role === 'COLLECTOR' || msg.sender_id === currentUserId;

        return (
          <div
            key={msg.message_id || idx}
            data-testid="chat-message-item"
            className={`flex flex-col ${isMe ? 'items-end' : 'items-start'}`}
          >
            <div
              className={`max-w-[82%] px-3.5 py-2.5 rounded-2xl text-sm leading-relaxed shadow-sm ${
                isMe
                  ? 'bg-emerald-600 text-white rounded-tr-none'
                  : 'bg-white text-slate-800 border border-slate-200 rounded-tl-none'
              }`}
            >
              {msg.is_quick_reply && (
                <div
                  data-testid="quick-reply-badge"
                  className={`text-[11px] font-semibold mb-1 flex items-center gap-1 ${
                    isMe ? 'text-emerald-100' : 'text-emerald-700'
                  }`}
                >
                  <span>⚡ ส่งด่วน</span>
                </div>
              )}
              <p className="whitespace-pre-wrap break-words">{msg.message_text}</p>
            </div>
            <span className="text-[10px] text-slate-400 mt-1 px-1">
              {formatTime(msg.sent_at)}
            </span>
          </div>
        );
      })}
      <div ref={bottomRef} />
    </div>
  );
}
