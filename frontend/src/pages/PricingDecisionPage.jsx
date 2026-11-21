import React, { useState, useEffect, useMemo } from "react";
import BenchmarkPriceTable from "../components/BenchmarkPriceTable.jsx";
import ItemPriceCalculator from "../components/ItemPriceCalculator.jsx";
import MultiItemBasketSummary from "../components/MultiItemBasketSummary.jsx";
import ThresholdGuardModal from "../components/ThresholdGuardModal.jsx";
import {
  fetchBenchmarkPrices,
  calculateEstimate,
  submitOrder,
} from "../services/pricingApi.js";

/**
 * PricingDecisionPage (Mobile-First Single Page Application)
 * รองรับ CC-01, REQ-DAT-001, REQ-FN-001, REQ-FN-006, BR-01, AC-S04-01..05, D-01..D-06
 */
export default function PricingDecisionPage({
  sellerId = "22222222-2222-2222-2222-222222222222",
  pickupLocationId = "33333333-3333-3333-3333-333333333333",
  initialBasket = [],
  showCalculator = true,
  onOrderSubmitted,
  apiBaseUrl,
  fetchFn = fetch,
}) {
  const [benchmarkData, setBenchmarkData] = useState({
    prices: [],
    last_updated_at: "",
    isOffline: false,
    offlineNotice: "",
  });
  const [basket, setBasket] = useState(() => initialBasket || []);

  // ซิงก์รายการจากขั้นที่ 1 เข้าตะกร้าประเมินราคาอัตโนมัติ
  useEffect(() => {
    if (initialBasket && initialBasket.length > 0) {
      setBasket(initialBasket);
    }
  }, [initialBasket]);
  const [isGuardModalOpen, setIsGuardModalOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [orderSuccess, setOrderSuccess] = useState(null);
  const [generalError, setGeneralError] = useState("");

  // โหลดราคากลางเมื่อเปิดหน้าจอ
  useEffect(() => {
    let isMounted = true;
    fetchBenchmarkPrices(fetchFn, apiBaseUrl)
      .then((data) => {
        if (isMounted) setBenchmarkData(data);
      })
      .catch((err) => {
        if (isMounted) setGeneralError(err.message || "ไม่สามารถดึงข้อมูลราคากลางได้");
      });
    return () => {
      isMounted = false;
    };
  }, [fetchFn, apiBaseUrl]);

  // คำนวณยอดรวม Min-Max ของตะกร้า
  const basketTotals = useMemo(() => {
    const min = basket.reduce((acc, i) => acc + (i.est_min_price || 0), 0);
    const max = basket.reduce((acc, i) => acc + (i.est_max_price || 0), 0);
    const bags = basket.reduce(
      (acc, i) =>
        i.unit === "bag" && (i.category_code.includes("GLASS") || i.category_code.includes("PLASTIC"))
          ? acc + i.quantity
          : acc,
      0
    );
    return {
      min: Math.round(min * 100) / 100,
      max: Math.round(max * 100) / 100,
      bags,
    };
  }, [basket]);

  const handleAddItem = (item) => {
    setBasket((prev) => [...prev, item]);
    setOrderSuccess(null);
    setGeneralError("");
  };

  const handleRemoveItem = (index) => {
    setBasket((prev) => prev.filter((_, idx) => idx !== index));
    setOrderSuccess(null);
  };

  // ดำเนินการส่งคำขอนัดหมาย
  const handlePerformSubmit = async (submissionType = "DIRECT") => {
    if (basket.length === 0) return;
    setIsSubmitting(true);
    setGeneralError("");

    try {
      const payload = {
        seller_id: sellerId,
        pickup_location_id: pickupLocationId,
        submission_type: submissionType,
        items: basket.map((i) => ({
          category_code: i.category_code,
          unit: i.unit,
          quantity: i.quantity,
        })),
      };

      const result = await submitOrder(payload, fetchFn, apiBaseUrl);

      if (result.ok) {
        setIsGuardModalOpen(false);
        setOrderSuccess(result.data);
        setBasket([]);
        if (onOrderSubmitted) onOrderSubmitted(result.data);
      } else if (result.error === "MINIMUM_THRESHOLD_NOT_MET") {
        // บล็อกและเปิดป๊อปอัปทางเลือก (AC-S04-03)
        setIsGuardModalOpen(true);
      }
    } catch (err) {
      setGeneralError(err.message || "เกิดข้อผิดพลาดในการส่งคำขอ");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      className="w-full text-black font-sans space-y-5"
      data-req="CC-01"
      data-testid="pricing-decision-page"
    >
      {/* Header Banner: Golden Yellow + Jet Black */}
      <header className="rounded-2xl p-4 bg-yellow-400 border-2 border-black shadow-sm flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-black text-yellow-400 flex items-center justify-center text-xl flex-shrink-0">
            💰
          </div>
          <div>
            <span className="inline-block bg-black text-yellow-400 text-[10px] font-bold px-2.5 py-0.5 rounded-full uppercase tracking-wider mb-0.5">
              Saleng Platform • ผู้ขาย
            </span>
            <h1 className="text-base sm:text-lg font-extrabold text-black tracking-tight leading-tight">
              ระบบราคาและการตัดสินใจ
            </h1>
            <p className="text-xs text-black/80">
              ตรวจสอบราคากลางรายวันและประเมินมูลค่าก่อนนัดหมาย
            </p>
          </div>
        </div>
        {basket.length > 0 && (
          <div className="px-4 py-2 rounded-xl bg-black text-yellow-400 text-right">
            <div className="text-[10px] text-white/80 font-medium">ยอดประเมินในตะกร้า ({basket.length} รายการ)</div>
            <div className="text-sm font-extrabold">{basketTotals.min}–{basketTotals.max} บาท</div>
          </div>
        )}
      </header>

      {/* ข้อความแจ้งเตือนความผิดพลาดทั่วไป */}
      {generalError && (
        <div className="bg-rose-50 border-2 border-rose-300 text-rose-700 text-xs font-semibold rounded-xl p-3" data-testid="general-error-banner">
          ⚠️ {generalError}
        </div>
      )}

      {/* การ์ดความสำเร็จเมื่อส่งคำขอเสร็จสิ้น */}
      {orderSuccess && (
        <div className="bg-yellow-100 border-2 border-black text-black rounded-2xl p-4 text-center shadow-sm" data-testid="order-success-card">
          <span className="text-3xl block mb-1">🎉</span>
          <h4 className="font-extrabold text-sm mb-1">{orderSuccess.message}</h4>
          <p className="text-xs text-zinc-800">
            รหัสคำขอ: <span className="font-mono font-bold">{orderSuccess.order_id.slice(0, 8)}...</span> | สถานะ: <span className="font-bold">{orderSuccess.status}</span>
          </p>
        </div>
      )}

      {/* Responsive 2-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
        {/* ซ้าย (7 ส่วน): ตารางราคากลางอ้างอิงรายวัน */}
        <div className="lg:col-span-7 bg-yellow-50/90 rounded-2xl p-4 border border-yellow-300">
          <BenchmarkPriceTable
            prices={benchmarkData.prices}
            lastUpdatedAt={benchmarkData.last_updated_at}
            isOffline={benchmarkData.isOffline}
            offlineNotice={benchmarkData.offlineNotice}
          />
        </div>

        {/* ขวา (5 ส่วน): ตะกร้าสรุปยอด + เครื่องคำนวณเพิ่มเติม */}
        <div className="lg:col-span-5 space-y-4">
          <div className="bg-yellow-50/90 rounded-2xl p-4 border-2 border-black shadow-sm">
            <MultiItemBasketSummary
              basket={basket}
              onRemoveItem={handleRemoveItem}
              totalMin={basketTotals.min}
              totalMax={basketTotals.max}
              onSubmitOrder={() => handlePerformSubmit("DIRECT")}
              isSubmitting={isSubmitting}
            />
          </div>

          {showCalculator && (
            <div className="bg-white rounded-2xl p-4 border border-yellow-300 shadow-xs">
              <ItemPriceCalculator
                benchmarkPrices={benchmarkData.prices}
                onAddItem={handleAddItem}
              />
            </div>
          )}
        </div>
      </div>

      {/* 4. ป๊อปอัปแจ้งเตือนเมื่อไม่ถึงเกณฑ์ขั้นต่ำ 500 บาท */}
      <ThresholdGuardModal
        isOpen={isGuardModalOpen}
        onClose={() => setIsGuardModalOpen(false)}
        totalMin={basketTotals.min}
        totalBags={basketTotals.bags}
        onSelectAlternative={(altType) => handlePerformSubmit(altType)}
      />
    </div>
  );
}

