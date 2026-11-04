import React from 'react';

/**
 * PurchaseHistoryCard Component
 * แสดงรายการคำขอรับซื้อของเก่าที่เสร็จสิ้นแล้ว (S7) พร้อมข้อมูล PII Masking
 * รองรับ UC-10, REQ-FN-005, REQ-SEC-002, CC-01, CC-06, D-B07-03..05
 */
export default function PurchaseHistoryCard({
  item,
  onViewReceipt,
  onToggleRegularCustomer,
  isToggling = false,
}) {
  if (!item) return null;

  const formattedDate = item.completed_at
    ? new Date(item.completed_at).toLocaleString('th-TH', {
        dateStyle: 'medium',
        timeStyle: 'short',
      })
    : '-';

  return (
    <div
      className="bg-white rounded-2xl border border-gray-200 p-4 shadow-sm space-y-3"
      data-req="UC-10"
      data-testid={`purchase-history-card-${item.order_id}`}
    >
      {/* ส่วนหัวบัตร: วันที่, รหัสคำขอ, และสถานะ S7 */}
      <div className="flex justify-between items-start border-b border-gray-100 pb-2.5">
        <div>
          <span className="text-xs text-gray-400 block font-mono" data-testid="order-id">
            คำขอ #{item.order_id}
          </span>
          <span className="text-xs font-medium text-gray-600 block mt-0.5" data-testid="completed-date">
            📅 {formattedDate}
          </span>
        </div>
        <span
          className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200"
          data-testid="status-badge"
        >
          ✓ S7 สำเร็จ
        </span>
      </div>

      {/* ข้อมูลคู่ค้าและ PII Masking (REQ-SEC-002, CC-06) */}
      <div className="bg-gray-50/80 rounded-xl p-3 text-xs space-y-1.5 border border-gray-100">
        <div className="flex justify-between items-center">
          <span className="text-gray-500">ผู้ขาย:</span>
          <span className="font-bold text-gray-800" data-testid="seller-name">
            {item.seller_name}
          </span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-gray-500">เบอร์โทรศัพท์ (PDPA):</span>
          <span className="font-mono font-medium text-gray-700" data-testid="seller-phone-masked">
            {item.seller_phone_masked}
          </span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-gray-500">ช่องทางชำระ:</span>
          <span className="font-semibold text-emerald-700" data-testid="payment-method">
            {item.payment_method === 'PROMPTPAY' ? '📱 พร้อมเพย์ QR' : '💵 เงินสด'}
          </span>
        </div>
      </div>

      {/* สรุปรายการของเก่าและยอดเงิน */}
      <div className="flex justify-between items-end pt-1">
        <div>
          <span className="text-xs text-gray-400 block">รายการวัสดุ</span>
          <span className="text-xs font-medium text-gray-700 block max-w-[200px] truncate" title={item.items_summary}>
            {item.items_summary || 'ของเก่าคละรายการ'}
          </span>
          <span className="text-[11px] text-gray-400 block mt-0.5">
            น้ำหนักรวม: <strong className="text-gray-700">{item.total_weight_kg} กก.</strong>
          </span>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400 block">ยอดจ่ายสุทธิ</span>
          <span className="text-lg font-black text-emerald-700" data-testid="total-amount">
            ฿{Number(item.total_settled_amount).toFixed(2)}
          </span>
        </div>
      </div>

      {/* ปุ่มกดดำเนินการ (ทัชทาร์เก็ต >= 48px ตาม REQ-UX-001, CC-01) */}
      <div className="grid grid-cols-2 gap-2 pt-1 border-t border-gray-100">
        <button
          type="button"
          onClick={() => onViewReceipt && onViewReceipt(item.order_id)}
          className="min-h-[48px] px-3 bg-gray-100 hover:bg-gray-200 text-gray-700 font-bold text-xs rounded-xl transition flex items-center justify-center gap-1.5"
          data-testid="view-receipt-btn"
        >
          <span>🧾</span> ดูใบเสร็จ
        </button>

        <button
          type="button"
          onClick={() => onToggleRegularCustomer && onToggleRegularCustomer(item)}
          disabled={isToggling}
          className={`min-h-[48px] px-3 font-bold text-xs rounded-xl transition flex items-center justify-center gap-1.5 border ${
            item.is_regular_customer
              ? 'bg-amber-50 text-amber-800 border-amber-300 hover:bg-amber-100'
              : 'bg-white hover:bg-gray-50 text-gray-700 border-gray-300'
          }`}
          data-testid="toggle-regular-customer-btn"
        >
          <span>{item.is_regular_customer ? '⭐' : '☆'}</span>
          <span>{item.is_regular_customer ? 'ลูกค้าประจำแล้ว' : 'ปักหมุดลูกค้าประจำ'}</span>
        </button>
      </div>
    </div>
  );
}

