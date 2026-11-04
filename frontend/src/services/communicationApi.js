/**
 * Frontend API Client สำหรับระบบสื่อสาร (In-App Chat & Quick Call)
 * รองรับ UC-08, REQ-UX-001, REQ-SEC-001, REQ-SEC-002, CC-01, CC-05, REQ-OP-001, AC-B05-01..06, D-B05-01..06
 */

const API_BASE = '/api/v1/collectors/chat';
const CHAT_CACHE_PREFIX = 'saleng_chat_cache_';

export const DEFAULT_QUICK_REPLIES = [
  { id: 'qr-01', text: 'กำลังเดินทางไปครับ', emoji: '🚚' },
  { id: 'qr-02', text: 'ถึงหน้าบ้านแล้วครับ', emoji: '📍' },
  { id: 'qr-03', text: 'ช่วยออกมารับหน่อยครับ', emoji: '🚪' },
  { id: 'qr-04', text: 'ขอเลื่อนเวลาประมาณ 15 นาทีครับ', emoji: '⏰' },
];

export const communicationApi = {
  /**
   * ดึงรายการข้อความด่วนสำเร็จรูป 4 ข้อความมาตรฐาน (AC-B05-02, D-B05-03)
   */
  async getQuickReplies() {
    const isOnline = typeof navigator !== 'undefined' ? (navigator.onLine !== false) : true;
    if (!isOnline) {
      return { quick_replies: DEFAULT_QUICK_REPLIES };
    }

    try {
      const res = await fetch(`${API_BASE}/quick-replies`);
      if (res.ok) {
        return await res.json();
      }
      return { quick_replies: DEFAULT_QUICK_REPLIES };
    } catch {
      return { quick_replies: DEFAULT_QUICK_REPLIES };
    }
  },

  /**
   * ดึงประวัติข้อความแชตและสถานะห้องแชต (AC-B05-01, AC-B05-06, CC-05, REQ-OP-001)
   */
  async getMessages(orderId, salengId = 'saleng-01') {
    const isOnline = typeof navigator !== 'undefined' ? (navigator.onLine !== false) : true;

    // ถ้าออฟไลน์ ให้ดึงจากแคชใน localStorage ทันที
    if (!isOnline) {
      return this.getCachedMessages(orderId);
    }

    try {
      const res = await fetch(`${API_BASE}/${encodeURIComponent(orderId)}/messages?saleng_id=${encodeURIComponent(salengId)}`);
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        const error = new Error(err.detail || 'ไม่สามารถดึงข้อมูลแชตได้');
        error.status = res.status;
        throw error;
      }

      const data = await res.json();
      // บันทึกลงแคชใน localStorage
      this.cacheMessages(orderId, data);
      return { ...data, from_cache: false, is_offline: false };
    } catch (err) {
      // หากเกิดข้อผิดพลาดในการเชื่อมต่อเครือข่าย ให้ fallback อ่านจากแคช
      if (typeof localStorage !== 'undefined') {
        const cached = this.getCachedMessages(orderId);
        if (cached) return cached;
      }
      throw err;
    }
  },

  /**
   * ส่งข้อความแชตใหม่ (ข้อความอิสระ หรือ Quick Reply) (AC-B05-01, AC-B05-02)
   */
  async sendMessage(orderId, { salengId = 'saleng-01', messageText, isQuickReply = false } = {}) {
    const isOnline = typeof navigator !== 'undefined' ? (navigator.onLine !== false) : true;
    if (!isOnline) {
      const offlineError = new Error('ไม่สามารถส่งข้อความได้ขณะออฟไลน์ กรุณาเชื่อมต่ออินเทอร์เน็ต');
      offlineError.status = 503;
      throw offlineError;
    }

    const res = await fetch(`${API_BASE}/${encodeURIComponent(orderId)}/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        saleng_id: salengId,
        message_text: messageText,
        is_quick_reply: Boolean(isQuickReply),
      }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      const error = new Error(err.detail || 'ส่งข้อความไม่สำเร็จ');
      error.status = res.status;
      throw error;
    }

    const data = await res.json();

    // อัปเดตแคชใน localStorage หากมีอยู่
    this.appendMessageToCache(orderId, data.message);

    return data;
  },

  /**
   * ส่งข้อความด่วนสำเร็จรูป Quick Reply (AC-B05-02)
   */
  async sendQuickReply(orderId, salengId, text) {
    return this.sendMessage(orderId, {
      salengId,
      messageText: text,
      isQuickReply: true,
    });
  },

  /**
   * บันทึก Audit Log การกดโทรด่วน Native Phone Dialer (AC-B05-03, REQ-SEC-001)
   */
  async logCall(orderId, salengId = 'saleng-01', dialedPhone) {
    const res = await fetch(`${API_BASE}/${encodeURIComponent(orderId)}/call-log`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        saleng_id: salengId,
        dialed_phone: dialedPhone,
      }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      const error = new Error(err.detail || 'บันทึกประวัติการโทรไม่สำเร็จ');
      error.status = res.status;
      throw error;
    }

    return await res.json();
  },

  /**
   * บันทึกแคชข้อความลงใน localStorage (CC-05, REQ-OP-001, D-B05-06)
   */
  cacheMessages(orderId, data) {
    if (typeof localStorage === 'undefined') return;
    try {
      localStorage.setItem(`${CHAT_CACHE_PREFIX}${orderId}`, JSON.stringify(data));
    } catch (e) {
      console.warn('Failed to cache chat messages:', e);
    }
  },

  /**
   * อ่านแคชข้อความจาก localStorage (CC-05, REQ-OP-001, D-B05-06)
   */
  getCachedMessages(orderId) {
    if (typeof localStorage === 'undefined') return null;
    const raw = localStorage.getItem(`${CHAT_CACHE_PREFIX}${orderId}`);
    if (!raw) return null;
    try {
      const parsed = JSON.parse(raw);
      return {
        ...parsed,
        from_cache: true,
        is_offline: true,
      };
    } catch {
      return null;
    }
  },

  /**
   * แนบข้อความใหม่เข้ากับแคชในเครื่อง
   */
  appendMessageToCache(orderId, message) {
    if (typeof localStorage === 'undefined' || !message) return;
    try {
      const cached = this.getCachedMessages(orderId);
      if (cached && Array.isArray(cached.messages)) {
        cached.messages.push(message);
        localStorage.setItem(`${CHAT_CACHE_PREFIX}${orderId}`, JSON.stringify(cached));
      }
    } catch (e) {
      console.warn('Failed to append to chat cache:', e);
    }
  },

  /**
   * ล้างแคชข้อความ
   */
  clearChatCache(orderId) {
    if (typeof localStorage === 'undefined') return;
    if (orderId) {
      localStorage.removeItem(`${CHAT_CACHE_PREFIX}${orderId}`);
    }
  },
};
