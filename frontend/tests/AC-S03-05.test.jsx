/**
 * Vitest Component Test สำหรับ AC-S03-05: DirectRequestModal & 15-Min Countdown
 * รองรับ UC-03, REQ-SEC-001, MD-STM-04, AC-S03-05, P-05, Q-01
 */

import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import DirectRequestModal from '../src/components/DirectRequestModal';

describe('AC-S03-05: DirectRequestModal Component Test', () => {
  const mockCollector = {
    saleng_id: 'saleng-01',
    display_name: 'ลุงสมชาย ซาเล้งสุทธิสาร',
    rating: 4.9,
    vehicle_type: 'TRICYCLE',
    distance_km: 1.2,
  };

  it('renders modal with collector info and 15-minute countdown alert', () => {
    render(
      <DirectRequestModal
        collector={mockCollector}
        isOpen={true}
        onClose={vi.fn()}
        onConfirm={vi.fn()}
      />
    );

    const modal = screen.getByTestId('direct-request-modal');
    expect(modal).not.toBeNull();
    expect(modal.textContent).toContain('นัดหมาย ลุงสมชาย ซาเล้งสุทธิสาร');
    expect(modal.textContent).toContain('เวลารอตอบรับ 15 นาที');
  });

  it('allows entering notes and clicking confirm button', () => {
    const handleConfirm = vi.fn();
    render(
      <DirectRequestModal
        collector={mockCollector}
        isOpen={true}
        onClose={vi.fn()}
        onConfirm={handleConfirm}
      />
    );

    const notesInput = screen.getByTestId('direct-request-notes');
    fireEvent.change(notesInput, { target: { value: 'สะดวกช่วงบ่ายสองครับ' } });
    expect(notesInput.value).toBe('สะดวกช่วงบ่ายสองครับ');

    const confirmBtn = screen.getByTestId('modal-confirm-btn');
    fireEvent.click(confirmBtn);
    expect(handleConfirm).toHaveBeenCalledWith('saleng-01', 'สะดวกช่วงบ่ายสองครับ');
  });
});

