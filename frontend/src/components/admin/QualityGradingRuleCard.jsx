import React, { useState, useEffect } from 'react';

/**
 * คอมโพเนนต์การ์ดจัดการเกณฑ์คุณภาพและการหักสิ่งปนเปื้อน 3 ระดับ
 * รองรับ UC-03, REQ-FN-003, AC-A02-02, D-A02-03, CC-01, REQ-UX-001
 * ทุกปุ่มกดมีทัชทาร์เก็ต >= 48px
 */
export default function QualityGradingRuleCard({
  categories,
  onFetchRules,
  onUpdateRules,
  isLoading,
}) {
  const [selectedCategory, setSelectedCategory] = useState(
    categories.length > 0 ? categories[0].category_code : 'MAT-CARDBOARD'
  );
  const [rules, setRules] = useState([]);
  const [isFetchingRules, setIsFetchingRules] = useState(false);
  const [feedbackMsg, setFeedbackMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  // โหลด rules เมื่อเลือก category ใหม่
  useEffect(() => {
    if (!selectedCategory) return;
    let isMounted = true;
    setIsFetchingRules(true);
    setErrorMsg('');
    setFeedbackMsg('');

    onFetchRules(selectedCategory)
      .then((data) => {
        if (isMounted) setRules(data || []);
      })
      .catch((err) => {
        if (isMounted) setErrorMsg(err.message || 'ไม่สามารถโหลดเกณฑ์คุณภาพได้');
      })
      .finally(() => {
        if (isMounted) setIsFetchingRules(false);
      });

    return () => {
      isMounted = false;
    };
  }, [selectedCategory, onFetchRules]);

  const handleRuleChange = (index, field, value) => {
    const updated = [...rules];
    updated[index] = {
      ...updated[index],
      [field]: field === 'contamination_deduction_percent' ? parseFloat(value) || 0 : value,
    };
    setRules(updated);
  };

  const handleSaveAll = async () => {
    setErrorMsg('');
    setFeedbackMsg('');

    // ตรวจสอบค่าหักสิ่งปนเปื้อน
    for (const r of rules) {
      if (r.contamination_deduction_percent < 0 || r.contamination_deduction_percent > 100) {
        setErrorMsg(`เปอร์เซ็นต์หักสิ่งปนเปื้อนของ ${r.grade_name} ต้องอยู่ระหว่าง 0% ถึง 100%`);
        return;
      }
    }

    try {
      await onUpdateRules(selectedCategory, { rules });
      setFeedbackMsg('บันทึกเกณฑ์คุณภาพ 3 ระดับสำเร็จ');
    } catch (err) {
      setErrorMsg(err.message || 'เกิดข้อผิดพลาดในการบันทึกเกณฑ์คุณภาพ');
    }
  };

  const getGradeBadge = (level) => {
    switch (level) {
      case 'GRADE_A':
        return <span className="px-2.5 py-1 text-xs font-bold rounded-lg bg-emerald-100 text-emerald-800 border border-emerald-300">เกรด A (หัก 0% • ราคาสูงสุด)</span>;
      case 'GRADE_B':
        return <span className="px-2.5 py-1 text-xs font-bold rounded-lg bg-sky-100 text-sky-800 border border-sky-300">เกรด B (หัก 5% • ราคากลาง)</span>;
      case 'GRADE_C':
        return <span className="px-2.5 py-1 text-xs font-bold rounded-lg bg-rose-100 text-rose-800 border border-rose-300">เกรด C (หัก 10% • ราคาต่ำสุด)</span>;
      default:
        return <span className="px-2.5 py-1 text-xs font-bold rounded-lg bg-slate-100 text-slate-800">{level}</span>;
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4" data-testid="quality-grading-card">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-5 border-b border-slate-100 pb-4">
        <div>
          <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2">
            <span>🏷️</span> กำหนดเกณฑ์คุณภาพและการหักสิ่งปนเปื้อน 3 ระดับ
          </h3>
          <p className="text-xs text-slate-500">
            เกณฑ์มาตรฐาน: GRADE_A (หัก 0%), GRADE_B (หัก 5%), GRADE_C (หัก 10%) ตาม D-A02-03
          </p>
        </div>

        {/* ตัวเลือกหมวดหมู่วัสดุ */}
        <div className="flex items-center gap-2 w-full sm:w-auto">
          <label htmlFor="select-category" className="text-xs font-semibold text-slate-600 whitespace-nowrap">
            เลือกหมวดหมู่:
          </label>
          <select
            id="select-category"
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="min-h-[48px] px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-emerald-500"
            data-testid="select-grading-category"
          >
            {categories.map((c) => (
              <option key={c.category_code} value={c.category_code}>
                {c.category_name} ({c.category_code})
              </option>
            ))}
          </select>
        </div>
      </div>

      {feedbackMsg && (
        <div className="p-3 mb-4 bg-emerald-50 border border-emerald-200 text-emerald-700 text-sm rounded-lg" role="alert">
          ✓ {feedbackMsg}
        </div>
      )}

      {errorMsg && (
        <div className="p-3 mb-4 bg-rose-50 border border-rose-200 text-rose-700 text-sm rounded-lg" role="alert">
          {errorMsg}
        </div>
      )}

      {isFetchingRules ? (
        <div className="py-8 text-center text-slate-400 text-sm">
          กำลังโหลดเกณฑ์คุณภาพ...
        </div>
      ) : (
        <div className="space-y-4">
          {rules.map((rule, idx) => (
            <div
              key={rule.grade_level || idx}
              className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 hover:bg-white transition-colors"
              data-testid={`grading-tier-${rule.grade_level}`}
            >
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 mb-3">
                <div className="flex items-center gap-2">
                  {getGradeBadge(rule.grade_level)}
                  <input
                    type="text"
                    value={rule.grade_name}
                    onChange={(e) => handleRuleChange(idx, 'grade_name', e.target.value)}
                    className="font-medium text-sm text-slate-800 bg-transparent border-b border-transparent hover:border-slate-300 focus:border-emerald-500 px-1 py-0.5 focus:outline-none"
                    placeholder="ชื่อเรียกเกรด"
                    data-testid={`input-grade-name-${rule.grade_level}`}
                  />
                </div>
                <div className="flex items-center gap-2">
                  <label className="text-xs text-slate-600 font-medium">
                    หักสิ่งปนเปื้อน:
                  </label>
                  <div className="flex items-center">
                    <input
                      type="number"
                      step="0.5"
                      min="0"
                      max="100"
                      value={rule.contamination_deduction_percent}
                      onChange={(e) => handleRuleChange(idx, 'contamination_deduction_percent', e.target.value)}
                      className="w-16 px-2 py-1 text-right text-sm border border-slate-300 rounded-l focus:outline-none focus:ring-1 focus:ring-emerald-500"
                      data-testid={`input-deduction-${rule.grade_level}`}
                    />
                    <span className="px-2 py-1 bg-slate-200 border border-l-0 border-slate-300 rounded-r text-xs font-semibold text-slate-600">
                      %
                    </span>
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-600 mb-1">
                  คำอธิบายสภาพทางกายภาพและเงื่อนไขการคัดแยก:
                </label>
                <textarea
                  rows="2"
                  value={rule.description}
                  onChange={(e) => handleRuleChange(idx, 'description', e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 bg-white"
                  placeholder="เช่น สะอาด แห้งสนิท ไม่มีคราบสกปรกหรือสิ่งเจือปน"
                  data-testid={`textarea-desc-${rule.grade_level}`}
                />
              </div>
            </div>
          ))}

          <div className="flex justify-end pt-3">
            <button
              type="button"
              onClick={handleSaveAll}
              disabled={isLoading || isFetchingRules}
              className="min-h-[48px] px-6 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-sm font-semibold transition-colors shadow-sm disabled:opacity-50"
              data-testid="btn-save-grading-rules"
            >
              บันทึกเกณฑ์คุณภาพ
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

