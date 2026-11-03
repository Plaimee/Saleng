/**
 * Vitest Component Test สำหรับ AC-S01-01: PhoneOtpLoginForm
 * รองรับ UC-01, REQ-UX-002, REQ-QA-001, AC-S01-01
 */

import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import PhoneOtpLoginForm from '../src/components/PhoneOtpLoginForm';
import { accountApi } from '../src/services/accountApi';

describe('AC-S01-01: PhoneOtpLoginForm Component', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders phone input and requests OTP on submit', async () => {
    vi.spyOn(accountApi, 'requestOtp').mockResolvedValue({
      phone_masked: '08X-XXX-5678',
      expires_in_seconds: 300,
      mock_otp: '123456',
    });

    render(<PhoneOtpLoginForm onLoginSuccess={vi.fn()} />);

    const phoneInput = screen.getByTestId('phone-input');
    expect(phoneInput).toBeDefined();

    fireEvent.change(phoneInput, { target: { value: '0812345678' } });
    const requestBtn = screen.getByTestId('request-otp-btn');
    fireEvent.click(requestBtn);

    await waitFor(() => {
      expect(accountApi.requestOtp).toHaveBeenCalledWith('0812345678');
      const otpInput = screen.getByTestId('otp-input');
      expect(otpInput).toBeDefined();
    });
  });

  it('verifies OTP and triggers onLoginSuccess callback', async () => {
    vi.spyOn(accountApi, 'requestOtp').mockResolvedValue({
      phone_masked: '08X-XXX-5678',
      expires_in_seconds: 300,
      mock_otp: '123456',
    });
    const mockAuth = {
      session_token: 'token-xyz',
      seller_id: 'SEL-001',
      display_name: 'ผู้ขาย ทดสอบ',
    };
    vi.spyOn(accountApi, 'verifyOtp').mockResolvedValue(mockAuth);

    const handleSuccess = vi.fn();
    render(<PhoneOtpLoginForm onLoginSuccess={handleSuccess} />);

    // Step 1: Request OTP
    fireEvent.change(screen.getByTestId('phone-input'), { target: { value: '0812345678' } });
    fireEvent.click(screen.getByTestId('request-otp-btn'));

    // Step 2: Verify OTP
    await waitFor(() => {
      const otpInput = screen.getByTestId('otp-input');
      expect(otpInput).toBeDefined();
    });

    const verifyBtn = screen.getByTestId('verify-otp-btn');
    fireEvent.click(verifyBtn);

    await waitFor(() => {
      expect(accountApi.verifyOtp).toHaveBeenCalledWith('0812345678', '123456');
      expect(handleSuccess).toHaveBeenCalledWith(mockAuth);
    });
  });
});

