import { describe, it, expect, vi, beforeEach } from 'vitest';
import {
  getAdminHeaders,
  getKycSubmissions,
  reviewKyc,
  getUsers,
  penalizeUser,
  reactivateUser,
} from '../src/services/adminUserApi.js';

describe('Admin User API Client (adminUserApi.js) Tests', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('getAdminHeaders generates correct headers with X-Admin-Role', () => {
    const headers = getAdminHeaders('admin-99', 'ADMIN');
    expect(headers['Content-Type']).toBe('application/json');
    expect(headers['X-Admin-Role']).toBe('ADMIN');
    expect(headers['X-Admin-Id']).toBe('admin-99');
  });

  it('getKycSubmissions calls correct endpoint and returns data', async () => {
    const mockData = [
      { id: 'sub-01', saleng_id: 'saleng-01', id_card_no_masked: '1-1002-XXXXX-XX-1', status: 'PENDING_REVIEW' },
    ];
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockData,
    });

    const result = await getKycSubmissions('PENDING_REVIEW');
    expect(global.fetch).toHaveBeenCalledWith(
      '/api/v1/admin/kyc/submissions?status=PENDING_REVIEW',
      expect.objectContaining({
        method: 'GET',
        headers: expect.objectContaining({ 'X-Admin-Role': 'ADMIN' }),
      })
    );
    expect(result).toEqual(mockData);
  });

  it('reviewKyc posts approval and returns review response', async () => {
    const mockResp = { success: true, submission_id: 'sub-01', action: 'APPROVE', verified: true };
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockResp,
    });

    const result = await reviewKyc('sub-01', 'APPROVE');
    expect(global.fetch).toHaveBeenCalledWith(
      '/api/v1/admin/kyc/review',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ submission_id: 'sub-01', action: 'APPROVE' }),
      })
    );
    expect(result.verified).toBe(true);
  });

  it('getUsers handles query params correctly', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => [],
    });

    await getUsers('COLLECTOR', 'ACTIVE', 'สมชาย');
    expect(global.fetch).toHaveBeenCalledWith(
      '/api/v1/admin/users?role=COLLECTOR&status=ACTIVE&search=%E0%B8%AA%E0%B8%A1%E0%B8%8A%E0%B8%B2%E0%B8%A2',
      expect.anything()
    );
  });

  it('penalizeUser posts penalty and handles errors', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 403,
      json: async () => ({ detail: 'สิทธิ์ไม่ถูกต้อง: เฉพาะผู้ดูแลระบบเท่านั้น' }),
    });

    await expect(penalizeUser('saleng-01', 'COLLECTOR', 'BAN', 'โกงตาชั่ง')).rejects.toThrow(
      'สิทธิ์ไม่ถูกต้อง: เฉพาะผู้ดูแลระบบเท่านั้น'
    );
  });

  it('reactivateUser posts reinstatement successfully', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ success: true, account_status: 'ACTIVE' }),
    });

    const res = await reactivateUser('saleng-01', 'COLLECTOR');
    expect(res.account_status).toBe('ACTIVE');
  });
});

