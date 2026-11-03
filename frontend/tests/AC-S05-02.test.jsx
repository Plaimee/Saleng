/**
 * Vitest Component Test สำหรับ AC-S05-02: Real-Time 9-State Timeline Stepper
 * รองรับ UC-04, MD-STM-04, REQ-FN-003, AC-S05-02, P-02
 */

import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import StatusTimelineStepper from '../src/components/StatusTimelineStepper';

describe('AC-S05-02: StatusTimelineStepper Component Test', () => {
  it('renders 5 steps and highlights the active step correctly', () => {
    render(
      <StatusTimelineStepper
        status="S4"
        statusLabel="กำลังเดินทางมาหาคุณ"
        stepperStep={3}
        scheduledTimeDisplay="เรียกทันที (ด่วนใน 1–2 ชม.)"
      />
    );

    // ตรวจสอบแผง Stepper
    expect(screen.getByTestId('status-stepper')).not.toBeNull();
    const label = screen.getByTestId('status-label');
    expect(label.textContent).toBe('กำลังเดินทางมาหาคุณ');

    // ตรวจสอบทั้ง 5 ขั้น
    for (let i = 1; i <= 5; i++) {
      expect(screen.getByTestId(`stepper-step-${i}`)).not.toBeNull();
    }

    // ขั้นที่ 3 กำลังเดินทาง ต้อง active
    const step3 = screen.getByTestId('stepper-step-3');
    expect(step3.getAttribute('data-active')).toBe('true');

    // ขั้นที่ 1 และ 2 ต้อง completed
    expect(screen.getByTestId('stepper-step-1').getAttribute('data-completed')).toBe('true');
    expect(screen.getByTestId('stepper-step-2').getAttribute('data-completed')).toBe('true');
  });

  it('renders cancellation banner when status is S8 (Cancelled)', () => {
    render(
      <StatusTimelineStepper
        status="S8"
        statusLabel="ยกเลิกนัดหมายแล้ว"
        stepperStep={1}
        cancellationReason="ติดธุระด่วน ไม่สะดวกอยู่บ้าน"
      />
    );

    const banner = screen.getByTestId('cancellation-banner');
    expect(banner).not.toBeNull();
    expect(banner.textContent).toContain('นัดหมายนี้ถูกยกเลิกแล้ว');
    expect(banner.textContent).toContain('ติดธุระด่วน ไม่สะดวกอยู่บ้าน');
  });

  it('renders dispute banner when status is S9 (Dispute)', () => {
    render(
      <StatusTimelineStepper
        status="S9"
        statusLabel="เกิดข้อพิพาท/ระงับชั่วคราว"
        stepperStep={4}
      />
    );

    const banner = screen.getByTestId('dispute-banner');
    expect(banner).not.toBeNull();
    expect(banner.textContent).toContain('มีข้อพิพาท');
  });
});

