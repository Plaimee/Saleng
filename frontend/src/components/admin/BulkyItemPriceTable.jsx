import React, { useState } from 'react';

/**
 * คอมโพเนนต์ตารางจัดการราคาขยะชิ้นใหญ่เหมาจ่าย (หน่วยชิ้น/เครื่อง PIECE)
 * รองรับ UC-05, REQ-FN-003, AC-A02-03, D-A02-04, CC-01, REQ-UX-001
 * ทุกปุ่มกดมีทัชทาร์เก็ต >= 48px
 */
export default function BulkyItemPriceTable({
  prices,
  onUpdatePrice,
  isLoading,
}) {
  const [editingItem, setEditingItem] = useState(null);
  const [formMinPrice, setFormMinPrice] = useState('');
  const [formMaxPrice, setFormMaxPrice] = useState('');
  const [formGrading, setFormGrading] = useState('');
  const [formError, setFormError] = useState('');

  // กรองเฉพาะหมวดขยะชิ้นใหญ่ (unit === 'piece')
  const bulkyPrices = prices.filter(p => p.unit === 'piece');

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
  };

  const handleSave = async () => {
    setFormError('');
    const minP = parseFloat(formMinPrice);
    const maxP = parseFloat(formMaxPrice);

    if (isNaN(minP) || minP <= 0) {
      setFormError('ราคาประเมินต่ำสุดต้องมากกว่า 0 บาท');
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

    try {
      await onUpdatePrice(editingItem.category_code, {
        min_price_per_unit: minP,
        max_price_per_unit: maxP,
        grading_condition: formGrading.trim() || null,
        confirm_shift: true,
        change_reason: 'ปรับปรุงราคาเหมาจ่ายขยะชิ้นใหญ่',
      });
      cancelEdit();
    } catch (err) {
      setFormError(err.message || 'เกิดข้อผิดพลาดในการบันทึกราคาขยะชิ้นใหญ่');
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4 mb-6" data-testid="bulky-item-table-container">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 mb-4">
        <div>
          <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2">
            <span>🧊</span> ช่วงราคาประเมินของขยะชิ้นใหญ่เหมาจ่าย (หน่วย PIECE)
          </h3>
          <p className="text-xs text-slate-500">
            คำนวณราคาเป็นรายชิ้น/เครื่อง ครอบคลุมตู้เย็น แอร์ เครื่องซักผ้า ทีวี เฟอร์นิเจอร์ (D-A02-04, UC-05)
          </p>
        </div>
        <span className="px-3 py-1 bg-amber-100 text-amber-800 text-xs font-semibold rounded-full">
          เหมาจ่ายต่อชิ้น (PIECE)
        </span>
      </div>

      {formError && (
        <div className="p-3 mb-4 bg-rose-50 border border-rose-200 text-rose-700 text-sm rounded-lg" role="alert">
          {formError}
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm border-collapse" data-testid="bulky-item-price-table">
          <thead>
            <tr className="bg-slate-50 border-b border-slate-200 text-slate-600">
              <th className="py-3 px-3 font-semibold">รหัสขยะชิ้นใหญ่</th>
              <th className="py-3 px-3 font-semibold">ประเภทขยะชิ้นใหญ่</th>
              <th className="py-3 px-3 font-semibold">หน่วย</th>
              <th className="py-3 px-3 font-semibold">ช่วงราคาเหมาจ่าย (บาท)</th>
              <th className="py-3 px-3 font-semibold">เกณฑ์สภาพอุปกรณ์</th>
              <th className="py-3 px-3 font-semibold text-center">จัดการ</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {bulkyPrices.length === 0 ? (
              <tr>
                <td colSpan="6" className="py-6 text-center text-slate-400">
                  ไม่พบรายการขยะชิ้นใหญ่
                </td>
              </tr>
            ) : (
              bulkyPrices.map((item) => {
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
                      <span className="px-2 py-0.5 text-xs bg-amber-50 text-amber-700 rounded-full font-mono border border-amber-200">
                        {item.unit}
                      </span>
                    </td>
                    <td className="py-3 px-3">
                      {isEditing ? (
                        <div className="flex items-center gap-1">
                          <input
                            type="number"
                            step="1"
                            value={formMinPrice}
                            onChange={(e) => setFormMinPrice(e.target.value)}
                            className="w-20 px-2 py-1 border border-amber-400 rounded text-right focus:outline-none focus:ring-1 focus:ring-amber-500"
                            placeholder="ต่ำสุด"
                            data-testid="input-bulky-min-price"
                          />
                          <span className="text-slate-400">–</span>
                          <input
                            type="number"
                            step="1"
                            value={formMaxPrice}
                            onChange={(e) => setFormMaxPrice(e.target.value)}
                            className="w-20 px-2 py-1 border border-amber-400 rounded text-right focus:outline-none focus:ring-1 focus:ring-amber-500"
                            placeholder="สูงสุด"
                            data-testid="input-bulky-max-price"
                          />
                        </div>
                      ) : (
                        <span className="font-semibold text-amber-800 bg-amber-50 px-2.5 py-1 rounded-md border border-amber-200/60">
                          {item.min_price_per_unit.toFixed(0)} – {item.max_price_per_unit.toFixed(0)} บ.
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
                          placeholder="ระบุเกณฑ์สภาพ เช่น คอมเพรสเซอร์ครบ"
                          data-testid="input-bulky-condition"
                        />
                      ) : (
                        item.grading_condition || '-'
                      )}
                    </td>
                    <td className="py-3 px-3 text-center">
                      {isEditing ? (
                        <div className="flex items-center justify-center gap-2">
                          <button
                            type="button"
                            onClick={handleSave}
                            disabled={isLoading}
                            className="min-h-[48px] px-3 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-xs font-medium transition-colors shadow-sm disabled:opacity-50"
                            data-testid="btn-save-bulky-price"
                          >
                            บันทึก
                          </button>
                          <button
                            type="button"
                            onClick={cancelEdit}
                            disabled={isLoading}
                            className="min-h-[48px] px-3 bg-slate-200 hover:bg-slate-300 text-slate-700 rounded-lg text-xs font-medium transition-colors"
                            data-testid="btn-cancel-bulky-edit"
                          >
                            ยกเลิก
                          </button>
                        </div>
                      ) : (
                        <button
                          type="button"
                          onClick={() => startEdit(item)}
                          className="min-h-[48px] px-4 bg-slate-100 hover:bg-amber-50 hover:text-amber-800 text-slate-700 rounded-lg text-xs font-medium transition-colors border border-slate-200"
                          data-testid={`btn-edit-bulky-${item.category_code}`}
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
    </div>
  );
}

