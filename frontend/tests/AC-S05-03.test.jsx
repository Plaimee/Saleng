/**
 * Vitest Component Test สำหรับ AC-S05-03: Pre-Transit Cancellation Enforcement (BR-03)
 * รองรับ UC-04, BR-03, REQ-FN-003, AC-S05-03, P-03, Q-02
 */

import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import InTransitTrackingCard from '../src/components/InTransitTrackingCard';

describe('AC-S05-03: Pre-Transit Cancellation Enforcement (BR-03)', () => {
  const mockSaleng = {
    saleng_id: 'saleng-01',
    name: 'ลุงสมชาย ซาเล้งสุทธิสาร',
    phone: '081-234-5678',
    vehicle_type: 'ซาเล้งพ่วงข้าง',
    rating: 4.9,
    kyc_verified: true,
  };

  it('allows cancellation when status is S2/S3 (canCancel is true)', () => {
    const handleOpenCancel = vi.fn();
    render(
      <InTransitTrackingCard
        status="S3"
        assignedSaleng={mockSaleng}
        canCancel={true}
        onOpenCancelModal={handleOpenCancel}
      />
    );

    const cancelBtn = screen.getByTestId('btn-cancel-booking');
    expect(cancelBtn).not.toBeNull();
    expect(cancelBtn.disabled).toBe(false);
    expect(cancelBtn.textContent).toContain('ยกเลิกการนัดหมาย');

    fireEvent.click(cancelBtn);
    expect(handleOpenCancel).toHaveBeenCalledTimes(1);
  });

  it('locks cancellation button and shows BR-03 warning when status is S4 (In-Transit)', () => {
    const handleOpenCancel = vi.fn();
    render(
      <InTransitTrackingCard
        status="S4"
        assignedSaleng={mockSaleng}
        distanceKm={2.4}
        etaMinutes={12}
        canCancel={false}
        onOpenCancelModal={handleOpenCancel}
      />
    );

    const cancelBtn = screen.getByTestId('btn-cancel-booking');
    expect(cancelBtn).not.toBeNull();
    expect(cancelBtn.disabled).toBe(true);
    expect(cancelBtn.textContent).toContain('ล็อกปุ่มยกเลิกตามกฎ BR-03');

    // ตรวจสอบคำเตือนกฎ BR-03
    const warning = screen.getByTestId('br03-warning');
    expect(warning).not.toBeNull();
    expect(warning.textContent).toContain('ไม่สามารถยกเลิกได้เนื่องจากซาเล้งกำลังเดินทางมายังหน้างานแล้วตามกฎ BR-03');

    // คลิกแล้วต้องไม่เรียก handleOpenCancel
    fireEvent.click(cancelBtn);
    expect(handleOpenCancel).not.toHaveBeenCalled();
  });
});

