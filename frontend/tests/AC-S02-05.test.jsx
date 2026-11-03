/**
 * Vitest Component Test สำหรับ AC-S02-05: LiftingHelpToggle
 * รองรับ UC-02, REQ-FN-004, MD-DOM-04, AC-S02-05
 */

import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import LiftingHelpToggle from '../src/components/LiftingHelpToggle';

describe('AC-S02-05: LiftingHelpToggle Component', () => {
  it('toggles needLiftingHelp checkbox and notifies parent callback', () => {
    const handleToggle = vi.fn();
    render(
      <LiftingHelpToggle
        needLiftingHelp={false}
        liftingHelpNotes=""
        onToggleHelp={handleToggle}
        onChangeNotes={vi.fn()}
      />
    );

    const checkbox = screen.getByTestId('lifting-help-checkbox');
    expect(checkbox.checked).toBe(false);
    expect(screen.queryByTestId('lifting-help-badge')).toBeNull();
    expect(screen.queryByTestId('lifting-help-notes-input')).toBeNull();

    fireEvent.click(checkbox);
    expect(handleToggle).toHaveBeenCalledWith(true);
  });

  it('renders badge and allows editing notes when needLiftingHelp is true', () => {
    const handleChangeNotes = vi.fn();
    render(
      <LiftingHelpToggle
        needLiftingHelp={true}
        liftingHelpNotes="ตู้เย็น 10 คิว อยู่ชั้น 3 ไม่มีลิฟต์"
        onToggleHelp={vi.fn()}
        onChangeNotes={handleChangeNotes}
      />
    );

    // ตรวจสอบ badge ขอคนช่วยยก
    const badge = screen.getByTestId('lifting-help-badge');
    expect(badge).not.toBeNull();
    expect(badge.textContent).toContain('⚠️ ขอคนช่วยยก');

    // ตรวจสอบ textarea หมายเหตุหน้างาน
    const notesInput = screen.getByTestId('lifting-help-notes-input');
    expect(notesInput).not.toBeNull();
    expect(notesInput.value).toBe('ตู้เย็น 10 คิว อยู่ชั้น 3 ไม่มีลิฟต์');

    fireEvent.change(notesInput, {
      target: { value: 'ตู้เย็น 10 คิว อยู่ชั้น 3 ไม่มีลิฟต์ ต้องใช้ 2 คนยก' },
    });
    expect(handleChangeNotes).toHaveBeenCalledWith(
      'ตู้เย็น 10 คิว อยู่ชั้น 3 ไม่มีลิฟต์ ต้องใช้ 2 คนยก'
    );
  });
});

