import React, { useState } from 'react';

/**
 * คอมโพเนนต์ตารางคิวนัดหมายตกค้างสถานะ S2 > 30 นาที (Manual Dispatch Fallback)
 * รองรับ UC-13, D-A03-02, D-A03-03, D-00-01, REQ-UX-001, CC-01, CC-06
 * ทัชทาร์เก็ตปุ่มกด >= 48px ทุกปุ่ม
 */
export default function StalledOrdersTable({
  orders = [],
  availableSalengs = [
    { saleng_id: 'saleng-01', display_name: 'ลุงสมชาย ซาเล้งสุทธิสาร (Online / KYC)', verified: true, is_online: true },
    { saleng_id: 'saleng-02', display_name: 'พี่นก ขยะรีไซเคิล (Online / KYC)', verified: true, is_online: true },
  ],
  onAssign,
  onExpandRadius,
  isLoading = false,
}) {
  const [selectedSalengMap, setSelectedSalengMap] = useState({});

  const handleSalengChange = (orderId, salengId) => {
    setSelectedSalengMap((prev) => ({
      ...prev,
      [orderId]: salengId,
    }));
  };

  const handleDirectAssign = (orderId) => {
    const salengId = selectedSalengMap[orderId] || (availableSalengs[0]?.saleng_id || 'saleng-01');
    if (onAssign) {
      onAssign(orderId, salengId);
    }
  };

  if (!orders || orders.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center text-gray-500">
        <svg className="w-12 h-12 mx-auto text-emerald-500 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p className="text-base font-medium text-gray-700">ไม่มีคำขอนัดหมายตกค้างเกินเกณฑ์เวลา</p>
        <p className="text-sm text-gray-400 mt-1">คำขอสถานะ S2 ทั้งหมดได้รับการรับงานหรืออยู่ในระยะเวลาปกติ</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <div className="p-4 bg-gray-50 border-b border-gray-200 flex flex-wrap justify-between items-center gap-2">
        <div>
          <h3 className="font-semibold text-gray-800 text-base">คิวนัดหมายตกค้างรอรับงาน (เกิน 30 นาที)</h3>
          <p className="text-xs text-gray-500">ระบบกรองคำขอ S2 ที่ไม่มีซาเล้งกดรับ เพื่อให้แอดมินแทรกแซงกระจายงานสำรอง</p>
        </div>
        <span className="px-3 py-1 bg-amber-100 text-amber-800 text-xs font-semibold rounded-full">
          ตกค้าง {orders.length} รายการ
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-gray-700">
          <thead className="bg-gray-100 text-gray-600 text-xs uppercase tracking-wider">
            <tr>
              <th className="py-3 px-4">รหัสคำขอ</th>
              <th className="py-3 px-4">ระยะเวลารอ</th>
              <th className="py-3 px-4">พื้นที่ (ตำบล/เขต)</th>
              <th className="py-3 px-4">ช่วงราคาประเมิน</th>
              <th className="py-3 px-4">รัศมีปัจจุบัน</th>
              <th className="py-3 px-4 text-center">การแทรกแซงกระจายงาน</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {orders.map((order) => {
              const selectedSaleng = selectedSalengMap[order.order_id] || (availableSalengs[0]?.saleng_id || 'saleng-01');
              return (
                <tr key={order.order_id} className="hover:bg-amber-50/40 transition">
                  <td className="py-4 px-4 font-mono font-medium text-gray-900">
                    {order.order_id}
                    <div className="text-xs text-gray-400 mt-0.5">ผู้ขาย: {order.seller_id}</div>
                  </td>
                  <td className="py-4 px-4">
                    <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-red-100 text-red-800">
                      รอ {order.waiting_minutes} นาที
                    </span>
                  </td>
                  <td className="py-4 px-4">
                    <div className="font-medium text-gray-800">{order.subdistrict || 'ไม่ระบุ'}</div>
                    <div className="text-xs text-gray-500">{order.district || 'กรุงเทพมหานคร'}</div>
                  </td>
                  <td className="py-4 px-4">
                    <span className="font-medium text-emerald-700">
                      ฿{order.total_est_min_price} – ฿{order.total_est_max_price}
                    </span>
                    <div className="text-xs text-gray-400">~{order.total_est_weight_kg} กก.</div>
                  </td>
                  <td className="py-4 px-4">
                    <span className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded text-xs font-medium">
                      {order.search_radius_km || 5.0} กม.
                    </span>
                  </td>
                  <td className="py-4 px-4">
                    <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-center gap-2">
                      {/* Dropdown เลือกซาเล้ง */}
                      <select
                        aria-label={`เลือกซาเล้งสำหรับ ${order.order_id}`}
                        value={selectedSaleng}
                        onChange={(e) => handleSalengChange(order.order_id, e.target.value)}
                        className="text-xs border border-gray-300 rounded-lg px-2 py-2 bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 min-h-[48px]"
                      >
                        {availableSalengs.map((s) => (
                          <option key={s.saleng_id} value={s.saleng_id}>
                            {s.display_name}
                          </option>
                        ))}
                      </select>

                      {/* ปุ่มมอบหมายงานตรง */}
                      <button
                        type="button"
                        onClick={() => handleDirectAssign(order.order_id)}
                        disabled={isLoading}
                        className="min-h-[48px] px-3 py-2 bg-emerald-600 hover:bg-emerald-700 active:scale-95 text-white text-xs font-medium rounded-lg shadow-sm transition flex items-center justify-center gap-1 disabled:opacity-50"
                      >
                        <span>มอบหมายตรง</span>
                      </button>

                      {/* ปุ่มขยายรัศมี 10 กม. */}
                      <button
                        type="button"
                        onClick={() => onExpandRadius && onExpandRadius(order.order_id)}
                        disabled={isLoading || order.search_radius_km >= 10.0}
                        className="min-h-[48px] px-3 py-2 bg-amber-500 hover:bg-amber-600 active:scale-95 text-white text-xs font-medium rounded-lg shadow-sm transition flex items-center justify-center gap-1 disabled:opacity-40"
                      >
                        <span>{order.search_radius_km >= 10.0 ? 'ขยาย 10 กม. แล้ว' : 'ขยาย 10 กม.'}</span>
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

