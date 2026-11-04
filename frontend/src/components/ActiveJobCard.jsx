/**
 * คอมโพเนนต์การ์ดงานที่รับแล้ว (ActiveJobCard)
 * แสดงข้อมูลบ้านเลขที่จริง เบอร์โทรผู้ขาย นำทาง GPS และปุ่มเริ่มออกเดินทาง / สละสิทธิ์
 * รองรับ UC-04, UC-09, UC-12, BR-02, BR-03, REQ-SEC-002, REQ-UX-001, CC-01, AC-B04-03, AC-B04-05, AC-B04-06
 */

import React from 'react';

export default function ActiveJobCard({
  job,
  onNavigate,
  onStartTransit,
  onOpenCancelModal,
  isProcessing = false,
}) {
  if (!job) return null;

  const {
    order_id,
    status = 'S3',
    seller_name = 'ผู้ขาย',
    address_text = 'ไม่ระบุที่อยู่',
    seller_phone = '',
    est_weight_kg = 0.0,
    appointment_slot = 'ไม่ระบุช่วงเวลา',
    sequence_order = 1,
    distance_from_prev_km = 0.0,
    navigation_url = `https://www.google.com/maps/dir/?api=1&destination=13.795,100.581&travelmode=driving`,
    items = [],
  } = job;

  const isInTransit = status === 'S4';

  const handleNavClick = (e) => {
    if (onNavigate) {
      e.preventDefault();
      onNavigate(job);
    }
  };

  return (
    <div
      data-testid="active-job-card"
      data-order-id={order_id}
      data-req="UC-04"
      className="bg-white rounded-2xl border border-slate-200 shadow-sm p-4 space-y-3"
    >
      {/* Header: Sequence & Status Badge */}
      <div className="flex items-center justify-between border-b border-slate-100 pb-2">
        <div className="flex items-center space-x-2">
          <span
            data-testid="sequence-badge"
            className="w-7 h-7 rounded-full bg-emerald-600 text-white flex items-center justify-center text-sm font-bold shadow-sm"
          >
            {sequence_order}
          </span>
          <span className="text-base font-bold text-slate-800">
            จุดแวะที่ {sequence_order}
          </span>
          {distance_from_prev_km > 0 && (
            <span className="text-xs text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full">
              ~{distance_from_prev_km.toFixed(1)} กม.
            </span>
          )}
        </div>

        <div>
          {isInTransit ? (
            <span
              data-testid="job-status-badge"
              className="px-2.5 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800 flex items-center gap-1"
            >
              🚚 กำลังเดินทาง (S4)
            </span>
          ) : (
            <span
              data-testid="job-status-badge"
              className="px-2.5 py-1 text-xs font-semibold rounded-full bg-emerald-100 text-emerald-800 flex items-center gap-1"
            >
              📋 รับงานแล้ว (S3)
            </span>
          )}
        </div>
      </div>

      {/* Seller & Appointment Details */}
      <div className="space-y-1.5 text-sm">
        <div className="flex items-center justify-between">
          <span className="font-semibold text-slate-700">👤 {seller_name}</span>
          {seller_phone && (
            <a
              href={`tel:${seller_phone}`}
              data-testid="seller-phone-link"
              className="text-emerald-700 hover:text-emerald-800 font-medium flex items-center gap-1 min-h-[36px]"
            >
              📞 <span data-testid="seller-phone-text">{seller_phone}</span>
            </a>
          )}
        </div>

        {/* Unmasked Address (REQ-SEC-002, AC-B04-03) */}
        <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-100">
          <div className="text-xs text-slate-500 font-medium">📍 ที่อยู่รับซื้อ (เปิดเผยพิกัดจริงแล้ว):</div>
          <div
            data-testid="seller-address-text"
            className="text-sm font-semibold text-slate-800 mt-0.5 break-words"
          >
            {address_text}
          </div>
        </div>

        {/* Appointment slot & weight */}
        <div className="grid grid-cols-2 gap-2 text-xs pt-1">
          <div className="bg-slate-50 p-2 rounded-lg">
            <span className="text-slate-500 block">⏰ เวลานัดหมาย:</span>
            <span data-testid="appointment-slot-text" className="font-bold text-slate-800">
              {appointment_slot}
            </span>
          </div>
          <div className="bg-slate-50 p-2 rounded-lg">
            <span className="text-slate-500 block">⚖️ น้ำหนักโดยประมาณ:</span>
            <span data-testid="job-weight-text" className="font-bold text-emerald-700">
              {est_weight_kg.toFixed(1)} กก.
            </span>
          </div>
        </div>

        {items.length > 0 && (
          <div className="text-xs text-slate-600 bg-emerald-50/60 p-2 rounded-lg border border-emerald-100">
            <span className="font-medium text-emerald-900">📦 รายการขยะ: </span>
            {items.map((it, idx) => (
              <span key={idx} className="mr-2">
                {it.category_name_th || it.category_id} ({it.est_weight_kg || 0} กก.)
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Action Buttons (REQ-UX-001: Touch target >= 48px) */}
      <div className="pt-2 border-t border-slate-100 space-y-2">
        <div className="grid grid-cols-2 gap-2">
          {/* Button 1: GPS Navigation (UC-09, AC-B04-03) */}
          <a
            href={navigation_url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={handleNavClick}
            data-testid="nav-gps-btn"
            data-req="UC-09"
            className="flex items-center justify-center gap-1.5 px-3 py-2.5 min-h-[48px] bg-slate-100 hover:bg-slate-200 text-slate-800 font-semibold text-sm rounded-xl transition-colors shadow-sm"
          >
            <span>🗺️</span>
            <span>นำทาง GPS</span>
          </a>

          {/* Button 2: Start Transit (UC-09, BR-03, AC-B04-05) */}
          <button
            type="button"
            data-testid="start-transit-btn"
            data-req="UC-09"
            disabled={isInTransit || isProcessing}
            onClick={() => onStartTransit && onStartTransit(order_id)}
            className={`flex items-center justify-center gap-1.5 px-3 py-2.5 min-h-[48px] font-semibold text-sm rounded-xl transition-colors shadow-sm ${
              isInTransit
                ? 'bg-blue-50 text-blue-700 border border-blue-200 cursor-default'
                : 'bg-emerald-600 hover:bg-emerald-700 text-white'
            }`}
          >
            <span>🚚</span>
            <span>{isInTransit ? 'กำลังเดินทาง...' : 'ออกเดินทาง'}</span>
          </button>
        </div>

        {/* Button 3: Cancel Job (S3 only) (MD-STM-04, AC-B04-06) */}
        {!isInTransit && (
          <button
            type="button"
            data-testid="cancel-job-btn"
            disabled={isProcessing}
            onClick={() => onOpenCancelModal && onOpenCancelModal(job)}
            className="w-full flex items-center justify-center gap-1 px-3 py-2 min-h-[48px] bg-white border border-rose-200 hover:bg-rose-50 text-rose-600 font-medium text-xs rounded-xl transition-colors"
          >
            <span>⚠️</span>
            <span>สละสิทธิ์ / ยกเลิกงาน</span>
          </button>
        )}
      </div>
    </div>
  );
}

