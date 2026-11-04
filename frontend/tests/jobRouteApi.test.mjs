/**
 * Unit Tests สำหรับ Frontend API Client: jobRouteApi
 * (T-06: CC-01, CC-05, REQ-OP-001, AC-B04-01..07, D-B04-01..06)
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { jobRouteApi } from '../src/services/jobRouteApi.js';

describe('jobRouteApi Client & Offline Queue Unit Tests (CC-01, CC-05, REQ-OP-001)', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  afterEach(() => {
    localStorage.clear();
  });

  describe('claimJob (Single Collector Atomic Claim - BR-02, CC-04, AC-B04-01)', () => {
    it('claims job successfully and returns unmasked contact & navigation (AC-B04-01, AC-B04-03)', async () => {
      const mockSuccessResponse = {
        order_id: 'order-s2-01',
        collector_id: 'saleng-01',
        status: 'S3',
        version: 2,
        address_text: '123/45 ซอยรัชดาภิเษก 18 แขวงสามเสนนอก เขตห้วยขวาง กทม.',
        dest_lat: 13.7930,
        dest_lng: 100.5780,
        seller_phone: '081-999-8888',
        navigation_url: 'https://www.google.com/maps/dir/?api=1&destination=13.793000,100.578000&travelmode=driving',
        claimed_at: '2026-11-04T10:00:00Z',
      };

      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => mockSuccessResponse,
      });

      const result = await jobRouteApi.claimJob('order-s2-01', {
        saleng_id: 'saleng-01',
        expected_version: 1,
      });

      expect(result.status).toBe('S3');
      expect(result.collector_id).toBe('saleng-01');
      expect(result.address_text).toContain('123/45');
      expect(result.navigation_url).toContain('travelmode=driving');
      expect(globalThis.fetch).toHaveBeenCalledWith(
        '/api/v1/collectors/jobs/order-s2-01/claim',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ saleng_id: 'saleng-01', expected_version: 1 }),
        })
      );
    });

    it('throws 409 conflict error when another collector claims first (BR-02, CC-04, AC-B04-01)', async () => {
      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 409,
        json: async () => ({ detail: 'มีผู้รับงานนี้แล้ว' }),
      });

      await expect(
        jobRouteApi.claimJob('order-s2-01', { saleng_id: 'saleng-02', expected_version: 1 })
      ).rejects.toThrow('มีผู้รับงานนี้แล้ว');
    });

    it('throws generic error when server responds with 500', async () => {
      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        json: async () => ({ detail: 'Database error' }),
      });

      await expect(
        jobRouteApi.claimJob('order-s2-01')
      ).rejects.toThrow('Database error');
    });
  });

  describe('skipJob (Skip Job Option - Extension A2, AC-B04-02)', () => {
    it('skips job and confirms status remains S2 (AC-B04-02)', async () => {
      const mockSkipResponse = {
        order_id: 'order-s2-01',
        status: 'S2',
        message: 'ข้ามงานเรียบร้อยแล้ว คำขอยังคงสถานะรอผู้รับงาน',
        skipped_by: 'saleng-01',
      };

      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => mockSkipResponse,
      });

      const res = await jobRouteApi.skipJob('order-s2-01', { saleng_id: 'saleng-01' });
      expect(res.status).toBe('S2');
      expect(res.skipped_by).toBe('saleng-01');
    });

    it('throws error when skip API fails', async () => {
      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: false,
        json: async () => ({ detail: 'Failed to skip' }),
      });

      await expect(
        jobRouteApi.skipJob('order-s2-01')
      ).rejects.toThrow('Failed to skip');
    });
  });

  describe('getActiveQueue & Offline Cache (BR-03, CC-05, REQ-OP-001, AC-B04-04)', () => {
    it('fetches active queue and saves to localStorage cache (CC-05)', async () => {
      const mockQueue = {
        collector_id: 'saleng-01',
        total_active_jobs: 2,
        current_load_kg: 55.0,
        max_capacity_kg: 200.0,
        remaining_capacity_kg: 145.0,
        total_route_distance_km: 3.5,
        total_estimated_duration_min: 25,
        jobs: [
          {
            order_id: 'order-s2-01',
            status: 'S4',
            seller_name: 'สมชาย ใจดี',
            address_text: '123/45 ซอยรัชดาภิเษก 18',
            seller_phone: '081-999-8888',
            est_weight_kg: 25.0,
            appointment_slot: '10:00 - 12:00 น.',
            sequence_order: 1,
            distance_from_prev_km: 1.2,
            navigation_url: 'https://www.google.com/maps/dir/?api=1&destination=13.793000,100.578000&travelmode=driving',
          },
          {
            order_id: 'order-s2-02',
            status: 'S3',
            seller_name: 'สมหญิง รักสะอาด',
            address_text: '456/78 ซอยลาดพร้าว 48',
            seller_phone: '089-111-2222',
            est_weight_kg: 30.0,
            appointment_slot: '13:00 - 15:00 น.',
            sequence_order: 2,
            distance_from_prev_km: 2.3,
            navigation_url: 'https://www.google.com/maps/dir/?api=1&destination=13.798000,100.585000&travelmode=driving',
          },
        ],
      };

      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => mockQueue,
      });

      const res = await jobRouteApi.getActiveQueue({
        saleng_id: 'saleng-01',
        saleng_lat: 13.790,
        saleng_lng: 100.575,
      });

      expect(res.total_active_jobs).toBe(2);
      expect(res.current_load_kg).toBe(55.0);
      expect(res.jobs.length).toBe(2);

      // ตรวจสอบแคชใน LocalStorage
      const cached = jobRouteApi.getCachedQueue('saleng-01');
      expect(cached).not.toBeNull();
      expect(cached.total_active_jobs).toBe(2);
      expect(cached.current_load_kg).toBe(55.0);
    });

    it('falls back to localStorage cache when network request fails (REQ-OP-001, CC-05)', async () => {
      // Seed cache first
      const cachedData = {
        collector_id: 'saleng-01',
        total_active_jobs: 1,
        current_load_kg: 25.0,
        max_capacity_kg: 200.0,
        jobs: [
          {
            order_id: 'order-s2-01',
            status: 'S3',
            address_text: '123/45 ซอยรัชดาภิเษก 18',
          },
        ],
      };
      localStorage.setItem(
        'saleng_active_schedule_cache_saleng-01',
        JSON.stringify({ cached_at: new Date().toISOString(), data: cachedData })
      );

      // Simulate network failure
      globalThis.fetch = vi.fn().mockRejectedValue(new Error('Network offline'));

      const res = await jobRouteApi.getActiveQueue({ saleng_id: 'saleng-01' });
      expect(res.is_offline_cached).toBe(true);
      expect(res.total_active_jobs).toBe(1);
      expect(res.message).toContain('โหมดออฟไลน์');
    });
  });

  describe('startTransit & Offline Transit Queue (UC-09, BR-03, CC-05, AC-B04-05)', () => {
    it('starts transit online and confirms seller cancel locked (BR-03, AC-B04-05)', async () => {
      const mockTransitRes = {
        order_id: 'order-s2-01',
        saleng_id: 'saleng-01',
        status: 'S4',
        started_at: '2026-11-04T10:15:00Z',
        seller_cancel_locked: true,
        navigation_url: 'https://www.google.com/maps/dir/?api=1&destination=13.793000,100.578000&travelmode=driving',
        message: 'เริ่มออกเดินทางเรียบร้อยแล้ว ล็อกปุ่มยกเลิกฝั่งผู้ขายแล้ว',
      };

      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => mockTransitRes,
      });

      const res = await jobRouteApi.startTransit('order-s2-01', {
        saleng_id: 'saleng-01',
        current_lat: 13.790,
        current_lng: 100.575,
      });

      expect(res.status).toBe('S4');
      expect(res.seller_cancel_locked).toBe(true);
    });

    it('queues transit command when offline with idempotency key (REQ-OP-001, CC-05)', async () => {
      // Mock navigator.onLine = false
      Object.defineProperty(navigator, 'onLine', {
        value: false,
        configurable: true,
      });

      const res = await jobRouteApi.startTransit('order-s2-01', {
        saleng_id: 'saleng-01',
        current_lat: 13.790,
        current_lng: 100.575,
      });

      expect(res.is_offline_queued).toBe(true);
      expect(res.seller_cancel_locked).toBe(true);

      const queue = jobRouteApi.getOfflineTransitQueue();
      expect(queue.length).toBe(1);
      expect(queue[0].orderId).toBe('order-s2-01');
      expect(queue[0].idempotency_key).toContain('transit_order-s2-01_');

      // Reset navigator.onLine
      Object.defineProperty(navigator, 'onLine', {
        value: true,
        configurable: true,
      });
    });
  });

  describe('cancelJob (Collector Cancel & Revert - D-B04-04, AC-B04-06)', () => {
    it('cancels job in S3 and confirms reversion to S2 (AC-B04-06)', async () => {
      const mockCancelRes = {
        order_id: 'order-s2-01',
        reverted_status: 'S2',
        message: 'ยกเลิกงานเรียบร้อยแล้ว คำขอถูกคืนกลับเป็นสถานะรอผู้รับงาน',
        reason: 'VEHICLE_BREAKDOWN',
      };

      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => mockCancelRes,
      });

      const res = await jobRouteApi.cancelJob('order-s2-01', {
        saleng_id: 'saleng-01',
        reason: 'VEHICLE_BREAKDOWN',
        note: 'ยางรั่วที่ซอยรัชดาภิเษก',
      });

      expect(res.reverted_status).toBe('S2');
      expect(res.reason).toBe('VEHICLE_BREAKDOWN');
    });

    it('throws error when cancel API fails', async () => {
      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: false,
        json: async () => ({ detail: 'Cannot cancel in transit' }),
      });

      await expect(
        jobRouteApi.cancelJob('order-s2-01')
      ).rejects.toThrow('Cannot cancel in transit');
    });
  });
});

