import React from 'react';

/**
 * RegularCustomerList Component
 * แสดงรายชื่อลูกค้าประจำที่ซาเล้งปักหมุดไว้ พร้อมบันทึกย่อช่วยจำและปุ่มนำทาง
 * รองรับ UC-10, REQ-SEC-002, CC-01, CC-06, D-B07-03
 */
export default function RegularCustomerList({
  customers = [],
  onRemoveCustomer,
  isLoading = false,
}) {
  if (customers.length === 0) {
    return (
      <div
        className="bg-white rounded-2xl border border-gray-200 p-8 text-center space-y-3"
        data-req="UC-10"
        data-testid="empty-regular-customers"
      >
        <div className="w-16 h-16 bg-amber-50 text-amber-500 rounded-full flex items-center justify-center mx-auto text-3xl">
          ⭐
        </div>
        <h3 className="text-sm font-bold text-gray-800">ยังไม่มีรายการลูกค้าประจำ</h3>
        <p className="text-xs text-gray-500 max-w-xs mx-auto">
          เมื่อปิดงานเสร็จสิ้น คุณสามารถกดปุ่ม "ปักหมุดลูกค้าประจำ" บนการ์ดประวัติการรับซื้อเพื่อบันทึกบ้านลูกค้าประจำไว้ใช้วางแผนเส้นทาง
        </p>
      </div>
    );
  }

  return (
    <div
      className="space-y-3"
      data-req="UC-10"
      data-testid="regular-customer-list"
    >
      <div className="flex justify-between items-center px-1">
        <span className="text-xs font-bold text-gray-700">
          ลูกค้าประจำที่ปักหมุดไว้ ({customers.length} ราย)
        </span>
      </div>

      {customers.map((cust) => {
        const mapUrl = `https://maps.google.com/?q=${cust.latitude},${cust.longitude}`;

        return (
          <div
            key={cust.id || cust.seller_id}
            className="bg-white rounded-2xl border border-gray-200 p-4 shadow-sm space-y-3"
            data-testid={`customer-card-${cust.seller_id}`}
          >
            {/* ส่วนหัวลูกค้า: ชื่อและป้ายลูกค้าประจำ */}
            <div className="flex justify-between items-start">
              <div>
                <span className="text-sm font-bold text-gray-800 block" data-testid="customer-name">
                  ⭐ {cust.seller_name}
                </span>
                <span className="text-xs text-gray-500 font-mono mt-0.5 block" data-testid="customer-phone">
                  📞 {cust.seller_phone_masked || '08X-XXX-XXXX'}
                </span>
              </div>
              <span className="text-[11px] font-mono text-gray-400 bg-gray-50 px-2 py-0.5 rounded border border-gray-100">
                {Number(cust.latitude).toFixed(4)}, {Number(cust.longitude).toFixed(4)}
              </span>
            </div>

            {/* บันทึกย่อช่วยจำ (Notes) */}
            {cust.notes && (
              <div
                className="bg-amber-50/70 border border-amber-200 rounded-xl p-2.5 text-xs text-amber-900"
                data-testid="customer-notes"
              >
                <span className="font-bold">📝 บันทึกช่วยจำ: </span>
                <span>{cust.notes}</span>
              </div>
            )}

            {/* ปุ่มดำเนินการ (ทัชทาร์เก็ต >= 48px ตาม REQ-UX-001, CC-01) */}
            <div className="grid grid-cols-2 gap-2 pt-1 border-t border-gray-100">
              <a
                href={mapUrl}
                target="_blank"
                rel="noreferrer"
                className="min-h-[48px] px-3 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-xl transition flex items-center justify-center gap-1.5 shadow-sm"
                data-testid="navigate-map-btn"
              >
                <span>🗺️</span> นำทางบนแผนที่
              </a>

              <button
                type="button"
                onClick={() => onRemoveCustomer && onRemoveCustomer(cust.seller_id)}
                disabled={isLoading}
                className="min-h-[48px] px-3 bg-white hover:bg-red-50 text-red-600 border border-red-200 font-bold text-xs rounded-xl transition flex items-center justify-center gap-1.5"
                data-testid="remove-customer-btn"
              >
                <span>🗑️</span> ลบออกจากรายการ
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
}

