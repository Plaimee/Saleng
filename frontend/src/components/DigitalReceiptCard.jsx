import React from "react";

/**
 * DigitalReceiptCard Component
 * แสดงใบเสร็จดิจิทัลสรุปรายการซื้อขาย พร้อม PII Masking
 * รองรับ REQ-FN-005, REQ-SEC-002, SC-03, AC-S06-04, P-05, Q-04
 */
export default function DigitalReceiptCard({
  receipt,
  isOffline = false,
  offlineNotice = "",
  onBackToHome,
}) {
  if (!receipt) return null;

  const items = receipt.items || [];
  const totalAmount = receipt.total_amount || 0;

  const handleDownload = () => {
    alert("ระบบกำลังดาวน์โหลดใบเสร็จดิจิทัลลงเครื่องของคุณ...");
  };

  return (
    <div
      className="bg-white rounded-2xl shadow-sm border border-emerald-100 p-5 mb-4"
      data-req="REQ-FN-005"
      data-testid="digital-receipt-card"
    >
      {/* สถานะสำเร็จ S7 */}
      <div className="text-center pb-4 border-b border-gray-100 mb-4">
        <div className="w-12 h-12 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mx-auto mb-2 text-2xl">
          ✓
        </div>
        <span className="text-xs font-semibold px-2.5 py-1 bg-emerald-50 text-emerald-700 rounded-full border border-emerald-200">
          สถานะ S7: สำเร็จ / ปิดงานเรียบร้อย
        </span>
        <h2 className="text-base font-bold text-gray-800 mt-2">
          ใบเสร็จดิจิทัล (Digital Receipt)
        </h2>
        <span className="text-xs font-mono font-medium text-gray-500 block mt-1" data-testid="receipt-no">
          เลขที่: {receipt.receipt_no}
        </span>
      </div>

      {/* ป้ายเตือนโหมดออฟไลน์ (CC-05, REQ-OP-001) */}
      {isOffline && (
        <div
          className="bg-amber-50 border border-amber-200 rounded-xl p-2.5 mb-4 text-[11px] text-amber-800 flex items-center gap-1.5"
          data-testid="offline-receipt-badge"
        >
          <span>📶</span>
          <span>{offlineNotice || "โหมดออฟไลน์: กำลังแสดงใบเสร็จที่บันทึกไว้ในเครื่อง"}</span>
        </div>
      )}

      {/* ข้อมูลการทำธุรกรรมและ PII Masking (REQ-SEC-002) */}
      <div
        className="bg-gray-50/70 rounded-xl p-3 mb-4 text-xs space-y-1.5 border border-gray-100"
        data-req="REQ-SEC-002"
        data-testid="receipt-phones"
      >
        <div className="flex justify-between">
          <span className="text-gray-500">วันที่-เวลา:</span>
          <span className="font-medium text-gray-700" data-testid="receipt-date">
            {receipt.issued_at ? new Date(receipt.issued_at).toLocaleString("th-TH") : "-"}
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">ผู้ขาย:</span>
          <span className="font-mono font-medium text-gray-800">
            {receipt.seller_phone_masked || "08X-XXX-XXXX"}
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">ซาเล้ง (ผู้รับซื้อ):</span>
          <span className="font-mono font-medium text-gray-800">
            {receipt.buyer_phone_masked || "08X-XXX-XXXX"}
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">วิธีชำระเงิน:</span>
          <span className="font-bold text-emerald-700" data-testid="receipt-method">
            {receipt.payment_method === "PROMPTPAY" ? "PromptPay QR Code" : "เงินสด (Cash)"}
          </span>
        </div>
      </div>

      {/* ตารางรายการของเก่า */}
      <div className="mb-4">
        <span className="text-xs font-semibold text-gray-700 block mb-2">
          สรุปรายการของเก่าที่ขาย:
        </span>
        <div className="border border-gray-100 rounded-xl overflow-hidden divide-y divide-gray-100">
          {items.map((item, idx) => (
            <div key={idx} className="p-2.5 bg-white flex justify-between items-center text-xs">
              <div>
                <span className="font-bold text-gray-800 block">
                  {item.category_name || item.category_code}
                </span>
                <span className="text-[11px] text-gray-400">
                  {item.actual_quantity} {item.unit} × {item.locked_unit_price} บ./{item.unit}
                </span>
              </div>
              <span className="font-bold text-gray-800">
                ฿{(item.settled_item_price || item.actual_quantity * item.locked_unit_price).toFixed(2)}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* ยอดเงินสุทธิรวม */}
      <div className="bg-emerald-50/60 border-t-2 border-dashed border-emerald-300 rounded-xl p-3.5 mb-5 flex justify-between items-center">
        <span className="text-xs font-bold text-emerald-900">ยอดเงินสุทธิที่ได้รับ</span>
        <div className="text-right">
          <span className="text-xl font-black text-emerald-700" data-testid="receipt-total">
            ฿{totalAmount.toFixed(2)}
          </span>
        </div>
      </div>

      {/* ปุ่มบันทึกใบเสร็จและกลับหน้าหลัก */}
      <div className="space-y-2">
        <button
          type="button"
          onClick={handleDownload}
          className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-2.5 px-4 rounded-xl text-xs transition duration-150 flex items-center justify-center gap-1.5 shadow-sm"
          data-testid="download-receipt-btn"
        >
          <span>📥</span> บันทึกรูปภาพใบเสร็จ
        </button>

        {onBackToHome && (
          <button
            type="button"
            onClick={onBackToHome}
            className="w-full bg-white hover:bg-gray-50 border border-gray-200 text-gray-700 font-medium py-2.5 px-4 rounded-xl text-xs transition duration-150 text-center"
            data-testid="back-to-home-btn"
          >
            🏠 กลับสู่หน้าหลัก
          </button>
        )}
      </div>
    </div>
  );
}

