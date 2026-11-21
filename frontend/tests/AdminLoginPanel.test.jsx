/** AC-A01-05: Admin portal login gate */
import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import AdminLoginPanel from '../src/components/admin/AdminLoginPanel';

describe('AdminLoginPanel', () => {
  it('AC-A01-05 rejects invalid credentials', () => {
    render(<AdminLoginPanel onLoginSuccess={vi.fn()} />);
    fireEvent.change(screen.getByLabelText('ชื่อผู้ใช้'), { target: { value: 'wrong' } });
    fireEvent.change(screen.getByLabelText('รหัสผ่าน'), { target: { value: 'wrong' } });
    fireEvent.click(screen.getByRole('button', { name: 'เข้าสู่ระบบ' }));
    expect(screen.getByRole('alert').textContent).toContain('ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง');
  });

  it('AC-A01-05 accepts demo admin credentials', () => {
    const onLoginSuccess = vi.fn();
    render(<AdminLoginPanel onLoginSuccess={onLoginSuccess} />);
    fireEvent.change(screen.getByLabelText('ชื่อผู้ใช้'), { target: { value: 'admin' } });
    fireEvent.change(screen.getByLabelText('รหัสผ่าน'), { target: { value: 'admin123' } });
    fireEvent.click(screen.getByRole('button', { name: 'เข้าสู่ระบบ' }));
    expect(onLoginSuccess).toHaveBeenCalledOnce();
  });
});
