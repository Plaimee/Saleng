import React from "react";

/**
 * MultiItemBasketSummary Component
 * รองรับ Card 01, BR-01, AC-S04-02, D-06
 */
export default function MultiItemBasketSummary({
  basket = [],
  onRemoveItem,
  totalMin = 0,
  totalMax = 0,
  disclaimer = "ราคาจริงขึ้นกับสภาพของหน้างาน",
  onSubmitOrder,
  isSubmitting = false,
}) {
  if (basket.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-dashed border-gray-200 p-6 text-center text-gray-400 text-xs mb-4" data-testid="empty-basket-placeholder">
        <span className="text-2xl block mb-1">🛒</span>
        ยังไม่มีรายการของเก่าในตะกร้า กรุณาเลือกรายการและระบุปริมาณด้านบน
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-emerald-100 p-4 mb-4" data-req="BR-01" data-testid="basket-summary">
      <h3 className="text-sm font-bold text-gray-800 mb-3 flex items-center justify-between">
        <span className="flex items-center gap-1.5">
          <span className="text-emerald-600">🧺</span> รายการของเก่าในตะกร้า ({basket.length})
        </span>
      </h3>

      {/* รายการแต่ละชิ้น */}
      <div className="divide-y divide-gray-100 mb-3" data-testid="basket-item-list">
        {basket.map((item, idx) => (
          <div key={`${item.category_code}-${idx}`} className="py-2.5 flex items-center justify-between text-xs" data-testid={`basket-item-${idx}`}>
            <div>
              <span className="font-semibold text-gray-800">{item.category_name}</span>
              <span className="text-gray-500 ml-1.5">
                ({item.quantity} {item.unit === "bag" ? "กระสอบ" : "กก."})
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-emerald-600">
                {item.est_min_price}–{item.est_max_price} บ.
              </span>
              <button
                type="button"
                onClick={() => onRemoveItem(idx)}
                className="text-gray-300 hover:text-rose-500 text-sm px-1"
                title="ลบรายการ"
                data-testid={`remove-item-${idx}`}
              >
                ✕
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* แถบสรุปยอดรวม Min-Max */}
      <div className="bg-emerald-50 rounded-xl p-3.5 border border-emerald-200 text-center mb-3" data-testid="total-estimate-card">
        <span className="text-xs text-gray-600 font-medium">ยอดประเมินรวมทั้งคำขอ (ต่ำสุด–สูงสุด):</span>
        <div className="text-xl font-black text-emerald-700 tracking-tight" data-testid="total-price-range">
          {totalMin}–{totalMax} บาท
        </div>
        {/* ข้อความกำกับตาม BR-01 */}
        <p className="text-[11px] text-gray-500 mt-1 font-normal italic" data-testid="disclaimer-text">
          *{disclaimer}
        </p>
      </div>

      {/* ปุ่มยืนยันสร้างคำขอ */}
      <button
        type="button"
        onClick={onSubmitOrder}
        disabled={isSubmitting}
        className="w-full bg-emerald-600 hover:bg-emerald-700 disabled:bg-gray-300 text-white font-bold py-3 px-4 rounded-xl text-xs transition duration-150 shadow-sm flex items-center justify-center gap-2"
        data-testid="submit-order-btn"
      >
        {isSubmitting ? "กำลังดำเนินการ..." : "ยืนยันสร้างคำขอนัดหมายรับซื้อ"}
      </button>
    </div>
  );
}

