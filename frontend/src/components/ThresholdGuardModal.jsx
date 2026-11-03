import React from "react";

/**
 * ThresholdGuardModal Component
 * รองรับ REQ-FN-001, REQ-FN-006, AC-S04-03, D-01, D-03
 */
export default function ThresholdGuardModal({
  isOpen,
  onClose,
  totalMin = 0,
  totalBags = 0,
  onSelectAlternative,
}) {
  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-xs"
      data-req="REQ-FN-001"
      data-testid="threshold-guard-modal"
    >
      <div className="bg-white rounded-2xl max-w-sm w-full p-5 shadow-xl border border-amber-100 text-center animate-in fade-in zoom-in duration-150">
        <div className="w-12 h-12 rounded-full bg-amber-50 text-amber-500 text-2xl flex items-center justify-center mx-auto mb-3">
          ⚠️
        </div>

        <h3 className="text-base font-bold text-gray-800 mb-1.5">
          ยอดประเมินไม่ถึงเกณฑ์ขั้นต่ำ
        </h3>

        <div className="text-xs text-gray-600 mb-4 space-y-1">
          <p>
            ยอดประเมินขั้นต่ำของคุณคือ{" "}
            <span className="font-bold text-rose-600">{totalMin} บาท</span> (มีขวด {totalBags} กระสอบ)
          </p>
          <p className="text-[11px] text-gray-400">
            *การเรียกรถซาเล้งมารับที่บ้านแบบเดี่ยว ต้องมียอดประเมินขั้นต่ำตั้งแต่ 500 บาท หรือขวดแก้ว/พลาสติกตั้งแต่ 2 กระสอบขึ้นไป เพื่อความคุ้มค่าในการเดินทาง
          </p>
        </div>

        {/* ตัวเลือกทางเลือกตาม REQ-FN-001 และ REQ-FN-006 */}
        <div className="space-y-2 mb-4">
          <button
            type="button"
            onClick={() => onSelectAlternative("ROUTE_DROP_IN")}
            className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-medium py-2.5 px-3 rounded-xl text-xs flex items-center justify-between transition"
            data-req="REQ-FN-001"
            data-testid="alt-route-drop-btn"
          >
            <span>🛵 ฝากรวมกับจุดรับทางผ่าน</span>
            <span className="text-[10px] bg-emerald-700 px-2 py-0.5 rounded-full">แนะนำ</span>
          </button>

          <button
            type="button"
            onClick={() => onSelectAlternative("BUILDING_GROUP")}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5 px-3 rounded-xl text-xs flex items-center justify-between transition"
            data-req="REQ-FN-006"
            data-testid="alt-building-group-btn"
          >
            <span>🏢 จุดรับรวมประจำอาคาร/หอพัก</span>
            <span className="text-[10px] bg-blue-700 px-2 py-0.5 rounded-full">&ge; 20 กก.</span>
          </button>
        </div>

        <button
          type="button"
          onClick={onClose}
          className="text-xs text-gray-500 hover:text-gray-700 font-medium py-1 px-3"
          data-testid="cancel-guard-modal-btn"
        >
          กลับไปเพิ่มจำนวนของเก่า
        </button>
      </div>
    </div>
  );
}

