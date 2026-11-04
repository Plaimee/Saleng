import React, { useState } from 'react';

/**
 * คอมโพเนนต์ตารางจัดการราคากลางรายวันของวัสดุรีไซเคิล (หน่วย kg, bag)
 * รองรับ UC-03, REQ-DAT-001, BR-01, D-A02-01, D-A02-02, CC-01, REQ-UX-001
 * ทุกปุ่มกดมีทัชทาร์เก็ต >= 48px
 */
export default function BenchmarkPriceTable({
  prices,
  onUpdatePrice,
  isLoading,
}) {
  const [editingItem, setEditingItem] = useState(null);
  const [formMinPrice, setFormMinPrice] = useState('');
  const [formMaxPrice, setFormMaxPrice] = useState('');
  const [formGrading, setFormGrading] = useState('');
  const [formError, setFormError] = useState('');
  const [showShiftWarningModal, setShowShiftWarningModal] = useState(false);
  const [shiftWarningData, setShiftWarningData] = useState(null);

  // กรองเฉพาะหมวดทั่วไปที่ไม่ใช่ชิ้นใหญ่ (kg, bag, crate)
  const generalPrices = prices.filter(p => p.unit !== 'piece');

  const startEdit = (item) => {
    setEditingItem(item);
    setFormMinPrice(item.min_price_per_unit.toString());
    setFormMaxPrice(item.max_price_per_unit.toString());
    setFormGrading(item.grading_condition || '');
    setFormError('');
  };

  const cancelEdit = () => {
    setEditingItem(null);
    setFormError('');
    setShowShiftWarningModal(false);
    setShiftWarningData(null);
  };

  const handleSave = async (forceConfirm = false) => {
    setFormError('');
    const minP = parseFloat(formMinPrice);
    const maxP = parseFloat(formMaxPrice);

    // Client-side validation ตาม D-A02-02
    if (isNaN(minP) || minP <= 0) {
      setFormError('ราคาต่ำสุดต้องมากกว่า 0 บาท');
      return;
    }
    if (isNaN(maxP) || maxP < minP) {
      setFormError('ราคาสูงสุดต้องมากกว่าหรือเท่ากับราคาต่ำสุด');
      return;
    }
    if (Math.round(minP * 100) / 100 !== minP || Math.round(maxP * 100) / 100 !== maxP) {
      setFormError('ค่าราคารองรับทศนิยมไม่เกิน 2 ตำแหน่ง');
      return;
    }

    // ตรวจสอบราคาเปลี่ยนเกิน 50% หรือไม่
    const oldMid = (editingItem.min_price_per_unit + editingItem.max_price_per_unit) / 2.0;
    const newMid = (minP + maxP) / 2.0;
    const shiftRatio = Math.abs(newMid - oldMid) / oldMid;

    if (shiftRatio > 0.50 && !forceConfirm) {
      setShiftWarningData({
        oldMid,
        newMid,
        shiftPercent: Math.round(shiftRatio * 100),
      });
      setShowShiftWarningModal(true);
      return;
    }

    try {
      await onUpdatePrice(editingItem.category_code, {
        min_price_per_unit: minP,
        max_price_per_unit: maxP,
        grading_condition: formGrading.trim() || null,
        confirm_shift: forceConfirm,
        change_reason: forceConfirm ? 'ยืนยันการเปลี่ยนราคาเกิน 50%' : 'ปรับปรุงราคารายวัน',
      });
      cancelEdit();
    } catch (err) {
      if (err.data?.detail?.error === 'PRICE_SHIFT_EXCEEDS_50_PERCENT') {
        setShiftWarningData({
          oldMid,
          newMid,
          shiftPercent: Math.round(shiftRatio * 100),
        });
        setShowShiftWarningModal(true);
      } else {
        setFormError(err.message || 'เกิดข้อผิดพลาดในการบันทึกราคา');
      }
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4 mb-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 mb-4">
        <div>
          <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2">
            <span>⚖️</span> ตารางราคากลางอ้างอิงรายวัน (ต่อ กก. / กระสอบ)
          </h3>
          <p className="text-xs text-slate-500">
            ตัดรอบเผยแพร่ทางการ 06:00 น. หากไม่ได้ตั้งใหม่จะดึงราคาฐานเดิมมาใช้ (D-A02-01)
          </p>
        </div>
      </div>

      {formError && (
        <div className="p-3 mb-4 bg-rose-50 border border-rose-200 text-rose-700 text-sm rounded-lg" role="alert">
          {formError}
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm border-collapse" data-testid="benchmark-price-table">
          <thead>
            <tr className="bg-slate-50 border-b border-slate-200 text-slate-600">
              <th className="py-3 px-3 font-semibold">รหัสหมวดหมู่</th>
              <th className="py-3 px-3 font-semibold">ชื่อวัสดุ</th>
              <th className="py-3 px-3 font-semibold">หน่วย</th>
              <th className="py-3 px-3 font-semibold">ช่วงราคาปัจจุบัน (บาท)</th>
              <th className="py-3 px-3 font-semibold">เงื่อนไขคุณภาพ</th>
              <th className="py-3 px-3 font-semibold">อัปเดตล่าสุด</th>
              <th className="py-3 px-3 font-semibold text-center">จัดการ</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {generalPrices.length === 0 ? (
              <tr>
                <td colSpan="7" className="py-6 text-center text-slate-400">
                  ไม่พบรายการราคากลาง
                </td>
              </tr>
            ) : (
              generalPrices.map((item) => {
                const isEditing = editingItem?.category_code === item.category_code;
                return (
                  <tr key={item.category_code} className="hover:bg-slate-50 transition-colors">
                    <td className="py-3 px-3 font-mono text-xs text-slate-500">
                      {item.category_code}
                    </td>
                    <td className="py-3 px-3 font-medium text-slate-800">
                      {item.category_name}
                    </td>
                    <td className="py-3 px-3 text-slate-600">
                      <span className="px-2 py-0.5 text-xs bg-slate-100 rounded-full font-mono">
                        {item.unit}
                      </span>
                    </td>
                    <td className="py-3 px-3">
                      {isEditing ? (
                        <div className="flex items-center gap-1">
                          <input
                            type="number"
                            step="0.01"
                            value={formMinPrice}
                            onChange={(e) => setFormMinPrice(e.target.value)}
                            className="w-20 px-2 py-1 border border-emerald-400 rounded text-right focus:outline-none focus:ring-1 focus:ring-emerald-500"
                            placeholder="ต่ำสุด"
                            data-testid="input-min-price"
                          />
                          <span className="text-slate-400">–</span>
                          <input
                            type="number"
                            step="0.01"
                            value={formMaxPrice}
                            onChange={(e) => setFormMaxPrice(e.target.value)}
                            className="w-20 px-2 py-1 border border-emerald-400 rounded text-right focus:outline-none focus:ring-1 focus:ring-emerald-500"
                            placeholder="สูงสุด"
                            data-testid="input-max-price"
                          />
                        </div>
                      ) : (
                        <span className="font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-md">
                          {item.min_price_per_unit.toFixed(2)} – {item.max_price_per_unit.toFixed(2)}
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-3 text-xs text-slate-600 max-w-xs truncate">
                      {isEditing ? (
                        <input
                          type="text"
                          value={formGrading}
                          onChange={(e) => setFormGrading(e.target.value)}
                          className="w-full px-2 py-1 border border-slate-300 rounded text-xs"
                          placeholder="ระบุเงื่อนไขคุณภาพ"
                          data-testid="input-grading-condition"
                        />
                      ) : (
                        item.grading_condition || '-'
                      )}
                    </td>
                    <td className="py-3 px-3 text-xs text-slate-400">
                      {item.updated_at ? new Date(item.updated_at).toLocaleDateString('th-TH') : '-'}
                    </td>
                    <td className="py-3 px-3 text-center">
                      {isEditing ? (
                        <div className="flex items-center justify-center gap-2">
                          <button
                            type="button"
                            onClick={() => handleSave(false)}
                            disabled={isLoading}
                            className="min-h-[48px] px-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-medium transition-colors shadow-sm disabled:opacity-50"
                            data-testid="btn-save-price"
                          >
                            บันทึก
                          </button>
                          <button
                            type="button"
                            onClick={cancelEdit}
                            disabled={isLoading}
                            className="min-h-[48px] px-3 bg-slate-200 hover:bg-slate-300 text-slate-700 rounded-lg text-xs font-medium transition-colors"
                            data-testid="btn-cancel-edit"
                          >
                            ยกเลิก
                          </button>
                        </div>
                      ) : (
                        <button
                          type="button"
                          onClick={() => startEdit(item)}
                          className="min-h-[48px] px-4 bg-slate-100 hover:bg-emerald-50 hover:text-emerald-700 text-slate-700 rounded-lg text-xs font-medium transition-colors border border-slate-200"
                          data-testid={`btn-edit-${item.category_code}`}
                        >
                          แก้ไขราคา
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Confirmation Warning Modal สำหรับราคาที่เปลี่ยนเกิน 50% ตาม D-A02-02 */}
      {showShiftWarningModal && shiftWarningData && (
        <div
          className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4 z-50"
          data-testid="shift-warning-modal"
          role="dialog"
          aria-modal="true"
        >
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl border border-amber-200 animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center gap-3 text-amber-600 mb-3">
              <span className="text-3xl">⚠️</span>
              <h4 className="text-lg font-bold text-slate-800">
                ยืนยันการเปลี่ยนแปลงราคาเกิน 50%
              </h4>
            </div>

            <p className="text-sm text-slate-600 mb-4 leading-relaxed">
              ราคาเฉลี่ยใหม่ที่คุณระบุ ({shiftWarningData.newMid.toFixed(2)} บาท)
              แตกต่างจากราคาเดิม ({shiftWarningData.oldMid.toFixed(2)} บาท)
              ถึง <strong className="text-amber-700">{shiftWarningData.shiftPercent}%</strong>
              {' '}ซึ่งเกินเกณฑ์เตือนความปลอดภัยเพื่อป้องกันการพิมพ์ผิด
            </p>

            <div className="bg-amber-50 rounded-xl p-3 mb-5 border border-amber-200/60 text-xs text-amber-800">
              หากแน่ใจว่าราคานี้ถูกต้องตามสถานการณ์ตลาด กรุณากดยืนยันเพื่อบันทึกและเผยแพร่ราคาใหม่
            </div>

            <div className="flex flex-col-reverse sm:flex-row gap-2">
              <button
                type="button"
                onClick={() => setShowShiftWarningModal(false)}
                className="min-h-[48px] flex-1 py-2 px-4 rounded-xl border border-slate-300 text-slate-700 font-medium text-sm hover:bg-slate-50 transition-colors"
                data-testid="btn-modal-cancel"
              >
                กลับไปแก้ไขตัวเลข
              </button>
              <button
                type="button"
                onClick={() => handleSave(true)}
                className="min-h-[48px] flex-1 py-2 px-4 rounded-xl bg-amber-600 hover:bg-amber-700 text-white font-medium text-sm transition-colors shadow-sm"
                data-testid="btn-modal-confirm"
              >
                ยืนยันบันทึกราคา
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

