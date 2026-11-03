/**
 * Vitest tests สำหรับ buyerSearchApi.js
 * รองรับ UC-03, CC-05, REQ-OP-001
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { buyerSearchApi } from '../src/services/buyerSearchApi.js';

describe('buyerSearchApi Client & Offline Cache', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it('searches collectors and caches results to localStorage when online', async () => {
    const mockData = {
      collectors: [
        {
          saleng_id: 'saleng-01',
          display_name: 'ลุงสมชาย ซาเล้งสุทธิสาร',
          verified: true,
          vehicle_type: 'TRICYCLE',
          distance_km: 1.2,
          is_favorite: true,
        },
      ],
      total_count: 1,
      has_bulky_items: false,
    };

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockData,
    });

    const result = await buyerSearchApi.searchCollectors({ sellerId: 'seller-01' });
    expect(result.total_count).toBe(1);
    expect(result.collectors[0].saleng_id).toBe('saleng-01');

    // ตรวจสอบว่ามีข้อมูลใน localStorage
    const cached = localStorage.getItem('saleng_cached_collectors');
    expect(cached).not.toBeNull();
    const parsed = JSON.parse(cached);
    expect(parsed[0].saleng_id).toBe('saleng-01');
  });

  it('falls back to localStorage cache when network request fails', async () => {
    const cachedCollectors = [
      {
        saleng_id: 'saleng-cached',
        display_name: 'ซาเล้งจากแคช',
        verified: true,
        vehicle_type: 'PICKUP_TRUCK',
        distance_km: 2.5,
      },
    ];
    localStorage.setItem('saleng_cached_collectors', JSON.stringify(cachedCollectors));

    // จำลองเครือข่ายล้มเหลว (Offline)
    global.fetch = vi.fn().mockRejectedValue(new Error('Network error'));

    const result = await buyerSearchApi.searchCollectors({ sellerId: 'seller-01' });
    expect(result.is_offline).toBe(true);
    expect(result.total_count).toBe(1);
    expect(result.collectors[0].saleng_id).toBe('saleng-cached');
  });

  it('sends direct request successfully', async () => {
    const mockDirectResp = {
      order_id: 'order-123',
      status: 'S2',
      assigned_saleng: { saleng_id: 'saleng-01', display_name: 'ลุงสมชาย' },
      direct_request_expires_at: '2026-11-04T12:15:00Z',
      message: 'ส่งคำขอสำเร็จ',
    };

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockDirectResp,
    });

    const result = await buyerSearchApi.sendDirectRequest('order-123', 'saleng-01', 'seller-01', 'มีของชิ้นใหญ่');
    expect(result.status).toBe('S2');
    expect(result.assigned_saleng.saleng_id).toBe('saleng-01');
  });
});

