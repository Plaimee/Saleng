import React, { useState, useMemo } from "react";

/**
 * ItemPriceCalculator Component
 * รองรับ Card 01, AC-S04-02, AC-S04-04, AC-S04-05, D-02
 */
export default function ItemPriceCalculator({ benchmarkPrices = [], onAddItem }) {
  const [selectedCategory, setSelectedCategory] = useState("MAT-CARDBOARD");
  const [unit, setUnit] = useState("kg");
  const [quantityStr, setQuantityStr] = useState("");
  const [errorMsg, setErrorMsg] = useState("");

  // ตรวจสอบว่าประเภทที่เลือก รองรับหน่วยกระสอบหรือไม่ (ขวดแก้ว, ขวดพลาสติก)
  const isBagSupported = useMemo(() => {
    return selectedCategory.includes("GLASS") || selectedCategory.includes("PLASTIC");
  }, [selectedCategory]);

  // ค้นหาราคากลางของรายการที่เลือก
  const currentBenchmark = useMemo(() => {
    let targetCode = selectedCategory;
    if (unit === "bag" && !targetCode.endsWith("-BAG")) {
      targetCode = `${targetCode}-BAG`;
    }
    return (
      benchmarkPrices.find((p) => p.category_code === targetCode) ||
      benchmarkPrices.find((p) => p.category_code === selectedCategory)
    );
  }, [selectedCategory, unit, benchmarkPrices]);

  // คำนวณช่วงราคาประเมินแบบเรียลไทม์ (Live Estimate)
  const liveEstimate = useMemo(() => {
    const qty = parseFloat(quantityStr);
    if (!qty || qty <= 0 || !currentBenchmark) return null;
    return {
      min: Math.round(qty * currentBenchmark.min_price_per_unit * 100) / 100,
      max: Math.round(qty * currentBenchmark.max_price_per_unit * 100) / 100,
    };
  }, [quantityStr, currentBenchmark]);

  const handleCategoryChange = (e) => {
    const newCat = e.target.value;
    setSelectedCategory(newCat);
    // ถ้าย้ายไปหมวดที่ไม่รองรับกระสอบ ให้รีเซ็ตหน่วยเป็น kg
    if (!newCat.includes("GLASS") && !newCat.includes("PLASTIC")) {
      setUnit("kg");
    }
    setErrorMsg("");
  };

  const handleAdd = (e) => {
    e.preventDefault();
    const qty = parseFloat(quantityStr);

    // AC-S04-04: ตรวจสอบปริมาณ <= 0
    if (!quantityStr || isNaN(qty) || qty <= 0) {
      setErrorMsg("กรุณากรอกปริมาณมากกว่า 0");
      return;
    }

    setErrorMsg("");
    onAddItem({
      category_code: selectedCategory,
      category_name: currentBenchmark?.category_name || selectedCategory,
      unit,
      quantity: qty,
      est_min_price: liveEstimate?.min || 0,
      est_max_price: liveEstimate?.max || 0,
    });

    setQuantityStr("");
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-emerald-100 p-4 mb-4" data-req="Card-01">
      <h3 className="text-sm font-bold text-gray-800 mb-3 flex items-center gap-1.5">
        <span className="text-emerald-600">➕</span> เลือกของเก่าและประเมินราคา
      </h3>

      <form onSubmit={handleAdd} className="space-y-3">
        {/* เลือกประเภท */}
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">ประเภทวัสดุ</label>
          <select
            value={selectedCategory}
            onChange={handleCategoryChange}
            className="w-full text-xs border border-gray-200 rounded-lg p-2.5 bg-gray-50/50 focus:border-emerald-500 focus:outline-none"
            data-testid="category-select"
          >
            <option value="MAT-CARDBOARD">กระดาษลัง (3–4 บาท/กก.)</option>
            <option value="MAT-WHITE-PAPER">กระดาษขาวดำ (6–7 บาท/กก.)</option>
            <option value="MAT-GLASS-BOTTLE">ขวดแก้ว</option>
            <option value="MAT-PLASTIC-BOTTLE">ขวดพลาสติก</option>
          </select>
        </div>

        {/* สลับหน่วย กก. / กระสอบ (AC-S04-05, D-02) */}
        {isBagSupported && (
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">หน่วยนับ</label>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setUnit("kg")}
                className={`flex-1 py-1.5 text-xs rounded-lg font-medium border ${
                  unit === "kg"
                    ? "bg-emerald-600 text-white border-emerald-600"
                    : "bg-gray-50 text-gray-700 border-gray-200"
                }`}
                data-testid="unit-kg-btn"
              >
                กิโลกรัม (กก.)
              </button>
              <button
                type="button"
                onClick={() => setUnit("bag")}
                className={`flex-1 py-1.5 text-xs rounded-lg font-medium border ${
                  unit === "bag"
                    ? "bg-emerald-600 text-white border-emerald-600"
                    : "bg-gray-50 text-gray-700 border-gray-200"
                }`}
                data-testid="unit-bag-btn"
              >
                กระสอบ (เหมาจ่าย)
              </button>
            </div>
          </div>
        )}

        {/* ช่องกรอกปริมาณ */}
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">
            ปริมาณ ({unit === "bag" ? "กระสอบ" : "กิโลกรัม"})
          </label>
          <input
            type="number"
            step="any"
            placeholder={unit === "bag" ? "เช่น 2" : "เช่น 10"}
            value={quantityStr}
            onChange={(e) => {
              setQuantityStr(e.target.value);
              if (errorMsg) setErrorMsg("");
            }}
            className="w-full text-xs border border-gray-200 rounded-lg p-2.5 focus:border-emerald-500 focus:outline-none"
            data-testid="quantity-input"
          />
          {errorMsg && (
            <p className="text-rose-500 text-[11px] mt-1 font-medium" data-testid="quantity-error">
              {errorMsg}
            </p>
          )}
        </div>

        {/* ช่วงราคาประเมินเรียลไทม์ (Live Min-Max) */}
        {liveEstimate && (
          <div className="bg-emerald-50/70 border border-emerald-200 rounded-lg p-2.5 text-center" data-testid="live-estimate-preview">
            <span className="text-xs text-emerald-800">ช่วงราคาประเมินเบื้องต้น:</span>
            <div className="text-base font-extrabold text-emerald-700">
              {liveEstimate.min}–{liveEstimate.max} บาท
            </div>
          </div>
        )}

        {/* ปุ่มเพิ่มลงตะกร้า */}
        <button
          type="submit"
          className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-medium py-2.5 px-4 rounded-lg text-xs transition duration-150 flex items-center justify-center gap-1.5"
          data-testid="add-item-btn"
        >
          <span>➕</span> เพิ่มรายการนี้ลงตะกร้า
        </button>
      </form>
    </div>
  );
}

