/**
 * คอมโพเนนต์แสดงรายการของเก่า รูปถ่าย และป้ายขอคนช่วยยก (BulkyItemDetailList)
 * รองรับ REQ-FN-003, REQ-FN-004, Card 02, AC-B03-01
 */

import React from 'react';

export default function BulkyItemDetailList({
  items = [],
  need_lifting_help = false,
  total_est_weight_kg = 0.0,
  total_min_price = 0.0,
  total_max_price = 0.0,
}) {
  const totalWeight = Number(total_est_weight_kg) || 0;
  const minPrice = Number(total_min_price) || 0;
  const maxPrice = Number(total_max_price) || 0;

  return (
    <div
      data-testid="bulky-item-list"
      data-req="REQ-FN-003"
      className="p-4 bg-white rounded-xl border border-slate-200 shadow-sm"
    >
      {/* ส่วนหัวสรุปน้ำหนักและมูลค่า */}
      <div className="flex justify-between items-start mb-3 border-b border-slate-100 pb-2.5">
        <div>
          <h3 className="text-sm font-bold text-slate-800 flex items-center gap-1.5">
            📦 รายการของเก่าที่จะขาย ({items.length} รายการ)
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            น้ำหนักรวมประมาณ: <strong>{totalWeight.toFixed(1)} กก.</strong>
          </p>
        </div>

        <div className="text-right">
          <span className="text-[11px] text-slate-500 block">มูลค่าประเมินรวม</span>
          <span className="text-sm font-extrabold text-emerald-700">
            {minPrice.toFixed(0)} - {maxPrice.toFixed(0)} บาท
          </span>
        </div>
      </div>

      {/* ป้ายเตือนขอคนช่วยยก (ถ้ามี) */}
      {need_lifting_help && (
        <div
          data-testid="need-lifting-help-badge"
          className="mb-3 p-2 bg-amber-50 border border-amber-300 rounded-lg flex items-center gap-2 text-xs text-amber-900 font-semibold"
        >
          <span className="text-base">💪</span>
          <span>ขอคนช่วยยก (ผู้ขายระบุ: ต้องการคนช่วยยกของหนัก / ของชิ้นใหญ่)</span>
        </div>
      )}

      {/* รายการสิ่งของแต่ละชิ้น */}
      <div className="space-y-3">
        {items.map((item) => (
          <div
            key={item.item_id}
            data-testid={`item-row-${item.item_id}`}
            className="p-3 bg-slate-50 rounded-lg border border-slate-100 flex flex-col gap-2"
          >
            <div className="flex justify-between items-start">
              <div>
                <span className="text-xs font-bold text-slate-800 block">
                  {item.category_name_th || item.category_id}
                </span>
                <span
                  data-testid={`item-weight-${item.item_id}`}
                  className="text-xs text-slate-600"
                >
                  น้ำหนักประเมิน: {item.est_weight_kg ? `${item.est_weight_kg.toFixed(1)} กก.` : 'ไม่ระบุ'}
                </span>
              </div>

              <div className="text-right">
                <span
                  data-testid={`item-price-${item.item_id}`}
                  className="text-xs font-semibold text-emerald-700"
                >
                  {item.est_min_price ? `${item.est_min_price.toFixed(0)} - ${item.est_max_price.toFixed(0)} บ.` : '-'}
                </span>
                {item.is_bulky && (
                  <span
                    data-testid={`item-bulky-badge-${item.item_id}`}
                    className="block mt-0.5 text-[10px] px-1.5 py-0.2 bg-purple-100 text-purple-800 border border-purple-200 rounded font-medium"
                  >
                    📦 ชิ้นใหญ่ (Bulky)
                  </span>
                )}
              </div>
            </div>

            {/* รูปถ่ายขยะ (REQ-FN-004) */}
            {item.photo_urls && item.photo_urls.length > 0 && (
              <div
                data-testid={`item-photos-${item.item_id}`}
                data-req="REQ-FN-004"
                className="flex gap-2 overflow-x-auto pt-1"
              >
                {item.photo_urls.map((url, idx) => (
                  <img
                    key={idx}
                    src={url}
                    alt={`รูปถ่าย ${item.category_name_th || item.category_id} รูปที่ ${idx + 1}`}
                    className="w-16 h-16 object-cover rounded-md border border-slate-200"
                  />
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
