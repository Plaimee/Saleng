import React, { useState } from 'react';

/**
 * WeighingInputForm Component
 * ฟอร์มกรอกผลการชั่งน้ำหนักจริงหน้างาน พร้อมแนบรูปตาชั่งดิจิทัลและคำนวณราคาล็อก
 * รองรับ UC-05, REQ-FN-002, REQ-BR-002, D-B06-02, D-B06-03, MD-STM-04
 */
export default function WeighingInputForm({
  orderId,
  items = [],
  initialScalePhotoUrl = '',
  onSubmitWeighing,
  isLoading = false,
}) {
  const [weights, setWeights] = useState(() => {
    const init = {};
    items.forEach((it) => {
      init[it.item_id] = it.actual_quantity || '';
    });
    return init;
  });

  const [scalePhotoUrl, setScalePhotoUrl] = useState(
    initialScalePhotoUrl || 'https://storage.saleng.app/scales/mock-scale.jpg'
  );
  const [errorMsg, setErrorMsg] = useState('');

  const handleWeightChange = (itemId, val) => {
    setWeights((prev) => ({
      ...prev,
      [itemId]: val,
    }));
    setErrorMsg('');
  };

  // คำนวณยอดเงินรวมสดและส่วนต่างน้ำหนัก
  let totalSettled = 0;
  let totalEstimated = 0;
  let totalActual = 0;
  let hasValidActual = false;

  items.forEach((it) => {
    const est = Number(it.estimated_quantity) || 0;
    const lockedPrice = Number(it.locked_unit_price) || 0;
    const actual = Number(weights[it.item_id]);

    totalEstimated += est;
    if (!isNaN(actual) && actual > 0) {
      hasValidActual = true;
      totalActual += actual;
      totalSettled += actual * lockedPrice;
    }
  });

  const diffRatio = totalEstimated > 0 && hasValidActual
    ? Math.abs(totalActual - totalEstimated) / totalEstimated
    : 0;
  const isReQuote = diffRatio > 0.15;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!scalePhotoUrl || !scalePhotoUrl.trim()) {
      setErrorMsg('จำเป็นต้องแนบภาพถ่ายหน้าตาชั่งดิจิทัลเพื่อเป็นหลักฐาน (REQ-FN-002)');
      return;
    }

    const weighingItems = [];
    for (const it of items) {
      const val = parseFloat(weights[it.item_id]);
      if (isNaN(val) || val <= 0) {
        setErrorMsg(`กรุณากรอกน้ำหนักชั่งจริงของ ${it.category_name} ให้มากกว่า 0 กก.`);
        return;
      }
      weighingItems.push({
        item_id: it.item_id,
        actual_quantity: val,
      });
    }

    if (onSubmitWeighing) {
      onSubmitWeighing({
        scalePhotoUrl: scalePhotoUrl.trim(),
        items: weighingItems,
      });
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-white rounded-2xl border border-gray-200 p-4 shadow-sm space-y-4"
      data-req="REQ-FN-002"
      data-testid="weighing-input-form"
    >
      <div className="border-b border-gray-100 pb-3">
        <h3 className="text-base font-bold text-gray-800">
          ⚖️ บันทึกผลชั่งจริงหน้างาน (Weighing Sheet)
        </h3>
        <p className="text-xs text-gray-500 mt-0.5">
          กรอกน้ำหนักจริงตามตาชั่งดิจิทัล คำนวณด้วยราคาล็อกตอนนัดหมาย (REQ-BR-002)
        </p>
      </div>

      {errorMsg && (
        <div
          className="bg-red-50 border border-red-200 rounded-xl p-3 text-xs text-red-700"
          data-testid="weighing-error-banner"
        >
          ⚠️ {errorMsg}
        </div>
      )}

      {/* รายการสิ่งของ */}
      <div className="space-y-3">
        {items.map((item) => {
          const lockedPrice = Number(item.locked_unit_price) || 0;
          const currentWeight = weights[item.item_id] || '';
          const lineTotal = !isNaN(parseFloat(currentWeight)) && parseFloat(currentWeight) > 0
            ? (parseFloat(currentWeight) * lockedPrice).toFixed(2)
            : '0.00';

          return (
            <div
              key={item.item_id}
              className="p-3 bg-gray-50 rounded-xl border border-gray-100 space-y-2"
              data-testid={`item-row-${item.item_id}`}
            >
              <div className="flex justify-between items-start">
                <div>
                  <span className="text-sm font-bold text-gray-800 block">
                    {item.category_name}
                  </span>
                  <span className="text-xs text-gray-500">
                    ประมาณการ: {item.estimated_quantity} {item.unit} | ราคาล็อก:{' '}
                    <span className="font-semibold text-emerald-700">
                      ฿{lockedPrice.toFixed(2)}/{item.unit}
                    </span>
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-xs text-gray-400 block">ยอดรวมรายการ</span>
                  <span className="text-sm font-black text-emerald-700">
                    ฿{lineTotal}
                  </span>
                </div>
              </div>

              <div>
                <label className="text-xs font-medium text-gray-700 block mb-1">
                  น้ำหนักชั่งจริง ({item.unit}) <span className="text-red-500">*</span>:
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="0.1"
                  required
                  value={currentWeight}
                  onChange={(e) => handleWeightChange(item.item_id, e.target.value)}
                  placeholder={`ระบุน้ำหนัก (${item.unit})`}
                  className="w-full min-h-[48px] px-3 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  data-testid={`input-weight-${item.item_id}`}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* ภาพถ่ายหน้าตาชั่งดิจิทัล (REQ-FN-002, D-B06-02) */}
      <div className="p-3 bg-emerald-50/50 rounded-xl border border-emerald-100 space-y-2">
        <label className="text-xs font-bold text-emerald-900 block">
          📸 รูปถ่ายหน้าตาชั่งดิจิทัล (บังคับ) <span className="text-red-500">*</span>:
        </label>
        <input
          type="url"
          required
          value={scalePhotoUrl}
          onChange={(e) => setScalePhotoUrl(e.target.value)}
          placeholder="https://storage.saleng.app/scales/photo.jpg"
          className="w-full min-h-[48px] px-3 border border-emerald-200 rounded-xl text-xs bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
          data-testid="input-scale-photo-url"
        />
        <p className="text-[11px] text-emerald-700">
          ถ่ายภาพหน้าจอตัวเลขดิจิทัลของตาชั่งเพื่อป้องกันข้อพิพาทและเป็นหลักฐาน 100%
        </p>
      </div>

      {/* แจ้งเตือนเกณฑ์ ±15% Re-quote (MD-STM-04) */}
      {isReQuote && (
        <div
          className="bg-amber-50 border border-amber-200 rounded-xl p-3 text-xs text-amber-800 flex items-start gap-2"
          data-testid="re-quote-warning"
        >
          <span>⚠️</span>
          <div>
            <span className="font-bold block">ส่วนต่างน้ำหนักเกิน ±15% ({((diffRatio) * 100).toFixed(1)}%)</span>
            <span>ระบบจะส่งคำขอปรับราคาใหม่ให้ผู้ขายยืนยันก่อนปิดยอด (Re-Quote Gate)</span>
          </div>
        </div>
      )}

      {/* ยอดเงินรวมสรุป */}
      <div className="bg-gray-100 rounded-xl p-3 flex justify-between items-center">
        <div>
          <span className="text-xs text-gray-500 block">ยอดรวมทั้งสิ้น (คำนวณจากราคาล็อก)</span>
          <span className="text-xs text-gray-400">น้ำหนักรวม: {totalActual.toFixed(1)} กก.</span>
        </div>
        <div className="text-right">
          <span className="text-xl font-black text-emerald-700" data-testid="total-settled-preview">
            ฿{totalSettled.toFixed(2)}
          </span>
        </div>
      </div>

      {/* ปุ่มบันทึกผลชั่ง */}
      <button
        type="submit"
        disabled={isLoading}
        className="w-full min-h-[48px] bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl text-sm transition duration-150 flex items-center justify-center gap-2 shadow-sm disabled:opacity-60"
        data-testid="submit-weighing-btn"
      >
        {isLoading ? 'กำลังบันทึก...' : '✅ บันทึกผลชั่งและส่งให้ผู้ขายยืนยัน'}
      </button>
    </form>
  );
}

