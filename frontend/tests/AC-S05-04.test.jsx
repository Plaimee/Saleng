/**
 * Vitest Component Test สำหรับ AC-S05-04: In-Transit ETA & Distance Display
 * รองรับ UC-04, CC-02, CC-03, D-00-01, REQ-FN-003, AC-S05-04, P-04, Q-03
 */

import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import InTransitTrackingCard from '../src/components/InTransitTrackingCard';

describe('AC-S05-04: In-Transit ETA & Distance Display (CC-02)', () => {
  const mockSaleng = {
    saleng_id: 'saleng-01',
    name: 'ลุงสมชาย ซาเล้งสุทธิสาร',
    phone: '081-234-5678',
    vehicle_type: 'ซาเล้งพ่วงข้าง',
    rating: 4.9,
    kyc_verified: true,
  };

  it('displays real-time ETA and remaining distance when in S4 (In-Transit)', () => {
    render(
      <InTransitTrackingCard
        status="S4"
        assignedSaleng={mockSaleng}
        distanceKm={3.8}
        etaMinutes={15}
        canCancel={false}
      />
    );

    // ตรวจสอบ ETA
    const etaBadge = screen.getByTestId('eta-badge');
    expect(etaBadge).not.toBeNull();
    expect(etaBadge.textContent).toContain('15 นาที');

    // ตรวจสอบระยะทาง
    const distBadge = screen.getByTestId('distance-badge');
    expect(distBadge).not.toBeNull();
    expect(distBadge.textContent).toContain('3.8 กม.');

    // ตรวจสอบข้อมูลซาเล้ง และป้าย KYC 100%
    expect(screen.getByText('ลุงสมชาย ซาเล้งสุทธิสาร')).not.toBeNull();
    const kycBadge = screen.getByTestId('kyc-badge');
    expect(kycBadge).not.toBeNull();
    expect(kycBadge.textContent).toContain('KYC 100%');

    // ตรวจสอบปุ่มโทร
    const callBtn = screen.getByTestId('btn-call-saleng');
    expect(callBtn).not.toBeNull();
    expect(callBtn.getAttribute('href')).toBe('tel:081-234-5678');
  });
});

