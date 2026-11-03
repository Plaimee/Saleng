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
  apiBaseUrl,
  fetchFn = fetch,
}) {
  const [benchmarkData, setBenchmarkData] = useState({
    prices: [],
    last_updated_at: "",
    isOffline: false,
    offlineNotice: "",
  });
  const [basket, setBasket] = useState([]);
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
      className="min-h-screen bg-gray-50 flex flex-col items-center p-3 sm:p-4 text-gray-800 font-sans"
      data-req="CC-01"
      data-testid="pricing-decision-page"
    >
      {/* Mobile-First Container (จำกัดกว้างสุด 420px สำหรับมือถือตาม CC-01) */}
      <div className="w-full max-w-md">
        {/* Header แพลตฟอร์ม */}
        <header className="mb-3 text-center">
          <div className="inline-block bg-emerald-100 text-emerald-800 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider mb-1">
            Saleng Platform • ผู้ขาย
          </div>
          <h1 className="text-lg font-black text-gray-900 tracking-tight">
            ระบบราคาและการตัดสินใจ
          </h1>
          <p className="text-xs text-gray-500">
            ตรวจสอบราคากลางรายวันและประเมินมูลค่าก่อนนัดหมาย
          </p>
        </header>

        {/* ข้อความแจ้งเตือนความผิดพลาดทั่วไป */}
        {generalError && (
          <div className="bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-xl p-3 mb-3" data-testid="general-error-banner">
            {generalError}
          </div>
        )}

        {/* การ์ดความสำเร็จเมื่อส่งคำขอเสร็จสิ้น */}
        {orderSuccess && (
          <div className="bg-emerald-50 border border-emerald-300 text-emerald-900 rounded-xl p-4 mb-4 text-center" data-testid="order-success-card">
            <span className="text-3xl block mb-1">🎉</span>
            <h4 className="font-bold text-sm mb-1">{orderSuccess.message}</h4>
            <p className="text-xs text-emerald-700">
              รหัสคำขอ: <span className="font-mono font-bold">{orderSuccess.order_id.slice(0, 8)}...</span> | สถานะ: <span className="font-bold">{orderSuccess.status}</span>
            </p>
          </div>
        )}

        {/* 1. ตารางราคากลางอ้างอิงรายวัน */}
        <BenchmarkPriceTable
          prices={benchmarkData.prices}
          lastUpdatedAt={benchmarkData.last_updated_at}
          isOffline={benchmarkData.isOffline}
          offlineNotice={benchmarkData.offlineNotice}
        />

        {/* 2. ฟอร์มเลือกของเก่าและคำนวณราคา */}
        <ItemPriceCalculator
          benchmarkPrices={benchmarkData.prices}
          onAddItem={handleAddItem}
        />

        {/* 3. ตะกร้าและแถบสรุปยอดรวม Min-Max */}
        <MultiItemBasketSummary
          basket={basket}
          onRemoveItem={handleRemoveItem}
          totalMin={basketTotals.min}
          totalMax={basketTotals.max}
          onSubmitOrder={() => handlePerformSubmit("DIRECT")}
          isSubmitting={isSubmitting}
        />

        {/* 4. ป๊อปอัปแจ้งเตือนเมื่อไม่ถึงเกณฑ์ขั้นต่ำ 500 บาท */}
        <ThresholdGuardModal
          isOpen={isGuardModalOpen}
          onClose={() => setIsGuardModalOpen(false)}
          totalMin={basketTotals.min}
          totalBags={basketTotals.bags}
          onSelectAlternative={(altType) => handlePerformSubmit(altType)}
        />
      </div>
    </div>
  );
}

