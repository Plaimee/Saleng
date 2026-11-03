/**
 * รายการการ์ดคำขอขายของเก่าแบบเลื่อนแนวตั้ง (JobCardList)
 * รองรับ UC-04, REQ-FN-002, REQ-UX-001, CC-01, D-00-01, AC-B02-01, AC-B02-02
 */

import React from 'react';

export default function JobCardList({
  jobs = [],
  loading = false,
  onSelectJob,
  onClaimJob,
  isVerified = true,
  canExpandRadius = false,
  onExpandRadius,
  radiusKm = 5.0,
}) {
  if (loading) {
    return (
      <div className="p-8 text-center text-gray-500 space-y-3" data-testid="job-list-loading">
        <div className="animate-spin text-3xl">⏳</div>
        <p className="text-sm font-medium">กำลังค้นหาคำขอขายในรัศมี {radiusKm} กม....</p>
      </div>
    );
  }

  // กรณีไม่พบงานในรัศมี (AC-B02-02, A1, Q-06)
  if (!jobs || jobs.length === 0) {
    return (
      <div
        className="p-6 text-center space-y-4 my-8 bg-gray-50 rounded-2xl mx-4 border border-dashed border-gray-300"
        data-req="UC-04"
        data-testid="no-jobs-box"
      >
        <div className="text-4xl">📭</div>
        <div className="space-y-1">
          <h3 className="text-base font-bold text-gray-800" data-testid="no-jobs-message">
            ยังไม่มีงานในเส้นทาง
          </h3>
          <p className="text-xs text-gray-500">
            ไม่พบคำขอขายสถานะรอผู้รับงานในรัศมี {radiusKm} กม.
          </p>
        </div>

        {canExpandRadius && onExpandRadius && (
          <button
            type="button"
            data-testid="btn-expand-10km"
            onClick={onExpandRadius}
            className="w-full min-h-[48px] bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm rounded-xl shadow-md transition-all active:scale-[0.99] flex items-center justify-center gap-2"
          >
            <span>🔍</span>
            <span>ขยายรัศมีเป็น 10 กม.</span>
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="p-3 space-y-3" data-req="UC-04" data-testid="job-card-list">
      <div className="flex items-center justify-between text-xs text-gray-500 px-1">
        <span>พบ {jobs.length} คำขอในรัศมี {radiusKm} กม.</span>
        <span>คำนวณตามโครงข่ายถนนจริง</span>
      </div>

      {jobs.map((job) => (
        <div
          key={job.order_id}
          data-testid={`job-card-${job.order_id}`}
          className="bg-white rounded-xl p-4 shadow-sm border border-gray-200 hover:border-emerald-500 transition-all space-y-3"
        >
          {/* ส่วนหัว: พื้นที่ และ ระยะทางถนน */}
          <div className="flex items-start justify-between gap-2">
            <div>
              <div className="flex items-center gap-1.5">
                <span className="text-base">📍</span>
                <h4 className="text-sm font-bold text-gray-900" data-testid={`job-location-${job.order_id}`}>
                  {job.subdistrict_name} {job.district_name}
                </h4>
              </div>
              <span className="text-xs text-gray-400 block mt-0.5">
                รหัสคำขอ: {job.order_id}
              </span>
            </div>

            <div className="text-right">
              <span
                className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200"
                data-testid={`job-distance-${job.order_id}`}
              >
                {job.road_distance_km} กม.
              </span>
              {job.is_fallback_distance && (
                <span
                  className="block text-[10px] text-amber-600 font-medium mt-0.5"
                  title="คำนวณระยะทางจากโหมดสำรอง Haversine Fallback"
                >
                  ⚡ สำรอง
                </span>
              )}
            </div>
          </div>

          {/* ป้ายหมวดหมู่วัสดุ และป้ายขอคนช่วยยก */}
          <div className="flex flex-wrap gap-1.5">
            {job.categories &&
              job.categories.map((cat, idx) => (
                <span
                  key={idx}
                  className="px-2 py-0.5 bg-gray-100 text-gray-700 rounded-md text-xs font-medium"
                >
                  {cat}
                </span>
              ))}
            {job.need_lifting_help && (
              <span className="px-2 py-0.5 bg-purple-50 text-purple-700 border border-purple-200 rounded-md text-xs font-bold">
                💪 ขอคนช่วยยก
              </span>
            )}
          </div>

          {/* ข้อมูลราคาประเมิน และน้ำหนักรวม */}
          <div className="grid grid-cols-2 gap-2 bg-gray-50 p-2.5 rounded-lg text-xs">
            <div>
              <span className="text-gray-500 block">ราคาประเมิน</span>
              <span className="font-bold text-emerald-700 text-sm" data-testid={`job-price-${job.order_id}`}>
                {job.estimated_price_min} - {job.estimated_price_max} บาท
              </span>
            </div>
            <div className="text-right">
              <span className="text-gray-500 block">น้ำหนักประเมิน</span>
              <span className="font-bold text-gray-800 text-sm" data-testid={`job-weight-${job.order_id}`}>
                ~ {job.estimated_weight_kg} กก.
              </span>
            </div>
          </div>

          {/* ปุ่มกดดูรายละเอียด / รับงาน (REQ-UX-001 ความสูง >= 48px) */}
          <button
            type="button"
            data-testid={`btn-claim-${job.order_id}`}
            onClick={() => onClaimJob ? onClaimJob(job) : (onSelectJob && onSelectJob(job))}
            className={`w-full min-h-[48px] rounded-xl font-bold text-sm shadow-sm flex items-center justify-center gap-2 transition-all active:scale-[0.99] ${
              !isVerified
                ? 'bg-gray-100 text-gray-700 hover:bg-gray-200 border border-gray-300'
                : 'bg-emerald-600 hover:bg-emerald-700 text-white'
            }`}
          >
            {!isVerified ? (
              <>
                <span role="img" aria-label="locked">🔒</span>
                <span>ดูรายละเอียด / ยืนยันตัวตนเพื่อรับงาน</span>
              </>
            ) : (
              <>
                <span>📋</span>
                <span>ดูรายละเอียด / รับงานนี้</span>
              </>
            )}
          </button>
        </div>
      ))}
    </div>
  );
}

