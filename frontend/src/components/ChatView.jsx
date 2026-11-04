import React, { useState, useEffect, useCallback } from 'react';
import { communicationApi, DEFAULT_QUICK_REPLIES } from '../services/communicationApi.js';
import ChatHeader from './ChatHeader.jsx';
import ChatMessageList from './ChatMessageList.jsx';
import QuickRepliesBar from './QuickRepliesBar.jsx';
import ChatInputBar from './ChatInputBar.jsx';
import ReadOnlyNoticeBanner from './ReadOnlyNoticeBanner.jsx';

/**
 * ChatView Component (Mobile-First SPA)
 * หน้ารวมระบบสื่อสารในแอป: แชตโดยตรง, ข้อความด่วน 4 รูปแบบ, โทรด่วน Native Dialer
 * รองรับ UC-08, REQ-UX-001, REQ-SEC-001, REQ-SEC-002, CC-01, CC-05, REQ-OP-001, AC-B05-01..06
 */
export default function ChatView({
  orderId = 'order-s2-01',
  salengId = 'saleng-01',
  onBack,
}) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [chatRoom, setChatRoom] = useState(null);
  const [quickReplies, setQuickReplies] = useState(DEFAULT_QUICK_REPLIES);
  const [isOffline, setIsOffline] = useState(
    typeof navigator !== 'undefined' ? (navigator.onLine === false) : false
  );
  const [sending, setSending] = useState(false);

  // ตรวจจับสถานะการเชื่อมต่ออินเทอร์เน็ต
  useEffect(() => {
    const handleOnline = () => setIsOffline(false);
    const handleOffline = () => setIsOffline(true);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // โหลดข้อมูลห้องแชตและข้อความด่วน
  const loadChatData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const [roomData, qrData] = await Promise.all([
        communicationApi.getMessages(orderId, salengId),
        communicationApi.getQuickReplies(),
      ]);

      setChatRoom(roomData);
      if (qrData?.quick_replies) {
        setQuickReplies(qrData.quick_replies);
      }
      if (roomData?.is_offline) {
        setIsOffline(true);
      }
    } catch (err) {
      setError(err.message || 'ไม่สามารถโหลดข้อมูลห้องแชตได้');
    } finally {
      setLoading(false);
    }
  }, [orderId, salengId]);

  useEffect(() => {
    loadChatData();
  }, [loadChatData]);

  // ส่งข้อความอิสระ
  const handleSendMessage = async (text) => {
    if (!text || sending) return;
    try {
      setSending(true);
      const res = await communicationApi.sendMessage(orderId, {
        salengId,
        messageText: text,
        isQuickReply: false,
      });

      if (res?.message) {
        setChatRoom((prev) => ({
          ...prev,
          messages: [...(prev?.messages || []), res.message],
        }));
      }
    } catch (err) {
      alert(err.message || 'ส่งข้อความไม่สำเร็จ');
    } finally {
      setSending(false);
    }
  };

  // ส่งข้อความด่วน Quick Reply
  const handleSelectQuickReply = async (text) => {
    if (!text || sending) return;
    try {
      setSending(true);
      const res = await communicationApi.sendQuickReply(orderId, salengId, text);

      if (res?.message) {
        setChatRoom((prev) => ({
          ...prev,
          messages: [...(prev?.messages || []), res.message],
        }));
      }
    } catch (err) {
      alert(err.message || 'ส่งข้อความด่วนไม่สำเร็จ');
    } finally {
      setSending(false);
    }
  };

  // กดโทรด่วน บันทึก Audit Log
  const handleCallClick = async (phone) => {
    try {
      await communicationApi.logCall(orderId, salengId, phone);
    } catch (err) {
      console.warn('บันทึกประวัติการโทรไม่สำเร็จ:', err);
    }
  };

  if (loading && !chatRoom) {
    return (
      <div
        data-req="UC-08"
        data-testid="chat-loading"
        className="max-w-md mx-auto min-h-screen bg-slate-50 flex flex-col items-center justify-center p-6 text-slate-500"
      >
        <div className="w-10 h-10 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mb-3" />
        <p className="text-sm font-medium">กำลังโหลดห้องแชต...</p>
      </div>
    );
  }

  if (error && !chatRoom) {
    return (
      <div
        data-req="UC-08"
        data-testid="chat-error"
        className="max-w-md mx-auto min-h-screen bg-slate-50 flex flex-col items-center justify-center p-6 text-center"
      >
        <span className="text-4xl mb-3">⚠️</span>
        <h2 className="text-base font-bold text-slate-800 mb-1">เกิดข้อผิดพลาด</h2>
        <p className="text-sm text-slate-500 mb-4">{error}</p>
        <button
          type="button"
          onClick={loadChatData}
          className="min-h-[48px] px-6 bg-emerald-600 text-white rounded-xl font-semibold text-sm shadow-sm"
        >
          ลองใหม่อีกครั้ง
        </button>
      </div>
    );
  }

  const isReadOnly = chatRoom?.is_read_only || false;
  const sellerInfo = chatRoom?.seller_info || {};

  return (
    <div
      data-req="UC-08"
      data-testid="chat-view"
      className="max-w-md mx-auto min-h-screen bg-white flex flex-col shadow-lg border-x border-slate-100"
    >
      {/* ส่วนหัวห้องแชต */}
      <ChatHeader
        orderId={orderId}
        orderStatus={chatRoom?.order_status}
        sellerName={sellerInfo.display_name}
        sellerPhone={sellerInfo.phone}
        phoneMasked={sellerInfo.phone_masked}
        onBack={onBack}
        onCallClick={handleCallClick}
      />

      {/* แบนเนอร์โหมดออฟไลน์ */}
      {isOffline && (
        <div
          data-testid="offline-chat-banner"
          className="bg-amber-500 text-white px-3 py-1.5 text-xs font-medium flex items-center justify-center gap-1.5"
        >
          <span>📡</span>
          <span>โหมดออฟไลน์: กำลังแสดงประวัติข้อความจากแคชในเครื่อง</span>
        </div>
      )}

      {/* แบนเนอร์ล็อกห้องแชต Read-only (S7/S8) */}
      {isReadOnly && (
        <ReadOnlyNoticeBanner reason={chatRoom?.read_only_reason} />
      )}

      {/* ฟีดข้อความสนทนา */}
      <ChatMessageList
        messages={chatRoom?.messages || []}
        currentUserId={salengId}
      />

      {/* แถบปุ่มลัดข้อความด่วน 4 ข้อความมาตรฐาน (ซ่อนหรือปิดเมื่อ Read-only) */}
      {!isReadOnly && (
        <QuickRepliesBar
          quickReplies={quickReplies}
          onSelectQuickReply={handleSelectQuickReply}
          disabled={isOffline || sending}
        />
      )}

      {/* ช่องพิมพ์ข้อความและปุ่มส่ง */}
      <ChatInputBar
        onSendMessage={handleSendMessage}
        disabled={sending}
        isReadOnly={isReadOnly}
        isOffline={isOffline}
      />
    </div>
  );
}

