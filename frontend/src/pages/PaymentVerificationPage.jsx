import React, { useState, useEffect } from "react";
import WeightVerificationCard from "../components/WeightVerificationCard.jsx";
import PaymentConfirmationCard from "../components/PaymentConfirmationCard.jsx";
import DigitalReceiptCard from "../components/DigitalReceiptCard.jsx";
import {
  confirmWeights,
  requestReweigh,
  raiseDispute,
  confirmPayment,
  fetchReceipt,
} from "../services/paymentApi.js";

/**
 * PaymentVerificationPage (Mobile-First Single Page Application)
 * ควบคุมโฟลว์การตรวจสอบน้ำหนัก ชำระเงิน และออกใบเสร็จดิจิทัล
 * รองรับ CC-01, REQ-FN-004, REQ-FN-005, REQ-FN-006, REQ-SEC-002, AC-S06-01..05
 */
export default function PaymentVerificationPage({
  orderId = "ORD-TEST-001",
  sellerId = "USR-SELLER-01",
  initialOrder = null,
  fetchFn = null,
}) {
  const [order, setOrder] = useState(
    initialOrder || {
      order_id: orderId,
      seller_id: sellerId,
      status: "S5",
      total_settled_amount: 300.0,
      scale_photo_url: "https://storage.saleng.app/scales/scale-demo.jpg",
      items: [
        {
          item_id: "itm-01",
          category_code: "MAT-CARDBOARD",
          category_name: "กระดาษลัง",
          unit: "kg",
          est_quantity: 50.0,
          actual_quantity: 60.0,
          locked_unit_price: 3.5,
          settled_item_price: 210.0,
        },
        {
          item_id: "itm-02",
          category_code: "MAT-GLASS-BOTTLE-BAG",
          category_name: "ขวดแก้ว (กระสอบ)",
          unit: "bag",
          est_quantity: 2.0,
          actual_quantity: 2.0,
          locked_unit_price: 45.0,
          settled_item_price: 90.0,
        },
      ],
    }
  );

  const [receiptData, setReceiptData] = useState(null);
  const [isOfflineReceipt, setIsOfflineReceipt] = useState(false);
  const [offlineNotice, setOfflineNotice] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [statusMessage, setStatusMessage] = useState("");

  const currentStatus = order?.status || "S5";

  // 1. ผู้ขายกดยืนยันน้ำหนักจริง (S5 -> S6)
  const handleConfirmWeights = async () => {
    setIsLoading(true);
    setErrorMsg("");
    try {
      const res = await confirmWeights(order.order_id, sellerId, fetchFn);
      setOrder((prev) => ({
        ...prev,
        status: "S6",
        seller_confirmed_weight_at: res.seller_confirmed_weight_at,
      }));
      setStatusMessage("ยืนยันตัวเลขน้ำหนักสำเร็จ กรุณาเลือกวิธีรับเงิน");
    } catch (err) {
      setErrorMsg(err.message || "เกิดข้อผิดพลาดในการยืนยันน้ำหนัก");
    } finally {
      setIsLoading(false);
    }
  };

  // 2. ผู้ขายขอให้ชั่งน้ำหนักซ้ำ (S5 -> S4)
  const handleRequestReweigh = async (reason) => {
    setIsLoading(true);
    setErrorMsg("");
    try {
      const res = await requestReweigh(order.order_id, sellerId, reason, fetchFn);
      setOrder((prev) => ({
        ...prev,
        status: "S4",
        reweigh_requested: true,
        reweigh_reason: reason,
      }));
      setStatusMessage("ส่งคำขอชั่งซ้ำแล้ว ซาเล้งกำลังตรวจสอบตาชั่งและชั่งใหม่");
    } catch (err) {
      setErrorMsg(err.message || "เกิดข้อผิดพลาดในการขอชั่งซ้ำ");
    } finally {
      setIsLoading(false);
    }
  };

  // 3. ผู้ขายปฏิเสธผลชั่งและส่งข้อพิพาท (S5 -> S8)
  const handleRaiseDispute = async (reason) => {
    setIsLoading(true);
    setErrorMsg("");
    try {
      const res = await raiseDispute(order.order_id, sellerId, reason, fetchFn);
      setOrder((prev) => ({
        ...prev,
        status: "S8",
        dispute_reason: reason,
        is_frozen: true,
      }));
      setStatusMessage("ส่งข้อพิพาทเรียบร้อยแล้ว ระบบล็อกข้อมูลและส่งให้ผู้ดูแลระบบตรวจสอบ");
    } catch (err) {
      setErrorMsg(err.message || "เกิดข้อผิดพลาดในการแจ้งข้อพิพาท");
    } finally {
      setIsLoading(false);
    }
  };

  // 4. ผู้ขายยืนยันการรับเงิน (S6 -> S7) และออกใบเสร็จดิจิทัล
  const handleConfirmPayment = async (paymentMethod) => {
    setIsLoading(true);
    setErrorMsg("");
    try {
      const res = await confirmPayment(order.order_id, sellerId, paymentMethod, fetchFn);
      setOrder((prev) => ({
        ...prev,
        status: "S7",
        payment_method: paymentMethod,
        receipt_id: res.receipt_id,
        receipt_no: res.receipt_no,
      }));

      // ดึงข้อมูลใบเสร็จดิจิทัลฉบับสมบูรณ์
      try {
        const receiptRes = await fetchReceipt(order.order_id, fetchFn);
        setReceiptData(receiptRes.receipt);
        setIsOfflineReceipt(receiptRes.isOffline);
        setOfflineNotice(receiptRes.offlineNotice);
      } catch (rErr) {
        // Fallback ใช้ข้อมูลจาก response ชั่วคราว
        setReceiptData({
          receipt_no: res.receipt_no,
          total_amount: res.total_amount,
          payment_method: paymentMethod,
          items: order.items,
          issued_at: new Date().toISOString(),
          seller_phone_masked: "08X-XXX-XXXX",
          buyer_phone_masked: "08X-XXX-XXXX",
        });
      }

      setStatusMessage("ชำระเงินและออกใบเสร็จดิจิทัลสำเร็จ ปิดงานเรียบร้อย");
    } catch (err) {
      setErrorMsg(err.message || "เกิดข้อผิดพลาดในการยืนยันรับเงิน");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      className="min-h-screen bg-slate-50 py-6 px-4 font-sans text-gray-800"
      data-testid="payment-verification-page"
    >
      <div className="max-w-md mx-auto">
        {/* หัวกระดาษ Mobile Header */}
        <div className="text-center mb-5">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-emerald-50 text-emerald-800 rounded-full text-xs font-semibold border border-emerald-200 mb-1.5">
            <span>♻️</span> Saleng Platform • ผู้ขาย
          </div>
          <h1 className="text-lg font-bold text-gray-900">
            ระบบชำระเงินและตรวจสอบ
          </h1>
          <p className="text-xs text-gray-500">
            ยืนยันผลชั่งจริง รับชำระเงิน และรับใบเสร็จดิจิทัล
          </p>
        </div>

        {/* แถบความคืบหน้า 3 ขั้นตอน (Step Indicator) */}
        <div className="flex items-center justify-between mb-5 px-2">
          <div className="flex items-center gap-1.5">
            <span
              className={`w-5 h-5 rounded-full text-[10px] font-bold flex items-center justify-center ${
                currentStatus === "S5" || currentStatus === "S4"
                  ? "bg-amber-500 text-white"
                  : "bg-emerald-600 text-white"
              }`}
            >
              1
            </span>
            <span className="text-[11px] font-medium text-gray-700">ตรวจน้ำหนัก</span>
          </div>
          <div className="flex-1 h-0.5 bg-gray-200 mx-2" />
          <div className="flex items-center gap-1.5">
            <span
              className={`w-5 h-5 rounded-full text-[10px] font-bold flex items-center justify-center ${
                currentStatus === "S6"
                  ? "bg-amber-500 text-white"
                  : currentStatus === "S7"
                  ? "bg-emerald-600 text-white"
                  : "bg-gray-200 text-gray-600"
              }`}
            >
              2
            </span>
            <span className="text-[11px] font-medium text-gray-700">รับชำระเงิน</span>
          </div>
          <div className="flex-1 h-0.5 bg-gray-200 mx-2" />
          <div className="flex items-center gap-1.5">
            <span
              className={`w-5 h-5 rounded-full text-[10px] font-bold flex items-center justify-center ${
                currentStatus === "S7" ? "bg-emerald-600 text-white" : "bg-gray-200 text-gray-600"
              }`}
            >
              3
            </span>
            <span className="text-[11px] font-medium text-gray-700">ใบเสร็จ</span>
          </div>
        </div>

        {/* แจ้งเตือนสถานะ / Error Banner */}
        {errorMsg && (
          <div className="bg-rose-50 border border-rose-200 text-rose-800 text-xs p-3 rounded-xl mb-4 flex items-center gap-2">
            <span>⚠️</span>
            <span>{errorMsg}</span>
          </div>
        )}

        {statusMessage && !errorMsg && (
          <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs p-3 rounded-xl mb-4 flex items-center gap-2">
            <span>ℹ️</span>
            <span>{statusMessage}</span>
          </div>
        )}

        {/* กรณีสถานะ S4: กำลังขอให้ชั่งซ้ำ */}
        {currentStatus === "S4" && (
          <div className="bg-white rounded-2xl border border-amber-200 p-5 mb-4 text-center">
            <span className="text-3xl block mb-2">🔄</span>
            <h3 className="text-sm font-bold text-amber-800 mb-1">
              กำลังรอซาเล้งตรวจสอบและชั่งใหม่
            </h3>
            <p className="text-xs text-gray-500 mb-3">
              คุณได้ส่งคำขอชั่งซ้ำเรียบร้อยแล้ว เมื่อซาเล้งกรอกน้ำหนักใหม่ ข้อมูลจะอัปเดตบนหน้าจอนี้โดยอัตโนมัติ
            </p>
            <span className="text-[11px] font-mono text-gray-400">
              เหตุผล: {order.reweigh_reason || "ขอให้ตรวจสอบตาชั่ง"}
            </span>
          </div>
        )}

        {/* กรณีสถานะ S8: อยู่ในกระบวนการข้อพิพาท (REQ-FN-006) */}
        {currentStatus === "S8" && (
          <div className="bg-white rounded-2xl border border-rose-200 p-5 mb-4 text-center" data-req="REQ-FN-006">
            <span className="text-3xl block mb-2">🚫</span>
            <span className="text-xs font-semibold px-2.5 py-1 bg-rose-50 text-rose-700 rounded-full border border-rose-200 inline-block mb-2">
              สถานะ S8: อยู่ระหว่างการตรวจสอบข้อพิพาท
            </span>
            <h3 className="text-sm font-bold text-gray-800 mb-1">
              คำขอถูกส่งต่อให้ผู้ดูแลระบบ (Admin)
            </h3>
            <p className="text-xs text-gray-500 mb-3 leading-relaxed">
              ระบบได้ทำการล็อกหลักฐานภาพถ่ายหน้าตาชั่ง พิกัด GPS และราคาที่ล็อกไว้เรียบร้อยแล้ว เจ้าหน้าที่จะติดต่อกลับเพื่อประสานงานต่อไป
            </p>
            <div className="bg-rose-50/50 p-2.5 rounded-xl border border-rose-100 text-left text-xs text-rose-900">
              <span className="font-bold block mb-1">เหตุผลข้อพิพาท:</span>
              <p className="text-[11px] text-gray-700">{order.dispute_reason}</p>
            </div>
          </div>
        )}

        {/* ขั้นตอนที่ 1: ตรวจสอบและยืนยันน้ำหนัก (S5) */}
        {currentStatus === "S5" && (
          <WeightVerificationCard
            order={order}
            onConfirmWeights={handleConfirmWeights}
            onRequestReweigh={handleRequestReweigh}
            onRaiseDispute={handleRaiseDispute}
            isLoading={isLoading}
          />
        )}

        {/* ขั้นตอนที่ 2: เลือกวิธีรับเงินและกดยืนยันรับเงิน (S6) */}
        {currentStatus === "S6" && (
          <PaymentConfirmationCard
            order={order}
            onConfirmPayment={handleConfirmPayment}
            isLoading={isLoading}
          />
        )}

        {/* ขั้นตอนที่ 3: แสดงใบเสร็จดิจิทัล (S7) */}
        {currentStatus === "S7" && receiptData && (
          <DigitalReceiptCard
            receipt={receiptData}
            isOffline={isOfflineReceipt}
            offlineNotice={offlineNotice}
            onBackToHome={() => alert("กลับสู่หน้าหลัก")}
          />
        )}
      </div>
    </div>
  );
}

