/**
 * Vitest Component Test สำหรับ AC-S01-03: SellerProfileCard
 * รองรับ UC-01, REQ-SEC-002, EV-09, AC-S01-03
 */

import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import SellerProfileCard from '../src/components/SellerProfileCard';
import { accountApi } from '../src/services/accountApi';

describe('AC-S01-03: SellerProfileCard Component & PDPA Masking', () => {
  const mockProfile = {
    seller_id: 'SEL-001',
    display_name: 'คุณสมชาย รักสะอาด',
    phone_masked: '08X-XXX-8899',
  };

  it('displays PDPA masked phone number and seller name', () => {
    render(
      <SellerProfileCard
        profile={mockProfile}
        onProfileUpdated={vi.fn()}
        onLogout={vi.fn()}
      />
    );

    const nameEl = screen.getByTestId('profile-name');
    expect(nameEl).not.toBeNull();
    expect(nameEl.textContent).toContain('คุณสมชาย รักสะอาด');

    const phoneEl = screen.getByTestId('profile-phone-masked');
    expect(phoneEl).not.toBeNull();
    expect(phoneEl.textContent).toBe('08X-XXX-8899');
  });

  it('allows inline editing of display name and calls updateProfile', async () => {
    vi.spyOn(accountApi, 'updateProfile').mockResolvedValue({
      seller_id: 'SEL-001',
      display_name: 'คุณสมชาย ใจดี',
      phone_masked: '08X-XXX-8899',
    });

    const handleUpdated = vi.fn();
    render(
      <SellerProfileCard
        profile={mockProfile}
        onProfileUpdated={handleUpdated}
        onLogout={vi.fn()}
      />
    );

    // Click edit button
    const editBtn = screen.getByTestId('edit-profile-btn');
    fireEvent.click(editBtn);

    const nameInput = screen.getByTestId('edit-name-input');
    fireEvent.change(nameInput, { target: { value: 'คุณสมชาย ใจดี' } });

    const saveBtn = screen.getByTestId('save-name-btn');
    fireEvent.click(saveBtn);

    await waitFor(() => {
      expect(accountApi.updateProfile).toHaveBeenCalledWith('SEL-001', 'คุณสมชาย ใจดี');
      expect(handleUpdated).toHaveBeenCalledWith(
        expect.objectContaining({ display_name: 'คุณสมชาย ใจดี' })
      );
    });
  });
});

