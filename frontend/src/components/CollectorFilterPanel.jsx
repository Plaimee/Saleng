/**
 * แผงตัวกรองค้นหาซาเล้งหลายมิติ (CollectorFilterPanel)
 * รองรับ UC-03, REQ-FN-001, Card 03, AC-S03-03, P-03, Q-03
 */

import React from 'react';

export default function CollectorFilterPanel({
  radiusKm = 5.0,
  onChangeRadius,
  vehicleType = null,
  onChangeVehicleType,
  minRating = null,
  onChangeMinRating,
  hasBulkyItems = false,
  bulkyWarningMessage = '',
}) {
  const radiusOptions = [1.0, 3.0, 5.0];
  const vehicleOptions = [
    { key: null, label: 'ทุกยานพาหนะ' },
    { key: 'TRICYCLE', label: '🛺 ซาเล้ง' },
    { key: 'PICKUP_TRUCK', label: '🛻 รถกระบะ' },
  ];

  return (
    <div data-req="UC-03" className="space-y-2.5">
      {/* แถบแจ้งเตือนเมื่อคำขอมีของชิ้นใหญ่ (Bulky Items Alert) */}
      {hasBulkyItems && (
        <div
          data-testid="bulky-warning-banner"
          className="p-3 bg-blue-50 border border-blue-200 text-blue-900 rounded-2xl text-xs flex items-start space-x-2"
        >
          <span className="text-base flex-shrink-0">📦</span>
          <div>
            <span className="font-bold block">คำขอของคุณมีของชิ้นใหญ่</span>
            <span className="text-[11px] text-blue-700">
              {bulkyWarningMessage ||
                'ระบบแนะนำให้เลือกซาเล้งที่มีรถกระบะหรือซาเล้งขนาดใหญ่ เพื่อให้บรรทุกของได้ครบ'}
            </span>
          </div>
        </div>
      )}

      {/* ชิปเลือกรัศมีและประเภทยานพาหนะ */}
      <div className="flex flex-wrap items-center gap-1.5 text-xs">
        {/* รัศมี */}
        <span className="text-[11px] font-semibold text-gray-500 mr-0.5">รัศมี:</span>
        {radiusOptions.map((r) => (
          <button
            key={r}
            type="button"
            data-testid={`radius-chip-${r}`}
            onClick={() => onChangeRadius && onChangeRadius(r)}
            className={`px-2.5 py-1 rounded-full border text-[11px] font-medium transition-all ${
              radiusKm === r
                ? 'bg-emerald-600 text-white border-emerald-600'
                : 'bg-white text-gray-600 border-gray-200 hover:border-emerald-300'
            }`}
          >
            {r} กม.
          </button>
        ))}

        <div className="w-px h-4 bg-gray-200 mx-1" />

        {/* ยานพาหนะ */}
        <span className="text-[11px] font-semibold text-gray-500 mr-0.5">รถ:</span>
        {vehicleOptions.map((v) => (
          <button
            key={v.key || 'all'}
            type="button"
            data-testid={`vehicle-chip-${v.key || 'all'}`}
            onClick={() => onChangeVehicleType && onChangeVehicleType(v.key)}
            className={`px-2.5 py-1 rounded-full border text-[11px] font-medium transition-all ${
              vehicleType === v.key
                ? 'bg-emerald-600 text-white border-emerald-600'
                : 'bg-white text-gray-600 border-gray-200 hover:border-emerald-300'
            }`}
          >
            {v.label}
          </button>
        ))}

        {/* คะแนนรีวิว */}
        <button
          type="button"
          data-testid="rating-chip-45"
          onClick={() => onChangeMinRating && onChangeMinRating(minRating ? null : 4.8)}
          className={`px-2.5 py-1 rounded-full border text-[11px] font-medium transition-all ${
            minRating
              ? 'bg-amber-500 text-white border-amber-500'
              : 'bg-white text-gray-600 border-gray-200 hover:border-amber-300'
          }`}
        >
          ★ 4.8+
        </button>
      </div>
    </div>
  );
}

