/**
 * แผงเลือกประเภทย่อยของชิ้นใหญ่เหมาจ่าย (BulkyItemSelector)
 * รองรับ REQ-FN-003, Card 03, AC-S02-02, AC-S02-03
 */

import React from 'react';

const BULKY_PRICES = [
  { name: 'ตู้เย็น', min: 200, max: 300, icon: '🧊' },
  { name: 'เครื่องซักผ้า', min: 150, max: 250, icon: '🧺' },
  { name: 'แอร์/คอมเพรสเซอร์', min: 300, max: 500, icon: '❄️' },
  { name: 'โซฟา/เฟอร์นิเจอร์', min: 100, max: 200, icon: '🛋️' },
];

export default function BulkyItemSelector({
  selectedSubCategory,
  onSelectSubCategory,
  errorMessage,
}) {
  return (
    <div
      data-req="UC-02"
      className="p-4 bg-amber-50/50 rounded-2xl border border-amber-200/80 space-y-3"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <span className="text-xl">⚠️</span>
          <div>
            <h4 className="text-xs font-bold text-amber-900">
              ระบุประเภทของชิ้นใหญ่ (จำเป็น)
            </h4>
            <p className="text-[11px] text-amber-700">
              เพื่อให้ผู้รับซื้อจัดสรรพื้นที่รถบรรทุกได้ถูกต้อง 100%
            </p>
          </div>
        </div>
      </div>

      {errorMessage && (
        <div
          data-testid="bulky-guard-error"
          className="p-2.5 bg-red-100 border border-red-300 text-red-800 text-xs rounded-xl font-medium"
        >
          {errorMessage}
        </div>
      )}

      <div className="grid grid-cols-2 gap-2">
        {BULKY_PRICES.map((item) => {
          const isSelected = selectedSubCategory === item.name;
          return (
            <button
              type="button"
              key={item.name}
              data-testid={`bulky-option-${item.name}`}
              onClick={() => onSelectSubCategory(item.name)}
              className={`p-2.5 rounded-xl border text-left transition-all ${
                isSelected
                  ? 'bg-amber-100/80 border-amber-600 ring-2 ring-amber-500/30'
                  : 'bg-white border-amber-200 hover:bg-amber-50/60'
              }`}
            >
              <div className="flex items-center space-x-1.5 mb-1">
                <span>{item.icon}</span>
                <span className="text-xs font-bold text-gray-800">{item.name}</span>
              </div>
              <div className="text-[10px] text-amber-900 font-semibold">
                ช่วงราคา: {item.min}–{item.max} บ./ชิ้น
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}

