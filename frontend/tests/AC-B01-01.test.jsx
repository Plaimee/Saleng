/**
 * Vitest Component Test สำหรับ AC-B01-01: Collector Phone Registration & Session Persistence
 * รองรับ UC-01, REQ-UX-001, REQ-SEC-002, REQ-QA-001, AC-B01-01, Q-01
 */

import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import CollectorPhoneLoginForm from '../src/components/CollectorPhoneLoginForm';
import CollectorProfileCard from '../src/components/CollectorProfileCard';
import { collectorAccountApi } from '../src/services/collectorAccountApi';

describe('AC-B01-01: Collector Phone Registration & Auth', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    localStorage.clear();
  });

  it('renders phone input and requests OTP on submit (AC-B01-01)', async () => {
    vi.spyOn(collectorAccountApi, 'requestOtp').mockResolvedValue({
      phone_masked: '08X-XXX-5678',
      expires_in_seconds: 300,
      mock_otp: '123456',
    });

    render(<CollectorPhoneLoginForm onLoginSuccess={vi.fn()} />);

    const phoneInput = screen.getByTestId('phone-input');
    expect(phoneInput).not.toBeNull();

    fireEvent.change(phoneInput, { target: { value: '0812345678' } });
    const requestBtn = screen.getByTestId('request-otp-btn');
    expect(requestBtn).not.toBeNull();
    fireEvent.click(requestBtn);

    await waitFor(() => {
      expect(collectorAccountApi.requestOtp).toHaveBeenCalledWith('0812345678');
      const otpInput = screen.getByTestId('otp-input');
      expect(otpInput).not.toBeNull();
    });
  });

  it('verifies OTP and triggers onLoginSuccess callback (AC-B01-01)', async () => {
    vi.spyOn(collectorAccountApi, 'requestOtp').mockResolvedValue({
      phone_masked: '08X-XXX-5678',
      expires_in_seconds: 300,
      mock_otp: '123456',
    });

    const mockAuthResponse = {
      saleng_id: 'saleng-01',
      display_name: 'ลุงสมชาย ซาเล้งสุทธิสาร',
      phone_masked: '08X-XXX-5678',
      session_token: 'saleng_tok_test_123',
      verified: false,
      kyc_status: 'UNVERIFIED',
      vehicle_type: 'TRICYCLE',
      max_capacity_kg: 150.0,
    };
    vi.spyOn(collectorAccountApi, 'verifyOtp').mockResolvedValue(mockAuthResponse);

    const onLoginSuccess = vi.fn();
    render(<CollectorPhoneLoginForm onLoginSuccess={onLoginSuccess} />);

    // Step 1: Request OTP
    const phoneInput = screen.getByTestId('phone-input');
    fireEvent.change(phoneInput, { target: { value: '0812345678' } });
    fireEvent.click(screen.getByTestId('request-otp-btn'));

    // Step 2: Verify OTP
    await waitFor(() => {
      expect(screen.getByTestId('otp-input')).not.toBeNull();
    });

    const verifyBtn = screen.getByTestId('verify-otp-btn');
    fireEvent.click(verifyBtn);

    await waitFor(() => {
      expect(collectorAccountApi.verifyOtp).toHaveBeenCalledWith('0812345678', '123456');
      expect(onLoginSuccess).toHaveBeenCalledWith(mockAuthResponse);
    });
  });

  it('displays masked phone number 08X-XXX-XXXX in CollectorProfileCard (REQ-SEC-002)', () => {
    const profile = {
      saleng_id: 'saleng-01',
      display_name: 'ลุงสมชาย ซาเล้งสุทธิสาร',
      phone_masked: '08X-XXX-5678',
      rating: 4.9,
      completed_jobs_count: 142,
      kyc_status: 'UNVERIFIED',
    };

    render(<CollectorProfileCard profile={profile} onLogout={vi.fn()} />);

    const phoneEl = screen.getByTestId('collector-phone-masked');
    expect(phoneEl).not.toBeNull();
    expect(phoneEl.textContent).toContain('08X-XXX-5678');

    const logoutBtn = screen.getByTestId('logout-btn');
    expect(logoutBtn).not.toBeNull();
  });
});

