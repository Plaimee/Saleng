/**
 * แผงหลักระบบนัดหมายและติดตามสถานะ (BookingTrackingPanel)
 * รวม Header, Stepper, Tracking Card, ปุ่มยกเลิก และแถบเตือนโหมดออฟไลน์
 * รองรับ UC-04, CC-01, CC-05, BR-03, MD-STM-04, REQ-FN-003, REQ-OP-001, AC-S05-01..05, P-01..P-06
 */

import React, { useState, useEffect } from 'react';
import BookingSlotSelector from './BookingSlotSelector';
import StatusTimelineStepper from './StatusTimelineStepper';
import InTransitTrackingCard from './InTransitTrackingCard';
import CancelBookingModal from './CancelBookingModal';
import { bookingTrackingApi } from '../services/bookingTrackingApi';

export default function BookingTrackingPanel({
  orderId = 'ord-test-01',
  sellerId = 'seller-01',
  initialOrder = null,
  showSimulator = true,
  onOrderUpdated = () => {},
}) {
  const [order, setOrder] = useState(initialOrder);
  const [loading, setLoading] = useState(!initialOrder);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isCancelModalOpen, setIsCancelModalOpen] = useState(false);
  const [isOffline, setIsOffline] = useState(false);

  // โหลดข้อมูลสถานะคำขอล่าสุดจาก Backend (รองรับการอัปเดตสดเมื่อฝั่งซาเล้งรับงาน/ออกเดินทาง)
  const fetchStatus = async (silent = false) => {
    try {
      if (!silent) setError(null);
      const data = await bookingTrackingApi.getStatus(orderId, sellerId);
      setOrder(data);
      setIsOffline(!!data.is_offline);
      onOrderUpdated(data);
    } catch (err) {
      if (!initialOrder && !silent) {
        setError(err.message || 'ไม่สามารถโหลดสถานะคำขอได้');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (initialOrder) {
      setOrder(initialOrder);
      setLoading(false);
      // ซิงก์สถานะจริงจาก Backend เบื้องหลังทันที
      fetchStatus(true);
    } else {
      fetchStatus(false);
    }

    // โพลล์อัปเดตสถานะจากฝั่งซาเล้งอัตโนมัติทุก 5 วินาที
    const timer = setInterval(() => {
      fetchStatus(true);
    }, 5000);
    return () => clearInterval(timer);
  }, [orderId]);

  // ส่งคำขอนัดหมาย (S1 -> S2)
  const handleConfirmBooking = async (bookingData) => {
    setActionLoading(true);
    setError(null);
    try {
      const updated = await bookingTrackingApi.bookSlot(orderId, bookingData, sellerId);
      setOrder(updated);
      onOrderUpdated(updated);
    } catch (err) {
      setError(err.message || 'ส่งคำขอนัดหมายไม่สำเร็จ');
    } finally {
      setActionLoading(false);
    }
  };

  // กดยืนยันยกเลิกคำขอตามกฎ BR-03
  const handleConfirmCancel = async (reason) => {
    setActionLoading(true);
    setError(null);
    try {
      const updated = await bookingTrackingApi.cancelOrder(orderId, reason, sellerId);
      setOrder(updated);
      setIsCancelModalOpen(false);
      onOrderUpdated(updated);
    } catch (err) {
      setError(err.message || 'ยกเลิกคำขอไม่สำเร็จ');
    } finally {
      setActionLoading(false);
    }
  };

  // จำลองการเปลี่ยนสถานะสำหรับทดสอบ (Simulate)
  const handleSimulateStatus = async (targetStatus) => {
    setActionLoading(true);
    setError(null);
    try {
      const updated = await bookingTrackingApi.simulateStatus(orderId, targetStatus, 'saleng-01', sellerId);
      setOrder(updated);
      onOrderUpdated(updated);
    } catch (err) {
      setError(err.message || 'จำลองสถานะไม่สำเร็จ');
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8 text-center text-xs text-gray-500">
        <span className="inline-block animate-spin mr-2">🔄</span> กำลังโหลดข้อมูลคำขอ...
      </div>
    );
  }

  const status = order?.status || 'S1';
  const isDraft = status === 'S1';

  return (
    <div
      data-req="UC-04"
      data-testid="booking-tracking-panel"
      className="w-full space-y-5 font-sans text-black"
    >
      {/* แจ้งเตือนโหมด Offline Cache (CC-05, REQ-OP-001) */}
      {isOffline && (
        <div
          data-testid="offline-alert"
          className="p-3 bg-amber-100 border border-amber-400 rounded-2xl text-xs text-amber-950 font-medium flex items-center justify-between"
        >
          <span className="flex items-center gap-1.5">
            <span>📡</span>
            <span>คุณอยู่ในโหมดออฟไลน์ ข้อมูลแสดงจากแคชในเครื่อง</span>
          </span>
          <button
            type="button"
            onClick={fetchStatus}
            className="text-xs font-bold text-black underline"
          >
            รีเฟรช
          </button>
        </div>
      )}

      {/* ข้อความแจ้งเตือน Error */}
      {error && (
        <div
          data-testid="error-alert"
          className="p-3 bg-red-50 border border-red-300 rounded-2xl text-xs text-red-700 font-medium flex items-center justify-between"
        >
          <span>⚠️ {error}</span>
          <button
            type="button"
            onClick={() => setError(null)}
            className="text-red-500 hover:text-red-700 text-xs font-bold"
          >
            ✕
          </button>
        </div>
      )}

      {/* Header สรุปคำขอ (Golden Yellow + Jet Black) */}
      <div className="rounded-2xl p-4 bg-yellow-400 border-2 border-black shadow-sm flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-black text-yellow-400 flex items-center justify-center text-xl flex-shrink-0">
            📍
          </div>
          <div>
            <span className="text-[11px] font-mono font-bold text-black/80 block">
              รหัสคำขอ: {order?.order_id || orderId}
            </span>
            <h2 className="text-base font-extrabold text-black leading-tight">
              {isDraft ? 'ระบุเวลานัดหมายรับซื้อ' : 'สถานะการเดินทางและการนัดหมาย'}
            </h2>
          </div>
        </div>
        <div className="px-4 py-2 rounded-xl bg-black text-yellow-400 text-right">
          <span className="text-xs font-extrabold block">
            {order?.items_count ?? 0} รายการ
          </span>
          <span className="text-[11px] text-white/90 font-semibold">
            ฿{order?.total_estimated_price?.min_price?.toFixed(0) || 0} – ฿
            {order?.total_estimated_price?.max_price?.toFixed(0) || 0}
          </span>
        </div>
      </div>

      {/* ส่วนที่ 1: แผงเลือกสล็อตเวลานัดหมาย (เมื่ออยู่ในสถานะ S1 Draft) */}
      {isDraft ? (
        <div className="bg-yellow-50/90 rounded-2xl p-5 border border-yellow-300">
          <BookingSlotSelector
            onConfirmBooking={handleConfirmBooking}
            loading={actionLoading}
          />
        </div>
      ) : (
        /* ส่วนที่ 2: ไทม์ไลน์สถานะ และการ์ดติดตามเส้นทางแบบ 2 คอลัมน์เต็มพื้นที่ */
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
          <div className="lg:col-span-7 bg-yellow-50/90 rounded-2xl p-4 border border-yellow-300">
            <StatusTimelineStepper
              status={order?.status}
              statusLabel={order?.status_label}
              stepperStep={order?.stepper_step || 1}
              scheduledTimeDisplay={order?.scheduled_time_display}
              cancellationReason={order?.cancellation_reason}
            />
          </div>

          <div className="lg:col-span-5">
            <InTransitTrackingCard
              status={order?.status}
              assignedSaleng={order?.assigned_saleng}
              distanceKm={order?.distance_km}
              etaMinutes={order?.eta_minutes}
              canCancel={order?.can_cancel}
              onOpenCancelModal={() => setIsCancelModalOpen(true)}
            />
          </div>
        </div>
      )}

      {/* แถบทดสอบการเปลี่ยนสถานะ (แสดงเฉพาะโหมดทดสอบ ไม่แสดงให้ผู้ใช้ทั่วไปกดข้ามสถานะ) */}
      {showSimulator && (
        <div
          data-testid="status-simulator-bar"
          className="p-3 bg-gray-50 border border-dashed border-gray-300 rounded-2xl space-y-1.5"
        >
          <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block">
            🛠️ แผงจำลองสถานะ (สำหรับทดสอบ E2E / UAT)
          </span>
          <div className="flex flex-wrap gap-1.5">
            {['S2', 'S3', 'S4', 'S5', 'S6', 'S7'].map((st) => (
              <button
                key={st}
                type="button"
                data-testid={`simulate-btn-${st}`}
                disabled={actionLoading}
                onClick={() => handleSimulateStatus(st)}
                className={`px-2 py-1 rounded-lg text-[10px] font-bold transition-all ${
                  order?.status === st
                    ? 'bg-emerald-600 text-white shadow-2xs'
                    : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-100'
                }`}
              >
                {st}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* ป๊อปอัปยืนยันการยกเลิกนัดหมาย */}
      <CancelBookingModal
        isOpen={isCancelModalOpen}
        onClose={() => setIsCancelModalOpen(false)}
        onConfirmCancel={handleConfirmCancel}
        loading={actionLoading}
      />
    </div>
  );
}

