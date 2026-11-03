/**
 * Toast แจ้งเตือนงานใหม่ในพื้นที่และตัวนับรอบการรีเฟรช (LiveJobAlertToast)
 * รองรับ UC-04, CC-02, Q-02, AC-B02-05
 */

import React from 'react';

export default function LiveJobAlertToast({
  newJob,
  onViewNewJob,
  onDismiss,
  refreshCountdown = 30,
}) {
  if (!newJob) return null;

  return (
    <div
      className="bg-emerald-600 text-white p-3 rounded-xl shadow-lg mx-3 my-2 flex items-center justify-between gap-3 animate-slide-down"
      data-req="UC-04"
      data-testid="live-job-alert-toast"
    >
      <div className="flex items-center gap-2 flex-1 min-w-0">
        <span className="text-xl animate-bounce">🔔</span>
        <div className="truncate">
          <p className="text-xs font-semibold uppercase tracking-wider text-emerald-200">
            ตรวจพบงานใหม่ใกล้คุณ
          </p>
          <p className="text-sm font-bold truncate">
            มีงานใหม่ใกล้คุณ {newJob.road_distance_km ? `${newJob.road_distance_km} กม.` : 'ในพื้นที่'} ({newJob.subdistrict_name})
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <button
          type="button"
          data-testid="btn-view-live-job"
          onClick={() => onViewNewJob(newJob)}
          className="min-h-[48px] px-3 bg-white text-emerald-700 font-bold text-xs rounded-lg shadow hover:bg-emerald-50 active:scale-95 transition-all flex items-center justify-center whitespace-nowrap"
        >
          ดูงานใหม่
        </button>
        <button
          type="button"
          data-testid="btn-dismiss-toast"
          onClick={onDismiss}
          className="min-h-[48px] px-2 text-emerald-200 hover:text-white text-lg flex items-center justify-center"
          aria-label="ปิดการแจ้งเตือน"
        >
          ✕
        </button>
      </div>
    </div>
  );
}

