/**
 * Vitest Component Test สำหรับ AC-S05-01: การเลือกสล็อตเวลานัดหมายและการส่งคำขอ
 * รองรับ UC-04, REQ-FN-003, REQ-UX-001, AC-S05-01, P-01, Q-01
 */

import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import BookingSlotSelector from '../src/components/BookingSlotSelector';

describe('AC-S05-01: BookingSlotSelector Component Test', () => {
  it('defaults to IMMEDIATE booking and submits correctly', () => {
    const handleConfirm = vi.fn();
    render(<BookingSlotSelector onConfirmBooking={handleConfirm} />);

    // ตรวจสอบแผงสล็อต
    expect(screen.getByTestId('booking-slot-selector')).not.toBeNull();
    const btnImmediate = screen.getByTestId('slot-immediate-btn');
    expect(btnImmediate).not.toBeNull();

    // กดปุ่มยืนยัน
    const submitBtn = screen.getByTestId('confirm-booking-btn');
    expect(submitBtn).not.toBeNull();
    fireEvent.click(submitBtn);

    expect(handleConfirm).toHaveBeenCalledWith({
      booking_type: 'IMMEDIATE',
      scheduled_date: null,
      scheduled_slot: null,
      notes: '',
    });
  });

  it('allows switching to SCHEDULED booking and selecting slot and date', () => {
    const handleConfirm = vi.fn();
    render(<BookingSlotSelector onConfirmBooking={handleConfirm} />);

    // สลับเป็นนัดล่วงหน้า
    const btnScheduled = screen.getByTestId('slot-scheduled-btn');
    fireEvent.click(btnScheduled);

    // ตรวจสอบอินพุตวันที่และสล็อต
    const dateInput = screen.getByTestId('booking-date-input');
    expect(dateInput).not.toBeNull();
    fireEvent.change(dateInput, { target: { value: '2026-11-10' } });

    // เลือกช่วงบ่าย
    const afternoonSlot = screen.getByTestId('slot-option-AFTERNOON_13_16');
    expect(afternoonSlot).not.toBeNull();
    fireEvent.click(afternoonSlot);

    // ระบุหมายเหตุ
    const notesInput = screen.getByTestId('booking-notes-input');
    fireEvent.change(notesInput, { target: { value: 'เข้าซอย 4 บ้านรั้วสีเขียว' } });

    // ยืนยัน
    const submitBtn = screen.getByTestId('confirm-booking-btn');
    fireEvent.click(submitBtn);

    expect(handleConfirm).toHaveBeenCalledWith({
      booking_type: 'SCHEDULED',
      scheduled_date: '2026-11-10',
      scheduled_slot: 'AFTERNOON_13_16',
      notes: 'เข้าซอย 4 บ้านรั้วสีเขียว',
    });
  });
});
