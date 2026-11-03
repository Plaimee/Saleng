import React from "react";

/**
 * BenchmarkPriceTable Component
 * รองรับ REQ-DAT-001, AC-S04-01, CC-05, REQ-OP-001, D-04
 */
export default function BenchmarkPriceTable({ prices = [], lastUpdatedAt, isOffline, offlineNotice }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-emerald-100 p-4 mb-4" data-req="REQ-DAT-001">
      <div className="flex items-center justify-between mb-3 border-b border-gray-100 pb-2">
        <h2 className="text-base font-bold text-gray-800 flex items-center gap-1.5">
          <span className="text-emerald-600">📊</span> ราคากลางรับซื้อขยะรีไซเคิล
        </h2>
        {lastUpdatedAt && (
          <span className="text-xs bg-emerald-50 text-emerald-700 px-2.5 py-1 rounded-full font-medium" data-testid="last-updated-badge">
            อัปเดต: {lastUpdatedAt.includes("06:00") ? "วันนี้ 06:00 น." : lastUpdatedAt}
          </span>
        )}
      </div>

      {isOffline && (
        <div className="bg-amber-50 border border-amber-200 text-amber-800 text-xs rounded-lg p-2.5 mb-3 flex items-center gap-1.5" data-testid="offline-alert">
          <span>⚠️</span>
          <span>{offlineNotice || "ข้อมูลอาจไม่อัปเดต (เปิดจากแคชออฟไลน์)"}</span>
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="w-full text-xs text-left" data-testid="benchmark-price-table">
          <thead>
            <tr className="text-gray-500 border-b border-gray-100 bg-gray-50">
              <th className="py-2 px-2.5 font-semibold">ประเภทวัสดุ</th>
              <th className="py-2 px-2.5 font-semibold text-center">หน่วย</th>
              <th className="py-2 px-2.5 font-semibold text-right">ช่วงราคากลาง</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {prices.map((p) => (
              <tr key={p.category_code} className="hover:bg-gray-50/50" data-testid={`price-row-${p.category_code}`}>
                <td className="py-2 px-2.5 font-medium text-gray-800">
                  {p.category_name}
                  {p.grading_condition && (
                    <span className="block text-[10px] text-gray-400 font-normal">{p.grading_condition}</span>
                  )}
                </td>
                <td className="py-2 px-2.5 text-center text-gray-500">
                  {p.unit === "bag" ? "กระสอบ" : "กก."}
                </td>
                <td className="py-2 px-2.5 text-right font-bold text-emerald-600">
                  {p.min_price_per_unit}–{p.max_price_per_unit} บาท
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

