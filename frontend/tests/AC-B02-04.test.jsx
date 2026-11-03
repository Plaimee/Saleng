/**
 * Component Tests for AC-B02-04: GPS Disabled or Denied Handling
 * (Task T-08: UC-04, REQ-OP-002, AC-04-09, CC-02, E1)
 */

import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import JobSearchPanel from '../src/components/JobSearchPanel';
import { jobSearchApi } from '../src/services/jobSearchApi';

describe('AC-B02-04: GPS Disabled or Denied Handling Component Tests', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('displays GPS warning banner when permission is denied and retries on button click', async () => {
    vi.spyOn(jobSearchApi, 'getNearbyJobs').mockResolvedValue({
      total_count: 0,
      radius_km: 5.0,
      jobs: [],
    });

    // จำลอง navigator.geolocation ปฏิเสธ (Permission Denied)
    let callCount = 0;
    const mockGetCurrentPosition = vi.fn().mockImplementation((success, error) => {
      callCount++;
      if (callCount === 1) {
        error({ code: 1, message: 'User denied Geolocation' });
      } else {
        success({
          coords: { latitude: 13.7900, longitude: 100.5750 },
        });
      }
    });

    Object.defineProperty(globalThis.navigator, 'geolocation', {
      value: { getCurrentPosition: mockGetCurrentPosition },
      configurable: true,
      writable: true,
    });

    render(<JobSearchPanel />);

    // ตรวจสอบกล่องแจ้งเตือน GPS
    await waitFor(() => {
      const banner = screen.getByTestId('gps-warning-banner');
      expect(banner).not.toBeNull();
      expect(banner.textContent).toContain('กรุณาเปิด GPS เพื่อค้นหางานใกล้เคียง');
    });

    // ตรวจสอบปุ่มลองใหม่อีกครั้ง
    const retryBtn = screen.getByTestId('btn-retry-gps');
    expect(retryBtn).not.toBeNull();
    expect(retryBtn.textContent).toContain('ลองใหม่อีกครั้ง');

    // กดปุ่มลองใหม่อีกครั้ง
    fireEvent.click(retryBtn);

    // ตรวจสอบว่าเรียก getCurrentPosition อีกครั้ง
    expect(mockGetCurrentPosition).toHaveBeenCalledTimes(2);
  });
});
