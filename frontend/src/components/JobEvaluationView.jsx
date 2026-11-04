/**
 * หน้าจอหลักประเมินรายละเอียดคำขอขายและค่าน้ำมันก่อนรับงาน (JobEvaluationView)
 * รวม OnlineStatusToggle, FuelCostEstimateCard, CapacityIndicatorBar, BulkyItemDetailList,
 * Fixed Bottom Action Bar (ปุ่ม >= 48px) และ KYC Gate Modal
 * รองรับ UC-04, Card 02, CC-01, CC-02, CC-03, CC-05, CC-06, REQ-FN-002, REQ-CON-003, REQ-SEC-002, REQ-UX-001,
 * D-00-01, D-00-02, D-B03-01..06, AC-B03-01..05
 */

import React, { useState, useEffect } from 'react';
import { jobEvaluationApi } from '../services/jobEvaluationApi';
import OnlineStatusToggle from './OnlineStatusToggle';
import FuelCostEstimateCard from './FuelCostEstimateCard';
import CapacityIndicatorBar from './CapacityIndicatorBar';
import BulkyItemDetailList from './BulkyItemDetailList';

export default function JobEvaluationView({
  orderId,
  salengId = 'saleng-01',
  initialEvaluation = null,
  onNavigateBack,
  onNavigateKyc,
  onClaimSuccess,
}) {
  const [evaluation, setEvaluation] = useState(initialEvaluation);
  const [loading, setLoading] = useState(!initialEvaluation);
  const [error, setError] = useState(null);
  const [statusLoading, setStatusLoading] = useState(false);
  const [showKycModal, setShowKycModal] = useState(false);

  // โหลดข้อมูลการประเมินจาก API
  const loadEvaluation = async () => {
    if (!orderId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await jobEvaluationApi.evaluateJob(orderId, { saleng_id: salengId });
      setEvaluation(data);
    } catch (err) {
      setError(err.message || 'ไม่สามารถโหลดข้อมูลการประเมินได้');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!initialEvaluation && orderId) {
      loadEvaluation();
    }
  }, [orderId]);

  // จัดการการสลับสถานะ Online / Offline (CC-02, AC-B03-03)
  const handleToggleOnline = async (newStatus) => {
    setStatusLoading(true);
    try {
      await jobEvaluationApi.toggleOnlineStatus(salengId, newStatus);
      // โหลดการประเมินใหม่เพื่ออัปเดตสิทธิ์การรับงาน
      await loadEvaluation();
    } catch (err) {
      alert(err.message || 'สลับสถานะไม่สำเร็จ');
    } finally {
      setStatusLoading(false);
    }
  };

  // จัดการกดปุ่มรับงาน
  const handleClaimClick = () => {
    if (!evaluation) return;

    // 1. ตรวจสอบ KYC Gate (D-00-01, AC-B03-05)
    if (!evaluation.collector_is_verified || evaluation.claim_block_reason === 'UNVERIFIED_KYC') {
      setShowKycModal(true);
      return;
    }

    // 2. ตรวจสอบสถานะ Online (CC-02, AC-B03-03)
    if (!evaluation.collector_is_online || evaluation.claim_block_reason === 'OFFLINE') {
      return;
    }

    // 3. ตรวจสอบความจุรถ (BR-03, REQ-CON-003, AC-B03-03)
    if (evaluation.is_capacity_exceeded || evaluation.claim_block_reason === 'CAPACITY_EXCEEDED') {
      return;
    }

    // 4. หากผ่านเงื่อนไขครบ ดำเนินการรับงาน
    if (onClaimSuccess) {
      onClaimSuccess(evaluation);
    }
  };

  if (loading) {
    return (
      <div
        data-testid="job-evaluation-loading"
        className="max-w-md mx-auto p-6 text-center text-slate-500 min-h-screen flex flex-col justify-center items-center"
      >
        <div className="w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mb-3" />
        <p className="text-sm">กำลังประเมินระยะทาง ค่าน้ำมัน และความจุรถ...</p>
      </div>
    );
  }

  if (error || !evaluation) {
    return (
      <div
        data-testid="job-evaluation-error"
        className="max-w-md mx-auto p-4 min-h-screen flex flex-col justify-center items-center text-center"
      >
        <div className="p-4 bg-red-50 border border-red-300 rounded-xl text-red-800 mb-4 w-full">
          <p className="font-semibold text-sm">เกิดข้อผิดพลาด</p>
          <p className="text-xs mt-1">{error || 'ไม่พบข้อมูลคำขอขาย'}</p>
        </div>
        <button
          type="button"
          onClick={loadEvaluation}
          style={{ minHeight: '48px' }}
          className="px-6 py-2 bg-emerald-600 text-white rounded-lg text-sm font-semibold"
        >
          ลองใหม่อีกครั้ง
        </button>
      </div>
    );
  }

  const {
    location_summary = {},
    vehicle_type = 'MOTORCYCLE',
    road_distance_km = 0.0,
    estimated_fuel_cost = 0.0,
    is_fallback_distance = false,
    current_load_kg = 0.0,
    max_capacity_kg = 200.0,
    total_est_weight_kg = 0.0,
    total_min_price = 0.0,
    total_max_price = 0.0,
    is_capacity_exceeded = false,
    collector_is_online = true,
    collector_is_verified = true,
    can_claim_job = true,
    claim_block_reason = null,
    items = [],
    need_lifting_help = false,
    is_offline_cached = false,
  } = evaluation;

  // ตรวจสอบสถานะการล็อกปุ่มรับงาน
  const isKycLocked = !collector_is_verified || claim_block_reason === 'UNVERIFIED_KYC';
  const isOfflineLocked = !collector_is_online || claim_block_reason === 'OFFLINE';
  const isCapacityLocked = is_capacity_exceeded || claim_block_reason === 'CAPACITY_EXCEEDED';

  return (
    <div
      data-testid="job-evaluation-view"
      data-req="UC-04"
      data-card="Card-02"
      className="max-w-md mx-auto min-h-screen bg-slate-100 flex flex-col pb-24"
    >
      {/* แถบด้านบน: ปุ่มย้อนกลับ และสวิตช์ Online / Offline */}
      <header className="bg-white border-b border-slate-200 px-4 py-3 sticky top-0 z-10 shadow-sm flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <button
            type="button"
            data-testid="back-button"
            onClick={onNavigateBack}
            style={{ minHeight: '48px', minWidth: '48px' }}
            className="flex items-center text-slate-700 hover:text-slate-900 font-medium text-sm -ml-2 px-2 rounded-lg"
          >
            ← ย้อนกลับ
          </button>
          <span className="text-xs font-bold text-slate-500">
            รหัสคำขอ: {orderId}
          </span>
        </div>

        {/* สวิตช์ Online / Offline (CC-02, AC-B03-03) */}
        <OnlineStatusToggle
          isOnline={collector_is_online}
          isLoading={statusLoading}
          onToggle={handleToggleOnline}
        />
      </header>

      {/* แถบแจ้งเตือนออฟไลน์แคช (CC-05, REQ-OP-001) */}
      {is_offline_cached && (
        <div
          data-testid="offline-cached-banner"
          className="bg-amber-100 border-b border-amber-300 px-4 py-2 text-xs text-amber-900 flex items-center gap-1.5"
        >
          <span>📶</span>
          <span>แสดงข้อมูลที่แคชไว้ในเครื่อง (เครือข่ายออฟไลน์)</span>
        </div>
      )}

      {/* เนื้อหาหลักการประเมิน (Scrollable) */}
      <main className="p-4 space-y-4 flex-1">
        {/* หัวข้อสถานที่: แสดงเฉพาะตำบล/แขวงและเขต (ซ่อนบ้านเลขที่และพิกัดจริง REQ-SEC-002, D-00-02, CC-06) */}
        <div
          data-testid="evaluation-location-header"
          data-req="REQ-SEC-002"
          className="p-3.5 bg-white rounded-xl border border-slate-200 shadow-sm"
        >
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
            พิกัดพื้นที่รับซื้อ (โดยประมาณ)
          </span>
          <div className="flex items-center gap-1.5 mt-1 text-slate-800 font-bold text-base">
            <span>📍</span>
            <span data-testid="location-subdistrict-text">
              {location_summary.subdistrict_name || 'แขวงสามเสนนอก'} {location_summary.district_name || 'เขตห้วยขวาง'}
            </span>
          </div>
          <p className="text-[11px] text-slate-500 mt-1">
            🔒 ซ่อนที่อยู่ละเอียดและพิกัดจริงเพื่อความปลอดภัยตาม PDPA (จะแสดงเมื่อกดรับงานแล้วเท่านั้น)
          </p>
        </div>

        {/* 1. การ์ดระยะทางและค่าน้ำมันตามประเภทรถ (Card 02, AC-B03-01, AC-B03-02) */}
        <FuelCostEstimateCard
          road_distance_km={road_distance_km}
          estimated_fuel_cost={estimated_fuel_cost}
          vehicle_type={vehicle_type}
          is_fallback_distance={is_fallback_distance}
        />

        {/* 2. แถบความจุรถสะสมและการเตือนน้ำหนักเกิน (BR-03, REQ-CON-003, AC-B03-03) */}
        <CapacityIndicatorBar
          current_load_kg={current_load_kg}
          job_est_weight_kg={total_est_weight_kg}
          max_capacity_kg={max_capacity_kg}
        />

        {/* 3. รายการของเก่า รูปถ่าย และป้ายช่วยยก (REQ-FN-003, REQ-FN-004, AC-B03-01) */}
        <BulkyItemDetailList
          items={items}
          need_lifting_help={need_lifting_help}
          total_est_weight_kg={total_est_weight_kg}
          total_min_price={total_min_price}
          total_max_price={total_max_price}
        />
      </main>

      {/* แถบล่างติดขอบจอ (Fixed Bottom Action Bar >= 48px ตาม REQ-UX-001 และ CC-01) */}
      <footer
        data-testid="fixed-bottom-action-bar"
        className="fixed bottom-0 left-0 right-0 max-w-md mx-auto bg-white border-t border-slate-200 p-3 shadow-lg z-20"
      >
        {isKycLocked ? (
          // ปุ่มล็อกสำหรับซาเล้งที่ยังไม่ผ่าน KYC (D-00-01, AC-B03-05)
          <button
            type="button"
            data-testid="unverified-claim-button"
            data-req="D-00-01"
            onClick={handleClaimClick}
            style={{ minHeight: '48px' }}
            className="w-full py-3 px-4 rounded-xl bg-amber-500 hover:bg-amber-600 text-white font-bold text-sm flex items-center justify-center gap-2 shadow transition-colors"
          >
            <span>🔒</span>
            <span>ยืนยันตัวตนเพื่อรับงาน</span>
          </button>
        ) : isOfflineLocked ? (
          // ปุ่มปิดรับงานเมื่อสถานะเป็น Offline (CC-02, AC-B03-03)
          <button
            type="button"
            disabled
            data-testid="offline-disabled-claim-button"
            data-req="CC-02"
            style={{ minHeight: '48px' }}
            className="w-full py-3 px-4 rounded-xl bg-slate-300 text-slate-500 font-bold text-sm cursor-not-allowed flex items-center justify-center gap-1.5"
          >
            <span>⚪</span>
            <span>กรุณาเปิดสถานะ Online เพื่อรับงาน</span>
          </button>
        ) : isCapacityLocked ? (
          // ปุ่มล็อกเมื่อน้ำหนักสะสมเกินความจุรถ 200 กก. (BR-03, REQ-CON-003, AC-B03-03)
          <button
            type="button"
            disabled
            data-testid="capacity-disabled-claim-button"
            data-req="REQ-CON-003"
            style={{ minHeight: '48px' }}
            className="w-full py-3 px-4 rounded-xl bg-red-400 text-white font-bold text-sm cursor-not-allowed flex items-center justify-center gap-1.5 shadow-sm"
          >
            <span>⚠️</span>
            <span>น้ำหนักเกินความจุรถ (ไม่สามารถรับงานได้)</span>
          </button>
        ) : (
          // ปุ่มรับงานปกติสีเขียว (พร้อมกดรับงาน)
          <button
            type="button"
            data-testid="claim-job-button"
            data-req="UC-04"
            onClick={handleClaimClick}
            style={{ minHeight: '48px' }}
            className="w-full py-3 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-base shadow transition-colors active:scale-[0.98]"
          >
            กดรับงานนี้
          </button>
        )}
      </footer>

      {/* KYC Gate Modal สำหรับซาเล้งที่ยังไม่ผ่าน KYC (D-00-01, AC-B03-05) */}
      {showKycModal && (
        <div
          data-testid="kyc-gate-modal"
          data-req="D-00-01"
          className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4"
        >
          <div className="bg-white rounded-2xl max-w-sm w-full p-5 shadow-2xl flex flex-col gap-3">
            <div className="w-12 h-12 bg-amber-100 rounded-full flex items-center justify-center text-2xl mx-auto">
              🔒
            </div>
            <h3 className="text-base font-bold text-slate-900 text-center">
              ต้องยืนยันตัวตน (KYC) ก่อนรับงาน
            </h3>
            <p className="text-xs text-slate-600 text-center leading-relaxed">
              คุณสามารถดูรายละเอียดและประเมินค่าน้ำมันของงานนี้ได้
              แต่ต้องผ่านการยืนยันตัวตนกับระบบก่อน จึงจะสามารถกดรับงานจริงได้เพื่อความปลอดภัยของผู้ขาย
            </p>

            <div className="flex flex-col gap-2 mt-2">
              <button
                type="button"
                data-testid="go-to-kyc-button"
                onClick={() => {
                  setShowKycModal(false);
                  if (onNavigateKyc) onNavigateKyc();
                }}
                style={{ minHeight: '48px' }}
                className="w-full py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold text-sm transition-colors shadow"
              >
                ไปหน้ายืนยันตัวตน (KYC)
              </button>
              <button
                type="button"
                data-testid="close-modal-button"
                onClick={() => setShowKycModal(false)}
                style={{ minHeight: '48px' }}
                className="w-full py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl font-semibold text-sm transition-colors"
              >
                ปิดหน้านี้
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
