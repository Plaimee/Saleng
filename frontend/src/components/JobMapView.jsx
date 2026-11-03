/**
 * แผนที่แสดงหมุดจำลอง Fuzzed Pins และตำแหน่งซาเล้ง (JobMapView)
 * รองรับ UC-04, REQ-SEC-002, D-00-02, CC-06, Q-01, AC-B02-03, AC-B02-05
 */

import React, { useState } from 'react';

export default function JobMapView({
  jobs = [],
  salengLat = 13.7900,
  salengLng = 100.5750,
  onSelectJob,
  onClaimJob,
  isVerified = true,
  radiusKm = 5.0,
}) {
  const [selectedPin, setSelectedPin] = useState(jobs.length > 0 ? jobs[0] : null);

  return (
    <div
      className="relative flex flex-col h-[520px] bg-slate-100 overflow-hidden"
      data-req="UC-04"
      data-testid="job-map-view"
    >
      {/* แถบข้อมูลบนแผนที่ */}
      <div className="absolute top-3 left-3 right-3 z-10 flex items-center justify-between bg-white/90 backdrop-blur-sm px-3 py-2 rounded-xl shadow-sm border border-gray-200 text-xs">
        <span className="font-semibold text-gray-700 flex items-center gap-1">
          <span>🗺️</span>
          <span>รัศมีค้นหา {radiusKm} กม. (หมุดจำลอง ±300–500 ม.)</span>
        </span>
        <span className="bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded-full">
          {jobs.length} จุด
        </span>
      </div>

      {/* แคนวาสแผนที่จำลอง (Interactive Map Canvas) */}
      <div className="flex-1 w-full relative bg-gradient-to-br from-slate-100 via-emerald-50/30 to-blue-50/20 p-6 flex items-center justify-center">
        {/* วงรัศมี 5.0 กม. */}
        <div className="absolute w-[360px] h-[360px] rounded-full border-2 border-emerald-400/40 bg-emerald-500/5 pointer-events-none flex items-center justify-center">
          <span className="text-[10px] text-emerald-600 font-bold uppercase tracking-wider mb-auto mt-2">
            ขอบเขตรัศมี {radiusKm} กม.
          </span>
        </div>

        {/* หมุดตำแหน่งซาเล้ง (Current Collector Pin) */}
        <div
          className="relative z-20 flex flex-col items-center cursor-pointer"
          data-testid="saleng-current-pin"
          title={`ตำแหน่งคุณ: ${salengLat.toFixed(4)}, ${salengLng.toFixed(4)}`}
        >
          <div className="w-10 h-10 rounded-full bg-blue-600 border-2 border-white shadow-lg flex items-center justify-center text-white text-lg animate-pulse">
            🚴
          </div>
          <span className="bg-blue-900 text-white text-[10px] font-bold px-1.5 py-0.5 rounded shadow mt-1 whitespace-nowrap">
            คุณอยู่ที่นี่
          </span>
        </div>

        {/* หมุดคำขอขายจำลอง (Fuzzed Job Pins) */}
        {jobs.map((job, idx) => {
          const isSelected = selectedPin && selectedPin.order_id === job.order_id;
          // คำนวณตำแหน่งสัมพัทธ์ในแคนวาสจำลอง
          const angle = (idx * (360 / Math.max(jobs.length, 1)) * Math.PI) / 180;
          const radiusPx = 80 + (idx % 3) * 35;
          const offsetX = Math.cos(angle) * radiusPx;
          const offsetY = Math.sin(angle) * radiusPx;

          return (
            <div
              key={job.order_id}
              data-testid={`map-pin-${job.order_id}`}
              onClick={() => setSelectedPin(job)}
              style={{
                transform: `translate(${offsetX}px, ${offsetY}px)`,
              }}
              className="absolute z-20 flex flex-col items-center cursor-pointer transition-transform hover:scale-110 active:scale-95"
            >
              <div
                className={`w-9 h-9 rounded-full border-2 border-white shadow-md flex items-center justify-center text-sm ${
                  isSelected ? 'bg-emerald-600 text-white ring-4 ring-emerald-300' : 'bg-emerald-500 text-white'
                }`}
              >
                📦
              </div>
              <span className="bg-gray-900/80 text-white text-[9px] font-medium px-1 rounded shadow mt-0.5 whitespace-nowrap">
                {job.road_distance_km} กม.
              </span>
            </div>
          );
        })}
      </div>

      {/* แถบพรีวิวการ์ดย่อด้านล่างเมื่อแตะหมุด (Bottom Sheet Mini Preview) */}
      {selectedPin ? (
        <div
          className="bg-white border-t border-gray-200 p-4 shadow-xl z-30 space-y-3"
          data-testid="map-bottom-preview"
        >
          <div className="flex items-start justify-between">
            <div>
              <span className="text-[10px] font-bold uppercase text-emerald-600 tracking-wider">
                📍 จุดนัดรับโดยประมาณ (PDPA Masked)
              </span>
              <h4 className="text-sm font-bold text-gray-900" data-testid="preview-location">
                {selectedPin.subdistrict_name} {selectedPin.district_name}
              </h4>
              <p className="text-xs text-gray-500">
                ระยะทางตามถนนจริง: <span className="font-bold text-emerald-700">{selectedPin.road_distance_km} กม.</span>
              </p>
            </div>
            <div className="text-right">
              <span className="text-xs text-gray-400 block">ราคาประเมิน</span>
              <span className="text-sm font-bold text-emerald-700" data-testid="preview-price">
                {selectedPin.estimated_price_min} - {selectedPin.estimated_price_max} บ.
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              data-testid="btn-preview-claim"
              onClick={() => onClaimJob ? onClaimJob(selectedPin) : (onSelectJob && onSelectJob(selectedPin))}
              className={`flex-1 min-h-[48px] rounded-xl font-bold text-sm shadow-sm flex items-center justify-center gap-2 transition-all active:scale-[0.99] ${
                !isVerified
                  ? 'bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200'
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
        </div>
      ) : (
        <div className="bg-white/80 p-3 text-center text-xs text-gray-500 border-t border-gray-200">
          แตะที่หมุด 📦 บนแผนที่เพื่อดูข้อมูลย่อและระยะทาง
        </div>
      )}
    </div>
  );
}

