/**
 * แผงตัวเลือกขอคนช่วยยกของหนักและหมายเหตุหน้างาน (LiftingHelpToggle)
 * รองรับ REQ-FN-004, MD-DOM-04, AC-S02-05
 */

import React from 'react';

export default function LiftingHelpToggle({
  needLiftingHelp,
  liftingHelpNotes,
  onToggleHelp,
  onChangeNotes,
}) {
  return (
    <div
      data-req="UC-02"
      className="p-4 bg-white rounded-2xl border border-gray-100 shadow-2xs space-y-3"
    >
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-2.5">
          <input
            type="checkbox"
            id="lifting-help-chk"
            data-testid="lifting-help-checkbox"
            checked={needLiftingHelp}
            onChange={(e) => onToggleHelp(e.target.checked)}
            className="w-4 h-4 rounded text-emerald-600 focus:ring-emerald-500 mt-0.5"
          />
          <label htmlFor="lifting-help-chk" className="cursor-pointer">
            <span className="text-xs font-bold text-gray-800 block">
              ต้องการคนช่วยยกของหนัก (บริการเสริม)
            </span>
            <span className="text-[11px] text-gray-500">
              สำหรับของชิ้นใหญ่ หรือบ้านพักที่อยู่ชั้นบน/ไม่มีลิฟต์
            </span>
          </label>
        </div>

        {needLiftingHelp && (
          <span
            data-testid="lifting-help-badge"
            className="text-[10px] font-bold bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full border border-amber-200"
          >
            ⚠️ ขอคนช่วยยก
          </span>
        )}
      </div>

      {needLiftingHelp && (
        <div className="pt-1">
          <label className="block text-[11px] font-medium text-gray-600 mb-1">
            หมายเหตุ/ข้อจำกัดหน้างาน (เช่น ชั้นอาคาร หรือขนาดสิ่งของ):
          </label>
          <textarea
            rows={2}
            data-testid="lifting-help-notes-input"
            value={liftingHelpNotes || ''}
            onChange={(e) => onChangeNotes(e.target.value)}
            placeholder="เช่น ตู้เย็น 10 คิว อยู่ชั้น 3 ไม่มีลิฟต์ ต้องใช้ 2 คนยก"
            className="w-full px-3 py-2 text-xs rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-emerald-500"
          />
        </div>
      )}
    </div>
  );
}

