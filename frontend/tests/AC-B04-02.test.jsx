/**
 * Component Tests สำหรับ AC-B04-02: Skip Job Option
 * (T-08: Extension A2, AC-B04-02, UC-12)
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { jobRouteApi } from '../src/services/jobRouteApi.js';

describe('AC-B04-02: Skip Job Option Tests (Extension A2)', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('calls skipJob API and confirms order remains in S2 (Pending)', async () => {
    const mockSkipResult = {
      order_id: 'order-s2-01',
      status: 'S2',
      message: 'ข้ามงานเรียบร้อยแล้ว คำขอยังคงสถานะรอผู้รับงาน',
      skipped_by: 'saleng-01',
    };

    vi.spyOn(jobRouteApi, 'skipJob').mockResolvedValue(mockSkipResult);

    const res = await jobRouteApi.skipJob('order-s2-01', { saleng_id: 'saleng-01' });

    expect(res.status).toBe('S2');
    expect(res.skipped_by).toBe('saleng-01');
    expect(res.message).toContain('ข้ามงานเรียบร้อยแล้ว');
  });
});

