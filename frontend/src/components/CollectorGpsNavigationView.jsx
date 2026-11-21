/**
 * หน้าจำลอง GPS นำทางฝั่งซาเล้งไปยังจุดนัดรับของผู้ขาย (CollectorGpsNavigationView)
 * จำลองการเคลื่อนที่ของรถซาเล้งบนแผนที่ Leaflet + OpenStreetMap เป็นเวลา 10 วินาที
 * เมื่อถึงจุดหมาย สามารถเข้าสู่หน้าชั่งน้ำหนักและออกใบเสร็จ (UC-05..07) ได้ทันที
 */

import React, { useCallback, useEffect, useRef, useState } from 'react';
import { bookingTrackingApi } from '../services/bookingTrackingApi';

export default function CollectorGpsNavigationView({
  job,
  salengId = 'saleng-01',
  durationSeconds = 10,
  onArrivedOpenBilling,
  onOpenChat,
  onBack,
}) {
  const startLat = 13.7885;
  const startLng = 100.5715;
  const destLat = Number(job?.dest_lat) || 13.7955;
  const destLng = Number(job?.dest_lng) || 100.5815;
  const initialDistKm = Number(job?.distance_km) || 1.2;

  const [elapsedSec, setElapsedSec] = useState(0);
  const [arrived, setArrived] = useState(false);
  const [arrivalSyncStatus, setArrivalSyncStatus] = useState('idle');
  const [arrivalSyncError, setArrivalSyncError] = useState(null);

  const mapContainerRef = useRef(null);
  const mapRef = useRef(null);
  const salengMarkerRef = useRef(null);
  const progressLineRef = useRef(null);

  const progress = Math.min(1, elapsedSec / durationSeconds);
  const remainingSec = Math.max(0, durationSeconds - elapsedSec);
  const remainingKm = Math.max(0, initialDistKm * (1 - progress));
  const currentLat = startLat + (destLat - startLat) * progress;
  const currentLng = startLng + (destLng - startLng) * progress;

  // 10-second live travel simulation timer (updates every 250ms for smooth map motion)
  useEffect(() => {
    if (arrived) return undefined;
    const interval = setInterval(() => {
      setElapsedSec((prev) => {
        const next = Math.min(durationSeconds, +(prev + 0.25).toFixed(2));
        if (next >= durationSeconds) {
          setArrived(true);
        }
        return next;
      });
    }, 250);
    return () => clearInterval(interval);
  }, [arrived, durationSeconds]);

  const syncArrivalStatus = useCallback(async () => {
    if (!job?.order_id) return;

    setArrivalSyncStatus('syncing');
    setArrivalSyncError(null);
    try {
      await bookingTrackingApi.simulateStatus(job.order_id, 'S5', salengId);
      setArrivalSyncStatus('synced');
    } catch (error) {
      setArrivalSyncStatus('failed');
      setArrivalSyncError(
        error instanceof Error ? error.message : 'ไม่สามารถแจ้งสถานะถึงหน้างานให้ผู้ขายได้'
      );
    }
  }, [job?.order_id, salengId]);

  // แจ้งสถานะ S5 ผ่าน Backend เมื่อ GPS ถึงจุดนัดรับ เพื่อให้หน้าผู้ขายซิงก์สถานะล่าสุด
  useEffect(() => {
    if (arrived && job?.order_id) {
      syncArrivalStatus();
    }
  }, [arrived, job?.order_id, syncArrivalStatus]);

  // Initialize Leaflet Map once
  useEffect(() => {
    const L = typeof window !== 'undefined' ? window.L : null;
    if (!L || !mapContainerRef.current || mapRef.current) return;

    const map = L.map(mapContainerRef.current, {
      center: [(startLat + destLat) / 2, (startLng + destLng) / 2],
      zoom: 15,
      zoomControl: true,
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap',
      maxZoom: 19,
    }).addTo(map);

    // Full route dashed line
    L.polyline(
      [
        [startLat, startLng],
        [destLat, destLng],
      ],
      { color: '#0a0a0a', weight: 4, dashArray: '8, 8', opacity: 0.65 }
    ).addTo(map);

    // Completed golden-yellow trail
    const progressLine = L.polyline(
      [
        [startLat, startLng],
        [startLat, startLng],
      ],
      { color: '#ffc400', weight: 6, opacity: 0.95 }
    ).addTo(map);

    // Seller destination pin
    const destIcon = L.divIcon({
      className: 'custom-dest-pin',
      html: '<div style="background:#0a0a0a;color:#ffc400;width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:18px;border:3px solid #ffffff;box-shadow:0 4px 10px rgba(0,0,0,0.35);">📍</div>',
      iconSize: [36, 36],
      iconAnchor: [18, 18],
    });
    L.marker([destLat, destLng], { icon: destIcon })
      .addTo(map)
      .bindPopup('จุดนัดรับของเก่า (ผู้ขาย)');

    // Moving Saleng vehicle pin
    const salengIcon = L.divIcon({
      className: 'custom-saleng-pin',
      html: '<div style="background:#ffc400;color:#0a0a0a;width:40px;height:40px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:20px;border:3px solid #0a0a0a;box-shadow:0 4px 12px rgba(0,0,0,0.4);">🛺</div>',
      iconSize: [40, 40],
      iconAnchor: [20, 20],
    });
    const salengMarker = L.marker([startLat, startLng], { icon: salengIcon }).addTo(map);

    map.fitBounds(
      [
        [startLat, startLng],
        [destLat, destLng],
      ],
      { padding: [50, 50] }
    );

    mapRef.current = map;
    salengMarkerRef.current = salengMarker;
    progressLineRef.current = progressLine;

    setTimeout(() => map.invalidateSize(), 150);

    return () => {
      map.remove();
      mapRef.current = null;
      salengMarkerRef.current = null;
      progressLineRef.current = null;
    };
  }, [startLat, startLng, destLat, destLng]);

  // Move Saleng marker smoothly along route
  useEffect(() => {
    if (salengMarkerRef.current) {
      salengMarkerRef.current.setLatLng([currentLat, currentLng]);
    }
    if (progressLineRef.current) {
      progressLineRef.current.setLatLngs([
        [startLat, startLng],
        [currentLat, currentLng],
      ]);
    }
  }, [currentLat, currentLng, startLat, startLng]);

  const hasLeaflet = typeof window !== 'undefined' && Boolean(window.L);

  return (
    <div data-testid="collector-gps-navigation" className="w-full space-y-5 font-sans text-black">
      {/* Header Banner */}
      <header className="rounded-2xl p-4 bg-yellow-400 border-2 border-black shadow-sm flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          {onBack && (
            <button
              type="button"
              onClick={onBack}
              className="min-h-[40px] px-3 rounded-full bg-black text-yellow-400 hover:bg-zinc-800 text-xs font-bold"
            >
              ← คิวงาน
            </button>
          )}
          <div className="w-10 h-10 rounded-xl bg-black text-yellow-400 flex items-center justify-center text-xl flex-shrink-0">
            {arrived ? '🏁' : '🧭'}
          </div>
          <div>
            <span className="text-[11px] font-mono font-bold text-black/80 block">
              คำขอ: {job?.order_id || 'ORD-ACTIVE'} • ซาเล้ง: {salengId}
            </span>
            <h2 className="text-base sm:text-lg font-extrabold text-black leading-tight">
              {arrived
                ? 'ถึงจุดนัดรับของเก่าเรียบร้อยแล้ว!'
                : 'กำลังนำทาง GPS ไปยังจุดนัดรับของผู้ขาย'}
            </h2>
          </div>
        </div>

        <span className="px-3.5 py-1.5 rounded-full bg-black text-yellow-400 text-xs font-extrabold">
          {arrived ? '✓ ถึงหน้างาน (S5)' : `🛵 กำลังเดินทาง (S4) • ${Math.ceil(remainingSec)} วิ`}
        </span>
      </header>

      {arrivalSyncStatus === 'syncing' && (
        <div role="status" className="rounded-xl border border-blue-300 bg-blue-50 p-3 text-sm text-blue-900">
          กำลังอัปเดตสถานะถึงหน้างานให้ผู้ขาย...
        </div>
      )}
      {arrivalSyncStatus === 'synced' && (
        <div
          role="status"
          data-testid="arrival-sync-success"
          className="rounded-xl border border-emerald-300 bg-emerald-50 p-3 text-sm font-bold text-emerald-900"
        >
          อัปเดตสถานะฝั่งผู้ขายเป็น “ถึงหน้างานแล้ว” แล้ว
        </div>
      )}
      {arrivalSyncError && (
        <div
          role="alert"
          data-testid="arrival-sync-error"
          className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-red-300 bg-red-50 p-3 text-sm text-red-900"
        >
          <span>แจ้งสถานะถึงหน้างานให้ผู้ขายไม่สำเร็จ: {arrivalSyncError}</span>
          <button
            type="button"
            onClick={syncArrivalStatus}
            disabled={arrivalSyncStatus === 'syncing'}
            className="min-h-[40px] rounded-lg border border-red-400 bg-white px-3 font-bold disabled:opacity-60"
          >
            ลองอีกครั้ง
          </button>
        </div>
      )}

      {/* Main 2-Column GPS Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
        {/* Left: Live Map */}
        <div className="lg:col-span-8 bg-yellow-50/90 rounded-2xl p-3 border-2 border-black shadow-sm space-y-3">
          {hasLeaflet ? (
            <div
              ref={mapContainerRef}
              style={{ height: '340px', width: '100%' }}
              className="rounded-xl overflow-hidden border border-zinc-300 z-0"
            />
          ) : (
            <div className="h-64 rounded-xl bg-white border border-dashed border-zinc-300 flex items-center justify-center text-sm text-zinc-500">
              🗺️ แผนที่นำทาง GPS ({currentLat.toFixed(4)}, {currentLng.toFixed(4)})
            </div>
          )}

          {/* Travel Progress Bar */}
          <div className="bg-white rounded-xl p-3.5 border border-yellow-300 space-y-2">
            <div className="flex items-center justify-between text-xs font-bold">
              <span className="text-black">
                {arrived ? '🎉 เดินทางถึงจุดหมายแล้ว' : '🛺 รถซาเล้งกำลังเคลื่อนที่ไปหาผู้ขาย...'}
              </span>
              <span className="text-black font-extrabold">
                {Math.round(progress * 100)}%
              </span>
            </div>
            <div className="w-full h-3 bg-zinc-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-black transition-all duration-200 rounded-full"
                style={{ width: `${Math.round(progress * 100)}%` }}
              />
            </div>
            <div className="flex items-center justify-between text-[11px] text-zinc-600">
              <span>ระยะทางที่เหลือ: <strong className="text-black">{remainingKm.toFixed(2)} กม.</strong></span>
              <span>
                {arrived
                  ? 'พร้อมเริ่มชั่งน้ำหนักหน้างาน'
                  : `จำลองถึงที่หมายในอีก ${Math.ceil(remainingSec)} วินาที`}
              </span>
            </div>
          </div>
        </div>

        {/* Right: Destination Info & Actions */}
        <div className="lg:col-span-4 space-y-4">
          <div className="bg-white rounded-2xl border-2 border-black overflow-hidden shadow-md">
            <div className="bg-black text-yellow-400 px-4 py-3 text-sm font-extrabold">
              📍 ข้อมูลจุดนัดรับผู้ขาย
            </div>
            <div className="p-4 space-y-3 text-xs">
              <div>
                <div className="text-zinc-500">ผู้ขาย / จุดรับ</div>
                <div className="text-sm font-extrabold text-black mt-0.5">
                  {job?.seller_name || 'ผู้ขายของเก่า'}
                </div>
                <div className="text-zinc-700 mt-0.5">
                  {job?.address_text || job?.subdistrict_name || 'สุทธิสาร / รัชดาภิเษก กรุงเทพฯ'}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2 pt-2 border-t border-zinc-100">
                <div className="p-2.5 rounded-xl bg-yellow-50 border border-yellow-200">
                  <div className="text-[10px] text-zinc-500">น้ำหนักประเมิน</div>
                  <div className="text-sm font-extrabold text-black">
                    {job?.total_est_weight_kg || 25} กก.
                  </div>
                </div>
                <div className="p-2.5 rounded-xl bg-yellow-50 border border-yellow-200">
                  <div className="text-[10px] text-zinc-500">ช่วงราคา</div>
                  <div className="text-sm font-extrabold text-black">
                    ฿{job?.total_est_price_min || 500}–{job?.total_est_price_max || 800}
                  </div>
                </div>
              </div>

              <div className="space-y-2 pt-2">
                {arrived ? (
                  <button
                    type="button"
                    onClick={() => onArrivedOpenBilling && onArrivedOpenBilling(job)}
                    className="w-full py-3 rounded-full bg-yellow-400 hover:bg-yellow-300 text-black border-2 border-black text-sm font-extrabold shadow-md transition"
                  >
                    ⚖️ เริ่มชั่งน้ำหนัก & ออกใบเสร็จ →
                  </button>
                ) : (
                  <button
                    type="button"
                    onClick={() => {
                      setElapsedSec(durationSeconds);
                      setArrived(true);
                    }}
                    className="w-full py-2.5 rounded-full bg-yellow-100 hover:bg-yellow-200 text-black border border-yellow-400 text-xs font-bold transition"
                  >
                    ⏩ ข้ามเวลาไปถึงหน้างานทันที
                  </button>
                )}

                {onOpenChat && (
                  <button
                    type="button"
                    onClick={() => onOpenChat(job)}
                    className="w-full py-2.5 rounded-full bg-black hover:bg-zinc-800 text-yellow-400 text-xs font-bold transition"
                  >
                    💬 แชต & โทรติดต่อผู้ขาย
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
