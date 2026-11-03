/**
 * Vitest tests สำหรับ bookingTrackingApi.js
 * รองรับ UC-04, CC-05, REQ-OP-001, BR-03
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { bookingTrackingApi } from '../src/services/bookingTrackingApi.js';

describe('bookingTrackingApi Client & Offline Fallback', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it('books slot and caches order status into localStorage', async () => {
    const mockOrder = {
      order_id: 'order-101',
      status: 'S2',
      status_label: 'รอผู้รับซื้อ',
      stepper_step: 1,
      can_cancel: true,
    };

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockOrder,
    });

    const result = await bookingTrackingApi.bookSlot('order-101', { booking_type: 'IMMEDIATE' });
    expect(result.status).toBe('S2');
    expect(result.can_cancel).toBe(true);

    const cached = localStorage.getItem('saleng_active_order_tracking');
    expect(cached).not.toBeNull();
    expect(JSON.parse(cached).order_id).toBe('order-101');
  });

  it('falls back to localStorage cache when getStatus encounters network error', async () => {
    const cachedData = {
      order_id: 'order-cached',
      status: 'S4',
      status_label: 'กำลังเดินทาง',
      stepper_step: 3,
      can_cancel: false,
    };
    localStorage.setItem('saleng_active_order_tracking', JSON.stringify(cachedData));

    global.fetch = vi.fn().mockRejectedValue(new Error('Network error'));

    const result = await bookingTrackingApi.getStatus('order-cached');
    expect(result.is_offline).toBe(true);
    expect(result.status).toBe('S4');
    expect(result.can_cancel).toBe(false);
  });

  it('handles cancellation error when BR-03 is violated', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      json: async () => ({
        detail: 'ไม่สามารถยกเลิกนัดหมายได้เนื่องจากซาเล้งกำลังเดินทางมายังหน้างานแล้วตามกฎ BR-03',
      }),
    });

    await expect(
      bookingTrackingApi.cancelOrder('order-s4', 'ขอยกเลิก')
    ).rejects.toThrow('BR-03');
  });
});

