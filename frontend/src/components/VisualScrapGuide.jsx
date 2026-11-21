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
    <div data-req="UC-02" className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h3 className="text-base font-extrabold text-black">คู่มือภาพเลือกประเภทของเก่า</h3>
          <p className="text-xs text-zinc-600">แตะเลือกประเภทที่คล้ายของท่านเพื่อประเมินราคา</p>
        </div>
        {selectedCategory && (
          <span className="text-xs font-bold px-3 py-1 rounded-full bg-black text-yellow-400">
            เลือกแล้ว: {selectedCategory.name}
          </span>
        )}
      </div>

      {/* แท็บสลับหมวดหมู่ 3 กลุ่มหลัก (Jet Black Pill Bar + Golden Yellow Active) */}
      <div className="flex bg-black p-1 rounded-full gap-1">
        {groups.map((g) => (
          <button
            type="button"
            key={g.key}
            data-testid={`tab-${g.key}`}
            onClick={() => {
              setActiveGroup(g.key);
              if (onSelectCategory && selectedCategory && selectedCategory.category_group !== g.key) {
                onSelectCategory(null);
              }
            }}
            className={`flex-1 py-2 text-xs font-bold rounded-full transition-all ${
              activeGroup === g.key
                ? 'bg-yellow-400 text-black shadow'
                : 'text-zinc-300 hover:text-white'
            }`}
          >
            {g.label}
          </button>
        ))}
      </div>

      {/* รายการของเก่าในหมวดที่เลือก */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        {filteredCategories.map((cat) => {
          const isSelected = selectedCategory?.category_code === cat.category_code;
          return (
            <button
              type="button"
              key={cat.category_code}
              data-testid={`category-card-${cat.category_code}`}
              onClick={() => onSelectCategory(cat)}
              className={`p-3.5 rounded-2xl border-2 text-left transition-all flex flex-col justify-between ${
                isSelected
                  ? 'bg-yellow-400 border-black shadow-md'
                  : 'bg-white border-yellow-200 hover:border-black hover:bg-yellow-50 shadow-xs'
              }`}
            >
              <div className="flex items-center space-x-2 mb-2.5">
                <span className="text-2xl">{cat.icon}</span>
                <span className="text-xs font-extrabold text-black line-clamp-1">
                  {cat.name}
                </span>
              </div>

              <div
                className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full inline-block self-start ${
                  isSelected
                    ? 'bg-black text-yellow-400'
                    : 'bg-yellow-100 text-black border border-yellow-300'
                }`}
              >
                {cat.min_price_per_unit}–{cat.max_price_per_unit} บ./{cat.unit === 'kg' ? 'กก.' : cat.unit === 'crate' ? 'ลัง' : cat.unit === 'bag' ? 'กระสอบ' : 'ชิ้น'}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}

