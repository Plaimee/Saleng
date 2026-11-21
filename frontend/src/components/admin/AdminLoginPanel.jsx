/**
 * หน้าเข้าสู่ระบบแอดมินสำหรับหน้าพอร์ทัลแยก /admin
 * รองรับ UC-11, AC-A01-05
 */
import React, { useState } from 'react';

export default function AdminLoginPanel({ onLoginSuccess }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (event) => {
    event.preventDefault();
    if (username === 'admin' && password === 'admin123') {
      setError('');
      onLoginSuccess();
      return;
    }
    setError('ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง');
  };

  return (
    <div
      data-req="AC-A01-05"
      className="max-w-md mx-auto mt-8 rounded-2xl border border-indigo-100 bg-white p-6 shadow-sm"
    >
      <h2 className="text-xl font-black text-indigo-900">เข้าสู่ระบบแอดมิน</h2>
      <p className="mt-1 text-sm text-gray-500">พอร์ทัลจัดการ KYC และความปลอดภัย</p>
      <form onSubmit={handleSubmit} className="mt-5 space-y-4">
        <label className="block">
          <span className="text-sm font-bold text-gray-700">ชื่อผู้ใช้</span>
          <input
            type="text"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            className="mt-1 min-h-[48px] w-full rounded-xl border border-gray-300 px-3"
            autoComplete="username"
          />
        </label>
        <label className="block">
          <span className="text-sm font-bold text-gray-700">รหัสผ่าน</span>
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="mt-1 min-h-[48px] w-full rounded-xl border border-gray-300 px-3"
            autoComplete="current-password"
          />
        </label>
        {error && (
          <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
            {error}
          </p>
        )}
        <button
          type="submit"
          className="min-h-[48px] w-full rounded-xl bg-indigo-700 px-4 font-bold text-white"
        >
          เข้าสู่ระบบ
        </button>
      </form>
    </div>
  );
}
