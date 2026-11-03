/**
 * Frontend Test สำหรับ collectorAccountApi.js
 * รองรับ UC-01, CC-01, CC-05, REQ-OP-001, D-00-01, AC-B01-01..05
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { collectorAccountApi } from '../src/services/collectorAccountApi.js';

describe('collectorAccountApi and LocalStorage Caching', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it('requestOtp should send POST request and return data', async () => {
    const mockResponse = {
      phone_masked: '08X-XXX-5678',
      expires_in_seconds: 300,
      mock_otp: '123456',
    };
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockResponse,
    });

    const result = await collectorAccountApi.requestOtp('0812345678');
    expect(result.phone_masked).toBe('08X-XXX-5678');
    expect(global.fetch).toHaveBeenCalledWith(
      '/api/v1/collectors/auth/request-otp',
      expect.objectContaining({
        method: 'POST',
      })
    );
  });

  it('verifyOtp should store session token and profile in localStorage', async () => {
    const mockAuth = {
      session_token: 'saleng_tok_123456',
      saleng_id: 'saleng-99',
      display_name: 'ลุงทวน ซาเล้งไฟแรง',
      phone_masked: '08X-XXX-9999',
      verified: false,
      kyc_status: 'UNVERIFIED',
      vehicle_type: 'TRICYCLE',
      max_capacity_kg: 150.0,
    };
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockAuth,
    });

    const result = await collectorAccountApi.verifyOtp('0899999999', '123456');
    expect(result.session_token).toBe('saleng_tok_123456');

    // ตรวจสอบ localStorage
    expect(localStorage.getItem('saleng_collector_session')).toBe('saleng_tok_123456');
    const storedProfile = JSON.parse(localStorage.getItem('saleng_collector_profile'));
    expect(storedProfile.saleng_id).toBe('saleng-99');
    expect(storedProfile.verified).toBe(false);

    // ตรวจสอบ getStoredSession
    const session = collectorAccountApi.getStoredSession();
    expect(session).not.toBeNull();
    expect(session.token).toBe('saleng_tok_123456');
    expect(session.saleng_id).toBe('saleng-99');
  });

  it('logout should clear localStorage', async () => {
    localStorage.setItem('saleng_collector_session', 'tok-abc');
    localStorage.setItem('saleng_collector_profile', JSON.stringify({ saleng_id: 'saleng-01' }));

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ message: 'ออกจากระบบสำเร็จ' }),
    });

    await collectorAccountApi.logout();
    expect(localStorage.getItem('saleng_collector_session')).toBeNull();
    expect(localStorage.getItem('saleng_collector_profile')).toBeNull();
  });

  it('getProfile should use offline cache when network fails', async () => {
    const cachedProfile = {
      saleng_id: 'saleng-01',
      display_name: 'ลุงสมชาย แคชออฟไลน์',
      max_capacity_kg: 200.0,
    };
    localStorage.setItem('saleng_collector_profile', JSON.stringify(cachedProfile));

    // จำลองเครือข่ายล้มเหลว
    global.fetch = vi.fn().mockRejectedValue(new Error('Network error'));

    const profile = await collectorAccountApi.getProfile('saleng-01');
    expect(profile.display_name).toBe('ลุงสมชาย แคชออฟไลน์');
    expect(profile.max_capacity_kg).toBe(200.0);
  });

  it('updateVehicle should send PUT request with vehicle data', async () => {
    const updatedProfile = {
      saleng_id: 'saleng-01',
      vehicle_type: 'SIDE_CAR_MOTORCYCLE',
      max_capacity_kg: 300.0,
      license_plate: '1กข-9999',
    };
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => updatedProfile,
    });

    const res = await collectorAccountApi.updateVehicle('saleng-01', {
      vehicle_type: 'SIDE_CAR_MOTORCYCLE',
      license_plate: '1กข-9999',
      max_capacity_kg: 300.0,
    });
    expect(res.vehicle_type).toBe('SIDE_CAR_MOTORCYCLE');
    expect(res.max_capacity_kg).toBe(300.0);
  });

  it('checkJobClaimGate should handle 403 Forbidden for unverified collector', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      status: 403,
      ok: false,
      json: async () => ({ detail: 'ยังไม่ได้ยืนยันตัวตน' }),
    });

    const result = await collectorAccountApi.checkJobClaimGate('saleng-05');
    expect(result.can_claim_job).toBe(false);
    expect(result.error_detail).toBe('ยังไม่ได้ยืนยันตัวตน');
  });

  it('checkJobClaimGate should handle 200 OK for verified collector', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      status: 200,
      ok: true,
      json: async () => ({ can_claim_job: true, verified: true }),
    });

    const result = await collectorAccountApi.checkJobClaimGate('saleng-01');
    expect(result.can_claim_job).toBe(true);
    expect(result.verified).toBe(true);
  });
});

