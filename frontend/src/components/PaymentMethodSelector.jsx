import React, { useState } from 'react';

/**
 * PaymentMethodSelector Component
 * ส่วนเลือกช่องทางการชำระเงินหน้างาน (เงินสด หรือ PromptPay QR)
 * รองรับ UC-06, REQ-FN-004, D-B06-04 (Non-goal: ไม่มี In-App Wallet หรือ Payment Gateway)
 */
export default function PaymentMethodSelector({
  orderId,
  totalAmount = 0,
  sellerPhoneMasked = '',
  selectedMethod = null,
  onSelectPaymentMethod,
  isLoading = false,
}) {
  const [method, setMethod] = useState(selectedMethod || 'CASH');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (onSelectPaymentMethod) {
      onSelectPaymentMethod(method);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-white rounded-2xl border border-gray-200 p-5 shadow-sm space-y-4"
      data-req="REQ-FN-004"
      data-testid="payment-method-selector"
    >
      <div className="border-b border-gray-100 pb-3">
        <h3 className="text-base font-bold text-gray-800">
          💵 เลือกช่องทางการชำระเงินหน้างาน
        </h3>
        <p className="text-xs text-gray-500 mt-0.5">
          ชำระเงินตามยอดสุทธิที่ผู้ขายยืนยันแล้ว (D-B06-04)
        </p>
      </div>

      <div className="bg-emerald-50 rounded-xl p-3 border border-emerald-100 flex justify-between items-center">
        <span className="text-xs font-bold text-emerald-900">ยอดเงินที่ต้องชำระ:</span>
        <span className="text-xl font-black text-emerald-700" data-testid="payment-total-amount">
          ฿{Number(totalAmount).toFixed(2)}
        </span>
      </div>

      {/* ตัวเลือกช่องทางชำระเงิน */}
      <div className="space-y-2.5">
        <label
          className={`min-h-[48px] p-3.5 rounded-xl border flex items-center justify-between cursor-pointer transition ${
            method === 'CASH'
              ? 'border-emerald-500 bg-emerald-50/40 text-emerald-900 font-bold'
              : 'border-gray-200 hover:bg-gray-50 text-gray-700 font-medium'
          }`}
          data-testid="option-cash"
        >
          <div className="flex items-center gap-3">
            <span className="text-2xl">💵</span>
            <div>
              <span className="text-sm block">ชำระด้วยเงินสด (Cash)</span>
              <span className="text-xs text-gray-500 font-normal">
                ส่งมอบเงินสดให้ผู้ขายโดยตรง ณ จุดรับซื้อ
              </span>
            </div>
          </div>
          <input
            type="radio"
            name="payment_method"
            value="CASH"
            checked={method === 'CASH'}
            onChange={() => setMethod('CASH')}
            className="w-4 h-4 text-emerald-600 focus:ring-emerald-500"
          />
        </label>

        <label
          className={`min-h-[48px] p-3.5 rounded-xl border flex items-center justify-between cursor-pointer transition ${
            method === 'PROMPTPAY'
              ? 'border-emerald-500 bg-emerald-50/40 text-emerald-900 font-bold'
              : 'border-gray-200 hover:bg-gray-50 text-gray-700 font-medium'
          }`}
          data-testid="option-promptpay"
        >
          <div className="flex items-center gap-3">
            <span className="text-2xl">📱</span>
            <div>
              <span className="text-sm block">พร้อมเพย์ QR Code (PromptPay)</span>
              <span className="text-xs text-gray-500 font-normal">
                สแกน QR ผ่านแอป Mobile Banking ของคุณ
              </span>
            </div>
          </div>
          <input
            type="radio"
            name="payment_method"
            value="PROMPTPAY"
            checked={method === 'PROMPTPAY'}
            onChange={() => setMethod('PROMPTPAY')}
            className="w-4 h-4 text-emerald-600 focus:ring-emerald-500"
          />
        </label>
      </div>

      {method === 'PROMPTPAY' && (
        <div
          className="bg-blue-50 border border-blue-200 rounded-xl p-3 text-xs text-blue-800 space-y-1"
          data-testid="promptpay-instructions"
        >
          <span className="font-bold block">ℹ️ คำแนะนำการชำระผ่าน PromptPay:</span>
          <p>
            ขอให้ผู้ขายเปิด QR Code หรือแจ้งเบอร์ PromptPay จากนั้นเปิดแอปธนาคารบนมือถือของคุณเพื่อสแกนจ่าย
            (ระบบไม่มี In-App Wallet หรือ Payment Gateway ตามขอบเขต D-B06-04)
          </p>
        </div>
      )}

      <div className="bg-amber-50 border border-amber-200 rounded-xl p-3 text-xs text-amber-800">
        <span>⚠️ </span>
        <span className="font-bold">กติกาสองฝ่าย (Two-Party Rule): </span>
        <span>
          หลังคุณชำระเงินแล้ว ผู้ขายจะต้องเป็นผู้กดยืนยันการรับเงินบนหน้าจอของผู้ขายเอง (S6 -&gt; S7) เพื่อออกใบเสร็จดิจิทัล
        </span>
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full min-h-[48px] bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl text-sm transition duration-150 flex items-center justify-center gap-2 shadow-sm disabled:opacity-60"
        data-testid="confirm-payment-method-btn"
      >
        {isLoading ? 'กำลังบันทึก...' : '✅ ยืนยันช่องทางชำระเงินและแจ้งผู้ขาย'}
      </button>
    </form>
  );
}

