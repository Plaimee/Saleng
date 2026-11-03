/**
 * กล่องแจ้งเตือนกรณี GPS ปิดหรือเบราว์เซอร์ไม่ได้รับอนุญาต (GpsWarningBanner)
 * รองรับ UC-04, REQ-OP-002, AC-B02-04, AC-04-09, E1, REQ-UX-001
 */

import React from 'react';

export default function GpsWarningBanner({ onRetry, errorMessage }) {
  return (
    <div
      className="bg-amber-50 border-l-4 border-amber-500 p-4 rounded-r-lg shadow-sm m-3 space-y-3"
      data-req="UC-04"
      data-testid="gps-warning-banner"
    >
      <div className="flex items-start gap-3">
        <span className="text-2xl" role="img" aria-label="warning">
          ⚠️
        </span>
        <div className="flex-1">
          <h4 className="text-sm font-bold text-amber-800">
            {errorMessage || 'กรุณาเปิด GPS เพื่อค้นหางานใกล้เคียง'}
          </h4>
          <p className="text-xs text-amber-700 mt-0.5">
            ระบบต้องการตำแหน่งปัจจุบันเพื่อคำนวณระยะทางถนนจริงและแสดงงานในรัศมี 5.0 กม. (ระบบไม่ใช้พิกัดเก่าหมดอายุ)
          </p>
        </div>
      </div>

      <button
        type="button"
        data-testid="btn-retry-gps"
        onClick={onRetry}
        className="w-full min-h-[48px] bg-amber-600 hover:bg-amber-700 text-white font-medium text-sm rounded-lg shadow-sm flex items-center justify-center gap-2 transition-colors active:scale-[0.99]"
      >
        <span>🔄</span>
        <span>ลองใหม่อีกครั้ง</span>
      </button>
    </div>
  );
}

