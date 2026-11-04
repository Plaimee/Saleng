/**
 * คอมโพเนนต์แถบแสดงความจุรถและการสะสมน้ำหนัก (CapacityIndicatorBar)
 * คำนวณน้ำหนักสะสม current_load + job_weight เทียบกับ max_capacity (200 กก.)
 * รองรับ BR-03, REQ-CON-003, AC-B03-03, D-B03-03, D-B03-04
 */

import React from 'react';

export default function CapacityIndicatorBar({
  current_load_kg = 0.0,
  job_est_weight_kg = 0.0,
  max_capacity_kg = 200.0,
}) {
  const current = Number(current_load_kg) || 0;
  const added = Number(job_est_weight_kg) || 0;
  const max = Number(max_capacity_kg) || 200;
  const projected = Math.round((current + added) * 100) / 100;
  const isOverload = projected > max;
  const overloadAmount = isOverload ? Math.round((projected - max) * 100) / 100 : 0;
  const remaining = Math.max(0, Math.round((max - projected) * 100) / 100);

  // คำนวณเปอร์เซ็นต์สำหรับ Progress Bar
  const currentPct = Math.min(100, Math.round((current / max) * 100));
  const addedPct = Math.min(100 - currentPct, Math.round((added / max) * 100));
  const totalPct = Math.min(100, Math.round((projected / max) * 100));

  return (
    <div
      data-testid="capacity-bar-container"
      data-req="REQ-CON-003"
      data-br="BR-03"
      className={`p-4 rounded-xl border ${
        isOverload ? 'bg-red-50 border-red-300' : 'bg-slate-50 border-slate-200'
      } shadow-sm`}
    >
      <div className="flex justify-between items-center mb-2">
        <span className="text-sm font-semibold text-slate-800">
          ⚖️ ความจุรถสะสม (สูงสุด {max.toFixed(0)} กก.)
        </span>
        <span
          data-testid="capacity-text-projected"
          className={`text-sm font-bold ${isOverload ? 'text-red-600' : 'text-emerald-700'}`}
        >
          {projected.toFixed(1)} / {max.toFixed(0)} กก. ({Math.round((projected / max) * 100)}%)
        </span>
      </div>

      {/* Progress Bar Container */}
      <div className="w-full bg-slate-200 rounded-full h-3.5 flex overflow-hidden">
        {/* ส่วนน้ำหนักปัจจุบัน */}
        <div
          data-testid="capacity-progress"
          style={{ width: `${currentPct}%` }}
          className={`h-full transition-all duration-300 ${isOverload ? 'bg-red-400' : 'bg-blue-500'}`}
          title={`มีของอยู่แล้ว: ${current.toFixed(1)} กก.`}
        />
        {/* ส่วนน้ำหนักจากงานนี้ */}
        <div
          style={{ width: `${addedPct}%` }}
          className={`h-full transition-all duration-300 ${isOverload ? 'bg-red-600' : 'bg-emerald-500'}`}
          title={`น้ำหนักงานนี้: +${added.toFixed(1)} กก.`}
        />
      </div>

      {/* รายละเอียดน้ำหนัก */}
      <div className="flex justify-between items-center mt-2 text-xs text-slate-600">
        <span data-testid="capacity-text-current">
          บรรทุกอยู่: <strong className="text-slate-800">{current.toFixed(1)} กก.</strong> + งานนี้:{' '}
          <strong className="text-slate-800">{added.toFixed(1)} กก.</strong>
        </span>
        <span>
          {isOverload ? (
            <span className="text-red-600 font-semibold">เกินความจุ</span>
          ) : (
            <span>
              เหลือรับได้อีก: <strong className="text-emerald-700">{remaining.toFixed(1)} กก.</strong>
            </span>
          )}
        </span>
      </div>

      {/* กล่องเตือนกรณีน้ำหนักเกิน */}
      {isOverload && (
        <div
          data-testid="capacity-overload-alert"
          className="mt-3 p-2.5 bg-red-100 border border-red-300 rounded-lg flex items-center gap-2 text-xs text-red-800 font-medium"
        >
          <span className="text-base">⚠️</span>
          <div>
            <strong>น้ำหนักเกินความจุรถ {overloadAmount.toFixed(1)} กก.</strong>
            <p className="text-[11px] text-red-700 mt-0.5">
              ไม่สามารถรับงานนี้ได้ กรุณานำของสะสมไปเทขายที่จุดรับซื้อก่อน
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

