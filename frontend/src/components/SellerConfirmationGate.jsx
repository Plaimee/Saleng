import React from 'react';

/**
 * SellerConfirmationGate Component
 * ประตูกั้นยืนยันน้ำหนัก 100% โดยผู้ขาย (100% Confirmation Gate)
 * ป้องกันซาเล้งยืนยันแทนหรือข้ามขั้นตอนไปจ่ายเงินก่อนได้รับความยินยอม
 * รองรับ REQ-FN-004, AC-B06-03, D-B06-01, Two-Party Safety Gate
 */
export default function SellerConfirmationGate({
  orderId,
  sellerConfirmed = false,
  orderStatus = 'S5',
  totalAmount = 0,
  onCheckStatus,
  onProceedToPayment,
  isLoading = false,
}) {
  const isConfirmed = sellerConfirmed || orderStatus === 'S6' || orderStatus === 'S7';

  return (
    <div
      className="bg-white rounded-2xl border border-gray-200 p-5 shadow-sm space-y-4"
      data-req="REQ-FN-004"
      data-testid="seller-confirmation-gate"
    >
      <div className="text-center space-y-2">
        <div
          className={`w-14 h-14 rounded-full flex items-center justify-center mx-auto text-2xl ${
            isConfirmed ? 'bg-emerald-100 text-emerald-600' : 'bg-amber-100 text-amber-600 animate-pulse'
          }`}
          data-testid="gate-status-icon"
        >
          {isConfirmed ? '✓' : '⏳'}
        </div>

        <span
          className={`inline-block text-xs font-semibold px-3 py-1 rounded-full border ${
            isConfirmed
              ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
              : 'bg-amber-50 text-amber-700 border-amber-200'
          }`}
          data-testid="gate-status-badge"
        >
          {isConfirmed ? 'สถานะ S6: ผู้ขายยืนยันน้ำหนักแล้ว' : 'สถานะ S5: รอผู้ขายกดยืนยันน้ำหนัก 100%'}
        </span>

        <h3 className="text-base font-bold text-gray-800">
          {isConfirmed ? 'ผู้ขายยืนยันน้ำหนักเรียบร้อยแล้ว' : 'รอผู้ขายตรวจสอบและยืนยันน้ำหนัก'}
        </h3>

        <p className="text-xs text-gray-600 max-w-sm mx-auto">
          {isConfirmed
            ? 'ผู้ขายได้ตรวจสอบผลการชั่งและกดยืนยันตัวเลขบนหน้าจอแล้ว คุณสามารถเลือกช่องทางชำระเงินเพื่อดำเนินการต่อ'
            : 'ซาเล้งไม่สามารถยืนยันหรือปิดยอดแทนผู้ขายได้ (Two-Party Rule) กรุณาแจ้งให้ผู้ขายตรวจสอบน้ำหนักบนหน้าจอของผู้ขาย'}
        </p>
      </div>

      <div className="bg-gray-50 rounded-xl p-3 border border-gray-100 text-xs flex justify-between items-center">
        <span className="text-gray-500">ยอดเงินที่รอการยืนยัน:</span>
        <span className="text-base font-black text-emerald-700" data-testid="gate-total-amount">
          ฿{Number(totalAmount).toFixed(2)}
        </span>
      </div>

      {!isConfirmed ? (
        <div className="space-y-2">
          <button
            type="button"
            onClick={onCheckStatus}
            disabled={isLoading}
            className="w-full min-h-[48px] bg-amber-500 hover:bg-amber-600 text-white font-bold rounded-xl text-sm transition duration-150 flex items-center justify-center gap-2 shadow-sm disabled:opacity-60"
            data-testid="check-confirmation-btn"
          >
            {isLoading ? 'กำลังตรวจสอบ...' : '🔄 ตรวจสอบสถานะการยืนยันของผู้ขาย'}
          </button>
          <p className="text-[11px] text-gray-400 text-center">
            ระบบจะปลดล็อกขั้นตอนชำระเงินอัตโนมัติเมื่อผู้ขายกดยืนยัน
          </p>
        </div>
      ) : (
        <button
          type="button"
          onClick={onProceedToPayment}
          className="w-full min-h-[48px] bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl text-sm transition duration-150 flex items-center justify-center gap-2 shadow-sm"
          data-testid="proceed-to-payment-btn"
        >
          💳 ดำเนินการชำระเงิน (เลือกเงินสด / PromptPay)
        </button>
      )}
    </div>
  );
}

