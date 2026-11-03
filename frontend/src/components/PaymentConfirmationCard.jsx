import React, { useState } from "react";

/**
 * PaymentConfirmationCard Component
 * เลือกช่องทางการรับเงินและกดยืนยันการรับเงินโดยผู้ขาย (S6 -> S7)
 * รองรับ UC-07, REQ-FN-005, AC-S06-03, P-04, Q-03
 */
export default function PaymentConfirmationCard({
  order,
  onConfirmPayment,
  isLoading = false,
}) {
  const [paymentMethod, setPaymentMethod] = useState("PROMPTPAY");

  const totalAmount = order?.total_settled_amount || 0;

  const handleConfirm = () => {
    onConfirmPayment(paymentMethod);
  };

  return (
    <div
      className="bg-white rounded-2xl shadow-sm border border-emerald-100 p-5 mb-4"
      data-req="UC-07"
      data-testid="payment-confirmation-card"
    >
      {/* ส่วนหัวสถานะ S6 */}
      <div className="flex items-center justify-between border-b border-gray-100 pb-3 mb-4">
        <div>
          <span className="text-xs font-semibold px-2.5 py-1 bg-emerald-50 text-emerald-700 rounded-full border border-emerald-200">
            สถานะ S6: ผ่านการยืนยันน้ำหนักแล้ว
          </span>
          <h2 className="text-sm font-bold text-gray-800 mt-1.5">
            💳 เลือกวิธีรับเงินและยืนยันยอด
          </h2>
        </div>
        <div className="text-right">
          <span className="text-[11px] text-gray-400 block">ยอดสุทธิ</span>
          <span className="text-base font-extrabold text-emerald-700 font-mono" data-testid="payment-amount-display">
            ฿{totalAmount.toFixed(2)}
          </span>
        </div>
      </div>

      {/* ตัวเลือกวิธีรับเงิน (เงินสด / PromptPay QR) */}
      <div className="mb-4">
        <label className="block text-xs font-medium text-gray-600 mb-2">
          เลือกช่องทางการรับเงิน:
        </label>
        <div className="grid grid-cols-2 gap-2.5">
          <button
            type="button"
            onClick={() => setPaymentMethod("PROMPTPAY")}
            className={`p-3 rounded-xl border text-xs font-medium flex flex-col items-center gap-1.5 transition duration-150 ${
              paymentMethod === "PROMPTPAY"
                ? "border-emerald-600 bg-emerald-50/50 text-emerald-800 ring-1 ring-emerald-500"
                : "border-gray-200 bg-white text-gray-600 hover:bg-gray-50"
            }`}
            data-testid="pay-method-promptpay"
          >
            <span className="text-xl">📲</span>
            <span className="font-bold">PromptPay QR Code</span>
            <span className="text-[10px] text-gray-500">โอนเงินเข้าบัญชี</span>
          </button>

          <button
            type="button"
            onClick={() => setPaymentMethod("CASH")}
            className={`p-3 rounded-xl border text-xs font-medium flex flex-col items-center gap-1.5 transition duration-150 ${
              paymentMethod === "CASH"
                ? "border-emerald-600 bg-emerald-50/50 text-emerald-800 ring-1 ring-emerald-500"
                : "border-gray-200 bg-white text-gray-600 hover:bg-gray-50"
            }`}
            data-testid="pay-method-cash"
          >
            <span className="text-xl">💵</span>
            <span className="font-bold">เงินสด (Cash)</span>
            <span className="text-[10px] text-gray-500">รับเงินสดหน้างาน</span>
          </button>
        </div>
      </div>

      {/* คำแนะนำตามวิธีชำระเงินที่เลือก */}
      {paymentMethod === "PROMPTPAY" ? (
        <div className="bg-sky-50 border border-sky-100 rounded-xl p-3.5 mb-5 text-center" data-testid="promptpay-box">
          <span className="text-xs font-bold text-sky-900 block mb-1">
            สแกน PromptPay QR เพื่อรับเงิน
          </span>
          <div className="w-28 h-28 mx-auto bg-white rounded-lg border border-sky-200 flex flex-col items-center justify-center p-2 shadow-xs my-2">
            <span className="text-3xl">⬛⬜</span>
            <span className="text-[10px] font-mono text-gray-500 mt-1">PromptPay QR</span>
          </div>
          <p className="text-[11px] text-sky-800">
            แสดง QR Code หรือให้ซาเล้งสแกนจ่ายยอด <strong>฿{totalAmount.toFixed(2)}</strong> เมื่อได้รับเงินเข้าบัญชีแล้วให้กดปุ่มยืนยันด้านล่าง
          </p>
        </div>
      ) : (
        <div className="bg-amber-50 border border-amber-100 rounded-xl p-3.5 mb-5 text-xs text-amber-900" data-testid="cash-box">
          <div className="font-bold mb-1 flex items-center gap-1">
            <span>💵</span> คำแนะนำการรับเงินสดหน้างาน:
          </div>
          <p className="text-[11px] text-amber-800 leading-relaxed">
            กรุณานับเงินสดที่ได้รับจากซาเล้งให้ครบถ้วนจำนวน <strong>฿{totalAmount.toFixed(2)}</strong> ก่อนกดยืนยันการรับเงิน
          </p>
        </div>
      )}

      {/* ปุ่มยืนยันการรับเงิน (Q-03: ผู้ขายเป็นผู้กดเพื่อความปลอดภัย) */}
      <button
        type="button"
        onClick={handleConfirm}
        disabled={isLoading}
        className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-3.5 px-4 rounded-xl text-xs transition duration-150 flex items-center justify-center gap-2 shadow-sm disabled:opacity-50"
        data-testid="confirm-payment-btn"
      >
        <span>🤝</span>
        {paymentMethod === "PROMPTPAY"
          ? "ข้าพเจ้าได้รับเงินโอนเรียบร้อยแล้ว (ปิดงาน)"
          : "ข้าพเจ้าได้รับเงินสดครบถ้วนแล้ว (ปิดงาน)"}
      </button>
    </div>
  );
}

