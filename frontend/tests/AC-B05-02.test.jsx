/**
 * Component Tests สำหรับ AC-B05-02: Quick Replies Preset Bar
 * (T-08: REQ-UX-001, CC-01, AC-B05-02, D-B05-03)
 */

import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import QuickRepliesBar from '../src/components/QuickRepliesBar.jsx';
import { DEFAULT_QUICK_REPLIES } from '../src/services/communicationApi.js';

describe('AC-B05-02: Quick Replies Preset Bar Component Tests', () => {
  it('renders 4 preset quick reply buttons with touch target >= 48px', () => {
    const handleSelect = vi.fn();

    render(
      <QuickRepliesBar
        quickReplies={DEFAULT_QUICK_REPLIES}
        onSelectQuickReply={handleSelect}
      />
    );

    const bar = screen.getByTestId('quick-replies-bar');
    expect(bar).not.toBeNull();

    const buttons = screen.getAllByTestId('quick-reply-btn');
    expect(buttons).toHaveLength(4);

    // ตรวจสอบขนาดทัชทาร์เก็ต min-h-[48px] ทุกปุ่ม
    buttons.forEach((btn) => {
      expect(btn.className).toContain('min-h-[48px]');
    });

    // ตรวจสอบการกดปุ่มแรก "กำลังเดินทางไปครับ"
    fireEvent.click(buttons[0]);
    expect(handleSelect).toHaveBeenCalledWith('กำลังเดินทางไปครับ');

    // ตรวจสอบการกดปุ่มที่สอง "ถึงหน้าบ้านแล้วครับ"
    fireEvent.click(buttons[1]);
    expect(handleSelect).toHaveBeenCalledWith('ถึงหน้าบ้านแล้วครับ');
  });

  it('disables all quick reply buttons when disabled prop is true', () => {
    render(
      <QuickRepliesBar
        quickReplies={DEFAULT_QUICK_REPLIES}
        onSelectQuickReply={() => {}}
        disabled={true}
      />
    );

    const buttons = screen.getAllByTestId('quick-reply-btn');
    buttons.forEach((btn) => {
      expect(btn.disabled).toBe(true);
    });
  });
});
