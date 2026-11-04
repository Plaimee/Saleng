import { describe, it, expect, vi, beforeEach } from 'vitest';
import {
  getAdminHeaders,
  getBenchmarkPrices,
  updateBenchmarkPrice,
  batchUpdatePrices,
  getGradingRules,
  updateGradingRules,
  getPriceHistory,
} from '../src/services/adminBenchmarkApi.js';

describe('Admin Benchmark API Client (adminBenchmarkApi.js) Tests', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('getAdminHeaders generates correct headers with X-Admin-Role', () => {
    const headers = getAdminHeaders('admin-01', 'ADMIN');
    expect(headers['Content-Type']).toBe('application/json');
    expect(headers['X-Admin-Role']).toBe('ADMIN');
    expect(headers['X-Admin-Id']).toBe('admin-01');
  });

  it('getBenchmarkPrices calls correct endpoint with filters and returns list', async () => {
    const mockPrices = [
      { category_code: 'MAT-CARDBOARD', category_name: 'กระดาษลัง', unit: 'kg', min_price_per_unit: 3.0, max_price_per_unit: 4.0 },
    ];
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockPrices,
    });

    const result = await getBenchmarkPrices({ unit: 'kg', q: 'กระดาษ' });
    expect(global.fetch).toHaveBeenCalledWith(
      '/api/v1/admin/benchmark-prices?unit=kg&q=%E0%B8%81%E0%B8%A3%E0%B8%B0%E0%B8%94%E0%B8%B2%E0%B8%A9',
      expect.objectContaining({
        method: 'GET',
        headers: expect.objectContaining({ 'X-Admin-Role': 'ADMIN' }),
      })
    );
    expect(result).toEqual(mockPrices);
  });

  it('updateBenchmarkPrice puts update payload and returns response', async () => {
    const mockResp = {
      success: true,
      category_code: 'MAT-CARDBOARD',
      min_price_per_unit: 3.5,
      max_price_per_unit: 4.5,
      updated_at: '2026-11-04T00:00:00Z',
    };
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockResp,
    });

    const result = await updateBenchmarkPrice('MAT-CARDBOARD', {
      min_price_per_unit: 3.5,
      max_price_per_unit: 4.5,
      grading_condition: 'สะอาด',
      confirm_shift: false,
    });

    expect(global.fetch).toHaveBeenCalledWith(
      '/api/v1/admin/benchmark-prices/MAT-CARDBOARD',
      expect.objectContaining({
        method: 'PUT',
        body: JSON.stringify({
          min_price_per_unit: 3.5,
          max_price_per_unit: 4.5,
          grading_condition: 'สะอาด',
          confirm_shift: false,
          updated_by: 'admin-01',
          change_reason: null,
        }),
      })
    );
    expect(result.success).toBe(true);
  });

  it('updateBenchmarkPrice throws on 400 price shift > 50%', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 400,
      json: async () => ({
        detail: {
          error: 'PRICE_SHIFT_EXCEEDS_50_PERCENT',
          message: 'ราคาเปลี่ยนแปลงเกิน 50%',
        },
      }),
    });

    await expect(
      updateBenchmarkPrice('MAT-CARDBOARD', {
        min_price_per_unit: 10.0,
        max_price_per_unit: 15.0,
      })
    ).rejects.toThrow('ราคาเปลี่ยนแปลงเกิน 50%');
  });

  it('batchUpdatePrices posts batch payload and returns response', async () => {
    const mockBatchResp = {
      success: true,
      updated_count: 2,
    };
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockBatchResp,
    });

    const result = await batchUpdatePrices({
      items: [
        { category_code: 'BULKY-FRIDGE', min_price_per_unit: 200, max_price_per_unit: 300 },
        { category_code: 'BULKY-TV', min_price_per_unit: 50, max_price_per_unit: 150 },
      ],
      effective_date: '2026-11-05',
    });

    expect(global.fetch).toHaveBeenCalledWith(
      '/api/v1/admin/benchmark-prices/batch-update',
      expect.objectContaining({
        method: 'POST',
      })
    );
    expect(result.updated_count).toBe(2);
  });

  it('getGradingRules and updateGradingRules call correct endpoints', async () => {
    const mockRules = [
      { grade_level: 'GRADE_A', contamination_deduction_percent: 0.0, price_target: 'MAX' },
      { grade_level: 'GRADE_B', contamination_deduction_percent: 5.0, price_target: 'MID' },
      { grade_level: 'GRADE_C', contamination_deduction_percent: 10.0, price_target: 'MIN' },
    ];
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockRules,
    });

    const rules = await getGradingRules('MAT-CARDBOARD');
    expect(rules).toEqual(mockRules);

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ success: true, category_code: 'MAT-CARDBOARD', rules: mockRules }),
    });

    const updated = await updateGradingRules('MAT-CARDBOARD', { rules: mockRules });
    expect(updated.success).toBe(true);
  });

  it('getPriceHistory calls history endpoint with limit', async () => {
    const mockHistory = [
      { history_id: 'h-1', old_min_price: 3.0, new_min_price: 3.5 },
    ];
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockHistory,
    });

    const history = await getPriceHistory('MAT-CARDBOARD', 10);
    expect(global.fetch).toHaveBeenCalledWith(
      '/api/v1/admin/benchmark-prices/history/MAT-CARDBOARD?limit=10',
      expect.anything()
    );
    expect(history).toEqual(mockHistory);
  });

  it('throws HTTP 403 error message when not authorized', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 403,
      json: async () => ({ detail: 'สิทธิ์ไม่ถูกต้อง: เฉพาะผู้ดูแลระบบ (ADMIN) เท่านั้น' }),
    });

    await expect(getBenchmarkPrices()).rejects.toThrow('สิทธิ์ไม่ถูกต้อง');
  });
});

