import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { jobSearchApi } from '../src/services/jobSearchApi.js';

describe('jobSearchApi Client & Offline Cache Unit Tests (CC-01, CC-05, REQ-OP-001)', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  afterEach(() => {
    localStorage.clear();
  });

  it('fetches nearby jobs successfully and caches results in localStorage (AC-B02-01, CC-05)', async () => {
    const mockResponse = {
      total_count: 2,
      radius_km: 5.0,
      jobs: [
        {
          order_id: 'order-s2-01',
          subdistrict_name: 'แขวงสามเสนนอก',
          district_name: 'เขตห้วยขวาง',
          approximate_lat: 13.795,
          approximate_lng: 100.581,
          road_distance_km: 0.8,
          estimated_price_min: 150,
          estimated_price_max: 220,
          estimated_weight_kg: 25,
          categories: ['MAT-CARDBOARD'],
        },
      ],
      active_filters: {},
    };

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockResponse,
    });

    const res = await jobSearchApi.getNearbyJobs({
      saleng_lat: 13.79,
      saleng_lng: 100.575,
      radius_km: 5.0,
    });

    expect(res).not.toBeNull();
    expect(res.total_count).toBe(2);
    expect(res.jobs.length).toBe(1);

    // ตรวจสอบว่าแคชถูกบันทึกลงใน localStorage
    const cached = jobSearchApi.getCachedJobs();
    expect(cached).not.toBeNull();
    expect(cached.total_count).toBe(2);
    expect(cached.jobs[0].order_id).toBe('order-s2-01');
  });

  it('falls back to cached jobs when network is unavailable (CC-05, REQ-OP-001)', async () => {
    // ใส่แคชไว้ล่วงหน้า
    const mockCache = {
      total_count: 1,
      radius_km: 5.0,
      jobs: [
        {
          order_id: 'order-cached-01',
          subdistrict_name: 'แขวงดินแดง',
          road_distance_km: 1.2,
        },
      ],
    };
    localStorage.setItem(
      'saleng_active_job_search_cache',
      JSON.stringify({
        cached_at: new Date().toISOString(),
        data: mockCache,
      })
    );

    // จำลองเครือข่ายล้มเหลว (Network Error)
    globalThis.fetch = vi.fn().mockRejectedValue(new Error('Failed to fetch (offline)'));

    const res = await jobSearchApi.getNearbyJobs({
      saleng_lat: 13.79,
      saleng_lng: 100.575,
      radius_km: 5.0,
    });

    expect(res).not.toBeNull();
    expect(res.is_offline_cached).toBe(true);
    expect(res.jobs[0].order_id).toBe('order-cached-01');
  });

  it('fetches job summary without PII (AC-B02-03)', async () => {
    const mockSummary = {
      order_id: 'order-s2-01',
      subdistrict_name: 'แขวงสามเสนนอก',
      district_name: 'เขตห้วยขวาง',
      approximate_lat: 13.795,
      approximate_lng: 100.581,
      road_distance_km: 0.8,
    };

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockSummary,
    });

    const res = await jobSearchApi.getJobSummary('order-s2-01', {
      saleng_lat: 13.79,
      saleng_lng: 100.575,
    });

    expect(res.order_id).toBe('order-s2-01');
    expect(res.subdistrict_name).toBe('แขวงสามเสนนอก');
    expect(res.address_text).toBeUndefined();
  });

  it('simulates new order successfully (Q-02)', async () => {
    const mockSim = {
      success: true,
      message: 'จำลองคำขอขายใหม่สถานะ S2 สำเร็จ',
      order: { order_id: 'order-sim-123' },
    };

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockSim,
    });

    const res = await jobSearchApi.simulateNewOrder({
      seller_id: 'seller-sim-01',
      lat: 13.791,
      lng: 100.576,
      subdistrict: 'แขวงสามเสนนอก',
    });

    expect(res.success).toBe(true);
    expect(res.order.order_id).toBe('order-sim-123');
  });
});

