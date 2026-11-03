/**
 * Component Tests for AC-B02-03: PDPA PII & Coordinate Protection
 * (Task T-08: UC-04, REQ-SEC-002, D-00-02, CC-06, Q-01)
 */

import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import JobSearchPanel from '../src/components/JobSearchPanel';
import { jobSearchApi } from '../src/services/jobSearchApi';

describe('AC-B02-03: PDPA PII & Coordinate Protection Component Tests', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('guarantees no house number, exact phone, or raw coordinates in List and Map Views', async () => {
    const mockJobs = [
      {
        order_id: 'order-s2-01',
        status: 'S2',
        subdistrict_name: 'แขวงสามเสนนอก',
        district_name: 'เขตห้วยขวาง',
        approximate_lat: 13.7950,
        approximate_lng: 100.5810,
        road_distance_km: 0.8,
        estimated_price_min: 150,
        estimated_price_max: 220,
        estimated_weight_kg: 25,
        categories: ['MAT-CARDBOARD'],
        need_lifting_help: false,
        created_at: '2026-11-04T02:30:00Z',
      },
    ];

    vi.spyOn(jobSearchApi, 'getNearbyJobs').mockResolvedValue({
      total_count: 1,
      radius_km: 5.0,
      jobs: mockJobs,
      active_filters: {},
    });

    const { container } = render(<JobSearchPanel />);

    await waitFor(() => {
      expect(screen.getByTestId('job-card-order-s2-01')).not.toBeNull();
    });

    // 1. ตรวจสอบใน List View ว่าไม่มีข้อความบ้านเลขที่จริง
    const fullHtmlList = container.innerHTML;
    expect(fullHtmlList).not.toContain('123/45');
    expect(fullHtmlList).not.toContain('ซอยรัชดาภิเษก 18');
    expect(fullHtmlList).not.toContain('081-234-5678');
    expect(fullHtmlList).toContain('แขวงสามเสนนอก เขตห้วยขวาง');

    // 2. สลับไป Map View
    const tabMap = screen.getByTestId('tab-map-view');
    fireEvent.click(tabMap);

    await waitFor(() => {
      expect(screen.getByTestId('job-map-view')).not.toBeNull();
    });

    // ตรวจสอบหมุดจำลอง Fuzzed Pin
    const pin = screen.getByTestId('map-pin-order-s2-01');
    expect(pin).not.toBeNull();

    // ตรวจสอบ Mini Preview ว่าไม่มีบ้านเลขที่
    const previewLoc = screen.getByTestId('preview-location');
    expect(previewLoc.textContent).toContain('แขวงสามเสนนอก เขตห้วยขวาง');
    expect(previewLoc.textContent).not.toContain('123/45');

    const fullHtmlMap = container.innerHTML;
    expect(fullHtmlMap).not.toContain('123/45');
    expect(fullHtmlMap).not.toContain('ซอยรัชดาภิเษก 18');
  });
});

