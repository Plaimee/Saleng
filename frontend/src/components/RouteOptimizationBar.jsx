/**
 * คอมโพเนนต์แถบลำดับเส้นทางและข้อมูลสรุปจุดแวะ (RouteOptimizationBar)
 * แสดงลำดับจุดแวะรับขยะ (1 -> 2 -> 3) พร้อมระยะทางรวมและเวลาถึงโดยประมาณ (ETA)
 * รองรับ UC-04, BR-03, REQ-CON-003, AC-B04-04
 */

import React from 'react';

export default function RouteOptimizationBar({
  jobs = [],
  total_route_distance_km = 0.0,
  total_estimated_duration_min = 0,
}) {
  if (!jobs || jobs.length === 0) {
    return null;
  }

  const sortedJobs = [...jobs].sort((a, b) => (a.sequence_order || 0) - (b.sequence_order || 0));

  return (
    <div
      data-testid="route-optimization-bar"
      data-req="UC-04"
      data-br="BR-03"
      className="bg-white rounded-2xl border border-slate-200 p-3.5 shadow-sm space-y-2.5"
    >
      <div className="flex items-center justify-between text-xs text-slate-600">
        <span className="font-bold text-slate-800 flex items-center gap-1">
          📍 ลำดับเส้นทางแวะรับ ({jobs.length} จุด)
        </span>
        <div className="flex items-center gap-3">
          <span>
            ระยะทางรวม: <strong data-testid="total-route-distance">{total_route_distance_km.toFixed(1)} กม.</strong>
          </span>
          <span>
            เวลาเดินทาง: <strong data-testid="total-route-duration">~{total_estimated_duration_min} นาที</strong>
          </span>
        </div>
      </div>

      {/* Waypoint Chips Timeline */}
      <div className="flex items-center overflow-x-auto py-1 space-x-2 scrollbar-none">
        {sortedJobs.map((job, idx) => {
          const isCurrent = job.status === 'S4';
          return (
            <React.Fragment key={job.order_id || idx}>
              <div
                data-testid={`waypoint-chip-${job.sequence_order || (idx + 1)}`}
                className={`flex-shrink-0 flex items-center gap-1.5 px-3 py-1.5 rounded-xl border text-xs font-semibold ${
                  isCurrent
                    ? 'bg-blue-50 border-blue-400 text-blue-800 shadow-sm'
                    : 'bg-slate-50 border-slate-200 text-slate-700'
                }`}
              >
                <span
                  className={`w-5 h-5 rounded-full flex items-center justify-center text-xs text-white ${
                    isCurrent ? 'bg-blue-600' : 'bg-slate-500'
                  }`}
                >
                  {job.sequence_order || (idx + 1)}
                </span>
                <span className="truncate max-w-[110px]">
                  {job.seller_name || `จุดแวะ ${idx + 1}`}
                </span>
                {isCurrent && (
                  <span className="text-[10px] bg-blue-200 text-blue-800 px-1 py-0.5 rounded">
                    กำลังไป
                  </span>
                )}
              </div>

              {idx < sortedJobs.length - 1 && (
                <span className="text-slate-300 font-bold flex-shrink-0">➡️</span>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}

