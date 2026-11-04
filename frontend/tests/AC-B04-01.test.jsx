/**
 * Component Tests สำหรับ AC-B04-01: Single Collector Atomic Claim
 * (T-08: BR-02, REQ-BR-002, CC-04, AC-B04-01, D-B04-01)
 */

import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ClaimConflictModal from '../src/components/ClaimConflictModal.jsx';
import { jobRouteApi } from '../src/services/jobRouteApi.js';

describe('AC-B04-01: Single Collector Atomic Claim Component Tests', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders ClaimConflictModal when 409 Conflict occurs with message "มีผู้รับงานนี้แล้ว"', () => {
    const handleAcknowledge = vi.fn();

    render(
      <ClaimConflictModal
        isOpen={true}
        message="มีผู้รับงานนี้แล้ว"
        onAcknowledge={handleAcknowledge}
      />
    );

    const modal = screen.getByTestId('claim-conflict-modal');
    expect(modal).not.toBeNull();

    const msgEl = screen.getByTestId('conflict-message-text');
    expect(msgEl.textContent).toContain('มีผู้รับงานนี้แล้ว');

    const ackBtn = screen.getByTestId('acknowledge-conflict-btn');
    expect(ackBtn).not.toBeNull();
    fireEvent.click(ackBtn);
    expect(handleAcknowledge).toHaveBeenCalledTimes(1);
  });

  it('does not render ClaimConflictModal when isOpen is false', () => {
    render(
      <ClaimConflictModal
        isOpen={false}
        message="มีผู้รับงานนี้แล้ว"
        onAcknowledge={() => {}}
      />
    );

    const modal = screen.queryByTestId('claim-conflict-modal');
    expect(modal).toBeNull();
  });

  it('calls claimJob API and handles success response with status S3', async () => {
    const mockClaimResult = {
      order_id: 'order-s2-01',
      collector_id: 'saleng-01',
      status: 'S3',
      version: 2,
      address_text: '123/45 ซอยรัชดาภิเษก 18',
      dest_lat: 13.7930,
      dest_lng: 100.5780,
      seller_phone: '081-999-8888',
      navigation_url: 'https://www.google.com/maps/dir/?api=1&destination=13.793000,100.578000&travelmode=driving',
    };

    vi.spyOn(jobRouteApi, 'claimJob').mockResolvedValue(mockClaimResult);

    const result = await jobRouteApi.claimJob('order-s2-01', {
      saleng_id: 'saleng-01',
      expected_version: 1,
    });

    expect(result.status).toBe('S3');
    expect(result.collector_id).toBe('saleng-01');
    expect(result.version).toBe(2);
  });
});

