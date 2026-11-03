import React, { useState } from "react";

/**
 * SalesOrderCard Component
 * แสดงรายการประวัติการขายที่สำเร็จ 1 ใบงาน พร้อมป้าย PII Masking, ผู้รับซื้อประจำ และปุ่มดูใบเสร็จ
 * รองรับ UC-10, REQ-FN-005, REQ-SEC-002, AC-S07-02, AC-S07-03, AC-S07-04
 */
export default function SalesOrderCard({
  order,
  onToggleFavorite,
  onOpenReceipt,
}) {
  if (!order) return null;

  const [favLoading, setFavLoading] = useState(false);
  const items = order.items || [];

  const handleFavClick = async () => {
    if (!onToggleFavorite) return;
    setFavLoading(true);
    try {
      await onToggleFavorite(order.collector_id);
    } finally {
      setFavLoading(false);
    }
  };

  return (
    <div
      className="bg-white rounded-2xl border border-gray-100 shadow-sm p-4 mb-3"
      data-testid={`sales-order-card-${order.order_id}`}
      data-req="REQ-FN-005"
    >
      {/* Header: วันที่เวลา และ รหัสคำขอ */}
      <div className="flex justify-between items-start pb-2.5 border-b border-gray-100 mb-2.5">
        <div>
          <span className="text-[10px] font-mono text-gray-400 block">
            {order.order_id}
          </span>
          <span className="text-xs font-semibold text-gray-800">
            {order.completed_at ? new Date(order.completed_at).toLocaleDateString("th-TH") : "จบงานสมบูรณ์"}
          </span>
        </div>
        <div className="text-right">
          <span className="text-xs font-bold text-emerald-600 block">
            ฿{Number(order.total_settled_amount || 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}
          </span>
          <span className="text-[10px] text-gray-400 font-medium">
            ชำระด้วย {order.payment_method === "PROMPTPAY" ? "PromptPay" : "เงินสด"}
          </span>
        </div>
      </div>

      {/* ข้อมูลซาเล้งผู้รับซื้อ พร้อม PII Masking (REQ-SEC-002) */}
      <div className="flex items-center justify-between bg-gray-50 rounded-xl p-2.5 mb-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center text-xs font-bold">
            🛒
          </div>
          <div>
            <div className="text-xs font-semibold text-gray-800 flex items-center gap-1.5">
              <span>{order.collector_name}</span>
              {order.is_favorite_collector && (
                <span
                  className="bg-amber-100 text-amber-700 text-[9px] font-bold px-1.5 py-0.5 rounded-full"
                  data-testid="favorite-collector-badge"
                >
                  ⭐ ขาประจำ
                </span>
              )}
            </div>
            {/* REQ-SEC-002: เบอร์โทรศัพท์ถูก Masking */}
            <div
              className="text-[10px] font-mono text-gray-500"
              data-testid="collector-phone-masked"
              data-req="REQ-SEC-002"
            >
              📞 {order.collector_phone_masked}
            </div>
          </div>
        </div>

        {/* ปุ่ม Toggle ผู้รับซื้อประจำ (AC-S07-02) */}
        {onToggleFavorite && (
          <button
            type="button"
            onClick={handleFavClick}
            disabled={favLoading}
            data-testid={`toggle-fav-btn-${order.order_id}`}
            data-req="UC-10"
            className={`p-1.5 rounded-xl text-xs transition-colors border ${
              order.is_favorite_collector
                ? "bg-amber-50 text-amber-600 border-amber-200"
                : "bg-white text-gray-400 border-gray-200 hover:text-amber-500"
            }`}
            title={order.is_favorite_collector ? "ยกเลิกผู้รับซื้อประจำ" : "บันทึกเป็นผู้รับซื้อประจำ"}
          >
            {order.is_favorite_collector ? "⭐" : "☆"}
          </button>
        )}
      </div>

      {/* สรุปรายการขยะคร่าวๆ */}
      <div className="text-[11px] text-gray-600 mb-3 space-y-1">
        {items.map((it, idx) => (
          <div key={idx} className="flex justify-between">
            <span>• {it.category_name} ({it.actual_quantity} {it.unit})</span>
            <span className="font-mono text-gray-500">฿{it.settled_item_price}</span>
          </div>
        ))}
      </div>

      {/* ปุ่มกดเปิดดูใบเสร็จดิจิทัล (AC-S07-04, REQ-FN-005) */}
      <button
        type="button"
        onClick={() => onOpenReceipt(order.order_id)}
        data-testid={`open-receipt-btn-${order.order_id}`}
        data-req="REQ-FN-005"
        className="w-full py-2 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 font-semibold rounded-xl text-xs border border-emerald-200 transition-colors flex items-center justify-center gap-1.5"
      >
        <span>📄</span>
        <span>ดูใบเสร็จดิจิทัล</span>
      </button>
    </div>
  );
}

