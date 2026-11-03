/**
 * แผงเลือกช่วงเวลานัดหมายและยืนยันส่งคำขอ (BookingSlotSelector)
 * รองรับ UC-04, REQ-FN-003, REQ-UX-001, AC-S05-01, P-01, Q-01
 */

import React, { useState } from 'react';

const SLOTS = [
  { id: 'MORNING_09_12', label: 'ช่วงเช้า', time: '09:00 – 12:00 น.', icon: '🌅' },
  { id: 'AFTERNOON_13_16', label: 'ช่วงบ่าย', time: '13:00 – 16:00 น.', icon: '☀️' },
  { id: 'EVENING_16_18', label: 'ช่วงเย็น', time: '16:00 – 18:00 น.', icon: '🌆' },
];

export default function BookingSlotSelector({ onConfirmBooking, loading = false }) {
  const [bookingType, setBookingType] = useState('IMMEDIATE'); // 'IMMEDIATE' | 'SCHEDULED'
  const [scheduledDate, setScheduledDate] = useState(
    new Date(Date.now() + 86400000).toISOString().split('T')[0]
  );
  const [scheduledSlot, setScheduledSlot] = useState('MORNING_09_12');
  const [notes, setNotes] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onConfirmBooking({
      booking_type: bookingType,
      scheduled_date: bookingType === 'SCHEDULED' ? scheduledDate : null,
      scheduled_slot: bookingType === 'SCHEDULED' ? scheduledSlot : null,
      notes,
    });
  };

  return (
    <form
      data-req="UC-04"
      data-testid="booking-slot-selector"
      onSubmit={handleSubmit}
      className="p-4 bg-white rounded-3xl border border-gray-200 shadow-2xs space-y-4"
    >
      <div>
        <h3 className="text-xs font-bold text-gray-800 flex items-center gap-1.5">
          <span>📅</span>
          <span>เลือกวันเวลานัดหมายรับซื้อของเก่า</span>
        </h3>
        <p className="text-[11px] text-gray-500">
          ระบุเวลาที่คุณสะดวกอยู่บ้านเพื่อให้ซาเล้งจัดคิวงานได้ตรงเวลา
        </p>
      </div>

      {/* สลับประเภทการนัดหมาย */}
      <div className="grid grid-cols-2 gap-2 p-1 bg-gray-100 rounded-2xl">
        <button
          type="button"
          data-testid="slot-immediate-btn"
          onClick={() => setBookingType('IMMEDIATE')}
          className={`py-2 px-3 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
            bookingType === 'IMMEDIATE'
              ? 'bg-white text-emerald-700 shadow-2xs'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          <span>⚡</span>
          <span>เรียกทันที (1–2 ชม.)</span>
        </button>

        <button
          type="button"
          data-testid="slot-scheduled-btn"
          onClick={() => setBookingType('SCHEDULED')}
          className={`py-2 px-3 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
            bookingType === 'SCHEDULED'
              ? 'bg-white text-emerald-700 shadow-2xs'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          <span>🗓️</span>
          <span>นัดหมายล่วงหน้า</span>
        </button>
      </div>

      {/* ตัวเลือกเพิ่มเติมกรณีเลือกนัดหมายล่วงหน้า */}
      {bookingType === 'SCHEDULED' && (
        <div className="space-y-3 pt-1 border-t border-gray-100 animate-fade-in">
          <div>
            <label className="block text-[11px] font-semibold text-gray-700 mb-1">
              วันที่นัดหมาย:
            </label>
            <input
              type="date"
              data-testid="booking-date-input"
              value={scheduledDate}
              onChange={(e) => setScheduledDate(e.target.value)}
              className="w-full px-3 py-2 text-xs rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              required
            />
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-gray-700 mb-1">
              ช่วงเวลาที่สะดวก:
            </label>
            <div className="grid grid-cols-3 gap-1.5">
              {SLOTS.map((slot) => {
                const isSelected = scheduledSlot === slot.id;
                return (
                  <button
                    key={slot.id}
                    type="button"
                    data-testid={`slot-option-${slot.id}`}
                    onClick={() => setScheduledSlot(slot.id)}
                    className={`p-2 rounded-xl border text-center transition-all ${
                      isSelected
                        ? 'bg-emerald-50 border-emerald-500 text-emerald-900 ring-1 ring-emerald-500/20'
                        : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'
                    }`}
                  >
                    <span className="text-sm block">{slot.icon}</span>
                    <span className="text-[11px] font-bold block">{slot.label}</span>
                    <span className="text-[9px] text-gray-400 block">{slot.time}</span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* หมายเหตุเพิ่มเติม */}
      <div>
        <label className="block text-[11px] font-semibold text-gray-700 mb-1">
          หมายเหตุหรือข้อความถึงผู้รับซื้อ (ถ้ามี):
        </label>
        <textarea
          rows={2}
          data-testid="booking-notes-input"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="เช่น บ้านรั้วสีฟ้า อยู่ติดกับร้านขายของชำ"
          className="w-full px-3 py-2 text-xs rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-emerald-500"
        />
      </div>

      {/* ปุ่มยืนยันการนัดหมาย (สูง >= 48px REQ-UX-001) */}
      <button
        type="submit"
        data-testid="confirm-booking-btn"
        disabled={loading}
        className="w-full min-h-[48px] py-2.5 px-4 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-2xl text-xs shadow-xs active:scale-98 transition-all flex items-center justify-center gap-1.5"
      >
        <span>{loading ? 'กำลังส่งคำขอ...' : 'ยืนยันการนัดหมาย'}</span>
        <span>→</span>
      </button>
    </form>
  );
}

