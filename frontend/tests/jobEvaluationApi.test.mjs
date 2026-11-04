/**
 * Unit Tests สำหรับ Frontend API Client: jobEvaluationApi
 * (T-06: CC-01, CC-05, REQ-OP-001, AC-B03-01..05)
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { jobEvaluationApi } from '../src/services/jobEvaluationApi.js';

describe('jobEvaluationApi Client & Offline Cache Unit Tests (CC-01, CC-05, REQ-OP-001)', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  afterEach(() => {
    localStorage.clear();
  });

  it('evaluates job successfully and caches result in localStorage (AC-B03-01, CC-05)', async () => {
    const mockResponse = {
      order_id: 'order-s2-01',
      collector_id: 'saleng-01',
      vehicle_type: 'MOTORCYCLE',
      road_distance_km: 1.2,
      estimated_fuel_cost: 3.0,
      is_fallback_distance: false,
      total_est_weight_kg: 25.0,
      total_min_price: 150.0,
      total_max_price: 220.0,
      need_lifting_help: false,
      current_load_kg: 0.0,
      max_capacity_kg: 200.0,
      remaining_capacity_kg: 200.0,
      projected_total_load_kg: 25.0,
      is_capacity_exceeded: false,
      collector_is_online: true,
      collector_is_verified: true,
      can_claim_job: true,
      claim_block_reason: null,
      items: [
        {
          item_id: 'item-01',
          category_id: 'MAT-CARDBOARD',
          category_name_th: 'ลังกระดาษ/กระดาษลูกฟูก',
          est_weight_kg: 25.0,
          est_min_price: 150.0,
          est_max_price: 220.0,
          photo_urls: ['https://example.com/photo1.jpg'],
          is_bulky: false,
        },
      ],
      location_summary: {
        subdistrict_name: 'แขวงสามเสนนอก',
        district_name: 'เขตห้วยขวาง',
        fuzzed_lat: 13.795,
        fuzzed_lng: 100.581,
      },
    };

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockResponse,
    });

    const res = await jobEvaluationApi.evaluateJob('order-s2-01', {
      saleng_id: 'saleng-01',
      saleng_lat: 13.79,
      saleng_lng: 100.575,
    });

    expect(res).not.toBeNull();
    expect(res.order_id).toBe('order-s2-01');
    expect(res.estimated_fuel_cost).toBe(3.0);
    expect(res.can_claim_job).toBe(true);

    // ตรวจสอบว่าแคชถูกบันทึกลงใน localStorage
    const cached = jobEvaluationApi.getCachedEvaluation('order-s2-01');
    expect(cached).not.toBeNull();
    expect(cached.order_id).toBe('order-s2-01');
    expect(cached.estimated_fuel_cost).toBe(3.0);
  });

  it('serves evaluation data from offline cache when network fails (REQ-OP-001, CC-05)', async () => {
    // เตรียมข้อมูลแคชไว้ล่วงหน้า
    const mockCached = {
      order_id: 'order-s2-01',
      collector_id: 'saleng-01',
      road_distance_km: 1.2,
      estimated_fuel_cost: 3.0,
      total_est_weight_kg: 25.0,
      items: [],
      location_summary: {
        subdistrict_name: 'แขวงสามเสนนอก',
        district_name: 'เขตห้วยขวาง',
      },
    };

    localStorage.setItem(
      'saleng_active_job_eval_cache_order-s2-01',
      JSON.stringify({ cached_at: new Date().toISOString(), data: mockCached })
    );

    // จำลองเครือข่ายล้มเหลว
    globalThis.fetch = vi.fn().mockRejectedValue(new Error('Network error / Offline'));

    const res = await jobEvaluationApi.evaluateJob('order-s2-01', { saleng_id: 'saleng-01' });

    expect(res).not.toBeNull();
    expect(res.order_id).toBe('order-s2-01');
    expect(res.is_offline_cached).toBe(true);
    expect(res.message).toBe('แสดงผลการประเมินจากแคชออฟไลน์');
  });

  it('toggles online status successfully (CC-02, AC-B03-03)', async () => {
    const mockStatusResponse = {
      saleng_id: 'saleng-01',
      is_online: false,
      updated_at: '2026-11-04T12:00:00Z',
      message: 'อัปเดตสถานะเป็นออฟไลน์แล้ว',
    };

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockStatusResponse,
    });

    const res = await jobEvaluationApi.toggleOnlineStatus('saleng-01', false);
    expect(res.is_online).toBe(false);
    expect(globalThis.fetch).toHaveBeenCalledWith(
      '/api/v1/collectors/saleng-01/status',
      expect.objectContaining({
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
      })
    );
  });

  it('fetches collector capacity correctly (BR-03, REQ-CON-003)', async () => {
    const mockCapacity = {
      saleng_id: 'saleng-01',
      vehicle_type: 'MOTORCYCLE',
      current_load_kg: 45.0,
      max_capacity_kg: 200.0,
      remaining_capacity_kg: 155.0,
      is_online: true,
      is_verified: true,
    };

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockCapacity,
    });

    const res = await jobEvaluationApi.getCollectorCapacity('saleng-01');
    expect(res.current_load_kg).toBe(45.0);
    expect(res.remaining_capacity_kg).toBe(155.0);
  });

  it('clears cached evaluation data properly', () => {
    localStorage.setItem('saleng_active_job_eval_cache_order-s2-01', JSON.stringify({ data: { test: true } }));
    expect(jobEvaluationApi.getCachedEvaluation('order-s2-01')).not.toBeNull();

    jobEvaluationApi.clearCachedEvaluation('order-s2-01');
    expect(jobEvaluationApi.getCachedEvaluation('order-s2-01')).toBeNull();
  });
});

