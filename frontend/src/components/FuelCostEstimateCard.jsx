/**
 * คอมโพเนนต์การ์ดแสดงระยะทางและค่าน้ำมันโดยประมาณ (FuelCostEstimateCard)
 * รองรับ UC-04, Card 02, REQ-FN-002, REQ-QA-002, CC-03, REQ-OP-002, AC-B03-01, AC-B03-02, D-B03-01, D-B03-02
 */

import React from 'react';

const VEHICLE_LABELS = {
  TRICYCLE: {
    name: 'รถซาเล้งถีบ / พ่วงมือ',
    rate: '0.00 บ./กม.',
    badge: 'bg-green-100 text-green-800 border-green-300',
  },
  MOTORCYCLE: {
    name: 'มอเตอร์ไซค์พ่วงข้าง',
    rate: '2.50 บ./กม.',
    badge: 'bg-blue-100 text-blue-800 border-blue-300',
  },
  PICKUP: {
    name: 'รถกระบะรับซื้อ',
    rate: '4.50 บ./กม.',
    badge: 'bg-purple-100 text-purple-800 border-purple-300',
  },
};

export default function FuelCostEstimateCard({
  road_distance_km = 0.0,
  estimated_fuel_cost = 0.0,
  vehicle_type = 'MOTORCYCLE',
  is_fallback_distance = false,
}) {
  const vInfo = VEHICLE_LABELS[vehicle_type] || VEHICLE_LABELS.MOTORCYCLE;
  const dist = Number(road_distance_km) || 0;
  const cost = Number(estimated_fuel_cost) || 0;

  return (
    <div
      data-testid="fuel-estimate-card"
      data-req="Card-02"
      className="p-4 bg-white rounded-xl border border-slate-200 shadow-sm"
    >
      <div className="flex justify-between items-start mb-3">
        <div>
          <h3 className="text-sm font-bold text-slate-800 flex items-center gap-1.5">
            ⛽ ระยะทางและค่าน้ำมันประเมิน
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            คำนวณตามประเภทยานพาหนะจริง (ความคลาดเคลื่อน ≤ 15%)
          </p>
        </div>

        {/* ป้ายประเภทยานพาหนะ */}
        <span
          data-testid="vehicle-type-badge"
          className={`px-2 py-0.5 rounded-full text-[11px] font-semibold border ${vInfo.badge}`}
        >
          {vInfo.name}
        </span>
      </div>

      {/* แผงแสดงค่าตัวเลขหลัก */}
      <div className="grid grid-cols-2 gap-3 p-3 bg-slate-50 rounded-lg border border-slate-100">
        <div>
          <span className="text-[11px] text-slate-500 block">ระยะทางถนน</span>
          <div className="flex items-baseline gap-1 mt-0.5">
            <span
              data-testid="road-distance-value"
              className="text-lg font-extrabold text-slate-800"
            >
              {dist.toFixed(1)}
            </span>
            <span className="text-xs text-slate-600">กม.</span>
          </div>
          {is_fallback_distance && (
            <span
              data-testid="routing-fallback-badge"
              className="inline-flex items-center gap-1 mt-1 px-1.5 py-0.5 bg-amber-100 text-amber-800 border border-amber-300 rounded text-[10px] font-medium"
            >
              ⚡ ระยะทางประเมินสำรอง
            </span>
          )}
        </div>

        <div className="border-l border-slate-200 pl-3">
          <span className="text-[11px] text-slate-500 block">ค่าน้ำมันโดยประมาณ</span>
          <div className="flex items-baseline gap-1 mt-0.5">
            <span
              data-testid="fuel-cost-value"
              className="text-lg font-extrabold text-emerald-700"
            >
              {cost.toFixed(2)}
            </span>
            <span className="text-xs text-slate-600">บาท</span>
          </div>
          <span className="text-[10px] text-slate-400 block mt-1">
            อัตราสิ้นเปลือง: {vInfo.rate}
          </span>
        </div>
      </div>
    </div>
  );
}

