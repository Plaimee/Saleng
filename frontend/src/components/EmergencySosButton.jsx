import React from "react";

/**
 * ปุ่มกดขอความช่วยเหลือฉุกเฉิน SOS (AC-S09-02, REQ-UX-001, UC-09)
 * ปุ่มสีแดงเด่นสะดุดตา ความสูงไม่น้อยกว่า 48px (min-h-[48px]) กดได้ทันทีด้วยมือเดียว
 */
export default function EmergencySosButton({
  onTriggerSos,
  disabled = false,
  className = "",
}) {
  return (
    <button
      type="button"
      data-req="UC-09"
      onClick={onTriggerSos}
      disabled={disabled}
      className={`w-full min-h-[48px] py-3 px-4 bg-red-600 hover:bg-red-700 active:bg-red-800 disabled:bg-gray-400 text-white font-bold text-base rounded-xl shadow-lg flex items-center justify-center gap-2 transition-all duration-150 transform active:scale-95 border-2 border-red-500 animate-pulse ${className}`}
      aria-label="ปุ่มแจ้งเหตุฉุกเฉิน SOS"
    >
      <span className="text-xl" role="img" aria-label="alarm">🚨</span>
      <span>SOS ฉุกเฉิน</span>
      <span className="text-xs bg-red-800 px-2 py-0.5 rounded-full font-normal">
        กดทันที
      </span>
    </button>
  );
}

