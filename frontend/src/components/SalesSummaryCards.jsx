import React from "react";

/**
 * SalesSummaryCards Component
 * แสดงสรุปสถิติสะสมการขายของเก่า (รายรับสะสม, น้ำหนักสะสม, จำนวนครั้งสำเร็จ)
 * รองรับ UC-10, REQ-FN-005, AC-S07-03, P-03, Q-04
 */
export default function SalesSummaryCards({ summary = {}, isOffline = false }) {
  const totalAmount = summary.total_sales_amount || 0;
  const totalWeight = summary.total_weight_kg || 0;
  const totalOrders = summary.total_completed_orders || 0;

  return (
    <div className="mb-5" data-testid="sales-summary-container" data-req="UC-10">
      {/* สรุปสถิติ 3 การ์ด */}
      <div className="grid grid-cols-3 gap-2.5">
        {/* การ์ดที่ 1: รายรับสะสม */}
        <div className="bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl p-3 text-white shadow-sm text-center">
          <div className="text-[10px] font-medium opacity-90 mb-1">💰 รายรับสะสม</div>
          <div className="text-sm font-extrabold tracking-tight" data-testid="total-sales-amount">
            ฿{totalAmount.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 2 })}
          </div>
        </div>

        {/* การ์ดที่ 2: น้ำหนักสะสม */}
        <div className="bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl p-3 text-white shadow-sm text-center">
          <div className="text-[10px] font-medium opacity-90 mb-1">⚖️ น้ำหนักสะสม</div>
          <div className="text-sm font-extrabold tracking-tight" data-testid="total-weight-kg">
            {totalWeight.toLocaleString(undefined, { maximumFractionDigits: 1 })} กก.
          </div>
        </div>

        {/* การ์ดที่ 3: จำนวนครั้งสำเร็จ */}
        <div className="bg-gradient-to-br from-amber-500 to-orange-600 rounded-2xl p-3 text-white shadow-sm text-center">
          <div className="text-[10px] font-medium opacity-90 mb-1">📦 ขายสำเร็จ</div>
          <div className="text-sm font-extrabold tracking-tight" data-testid="total-completed-orders">
            {totalOrders} ครั้ง
          </div>
        </div>
      </div>
    </div>
  );
}

