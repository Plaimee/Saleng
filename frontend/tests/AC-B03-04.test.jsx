/**
 * Component Tests สำหรับ AC-B03-04: PDPA PII & Coordinate Protection in Evaluation
 * (T-08: REQ-SEC-002, D-00-02, CC-06, D-B03-06)
 */

import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import JobEvaluationView from '../src/components/JobEvaluationView';
import { jobEvaluationApi } from '../src/services/jobEvaluationApi';

describe('AC-B03-04: PDPA PII & Coordinate Protection Component Tests', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('displays only subdistrict and district, masking exact house number and seller phone', async () => {
    const mockEval = {
      order_id: 'order-s2-pii-test',
      collector_id: 'saleng-01',
      vehicle_type: 'MOTORCYCLE',
      road_distance_km: 1.2,
      estimated_fuel_cost: 3.0,
      is_fallback_distance: false,
      total_est_weight_kg: 25.0,
      total_min_price: 150.0,
      total_max_price: 220.0,
      current_load_kg: 0.0,
      max_capacity_kg: 200.0,
      remaining_capacity_kg: 200.0,
      projected_total_load_kg: 25.0,
      is_capacity_exceeded: false,
      collector_is_online: true,
      collector_is_verified: true,
      can_claim_job: true,
      claim_block_reason: null,
      items: [],
      location_summary: {
        subdistrict_name: 'แขวงสามเสนนอก',
        district_name: 'เขตห้วยขวาง',
        fuzzed_lat: 13.795,
        fuzzed_lng: 100.581,
      },
    };

    vi.spyOn(jobEvaluationApi, 'evaluateJob').mockResolvedValue(mockEval);

    const { container } = render(<JobEvaluationView orderId="order-s2-pii-test" salengId="saleng-01" />);

    await waitFor(() => {
      const locEl = screen.getByTestId('location-subdistrict-text');
      expect(locEl).not.toBeNull();
      expect(locEl.textContent).toContain('แขวงสามเสนนอก เขตห้วยขวาง');
    });

    const fullHtml = container.innerHTML;

    // ตรวจสอบอย่างเข้มงวด: ต้องไม่มีบ้านเลขที่ เบอร์โทรศัพท์ หรือคำว่า 081 / ซอยรัชดา
    expect(fullHtml).not.toContain('บ้านเลขที่');
    expect(fullHtml).not.toContain('081-');
    expect(fullHtml).not.toContain('089-');
    expect(fullHtml).not.toContain('082-');
    expect(fullHtml).not.toContain('123/45');
    expect(fullHtml).not.toContain('ซอยประชาราษฎร์บำเพ็ญ 24');

    // ตรวจสอบข้อความเตือนความปลอดภัย PDPA
    expect(fullHtml).toContain('ซ่อนที่อยู่ละเอียดและพิกัดจริงเพื่อความปลอดภัยตาม PDPA');
  });
});
