/**
 * การ์ดแสดงโปรไฟล์ซาเล้ง (SalengProfileCard)
 * รองรับ UC-03, REQ-QA-001, REQ-UX-001, REQ-SEC-002, AC-S03-01, AC-S03-04
 */

import React from 'react';

export default function SalengProfileCard({
  collector,
  onSelect,
  onToggleFavorite,
  onStartChat,
}) {
  const {
    saleng_id,
    display_name,
    phone,
    avatar_url,
    verified,
    rating,
    completed_jobs_count,
    vehicle_type,
    distance_km,
    is_favorite,
  } = collector;

  const vehicleLabel = {
    TRICYCLE: 'ซาเล้งสามล้อ',
    LARGE_SIDECAR: 'ซาเล้งพ่วงข้างใหญ่',
    PICKUP_TRUCK: 'รถกระบะขนของ',
  }[vehicle_type] || vehicle_type;

  const vehicleIcon = {
    TRICYCLE: '🛺',
    LARGE_SIDECAR: '🛵',
    PICKUP_TRUCK: '🛻',
  }[vehicle_type] || '🚛';

  return (
    <div
      data-req="UC-03"
      data-testid={`saleng-card-${saleng_id}`}
      className={`p-4 bg-white rounded-2xl border transition-all ${
        is_favorite
          ? 'border-amber-300 shadow-sm ring-1 ring-amber-400/40'
          : 'border-gray-200 shadow-2xs hover:border-emerald-300'
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        {/* รูปโปรไฟล์และข้อมูลหลัก */}
        <div className="flex items-center space-x-3">
          <div className="relative w-12 h-12 rounded-full overflow-hidden bg-emerald-100 flex-shrink-0 border border-emerald-200">
            {avatar_url ? (
              <img
                src={avatar_url}
                alt={display_name}
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-lg">
                👨‍🔧
              </div>
            )}
            {verified && (
              <span
                data-testid="kyc-badge-icon"
                title="ยืนยันตัวตนแล้ว 100%"
                className="absolute bottom-0 right-0 w-3.5 h-3.5 bg-emerald-500 text-white text-[9px] rounded-full flex items-center justify-center ring-1 ring-white font-bold"
              >
                ✓
              </span>
            )}
          </div>

          <div>
            <div className="flex items-center space-x-1.5">
              <h3 className="text-xs font-bold text-gray-800 line-clamp-1">
                {display_name}
              </h3>
            </div>

            {/* ป้าย KYC 100% */}
            {verified && (
              <span
                data-testid="kyc-badge"
                className="inline-flex items-center text-[9px] font-semibold text-emerald-800 bg-emerald-50 border border-emerald-200 px-1.5 py-0.5 rounded-md mt-0.5"
              >
                ✓ ยืนยันตัวตนแล้ว 100%
              </span>
            )}

            <div className="flex items-center space-x-2 text-[10px] text-gray-500 mt-1">
              <span className="font-semibold text-amber-600 flex items-center gap-0.5">
                ★ {rating.toFixed(1)}
              </span>
              <span>•</span>
              <span>สำเร็จ {completed_jobs_count} งาน</span>
              <span>•</span>
              <span className="font-medium text-emerald-700">
                {distance_km.toFixed(1)} กม.
              </span>
            </div>
          </div>
        </div>

        {/* ปุ่มบันทึกเป็นคนโปรด */}
        <button
          type="button"
          data-testid={`btn-toggle-fav-${saleng_id}`}
          onClick={() => onToggleFavorite && onToggleFavorite(saleng_id)}
          className={`p-1.5 rounded-xl border text-xs transition-colors ${
            is_favorite
              ? 'bg-amber-50 border-amber-300 text-amber-600'
              : 'bg-gray-50 border-gray-200 text-gray-400 hover:text-amber-500'
          }`}
          title={is_favorite ? 'ซาเล้งที่เคยใช้บริการ' : 'บันทึกเป็นคนโปรด'}
        >
          {is_favorite ? '⭐' : '☆'}
        </button>
      </div>

      {/* ป้ายประเภทยานพาหนะ */}
      <div className="mt-2.5 pt-2 border-t border-gray-100 flex items-center justify-between text-[11px]">
        <div className="flex items-center space-x-1.5 text-gray-600">
          <span>{vehicleIcon}</span>
          <span className="font-medium">{vehicleLabel}</span>
        </div>

        {is_favorite && (
          <span
            data-testid="favorite-badge"
            className="text-[9px] font-bold text-amber-800 bg-amber-100/80 px-2 py-0.5 rounded-full"
          >
            ซาเล้งที่เคยใช้บริการ
          </span>
        )}
      </div>

      {/* แถบปุ่มการดำเนินการ (โทรด่วน, แชต, เลือกซาเล้ง) */}
      <div className="mt-3 grid grid-cols-5 gap-2">
        <a
          href={`tel:${phone}`}
          data-testid={`btn-call-collector-${saleng_id}`}
          className="col-span-1 min-h-[44px] flex items-center justify-center rounded-xl border border-emerald-300 bg-emerald-50 text-emerald-700 hover:bg-emerald-100 text-sm font-semibold transition-colors"
          title="โทรด่วน"
        >
          📞
        </a>

        <button
          type="button"
          data-testid={`btn-chat-collector-${saleng_id}`}
          onClick={() => onStartChat && onStartChat(collector)}
          className="col-span-1 min-h-[44px] flex items-center justify-center rounded-xl border border-blue-300 bg-blue-50 text-blue-700 hover:bg-blue-100 text-sm font-semibold transition-colors"
          title="แชตข้อความ"
        >
          💬
        </button>

        <button
          type="button"
          data-testid={`btn-select-collector-${saleng_id}`}
          onClick={() => onSelect && onSelect(collector)}
          className="col-span-3 min-h-[48px] px-3 py-2 bg-emerald-600 text-white rounded-xl text-xs font-bold shadow-xs hover:bg-emerald-700 active:scale-98 transition-all flex items-center justify-center gap-1.5"
        >
          <span>เลือกซาเล้งท่านนี้</span>
          <span>→</span>
        </button>
      </div>
    </div>
  );
}

