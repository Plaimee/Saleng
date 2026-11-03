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
  onOrderUpdated = () => {},
}) {
  const [order, setOrder] = useState(initialOrder);
  const [loading, setLoading] = useState(!initialOrder);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isCancelModalOpen, setIsCancelModalOpen] = useState(false);
  const [isOffline, setIsOffline] = useState(false);

  // โหลดข้อมูลสถานะคำขอล่าสุด
  const fetchStatus = async () => {
    try {
      setError(null);
      const data = await bookingTrackingApi.getStatus(orderId, sellerId);
      setOrder(data);
      setIsOffline(!!data.is_offline);
      onOrderUpdated(data);
    } catch (err) {
      setError(err.message || 'ไม่สามารถโหลดสถานะคำขอได้');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!initialOrder) {
      fetchStatus();
    } else {
      setOrder(initialOrder);
    }
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
      className="max-w-md mx-auto space-y-4 p-2 sm:p-4 font-sans text-gray-800"
    >
      {/* แจ้งเตือนโหมด Offline Cache (CC-05, REQ-OP-001) */}
      {isOffline && (
        <div
          data-testid="offline-alert"
          className="p-2.5 bg-amber-50 border border-amber-200 rounded-2xl text-[11px] text-amber-800 flex items-center justify-between"
        >
          <span className="flex items-center gap-1.5">
            <span>📡</span>
            <span>คุณอยู่ในโหมดออฟไลน์ ข้อมูลแสดงจากแคชในเครื่อง</span>
          </span>
          <button
            type="button"
            onClick={fetchStatus}
            className="text-[10px] font-bold text-amber-900 underline"
          >
            รีเฟรช
          </button>
        </div>
      )}

      {/* ข้อความแจ้งเตือน Error */}
      {error && (
        <div
          data-testid="error-alert"
          className="p-3 bg-red-50 border border-red-200 rounded-2xl text-xs text-red-700 flex items-center justify-between"
        >
          <span>⚠️ {error}</span>
          <button
            type="button"
            onClick={() => setError(null)}
            className="text-gray-400 hover:text-gray-600 text-xs"
          >
            ✕
          </button>
        </div>
      )}

      {/* Header สรุปคำขอ */}
      <div className="bg-white p-4 rounded-3xl border border-gray-200 shadow-2xs flex items-center justify-between">
        <div>
          <span className="text-[10px] font-mono text-gray-400 block">
            รหัสคำขอ: {order?.order_id || orderId}
          </span>
          <h2 className="text-sm font-bold text-gray-800">
            {isDraft ? 'ระบุเวลานัดหมายรับซื้อ' : 'สถานะการเดินทางและการนัดหมาย'}
          </h2>
        </div>
        <div className="text-right">
          <span className="text-xs font-bold text-emerald-700 block">
            {order?.items_count ?? 0} รายการ
          </span>
          <span className="text-[10px] text-gray-400">
            ฿{order?.total_estimated_price?.min_price?.toFixed(0) || 0} - ฿
            {order?.total_estimated_price?.max_price?.toFixed(0) || 0}
          </span>
        </div>
      </div>

      {/* ส่วนที่ 1: แผงเลือกสล็อตเวลานัดหมาย (เมื่ออยู่ในสถานะ S1 Draft) */}
      {isDraft ? (
        <BookingSlotSelector
          onConfirmBooking={handleConfirmBooking}
          loading={actionLoading}
        />
      ) : (
        /* ส่วนที่ 2: ไทม์ไลน์ 9 สถานะ และการ์ดติดตามเส้นทาง (เมื่อสถานะ >= S2) */
        <div className="space-y-4">
          <StatusTimelineStepper
            status={order?.status}
            statusLabel={order?.status_label}
            stepperStep={order?.stepper_step || 1}
            scheduledTimeDisplay={order?.scheduled_time_display}
            cancellationReason={order?.cancellation_reason}
          />

          <InTransitTrackingCard
            status={order?.status}
            assignedSaleng={order?.assigned_saleng}
            distanceKm={order?.distance_km}
            etaMinutes={order?.eta_minutes}
            canCancel={order?.can_cancel}
            onOpenCancelModal={() => setIsCancelModalOpen(true)}
          />
        </div>
      )}

      {/* แถบทดสอบการเปลี่ยนสถานะ (Simulator Control สำหรับการตรวจรับ AC) */}
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

