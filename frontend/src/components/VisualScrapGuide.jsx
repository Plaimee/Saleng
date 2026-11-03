/**
 * คู่มือภาพสำหรับเลือกประเภทของเก่า (VisualScrapGuide)
 * รองรับ UC-02, REQ-UX-002, Card 03, AC-S02-01
 */

import React, { useState } from 'react';

export default function VisualScrapGuide({ categories, selectedCategory, onSelectCategory }) {
  const [activeGroup, setActiveGroup] = useState('GENERAL_WEIGHT');

  const groups = [
    { key: 'GENERAL_WEIGHT', label: 'ชั่งกิโลกรัม' },
    { key: 'BOXED_CRATE_ITEMS', label: 'บรรจุลัง/กระสอบ' },
    { key: 'BULKY_FLAT_RATE', label: 'ของชิ้นใหญ่เหมา' },
  ];

  const filteredCategories = categories.filter(
    (c) => c.category_group === activeGroup
  );

  return (
    <div data-req="UC-02" className="space-y-3">
      <div>
        <h3 className="text-sm font-bold text-gray-900">คู่มือภาพเลือกประเภทของเก่า</h3>
        <p className="text-xs text-gray-500">แตะเลือกประเภทที่คล้ายของท่านเพื่อประเมินราคา</p>
      </div>

      {/* แท็บสลับหมวดหมู่ 3 กลุ่มหลัก */}
      <div className="flex bg-gray-100 p-1 rounded-xl gap-1">
        {groups.map((g) => (
          <button
            type="button"
            key={g.key}
            data-testid={`tab-${g.key}`}
            onClick={() => setActiveGroup(g.key)}
            className={`flex-1 py-1.5 text-xs font-semibold rounded-lg transition-all ${
              activeGroup === g.key
                ? 'bg-white text-emerald-700 shadow-xs'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {g.label}
          </button>
        ))}
      </div>

      {/* รายการของเก่าในหมวดที่เลือก */}
      <div className="grid grid-cols-2 gap-2.5">
        {filteredCategories.map((cat) => {
          const isSelected = selectedCategory?.category_code === cat.category_code;
          return (
            <button
              type="button"
              key={cat.category_code}
              data-testid={`category-card-${cat.category_code}`}
              onClick={() => onSelectCategory(cat)}
              className={`p-3.5 rounded-2xl border text-left transition-all flex flex-col justify-between ${
                isSelected
                  ? 'bg-emerald-50 border-emerald-500 ring-2 ring-emerald-500/20'
                  : 'bg-white border-gray-100 hover:border-gray-200 shadow-xs'
              }`}
            >
              <div className="flex items-center space-x-2 mb-2">
                <span className="text-2xl">{cat.icon}</span>
                <span className="text-xs font-bold text-gray-800 line-clamp-1">
                  {cat.name}
                </span>
              </div>

              <div className="text-[11px] font-semibold text-emerald-600 bg-emerald-50/80 px-2 py-0.5 rounded-md inline-block">
                {cat.min_price_per_unit}–{cat.max_price_per_unit} บ./{cat.unit === 'kg' ? 'กก.' : cat.unit === 'crate' ? 'ลัง' : cat.unit === 'bag' ? 'กระสอบ' : 'ชิ้น'}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}

