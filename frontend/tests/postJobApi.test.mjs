/**
 * Unit Tests สำหรับ Frontend API Client: postJobApi
 * (Task T-05: UC-10, UC-13, CC-05, REQ-OP-001, D-B07-01..06)
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { postJobApi } from '../src/services/postJobApi.js';

describe('postJobApi Client & Offline Cache Unit Tests (CC-05, REQ-OP-001)', () => {
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

  describe('getPurchaseHistory', () => {
    it('fetches purchase history online and caches in localStorage', async () => {
      const mockHistory = {
        period: 'all',
        summary: {
          total_expense_baht: 850.0,
          total_weight_kg: 150.0,
          total_completed_jobs: 2,
        },
        items: [
          {
            order_id: 'order-101',
            seller_name: 'คุณวิภาดา',
            seller_phone_masked: '08X-XXX-4567',
            total_settled_amount: 500.0,
            status: 'S7',
          },
        ],
      };

      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => mockHistory,
      });

      const res = await postJobApi.getPurchaseHistory('saleng-01', 'all');
      expect(res.period).toBe('all');
      expect(res.summary.total_expense_baht).toBe(850.0);
      expect(res.items).toHaveLength(1);
      expect(res.from_cache).toBe(false);

      // Verify localStorage cache
      const cached = JSON.parse(localStorage.getItem('saleng_purchase_history_cache_all'));
      expect(cached).toBeDefined();
      expect(cached.summary.total_expense_baht).toBe(850.0);
    });

    it('returns cached history when offline', async () => {
      const mockCached = {
        period: 'today',
        summary: { total_expense_baht: 300.0, total_weight_kg: 50.0, total_completed_jobs: 1 },
        items: [],
      };
      localStorage.setItem('saleng_purchase_history_cache_today', JSON.stringify(mockCached));

      Object.defineProperty(navigator, 'onLine', { value: false });

      const res = await postJobApi.getPurchaseHistory('saleng-01', 'today');
      expect(res.from_cache).toBe(true);
      expect(res.is_offline).toBe(true);
      expect(res.summary.total_expense_baht).toBe(300.0);
    });
  });

  describe('regular customers management', () => {
    it('fetches regular customers list', async () => {
      const mockList = [
        {
          id: 'fav-1',
          seller_id: 'seller-01',
          seller_name: 'คุณสมศรี',
          notes: 'บ้านรั้วสีฟ้า',
        },
      ];

      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => mockList,
      });

      const res = await postJobApi.getRegularCustomers('saleng-01');
      expect(res).toHaveLength(1);
      expect(res[0].notes).toBe('บ้านรั้วสีฟ้า');
    });

    it('toggles regular customer bookmark', async () => {
      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({
          status: 'success',
          seller_id: 'seller-01',
          is_favorite: true,
        }),
      });

      const res = await postJobApi.toggleRegularCustomer('saleng-01', {
        seller_id: 'seller-01',
        notes: 'สะดวกเสาร์-อาทิตย์',
      });
      expect(res.status).toBe('success');
      expect(res.is_favorite).toBe(true);
    });
  });

  describe('reportSellerMismatch', () => {
    it('submits mismatch dispute report', async () => {
      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({
          status: 'success',
          order_id: 'order-101',
          new_status: 'S8',
          dispute_id: 'DISP-20261104-0001',
        }),
      });

      const res = await postJobApi.reportSellerMismatch({
        saleng_id: 'saleng-01',
        order_id: 'order-101',
        mismatch_reason: 'SELLER_NO_SHOW',
        evidence_photo_url: 'https://storage.saleng.app/disp.jpg',
      });

      expect(res.status).toBe('success');
      expect(res.new_status).toBe('S8');
      expect(res.dispute_id).toBe('DISP-20261104-0001');
    });

    it('throws error when server responds with 400', async () => {
      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 400,
        json: async () => ({ detail: 'คำขอขายอยู่ในสถานะ S7 แล้ว' }),
      });

      await expect(
        postJobApi.reportSellerMismatch({
          saleng_id: 'saleng-01',
          order_id: 'order-101',
          mismatch_reason: 'OTHER',
          evidence_photo_url: 'https://storage.saleng.app/disp.jpg',
        })
      ).rejects.toThrow('คำขอขายอยู่ในสถานะ S7 แล้ว');
    });
  });
});

