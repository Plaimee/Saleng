/**
 * Unit Tests สำหรับ Frontend API Client: billingReceiptApi
 * (T-06: UC-05, UC-06, UC-07, CC-01, CC-05, REQ-OP-001, D-B06-01..06)
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { billingReceiptApi, OFFLINE_QUEUE_KEY } from '../src/services/billingReceiptApi.js';

describe('billingReceiptApi Client & Offline Queue Unit Tests (CC-01, CC-05, REQ-OP-001)', () => {
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

  describe('getWeighingSheet', () => {
    it('fetches weighing sheet online and caches in localStorage', async () => {
      const mockSheet = {
        order_id: 'order-101',
        order_status: 'S4',
        seller_name: 'คุณวิภาดา',
        seller_phone_masked: '08X-XXX-4567',
        items: [
          {
            item_id: 'item-1',
            category_code: 'PAPER_BOX',
            category_name: 'กระดาษลัง',
            estimated_quantity: 30.0,
            locked_unit_price: 4.5,
          },
        ],
      };

      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => mockSheet,
      });

      const res = await billingReceiptApi.getWeighingSheet('order-101', 'saleng-01');
      expect(res.order_id).toBe('order-101');
      expect(res.items).toHaveLength(1);
      expect(res.items[0].locked_unit_price).toBe(4.5);
      expect(res.from_cache).toBe(false);

      // Check localStorage cache
      const cached = JSON.parse(localStorage.getItem('saleng_weighing_sheet_order-101'));
      expect(cached).toBeDefined();
      expect(cached.order_id).toBe('order-101');
    });

    it('returns cached sheet when offline', async () => {
      const mockSheet = {
        order_id: 'order-102',
        order_status: 'S4',
        seller_name: 'ยายสมศรี',
        seller_phone_masked: '08X-XXX-9999',
        items: [],
      };
      localStorage.setItem('saleng_weighing_sheet_order-102', JSON.stringify(mockSheet));

      Object.defineProperty(navigator, 'onLine', { value: false });

      const res = await billingReceiptApi.getWeighingSheet('order-102', 'saleng-01');
      expect(res.order_id).toBe('order-102');
      expect(res.from_cache).toBe(true);
      expect(res.is_offline).toBe(true);
    });
  });

  describe('submitWeighing & Offline Queue', () => {
    it('submits weighing online successfully', async () => {
      const mockResult = {
        status: 'success',
        order_id: 'order-101',
        new_status: 'S5',
        total_settled_amount: 135.0,
        is_re_quote: false,
        seller_confirmed_weight: false,
      };

      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => mockResult,
      });

      const res = await billingReceiptApi.submitWeighing('order-101', {
        salengId: 'saleng-01',
        scalePhotoUrl: 'https://storage.saleng.app/scale1.jpg',
        items: [{ item_id: 'item-1', actual_quantity: 30.0 }],
      });

      expect(res.status).toBe('success');
      expect(res.total_settled_amount).toBe(135.0);
    });

    it('queues weighing submission in localStorage when offline (REQ-OP-001, CC-05)', async () => {
      Object.defineProperty(navigator, 'onLine', { value: false });

      const res = await billingReceiptApi.submitWeighing('order-101', {
        salengId: 'saleng-01',
        scalePhotoUrl: 'https://storage.saleng.app/scale1.jpg',
        items: [{ item_id: 'item-1', actual_quantity: 30.0 }],
      });

      expect(res.status).toBe('queued');
      expect(res.is_offline).toBe(true);

      const queue = JSON.parse(localStorage.getItem(OFFLINE_QUEUE_KEY) || '[]');
      expect(queue).toHaveLength(1);
      expect(queue[0].order_id).toBe('order-101');
      expect(queue[0].payload.scale_photo_url).toBe('https://storage.saleng.app/scale1.jpg');
    });

    it('syncs offline queue when triggered online', async () => {
      // Seed queue
      const queueItem = {
        order_id: 'order-queue-1',
        payload: {
          saleng_id: 'saleng-01',
          scale_photo_url: 'https://storage.saleng.app/scale1.jpg',
          items: [{ item_id: 'item-1', actual_quantity: 20.0 }],
          idempotency_key: 'idemp-test-1',
        },
        queued_at: new Date().toISOString(),
      };
      localStorage.setItem(OFFLINE_QUEUE_KEY, JSON.stringify([queueItem]));

      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({ status: 'success' }),
      });

      const syncResult = await billingReceiptApi.syncOfflineWeighingQueue();
      expect(syncResult.syncedCount).toBe(1);
      expect(syncResult.failedCount).toBe(0);

      const remainingQueue = JSON.parse(localStorage.getItem(OFFLINE_QUEUE_KEY) || '[]');
      expect(remainingQueue).toHaveLength(0);
    });
  });

  describe('selectPaymentMethod', () => {
    it('submits payment method selection', async () => {
      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({
          status: 'success',
          order_id: 'order-101',
          payment_method: 'PROMPTPAY',
          order_status: 'S6',
        }),
      });

      const res = await billingReceiptApi.selectPaymentMethod('order-101', {
        salengId: 'saleng-01',
        paymentMethod: 'PROMPTPAY',
      });

      expect(res.status).toBe('success');
      expect(res.payment_method).toBe('PROMPTPAY');
    });

    it('throws error when server returns 403 (e.g. seller not confirmed weight)', async () => {
      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 403,
        json: async () => ({ detail: 'ผู้ขายยังไม่ได้ยืนยันผลการชั่งน้ำหนัก' }),
      });

      await expect(
        billingReceiptApi.selectPaymentMethod('order-101', {
          salengId: 'saleng-01',
          paymentMethod: 'CASH',
        })
      ).rejects.toThrow('ผู้ขายยังไม่ได้ยืนยันผลการชั่งน้ำหนัก');
    });
  });

  describe('getReceipt', () => {
    it('fetches digital receipt and caches in localStorage', async () => {
      const mockReceipt = {
        receipt_id: 'REC-20261104-0001',
        order_id: 'order-101',
        seller_name: 'คุณวิภาดา',
        seller_phone_masked: '08X-XXX-4567',
        collector_name: 'สมชาย ซาเล้ง',
        collector_phone_masked: '08X-XXX-8901',
        payment_method: 'CASH',
        total_settled_amount: 500.0,
        items: [],
      };

      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => mockReceipt,
      });

      const res = await billingReceiptApi.getReceipt('order-101', 'saleng-01');
      expect(res.receipt_id).toBe('REC-20261104-0001');
      expect(res.seller_phone_masked).toBe('08X-XXX-4567');

      const cached = JSON.parse(localStorage.getItem('saleng_receipt_order-101'));
      expect(cached).toBeDefined();
      expect(cached.receipt_id).toBe('REC-20261104-0001');
    });
  });
});

