/**
 * Component Tests สำหรับ AC-B04-05: In-Transit Status Transition & Seller Cancel Lock
 * (T-08: BR-03, UC-09, AC-B04-05)
 */

import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import ActiveJobCard from '../src/components/ActiveJobCard.jsx';

describe('AC-B04-05: In-Transit Status Transition Component Tests', () => {
  const mockS3Job = {
    order_id: 'order-s2-01',
    status: 'S3',
    seller_name: 'สมชาย ใจดี',
    address_text: '123/45 ซอยรัชดาภิเษก 18',
    seller_phone: '081-999-8888',
    est_weight_kg: 25.0,
    appointment_slot: '10:00 - 12:00 น.',
    sequence_order: 1,
    navigation_url: 'https://www.google.com/maps/dir/?api=1&destination=13.793000,100.578000&travelmode=driving',
  };

  const mockS4Job = {
    ...mockS3Job,
    status: 'S4',
  };

  it('triggers onStartTransit when user clicks start-transit button in status S3', () => {
    const handleStartTransit = vi.fn();

    render(<ActiveJobCard job={mockS3Job} onStartTransit={handleStartTransit} />);

    const transitBtn = screen.getByTestId('start-transit-btn');
    expect(transitBtn).not.toBeNull();
    expect(transitBtn.textContent).toContain('ออกเดินทาง');
    expect(transitBtn.disabled).toBe(false);

    fireEvent.click(transitBtn);
    expect(handleStartTransit).toHaveBeenCalledWith('order-s2-01');
  });

  it('disables start-transit button and hides cancel button when job is in status S4 (In-Transit) (BR-03)', () => {
    render(<ActiveJobCard job={mockS4Job} />);

    const transitBtn = screen.getByTestId('start-transit-btn');
    expect(transitBtn.textContent).toContain('กำลังเดินทาง...');
    expect(transitBtn.disabled).toBe(true);

    // Cancel button must NOT be present in S4
    const cancelBtn = screen.queryByTestId('cancel-job-btn');
    expect(cancelBtn).toBeNull();

    // Job status badge shows S4
    const badge = screen.getByTestId('job-status-badge');
    expect(badge.textContent).toContain('กำลังเดินทาง (S4)');
  });
});

