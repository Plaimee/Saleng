/**
 * Frontend Test สำหรับ accountApi.js
 * รองรับ UC-01, CC-01, CC-05, REQ-OP-001, AC-S01-01..04
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { accountApi } from '../src/services/accountApi.js';

describe('accountApi service and LocalStorage caching', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it('requestOtp should send POST request and return data', async () => {
    const mockResponse = {
      phone_masked: '08X-XXX-8888',
      expires_in_seconds: 300,
      mock_otp: '123456',
    };
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockResponse,
    });

    const result = await accountApi.requestOtp('0812348888');
    expect(result.phone_masked).toBe('08X-XXX-8888');
    expect(global.fetch).toHaveBeenCalledWith(
      '/api/v1/sellers/auth/request-otp',
      expect.objectContaining({
        method: 'POST',
      })
    );
  });

  it('verifyOtp should store session token and profile in localStorage', async () => {
    const mockAuth = {
      session_token: 'token-abc-123',
      seller_id: 'SEL-001',
      phone_masked: '08X-XXX-1111',
      display_name: 'ผู้ขาย ทดสอบ',
    };
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockAuth,
    });

    const result = await accountApi.verifyOtp('0812341111', '123456');
    expect(result.session_token).toBe('token-abc-123');
    expect(localStorage.getItem('saleng_seller_token')).toBe('token-abc-123');

    const storedSession = accountApi.getStoredSession();
    expect(storedSession).not.toBeNull();
    expect(storedSession.seller_id).toBe('SEL-001');
    expect(storedSession.token).toBe('token-abc-123');
  });

  it('logout should clear token and profile from localStorage', async () => {
    localStorage.setItem('saleng_seller_token', 'token-to-delete');
    localStorage.setItem('saleng_seller_profile', JSON.stringify({ seller_id: 'SEL-001' }));

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ success: true }),
    });

    await accountApi.logout();
    expect(localStorage.getItem('saleng_seller_token')).toBeNull();
    expect(localStorage.getItem('saleng_seller_profile')).toBeNull();
  });

  it('listLocations should fall back to localStorage cache when offline (CC-05, REQ-OP-001)', async () => {
    const cachedLocations = [
      {
        location_id: 'LOC-1',
        label: 'บ้าน',
        sub_district: 'บางซื่อ',
        address_text: '123/45',
        is_default: true,
      },
    ];
    localStorage.setItem('saleng_seller_locations', JSON.stringify(cachedLocations));

    // จำลองเครือข่ายล่ม
    global.fetch = vi.fn().mockRejectedValue(new Error('Network error'));

    const result = await accountApi.listLocations('SEL-001');
    expect(result.total_locations).toBe(1);
    expect(result.locations[0].location_id).toBe('LOC-1');
    expect(result.is_offline).toBe(true);
  });
});

