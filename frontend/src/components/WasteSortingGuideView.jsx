import React, { useState } from "react";

/**
 * WasteSortingGuideView Component
 * แสดงคู่มือแนะนำการคัดแยกขยะเพื่อเพิ่มมูลค่าราคา 4 หมวดหลัก
 * รองรับ UC-08, CC-05, REQ-OP-001, AC-S08-02, P-02, Q-02
 */
export default function WasteSortingGuideView({ guides = [], isOffline = false }) {
  const [activeCode, setActiveCode] = useState(guides[0]?.category_code || "MAT-CARDBOARD");

  const activeGuide = guides.find((g) => g.category_code === activeCode) || guides[0];

  if (!guides || guides.length === 0) return null;

  return (
    <div className="mb-6" data-testid="waste-sorting-guide-view" data-req="UC-08">
      {/* Category Tabs */}
      <div className="flex gap-2 overflow-x-auto pb-2 mb-3 scrollbar-none" data-testid="guide-category-tabs">
        {guides.map((g) => (
          <button
            key={g.category_code}
            onClick={() => setActiveCode(g.category_code)}
            data-testid={`guide-tab-${g.category_code}`}
            className={`px-3 py-2 rounded-2xl text-xs font-semibold whitespace-nowrap transition-all flex items-center gap-1.5 border ${
              activeCode === g.category_code
                ? "bg-emerald-600 text-white border-emerald-600 shadow-sm"
                : "bg-white text-gray-600 border-gray-200 hover:bg-gray-50"
            }`}
          >
            <span>{g.icon}</span>
            <span>{g.category_name.split(" ")[0]}</span>
          </button>
        ))}
      </div>

      {/* Guide Details Card */}
      {activeGuide && (
        <div
          className="bg-white rounded-3xl border border-gray-100 shadow-sm p-4"
          data-testid={`guide-detail-${activeGuide.category_code}`}
        >
          {/* Header */}
          <div className="flex items-center gap-3 pb-3 border-b border-gray-100 mb-3">
            <span className="text-3xl p-2 bg-emerald-50 rounded-2xl">
              {activeGuide.icon}
            </span>
            <div>
              <h3 className="text-sm font-bold text-gray-800">
                {activeGuide.category_name}
              </h3>
              <span className="text-[10px] font-mono text-gray-400">
                รหัส: {activeGuide.category_code}
              </span>
            </div>
          </div>

          {/* เคล็ดลับเพิ่มมูลค่าราคา (Value-add Tips) */}
          <div className="mb-3.5">
            <h4 className="text-xs font-bold text-emerald-800 flex items-center gap-1.5 mb-2">
              <span>💡</span>
              <span>เคล็ดลับเตรียมของเก่าให้ได้ราคาสูง</span>
            </h4>
            <div className="space-y-1.5 bg-emerald-50/60 rounded-2xl p-3 border border-emerald-100">
              {activeGuide.value_add_tips.map((tip, idx) => (
                <div key={idx} className="text-xs text-emerald-950 flex items-start gap-1.5">
                  <span className="text-emerald-600 font-bold">•</span>
                  <span>{tip}</span>
                </div>
              ))}
            </div>
          </div>

          {/* ผลต่อราคา (Price Impact) */}
          <div className="mb-3.5 bg-blue-50/60 rounded-2xl p-3 border border-blue-100">
            <div className="text-[11px] font-bold text-blue-900 mb-1 flex items-center gap-1">
              <span>📈</span>
              <span>ประโยชน์ด้านราคา:</span>
            </div>
            <p className="text-xs text-blue-950 leading-relaxed">
              {activeGuide.price_impact_description}
            </p>
          </div>

          {/* ข้อควรระวัง (Precautions) */}
          <div className="bg-amber-50/60 rounded-2xl p-3 border border-amber-100">
            <div className="text-[11px] font-bold text-amber-900 mb-1 flex items-center gap-1">
              <span>⚠️</span>
              <span>ข้อควรระวัง:</span>
            </div>
            <div className="space-y-1">
              {activeGuide.precautions.map((pre, idx) => (
                <div key={idx} className="text-xs text-amber-950 flex items-start gap-1">
                  <span className="text-amber-600 font-bold">•</span>
                  <span>{pre}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

