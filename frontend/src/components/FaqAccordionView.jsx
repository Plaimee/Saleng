import React, { useState } from "react";

/**
 * FaqAccordionView Component
 * แสดงคำถามที่พบบ่อย (FAQ) แยกตาม 3 หมวดหมู่ พร้อมระบบ Accordion และช่องค้นหาคำสำคัญ
 * รองรับ UC-08, CC-05, REQ-OP-001, AC-S08-03, P-03, Q-03
 */
export default function FaqAccordionView({
  categories = [],
  searchQuery = "",
  onSearchChange,
}) {
  const [expandedIds, setExpandedIds] = useState(new Set(["FAQ-01", "FAQ-04"]));

  const toggleFaq = (id) => {
    setExpandedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  return (
    <div className="mb-6" data-testid="faq-accordion-view" data-req="UC-08">
      {/* Search Filter Box */}
      <div className="mb-4">
        <div className="relative">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="🔍 ค้นหาคำถาม เช่น ขั้นต่ำ, 500 บาท, PromptPay..."
            data-testid="faq-search-input"
            className="w-full text-xs p-3 pl-9 rounded-2xl border border-gray-200 bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500 shadow-xs"
          />
          <span className="absolute left-3 top-3 text-xs text-gray-400">🔍</span>
          {searchQuery && (
            <button
              onClick={() => onSearchChange("")}
              className="absolute right-3 top-2.5 text-xs text-gray-400 hover:text-gray-600 p-1"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* Categories & FAQ Accordions */}
      {categories.length === 0 ? (
        <div className="bg-white rounded-3xl border border-dashed border-gray-200 p-8 text-center text-xs text-gray-400">
          ไม่พบคำถามที่ตรงกับคำค้นหา "{searchQuery}"
        </div>
      ) : (
        <div className="space-y-4">
          {categories.map((cat) => (
            <div key={cat.category_id} className="space-y-2">
              <h3 className="text-xs font-bold text-gray-700 px-1 uppercase tracking-wider">
                {cat.category_name} ({cat.faqs.length})
              </h3>
              <div className="space-y-2">
                {cat.faqs.map((faq) => {
                  const isOpen = expandedIds.has(faq.id);
                  return (
                    <div
                      key={faq.id}
                      className="bg-white rounded-2xl border border-gray-100 shadow-xs overflow-hidden transition-all"
                      data-testid={`faq-item-${faq.id}`}
                    >
                      <button
                        type="button"
                        onClick={() => toggleFaq(faq.id)}
                        data-testid={`faq-toggle-${faq.id}`}
                        className="w-full p-3.5 text-left text-xs font-semibold text-gray-800 flex justify-between items-center gap-2 hover:bg-gray-50/50"
                      >
                        <span>{faq.question}</span>
                        <span className="text-gray-400 text-sm transform transition-transform duration-200">
                          {isOpen ? "▲" : "▼"}
                        </span>
                      </button>
                      {isOpen && (
                        <div
                          className="px-3.5 pb-3.5 pt-1 text-xs text-gray-600 bg-gray-50/40 border-t border-gray-50 leading-relaxed"
                          data-testid={`faq-answer-${faq.id}`}
                        >
                          {faq.answer}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

