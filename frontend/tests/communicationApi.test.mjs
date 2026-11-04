/**
 * Unit Tests สำหรับ Frontend API Client: communicationApi
 * (T-06: CC-01, CC-05, REQ-OP-001, AC-B05-01..06, D-B05-01..06)
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { communicationApi, DEFAULT_QUICK_REPLIES } from '../src/services/communicationApi.js';

describe('communicationApi Client & Offline Cache Unit Tests (CC-01, CC-05, REQ-OP-001)', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
    Object.defineProperty(navigator, 'onLine', {
      value: true,
      configurable: true,
      writable: true,
    });
  });

  afterEach(() => {
    localStorage.clear();
  });

  describe('getQuickReplies', () => {
    it('fetches quick replies from server when online', async () => {
      const mockResponse = {
        quick_replies: DEFAULT_QUICK_REPLIES,
      };

      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const res = await communicationApi.getQuickReplies();
      expect(res.quick_replies).toHaveLength(4);
      expect(res.quick_replies[0].emoji).toBe('🚚');
    });

    it('returns default quick replies when offline or server error occurs', async () => {
      Object.defineProperty(navigator, 'onLine', { value: false });

      const res = await communicationApi.getQuickReplies();
      expect(res.quick_replies).toHaveLength(4);
      expect(res.quick_replies[1].text).toBe('ถึงหน้าบ้านแล้วครับ');
    });
  });

  describe('getMessages & Offline Cache (CC-05, AC-B05-01, AC-B05-06)', () => {
    it('fetches messages online and stores them into localStorage cache', async () => {
      const mockChatRoom = {
        order_id: 'order-101',
        order_status: 'S3',
        is_read_only: false,
        read_only_reason: null,
        seller_info: {
          seller_id: 'seller-01',
          display_name: 'คุณวิภาดา',
          phone: '081-234-5678',
          phone_masked: false,
        },
        messages: [
          {
            message_id: 'msg-01',
            order_id: 'order-101',
            sender_id: 'saleng-01',
            sender_role: 'COLLECTOR',
            message_text: 'กำลังเดินทางไปครับ',
            is_quick_reply: true,
            sent_at: '2026-11-04T10:00:00Z',
          },
        ],
      };

      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => mockChatRoom,
      });

      const res = await communicationApi.getMessages('order-101', 'saleng-01');
      expect(res.order_id).toBe('order-101');
      expect(res.from_cache).toBe(false);
      expect(res.is_offline).toBe(false);

      // ตรวจสอบว่ามีข้อมูลใน localStorage
      const cached = JSON.parse(localStorage.getItem('saleng_chat_cache_order-101'));
      expect(cached).toBeDefined();
      expect(cached.messages).toHaveLength(1);
    });

    it('retrieves messages from localStorage cache when offline (AC-B05-06)', async () => {
      const cachedData = {
        order_id: 'order-101',
        order_status: 'S3',
        is_read_only: false,
        seller_info: {
          display_name: 'คุณวิภาดา',
          phone: '081-234-5678',
        },
        messages: [
          {
            message_id: 'msg-01',
            message_text: 'ของพร้อมไหมครับ',
          },
        ],
      };
      localStorage.setItem('saleng_chat_cache_order-101', JSON.stringify(cachedData));

      // กำหนดให้ออฟไลน์
      Object.defineProperty(navigator, 'onLine', { value: false });

      const res = await communicationApi.getMessages('order-101', 'saleng-01');
      expect(res.from_cache).toBe(true);
      expect(res.is_offline).toBe(true);
      expect(res.messages[0].message_text).toBe('ของพร้อมไหมครับ');
    });
  });

  describe('sendMessage & sendQuickReply (AC-B05-01, AC-B05-02)', () => {
    it('sends message successfully when online and appends to local cache', async () => {
      // เตรียมแคชเดิม
      localStorage.setItem(
        'saleng_chat_cache_order-202',
        JSON.stringify({
          order_id: 'order-202',
          messages: [],
        })
      );

      const mockSent = {
        status: 'success',
        message: {
          message_id: 'msg-99',
          order_id: 'order-202',
          sender_id: 'saleng-01',
          sender_role: 'COLLECTOR',
          message_text: 'ถึงหน้าบ้านแล้วครับ',
          is_quick_reply: true,
          sent_at: '2026-11-04T10:15:00Z',
        },
      };

      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 201,
        json: async () => mockSent,
      });

      const res = await communicationApi.sendQuickReply(
        'order-202',
        'saleng-01',
        'ถึงหน้าบ้านแล้วครับ'
      );
      expect(res.status).toBe('success');
      expect(res.message.message_text).toBe('ถึงหน้าบ้านแล้วครับ');

      // ตรวจสอบว่าแคชถูกอัปเดต
      const updatedCache = JSON.parse(localStorage.getItem('saleng_chat_cache_order-202'));
      expect(updatedCache.messages).toHaveLength(1);
      expect(updatedCache.messages[0].message_id).toBe('msg-99');
    });

    it('throws error when trying to send message offline', async () => {
      Object.defineProperty(navigator, 'onLine', { value: false });

      await expect(
        communicationApi.sendMessage('order-202', {
          salengId: 'saleng-01',
          messageText: 'สวัสดีครับ',
        })
      ).rejects.toThrow('ไม่สามารถส่งข้อความได้ขณะออฟไลน์');
    });
  });

  describe('logCall (AC-B05-03, REQ-SEC-001)', () => {
    it('calls POST /call-log successfully', async () => {
      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({
          status: 'logged',
          action: 'COLLECTOR_INITIATED_CALL',
          order_id: 'order-303',
          saleng_id: 'saleng-01',
        }),
      });

      const res = await communicationApi.logCall('order-303', 'saleng-01', '081-234-5678');
      expect(res.status).toBe('logged');
      expect(res.action).toBe('COLLECTOR_INITIATED_CALL');
      expect(globalThis.fetch).toHaveBeenCalledWith(
        '/api/v1/collectors/chat/order-303/call-log',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            saleng_id: 'saleng-01',
            dialed_phone: '081-234-5678',
          }),
        })
      );
    });
  });
});

