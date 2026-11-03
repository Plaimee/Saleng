/**
 * Vitest Component Test สำหรับ AC-S03-01: SalengProfileCard & KYC Badge
 * รองรับ UC-03, REQ-QA-001, AC-S03-01
 */

import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import SalengProfileCard from '../src/components/SalengProfileCard';

describe('AC-S03-01: SalengProfileCard Component Test', () => {
  const mockCollector = {
    saleng_id: 'saleng-01',
    display_name: 'ลุงสมชาย ซาเล้งสุทธิสาร',
    phone: '081-234-5678',
    avatar_url: 'https://example.com/avatar.jpg',
    verified: true,
    rating: 4.9,
    completed_jobs_count: 142,
    vehicle_type: 'TRICYCLE',
    distance_km: 1.5,
    is_favorite: false,
  };

  it('renders saleng profile details and KYC 100% verified badge', () => {
    render(
      <SalengProfileCard
        collector={mockCollector}
        onSelect={vi.fn()}
        onToggleFavorite={vi.fn()}
        onStartChat={vi.fn()}
      />
    );

    // ตรวจสอบชื่อและยานพาหนะ
    expect(screen.getByText('ลุงสมชาย ซาเล้งสุทธิสาร')).not.toBeNull();
    expect(screen.getByText('ซาเล้งสามล้อ')).not.toBeNull();
    expect(screen.getByText('1.5 กม.')).not.toBeNull();

    // ตรวจสอบป้ายยืนยันตัวตนแล้ว 100% (KYC Badge)
    const kycBadge = screen.getByTestId('kyc-badge');
    expect(kycBadge).not.toBeNull();
    expect(kycBadge.textContent).toContain('ยืนยันตัวตนแล้ว 100%');
  });

  it('triggers onSelect when clicking select collector button', () => {
    const handleSelect = vi.fn();
    render(
      <SalengProfileCard
        collector={mockCollector}
        onSelect={handleSelect}
        onToggleFavorite={vi.fn()}
        onStartChat={vi.fn()}
      />
    );

    const selectBtn = screen.getByTestId('btn-select-collector-saleng-01');
    expect(selectBtn).not.toBeNull();
    fireEvent.click(selectBtn);
    expect(handleSelect).toHaveBeenCalledWith(mockCollector);
  });
});

