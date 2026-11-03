/**
 * Component Tests for AC-B02-02: No Jobs in Radius & 10.0 km Expansion
 * (Task T-08: UC-04, REQ-FN-002, AC-04-04, P-06, Q-06)
 */

import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import JobSearchPanel from '../src/components/JobSearchPanel';
import { jobSearchApi } from '../src/services/jobSearchApi';

describe('AC-B02-02: Empty State & 10.0 km Radius Expansion Component Tests', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('displays empty state and expand button when no jobs in 5.0 km, and expands on click', async () => {
    // 1. ครั้งแรก: รัศมี 5.0 กม. ไม่พบงาน -> can_expand_radius = true
    const getNearbyMock = vi.spyOn(jobSearchApi, 'getNearbyJobs')
      .mockResolvedValueOnce({
        total_count: 0,
        radius_km: 5.0,
        jobs: [],
        message: 'ยังไม่มีงานในเส้นทาง',
        can_expand_radius: true,
      })
      // 2. ครั้งที่สอง: หลังกดขยายเป็น 10.0 กม. -> คืนค่างานที่พบ
      .mockResolvedValueOnce({
        total_count: 1,
        radius_km: 10.0,
        jobs: [
          {
            order_id: 'order-s2-04',
            status: 'S2',
            subdistrict_name: 'แขวงลาดยาว',
            district_name: 'เขตจตุจักร',
            approximate_lat: 13.8520,
            approximate_lng: 100.5870,
            road_distance_km: 7.5,
            estimated_price_min: 60,
            estimated_price_max: 90,
            estimated_weight_kg: 15,
            categories: ['MAT-CARDBOARD'],
            need_lifting_help: false,
            created_at: '2026-11-04T02:55:00Z',
          },
        ],
        can_expand_radius: false,
      });

    render(<JobSearchPanel />);

    // ตรวจสอบข้อความแจ้งเตือน "ยังไม่มีงานในเส้นทาง"
    await waitFor(() => {
      const emptyBox = screen.getByTestId('no-jobs-box');
      expect(emptyBox).not.toBeNull();
      const emptyMsg = screen.getByTestId('no-jobs-message');
      expect(emptyMsg.textContent).toContain('ยังไม่มีงานในเส้นทาง');
    });

    // ตรวจสอบปุ่มขยายรัศมี 10 กม.
    const expandBtn = screen.getByTestId('btn-expand-10km');
    expect(expandBtn).not.toBeNull();
    expect(expandBtn.textContent).toContain('ขยายรัศมีเป็น 10 กม.');

    // กดปุ่มขยายรัศมี
    fireEvent.click(expandBtn);

    // ตรวจสอบว่าระบบค้นหาด้วยรัศมี 10 กม. และแสดงการ์ดงานที่พบ
    await waitFor(() => {
      expect(getNearbyMock).toHaveBeenCalledTimes(2);
      const callArgs = getNearbyMock.mock.calls[1][0];
      expect(callArgs.radius_km).toBe(10.0);

      const jobCard = screen.getByTestId('job-card-order-s2-04');
      expect(jobCard).not.toBeNull();
    });
  });
});

