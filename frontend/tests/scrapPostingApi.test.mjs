/**
 * Frontend Test สำหรับ scrapPostingApi.js
 * รองรับ UC-02, CC-01, CC-05, REQ-OP-001, AC-S02-01..05
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { scrapPostingApi } from '../src/services/scrapPostingApi.js';

describe('scrapPostingApi service and Offline Caching', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it('getCategories should return categories and cache them', async () => {
    const mockCats = {
      categories: [
        { category_code: 'MAT-CARDBOARD', name: 'กระดาษลัง', min_price_per_unit: 3.0 },
      ],
    };
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockCats,
    });

    const result = await scrapPostingApi.getCategories();
    expect(result.categories.length).toBe(1);
    expect(localStorage.getItem('saleng_scrap_categories')).not.toBeNull();
  });

  it('createDraft should store draft in localStorage', async () => {
    const mockDraft = {
      order_id: 'ORD-DRAFT-1',
      seller_id: 'SEL-001',
      status: 'S1',
      total_est_min_price: 0,
    };
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockDraft,
    });

    const draft = await scrapPostingApi.createDraft('SEL-001', 'LOC-001');
    expect(draft.order_id).toBe('ORD-DRAFT-1');
    expect(localStorage.getItem('saleng_draft_order')).toContain('ORD-DRAFT-1');
  });

  it('getDraft should fall back to localStorage when offline (CC-05, REQ-OP-001)', async () => {
    const cachedDraft = {
      order_id: 'ORD-OFFLINE-99',
      seller_id: 'SEL-001',
      status: 'S1',
      total_est_min_price: 150.0,
    };
    localStorage.setItem('saleng_draft_order', JSON.stringify(cachedDraft));

    // จำลองเครือข่ายล่ม
    global.fetch = vi.fn().mockRejectedValue(new Error('Network offline'));

    const draft = await scrapPostingApi.getDraft('ORD-OFFLINE-99');
    expect(draft.order_id).toBe('ORD-OFFLINE-99');
    expect(draft.is_offline).toBe(true);
  });
});

