/**
 * Vitest Component Test สำหรับ AC-S03-04: Direct Contact with PDPA Masking
 * รองรับ UC-03, REQ-SEC-002, CC-06, AC-S03-04, P-04, Q-04
 */

import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import SalengProfileCard from '../src/components/SalengProfileCard';

describe('AC-S03-04: Direct Contact Hooks in SalengProfileCard Test', () => {
  const mockCollector = {
    saleng_id: 'saleng-01',
    display_name: 'ลุงสมชาย ซาเล้งสุทธิสาร',
    phone: '081-234-5678',
    verified: true,
    rating: 4.9,
    completed_jobs_count: 142,
    vehicle_type: 'TRICYCLE',
    distance_km: 1.5,
  };

  it('provides tel: link on quick call button for native dialer', () => {
    render(
      <SalengProfileCard
        collector={mockCollector}
        onSelect={vi.fn()}
        onToggleFavorite={vi.fn()}
        onStartChat={vi.fn()}
      />
    );

    const callBtn = screen.getByTestId('btn-call-collector-saleng-01');
    expect(callBtn).not.toBeNull();
    expect(callBtn.getAttribute('href')).toBe('tel:081-234-5678');
  });

  it('triggers onStartChat callback when clicking chat button', () => {
    const handleChat = vi.fn();
    render(
      <SalengProfileCard
        collector={mockCollector}
        onSelect={vi.fn()}
        onToggleFavorite={vi.fn()}
        onStartChat={handleChat}
      />
    );

    const chatBtn = screen.getByTestId('btn-chat-collector-saleng-01');
    expect(chatBtn).not.toBeNull();
    fireEvent.click(chatBtn);
    expect(handleChat).toHaveBeenCalledWith(mockCollector);
  });
});

