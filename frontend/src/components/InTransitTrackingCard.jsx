/**
 * การ์ดแสดงระยะทาง, เวลา ETA, โปรไฟล์ซาเล้ง, และปุ่มยกเลิกตามกฎ BR-03 (InTransitTrackingCard)
 * รองรับ UC-04, CC-02, CC-03, BR-03, REQ-FN-003, REQ-SEC-002, D-00-01, AC-S05-03, AC-S05-04, P-03, P-04
 */

import React from 'react';

export default function InTransitTrackingCard({
  status = 'S4',
  assignedSaleng = null,
  distanceKm = null,
  etaMinutes = null,
  canCancel = false,
  onOpenCancelModal = () => {},
}) {
  const isInTransit = status === 'S4';
  const hasSaleng = !!assignedSaleng;

  return (
    <div
      data-req="UC-04"
      data-testid="in-transit-card"
      className="p-4 bg-white rounded-3xl border border-gray-200 shadow-2xs space-y-4"
    >
      {/* ข้อมูลความคืบหน้าการเดินทางสด (เมื่ออยู่ในสถานะ S4) */}
      {isInTransit && (
        <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-3.5 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-emerald-800 flex items-center gap-1.5">
              <span>🛵</span>
              <span>ซาเล้งกำลังเดินทางมาหาคุณ</span>
            </span>
            <span className="text-[10px] bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full font-medium">
              GPS สด (รอบ 60 วินาที)
            </span>
          </div>

          <div className="grid grid-cols-2 gap-3 pt-1">
            <div
              data-testid="eta-badge"
              className="bg-white rounded-xl p-2.5 border border-emerald-100 shadow-2xs text-center"
            >
              <span className="text-[10px] text-gray-500 block">เวลาถึงโดยประมาณ (ETA)</span>
              <span className="text-base font-extrabold text-emerald-700">
                {etaMinutes != null ? `${etaMinutes} นาที` : 'กำลังคำนวณ...'}
              </span>
            </div>

            <div
              data-testid="distance-badge"
              className="bg-white rounded-xl p-2.5 border border-emerald-100 shadow-2xs text-center"
            >
              <span className="text-[10px] text-gray-500 block">ระยะทางที่เหลือ</span>
              <span className="text-base font-extrabold text-emerald-700">
                {distanceKm != null ? `${distanceKm.toFixed(1)} กม.` : 'กำลังคำนวณ...'}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* ข้อมูลซาเล้งที่รับงาน */}
      {hasSaleng ? (
        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-2xl border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-full bg-emerald-600 text-white flex items-center justify-center text-lg font-bold shadow-2xs">
              👨‍🦱
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="text-xs font-bold text-gray-800">{assignedSaleng.name}</span>
                {assignedSaleng.kyc_verified && (
                  <span
                    data-testid="kyc-badge"
                    className="text-[9px] bg-blue-100 text-blue-700 font-bold px-1.5 py-0.2 rounded-md"
                    title="ผ่านการยืนยันตัวตน KYC 100%"
                  >
                    ✓ KYC 100%
                  </span>
                )}
              </div>
              <p className="text-[10px] text-gray-500 mt-0.5">
                ยานพาหนะ: {assignedSaleng.vehicle_type || 'ซาเล้งพ่วงข้าง'} • ⭐{' '}
                {assignedSaleng.rating || 4.9}
              </p>
              <p className="text-[10px] text-gray-400 font-mono mt-0.5">
                {assignedSaleng.phone || '08X-XXX-XXXX'}
              </p>
            </div>
          </div>

          <a
            href={`tel:${assignedSaleng.phone || ''}`}
            data-testid="btn-call-saleng"
            className="w-9 h-9 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center hover:bg-emerald-200 transition-colors"
            title="โทรหาซาเล้ง"
          >
            📞
          </a>
        </div>
      ) : (
        <div className="p-3 bg-gray-50 rounded-2xl text-center text-xs text-gray-400">
          ยังไม่มีผู้รับงาน อยู่ระหว่างส่งคำขอให้ซาเล้งในรัศมี
        </div>
      )}

      {/* ปุ่มยกเลิกนัดหมาย พร้อมการบังคับใช้กฎเหล็ก BR-03 */}
      <div className="pt-1">
        <button
          type="button"
          data-testid="btn-cancel-booking"
          disabled={!canCancel}
          onClick={onOpenCancelModal}
          className={`w-full py-2.5 rounded-2xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
            canCancel
              ? 'bg-red-50 text-red-600 border border-red-200 hover:bg-red-100 active:scale-[0.99]'
              : 'bg-gray-100 text-gray-400 border border-gray-200 cursor-not-allowed opacity-75'
          }`}
        >
          <span>{canCancel ? '❌' : '🔒'}</span>
          <span>{canCancel ? 'ยกเลิกการนัดหมาย' : 'ล็อกปุ่มยกเลิกตามกฎ BR-03'}</span>
        </button>

        {!canCancel && status === 'S4' && (
          <p
            data-testid="br03-warning"
            className="text-[10px] text-center text-amber-600 mt-1.5"
          >
            * ไม่สามารถยกเลิกได้เนื่องจากซาเล้งกำลังเดินทางมายังหน้างานแล้วตามกฎ BR-03
          </p>
        )}
      </div>
    </div>
  );
}

