/**
 * แผงควบคุมหลักระบบค้นหาและแสดงงานรับซื้อตามพิกัด (JobSearchPanel)
 * รวม Segmented Tab Switcher (List ⇄ Map), Filter Bar, GPS Banner, Alert Toast, และ Unverified Gate
 * รองรับ UC-04, REQ-FN-002, REQ-UX-001, CC-01, CC-02, CC-05, D-00-01, D-00-02, AC-B02-01..05, P-01..P-06
 */

import React, { useState, useEffect, useRef } from 'react';
import { jobSearchApi } from '../services/jobSearchApi';
import JobSearchFilterBar from './JobSearchFilterBar';
import JobCardList from './JobCardList';
import JobMapView from './JobMapView';
import GpsWarningBanner from './GpsWarningBanner';
import LiveJobAlertToast from './LiveJobAlertToast';

export default function JobSearchPanel({
  collectorProfile = null,
  onNavigateToKyc,
  onJobAccepted,
}) {
  // State มุมมองหน้าจอ (LIST | MAP) - Tab Switcher >= 48px (REQ-UX-001, Q-04)
  const [activeTab, setActiveTab] = useState('LIST');

  // State พิกัด GPS ของซาเล้ง (Default: สุทธิสาร กรุงเทพฯ)
  const [gpsCoords, setGpsCoords] = useState({ lat: 13.7900, lng: 100.5750 });
  const [gpsError, setGpsError] = useState(null);

  // State การค้นหาและตัวกรอง
  const [radiusKm, setRadiusKm] = useState(5.0);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [selectedWeight, setSelectedWeight] = useState('ALL');
  const [sortBy, setSortBy] = useState('DISTANCE');

  // State ข้อมูลงาน
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [canExpandRadius, setCanExpandRadius] = useState(false);
  const [isOfflineCached, setIsOfflineCached] = useState(false);

  // State Live Alert & Polling (Q-02, CC-02)
  const [liveNewJob, setLiveNewJob] = useState(null);
  const previousJobIdsRef = useRef(new Set());

  // State Gate Modal สำหรับซาเล้งที่ยังไม่ผ่าน KYC (D-00-01, Q-05)
  const [showGateModal, setShowGateModal] = useState(false);
  const [selectedJobForGate, setSelectedJobForGate] = useState(null);

  // ตรวจสอบสถานะการยืนยันตัวตน KYC
  const isVerified = collectorProfile ? (collectorProfile.verified === true && collectorProfile.kyc_status === 'VERIFIED') : true;

  // โหลดตำแหน่ง GPS เริ่มต้นจาก Geolocation API
  const acquireGps = () => {
    setGpsError(null);
    if (typeof navigator !== 'undefined' && navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setGpsCoords({
            lat: pos.coords.latitude,
            lng: pos.coords.longitude,
          });
        },
        (err) => {
          console.warn('GPS Geolocation error:', err);
          // หากผู้ใช้ปฏิเสธพิกัด
          setGpsError('กรุณาเปิด GPS เพื่อค้นหางานใกล้เคียง (GPS Disabled/Denied)');
        },
        { enableHighAccuracy: true, timeout: 5000 }
      );
    }
  };

  useEffect(() => {
    acquireGps();
  }, []);

  // ค้นหางานตามเงื่อนไข
  const fetchJobs = async (isBackgroundPoll = false) => {
    if (gpsError || !gpsCoords.lat || !gpsCoords.lng) {
      return;
    }
    if (!isBackgroundPoll) {
      setLoading(true);
    }

    try {
      const res = await jobSearchApi.getNearbyJobs({
        saleng_lat: gpsCoords.lat,
        saleng_lng: gpsCoords.lng,
        radius_km: radiusKm,
        category: selectedCategory,
        weight_range: selectedWeight,
        sort_by: sortBy,
      });

      const currentJobs = res.jobs || [];
      setIsOfflineCached(!!res.is_offline_cached);
      setCanExpandRadius(!!res.can_expand_radius);

      // ตรวจจับงานใหม่สำหรับการแจ้งเตือน Live Alert (Q-02)
      if (previousJobIdsRef.current.size > 0) {
        const newlyAdded = currentJobs.find((j) => !previousJobIdsRef.current.has(j.order_id));
        if (newlyAdded) {
          setLiveNewJob(newlyAdded);
        }
      }

      // บันทึก ID งานทั้งหมด
      previousJobIdsRef.current = new Set(currentJobs.map((j) => j.order_id));
      setJobs(currentJobs);
    } catch (err) {
      console.error('Failed to fetch nearby jobs:', err);
      // หากเกิดข้อผิดพลาดจาก GPS ปฏิเสธ
      if (err.message && err.message.includes('GPS')) {
        setGpsError(err.message);
      }
    } finally {
      if (!isBackgroundPoll) {
        setLoading(false);
      }
    }
  };

  // โหลดงานเมื่อตัวกรองหรือพิกัดเปลี่ยน
  useEffect(() => {
    fetchJobs();
  }, [gpsCoords, radiusKm, selectedCategory, selectedWeight, sortBy, gpsError]);

  // ระบบ Auto-Refresh Polling ทุก 45 วินาที ตาม CC-02, Q-02
  useEffect(() => {
    const timer = setInterval(() => {
      fetchJobs(true);
    }, 45000);
    return () => clearInterval(timer);
  }, [gpsCoords, radiusKm, selectedCategory, selectedWeight, sortBy]);

  // จัดการเมื่อกดปุ่มรับงาน (Claim Gate - D-00-01)
  const handleClaimJob = (job) => {
    if (!isVerified) {
      setSelectedJobForGate(job);
      setShowGateModal(true);
      return;
    }
    if (onJobAccepted) {
      onJobAccepted(job);
    }
  };

  // จัดการขยายรัศมีเป็น 10.0 กม. (AC-B02-02, Q-06)
  const handleExpandRadius = () => {
    setRadiusKm(10.0);
  };

  return (
    <div
      className="max-w-md mx-auto bg-gray-50 min-h-screen flex flex-col pb-16 font-sans text-gray-800"
      data-req="UC-04"
      data-testid="job-search-panel"
    >
      {/* Header แผงค้นหางาน */}
      <header className="bg-emerald-700 text-white p-4 shadow-sm flex items-center justify-between sticky top-0 z-40">
        <div>
          <h1 className="text-base font-bold flex items-center gap-1.5">
            <span>♻️</span>
            <span>ค้นหางานรับซื้อของเก่า</span>
          </h1>
          <p className="text-xs text-emerald-100 mt-0.5">
            รัศมีทำการ: <span className="font-bold underline">{radiusKm} กม.</span>
            {isOfflineCached && ' (โหมดแคชออฟไลน์)'}
          </p>
        </div>

        <button
          type="button"
          data-testid="btn-manual-refresh"
          onClick={() => fetchJobs(false)}
          className="min-h-[48px] px-3 bg-emerald-800/80 hover:bg-emerald-800 text-white text-xs font-semibold rounded-lg flex items-center gap-1 transition-colors active:scale-95"
          title="รีเฟรชข้อมูลงาน"
        >
          <span>🔄</span>
          <span>รีเฟรช</span>
        </button>
      </header>

      {/* Segmented Control Tab Switcher (List ⇄ Map) [REQ-UX-001 >= 48px, Q-04] */}
      <div className="bg-white p-2 border-b border-gray-200">
        <div className="grid grid-cols-2 gap-2 bg-gray-100 p-1 rounded-xl">
          <button
            type="button"
            data-testid="tab-list-view"
            onClick={() => setActiveTab('LIST')}
            className={`min-h-[48px] rounded-lg font-bold text-sm transition-all flex items-center justify-center gap-1.5 ${
              activeTab === 'LIST'
                ? 'bg-white text-emerald-700 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <span>📋</span>
            <span>รายการงาน ({jobs.length})</span>
          </button>

          <button
            type="button"
            data-testid="tab-map-view"
            onClick={() => setActiveTab('MAP')}
            className={`min-h-[48px] rounded-lg font-bold text-sm transition-all flex items-center justify-center gap-1.5 ${
              activeTab === 'MAP'
                ? 'bg-white text-emerald-700 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <span>🗺️</span>
            <span>แผนที่งาน</span>
          </button>
        </div>
      </div>

      {/* แถบตัวกรองหลายมิติ (Multi-criteria Filter Bar) */}
      <JobSearchFilterBar
        selectedCategory={selectedCategory}
        onSelectCategory={setSelectedCategory}
        selectedWeight={selectedWeight}
        onSelectWeight={setSelectedWeight}
        sortBy={sortBy}
        onSelectSort={setSortBy}
      />

      {/* กล่องแจ้งเตือน GPS Error หากเปิดไม่สำเร็จ (AC-B02-04) */}
      {gpsError && (
        <GpsWarningBanner
          errorMessage={gpsError}
          onRetry={acquireGps}
        />
      )}

      {/* Toast แจ้งเตือนงานใหม่ในพื้นที่ (Live Job Alert - Q-02) */}
      {liveNewJob && (
        <LiveJobAlertToast
          newJob={liveNewJob}
          onViewNewJob={(j) => {
            setActiveTab('LIST');
            setLiveNewJob(null);
          }}
          onDismiss={() => setLiveNewJob(null)}
        />
      )}

      {/* เนื้อหาหลัก: สลับระหว่าง List View และ Map View */}
      <main className="flex-1">
        {activeTab === 'LIST' ? (
          <JobCardList
            jobs={jobs}
            loading={loading}
            onSelectJob={handleClaimJob}
            onClaimJob={handleClaimJob}
            isVerified={isVerified}
            canExpandRadius={canExpandRadius}
            onExpandRadius={handleExpandRadius}
            radiusKm={radiusKm}
          />
        ) : (
          <JobMapView
            jobs={jobs}
            salengLat={gpsCoords.lat}
            salengLng={gpsCoords.lng}
            onSelectJob={handleClaimJob}
            onClaimJob={handleClaimJob}
            isVerified={isVerified}
            radiusKm={radiusKm}
          />
        )}
      </main>

      {/* Informative Gate Modal สำหรับซาเล้งที่ยังไม่ผ่าน KYC (D-00-01, Q-05) */}
      {showGateModal && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
          data-testid="unverified-gate-modal"
        >
          <div className="bg-white rounded-2xl max-w-sm w-full p-5 shadow-2xl space-y-4 animate-scale-up">
            <div className="text-center space-y-2">
              <span className="text-4xl inline-block" role="img" aria-label="locked">
                🔒
              </span>
              <h3 className="text-base font-bold text-gray-900" data-testid="gate-modal-title">
                ยืนยันตัวตนก่อนรับงาน
              </h3>
              <p className="text-xs text-gray-600" data-testid="gate-modal-message">
                เฉพาะซาเล้งที่ยืนยันตัวตน (KYC) แล้วเท่านั้น จึงจะสามารถรับงานนี้ได้ เพื่อความปลอดภัยและความน่าเชื่อถือตามกฎหมาย
              </p>
            </div>

            {selectedJobForGate && (
              <div className="bg-gray-50 p-3 rounded-xl border border-gray-200 text-xs space-y-1">
                <p className="font-semibold text-gray-800">
                  📍 {selectedJobForGate.subdistrict_name} {selectedJobForGate.district_name}
                </p>
                <p className="text-emerald-700 font-bold">
                  ราคาประเมิน {selectedJobForGate.estimated_price_min} - {selectedJobForGate.estimated_price_max} บาท
                </p>
              </div>
            )}

            <div className="space-y-2 pt-2">
              <button
                type="button"
                data-testid="btn-gate-to-kyc"
                onClick={() => {
                  setShowGateModal(false);
                  if (onNavigateToKyc) {
                    onNavigateToKyc();
                  }
                }}
                className="w-full min-h-[48px] bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm rounded-xl shadow transition-colors flex items-center justify-center gap-1.5"
              >
                <span>🪪</span>
                <span>ไปหน้ายืนยันตัวตน (KYC)</span>
              </button>

              <button
                type="button"
                data-testid="btn-gate-close"
                onClick={() => setShowGateModal(false)}
                className="w-full min-h-[48px] bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold text-sm rounded-xl transition-colors flex items-center justify-center"
              >
                ปิด
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

