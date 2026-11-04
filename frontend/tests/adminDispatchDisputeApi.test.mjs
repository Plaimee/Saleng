/**
 * Test Suite for adminDispatchDisputeApi.js
 * ทดสอบ Frontend API Client ครบทุกฟังก์ชัน พร้อมการจัดการ Error 403/400 (CC-03, CC-05)
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  getAdminHeaders,
  getStalledOrders,
  manualDispatchOrder,
  expandSearchRadius,
  getDisputes,
  getDisputeDossier,
  resolveDispute,
} from '../src/services/adminDispatchDisputeApi.js';

describe('adminDispatchDisputeApi', () => {
  const originalFetch = global.fetch;

  beforeEach(() => {
    global.fetch = vi.fn();
  });

  afterEach(() => {
    global.fetch = originalFetch;
    vi.restoreAllMocks();
  });

  it('getAdminHeaders สร้าง header แอดมินถูกต้อง', () => {
    const headers = getAdminHeaders('admin-01', 'ADMIN');
    expect(headers['Content-Type']).toBe('application/json');
    expect(headers['X-Admin-Role']).toBe('ADMIN');
    expect(headers['X-Admin-Id']).toBe('admin-01');
  });

  it('getStalledOrders ส่งคำขอและรับรายการสำเร็จ', async () => {
    const mockData = [
      { order_id: 'ord-1', status: 'S2', waiting_minutes: 42.0 },
    ];
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockData,
    });

    const result = await getStalledOrders({ min_wait_minutes: 30 });
    expect(result).toEqual(mockData);
    expect(global.fetch).toHaveBeenCalledWith(
      '/api/v1/admin/dispatch/stalled-orders?min_wait_minutes=30',
      expect.objectContaining({
        method: 'GET',
        headers: expect.objectContaining({ 'X-Admin-Role': 'ADMIN' }),
      })
    );
  });

  it('manualDispatchOrder มอบหมายงานตรงสำเร็จ', async () => {
    const mockRes = { success: true, order_id: 'ord-1', status: 'S3' };
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockRes,
    });

    const result = await manualDispatchOrder({ order_id: 'ord-1', saleng_id: 'sal-1' });
    expect(result.status).toBe('S3');
    expect(global.fetch).toHaveBeenCalledWith(
      '/api/v1/admin/dispatch/assign',
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({ 'X-Admin-Role': 'ADMIN' }),
      })
    );
  });

  it('expandSearchRadius ขยายรัศมีสำเร็จ', async () => {
    const mockRes = { success: true, new_radius_km: 10.0 };
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockRes,
    });

    const result = await expandSearchRadius({ order_id: 'ord-1', new_radius_km: 10.0 });
    expect(result.new_radius_km).toBe(10.0);
    expect(global.fetch).toHaveBeenCalledWith(
      '/api/v1/admin/dispatch/expand-radius',
      expect.objectContaining({ method: 'POST' })
    );
  });

  it('getDisputes และ getDisputeDossier ดึงข้อมูลสำเร็จ', async () => {
    const mockList = [{ dispute_id: 'DISP-1', status: 'PENDING_ADMIN' }];
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockList,
    });
    const listRes = await getDisputes();
    expect(listRes).toEqual(mockList);

    const mockDossier = { dispute_id: 'DISP-1', original_order: {} };
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockDossier,
    });
    const dossierRes = await getDisputeDossier('DISP-1');
    expect(dossierRes.dispute_id).toBe('DISP-1');
  });

  it('resolveDispute ตัดสินชี้ขาดสำเร็จ', async () => {
    const mockRes = { success: true, order_status: 'S7', arbitrated_amount: 200.0 };
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockRes,
    });

    const result = await resolveDispute('DISP-1', {
      action: 'RESOLVE_COMPLETE',
      arbitrated_amount: 200.0,
      arbitration_note: 'จบงาน',
    });
    expect(result.order_status).toBe('S7');
  });

  it('จัดการ Error 403 Forbidden ได้ถูกต้อง', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: false,
      status: 403,
      json: async () => ({ detail: 'สิทธิ์ไม่ถูกต้อง: เฉพาะผู้ดูแลระบบ (ADMIN) เท่านั้น' }),
    });

    await expect(getStalledOrders({ customRole: 'GUEST' })).rejects.toThrow(
      'สิทธิ์ไม่ถูกต้อง: เฉพาะผู้ดูแลระบบ (ADMIN) เท่านั้น'
    );
  });

  it('จัดการ Error 400 Bad Request ได้ถูกต้อง', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: false,
      status: 400,
      json: async () => ({ detail: 'ซาเล้งยังไม่ผ่านการยืนยันตัวตน KYC' }),
    });

    await expect(
      manualDispatchOrder({ order_id: 'ord-1', saleng_id: 'sal-unverified' })
    ).rejects.toThrow('ซาเล้งยังไม่ผ่านการยืนยันตัวตน KYC');
  });
});

