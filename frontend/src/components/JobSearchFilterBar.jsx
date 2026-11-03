/**
 * แถบตัวกรองและจัดเรียงคำขอขาย (JobSearchFilterBar)
 * รองรับ UC-04, REQ-FN-002, REQ-UX-001, CC-01, Q-03, AC-B02-05
 */

import React from 'react';

const CATEGORIES = [
  { code: 'ALL', label: 'ทั้งหมด' },
  { code: 'MAT-CARDBOARD', label: '📦 กระดาษ' },
  { code: 'MAT-PET-BOTTLE', label: '🧴 พลาสติก' },
  { code: 'MAT-GLASS-BOTTLE', label: '🍾 ขวดแก้ว' },
  { code: 'MAT-ALU-CAN', label: '🥫 โลหะ' },
  { code: 'BULKY-APPLIANCE', label: '🧊 ของชิ้นใหญ่' },
];

const WEIGHT_RANGES = [
  { code: 'ALL', label: 'ทุกขนาด' },
  { code: 'SMALL', label: '< 50 กก.' },
  { code: 'MEDIUM', label: '50–100 กก.' },
  { code: 'LARGE', label: '> 100 กก.' },
];

const SORT_OPTIONS = [
  { code: 'DISTANCE', label: '📍 ใกล้สุด' },
  { code: 'PRICE_DESC', label: '💰 ราคาสูงสุด' },
];

export default function JobSearchFilterBar({
  selectedCategory,
  onSelectCategory,
  selectedWeight,
  onSelectWeight,
  sortBy,
  onSelectSort,
}) {
  return (
    <div
      className="bg-white p-3 border-b border-gray-200 space-y-3"
      data-req="UC-04"
      data-testid="job-search-filter-bar"
    >
      {/* หมวดหมู่วัสดุ */}
      <div>
        <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider block mb-1">
          หมวดหมู่วัสดุ
        </span>
        <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-none">
          {CATEGORIES.map((cat) => {
            const isActive = selectedCategory === cat.code || (!selectedCategory && cat.code === 'ALL');
            return (
              <button
                key={cat.code}
                type="button"
                data-testid={`filter-cat-${cat.code}`}
                onClick={() => onSelectCategory(cat.code === 'ALL' ? null : cat.code)}
                className={`min-h-[48px] px-3 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors flex items-center justify-center ${
                  isActive
                    ? 'bg-emerald-600 text-white shadow-sm'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {cat.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* ช่วงน้ำหนัก และการจัดเรียง */}
      <div className="flex flex-wrap items-center justify-between gap-2 pt-1 border-t border-gray-100">
        {/* ตัวกรองน้ำหนัก */}
        <div className="flex gap-1 overflow-x-auto pb-1">
          {WEIGHT_RANGES.map((wt) => {
            const isActive = selectedWeight === wt.code || (!selectedWeight && wt.code === 'ALL');
            return (
              <button
                key={wt.code}
                type="button"
                data-testid={`filter-weight-${wt.code}`}
                onClick={() => onSelectWeight(wt.code)}
                className={`min-h-[48px] px-2.5 py-1.5 rounded-md text-xs font-medium transition-colors ${
                  isActive
                    ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                    : 'bg-gray-50 text-gray-600 hover:bg-gray-100 border border-gray-200'
                }`}
              >
                {wt.label}
              </button>
            );
          })}
        </div>

        {/* จัดเรียงลำดับ */}
        <div className="flex gap-1">
          {SORT_OPTIONS.map((opt) => {
            const isActive = sortBy === opt.code;
            return (
              <button
                key={opt.code}
                type="button"
                data-testid={`sort-${opt.code}`}
                onClick={() => onSelectSort(opt.code)}
                className={`min-h-[48px] px-3 py-1.5 rounded-md text-xs font-semibold transition-colors ${
                  isActive
                    ? 'bg-gray-800 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {opt.label}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}

