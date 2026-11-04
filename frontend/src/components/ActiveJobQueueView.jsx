/**
 * หน้ารวมคิวงานและเส้นทางรับซื้อของซาเล้ง (ActiveJobQueueView)
 * รวมการ์ดงานที่รับแล้ว แถบลำดับเส้นทาง แถบความจุรถ และการรองรับโหมดออฟไลน์
 * รองรับ UC-04, UC-09, UC-12, BR-02, BR-03, REQ-CON-003, REQ-UX-001, CC-01, CC-05, AC-B04-01..07
 */

import React, { useState, useEffect, useCallback } from 'react';
import ActiveJobCard from './ActiveJobCard.jsx';
import RouteOptimizationBar from './RouteOptimizationBar.jsx';
import CollectorCancelModal from './CollectorCancelModal.jsx';
import ClaimConflictModal from './ClaimConflictModal.jsx';
import CapacityIndicatorBar from './CapacityIndicatorBar.jsx';
import { jobRouteApi } from '../services/jobRouteApi.js';

export default function ActiveJobQueueView({
  salengId = 'saleng-01',
  salengLat = 13.790,
  salengLng = 100.575,
  onBack,
  initialData = null,
}) {
  const [queueData, setQueueData] = useState(initialData);
  const [isLoading, setIsLoading] = useState(!initialData);
  const [error, setError] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  // Modals state
  const [cancelModalJob, setCancelModalJob] = useState(null);
  const [conflictModalOpen, setConflictModalOpen] = useState(false);
  const [conflictMessage, setConflictMessage] = useState('');

  const fetchQueue = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await jobRouteApi.getActiveQueue({
        saleng_id: salengId,
        saleng_lat: salengLat,
        saleng_lng: salengLng,
      });
      setQueueData(data);
    } catch (err) {
      setError(err.message || 'เกิดข้อผิดพลาดในการโหลดคิวงาน');
    } finally {
      setIsLoading(false);
    }
  }, [salengId, salengLat, salengLng]);

  useEffect(() => {
    if (!initialData) {
      fetchQueue();
    }
  }, [fetchQueue, initialData]);

  // Handle Start Transit (UC-09, BR-03, AC-B04-05)
  const handleStartTransit = async (orderId) => {
    setIsProcessing(true);
    try {
      const res = await jobRouteApi.startTransit(orderId, {
        saleng_id: salengId,
        current_lat: salengLat,
        current_lng: salengLng,
      });

      // Update state in queue
      setQueueData((prev) => {
        if (!prev) return prev;
        const updatedJobs = prev.jobs.map((j) =>
          j.order_id === orderId ? { ...j, status: 'S4' } : j
        );
        return { ...prev, jobs: updatedJobs };
      });
    } catch (err) {
      alert(err.message || 'ไม่สามารถเริ่มออกเดินทางได้');
    } finally {
      setIsProcessing(false);
    }
  };

  // Handle Cancel Job (MD-STM-04, AC-B04-06)
  const handleConfirmCancel = async (orderId, { reason, note }) => {
    setIsProcessing(true);
    try {
      await jobRouteApi.cancelJob(orderId, {
        saleng_id: salengId,
        reason,
        note,
      });
      setCancelModalJob(null);
      // Refresh queue
      await fetchQueue();
    } catch (err) {
      alert(err.message || 'ยกเลิกงานไม่สำเร็จ');
    } finally {
      setIsProcessing(false);
    }
  };

  const jobs = queueData?.jobs || [];
  const totalLoad = queueData?.current_load_kg || 0;
  const maxCapacity = queueData?.max_capacity_kg || 200.0;
  const isOffline = queueData?.is_offline_cached || (typeof navigator !== 'undefined' && navigator.onLine === false);

  return (
    <div
      data-testid="active-job-queue-view"
      data-req="UC-04"
      className="max-w-md mx-auto min-h-screen bg-slate-50 flex flex-col pb-10"
    >
      {/* Top App Bar */}
      <header className="sticky top-0 z-20 bg-white/95 backdrop-blur-md border-b border-slate-200 px-4 py-3 flex items-center justify-between shadow-xs">
        <button
          type="button"
          data-testid="back-to-jobs-btn"
          onClick={onBack}
          className="flex items-center gap-1 min-h-[48px] px-3 text-slate-700 hover:text-slate-900 font-semibold text-sm rounded-xl hover:bg-slate-100 transition-colors"
        >
          <span>⬅️</span>
          <span>กลับ</span>
        </button>

        <h1 className="text-base font-bold text-slate-800">
          คิวงานและเส้นทาง ({jobs.length})
        </h1>

        <button
          type="button"
          data-testid="refresh-queue-btn"
          onClick={fetchQueue}
          disabled={isLoading || isProcessing}
          className="min-h-[48px] min-w-[48px] flex items-center justify-center text-slate-600 hover:text-slate-800 rounded-xl hover:bg-slate-100 transition-colors"
          title="รีเฟรชข้อมูล"
        >
          🔄
        </button>
      </header>

      {/* Main Content Area */}
      <main className="p-4 space-y-4 flex-1">
        {/* Offline Banner (REQ-OP-001, CC-05) */}
        {isOffline && (
          <div
            data-testid="offline-banner"
            className="p-3 bg-amber-50 border border-amber-300 rounded-2xl flex items-center gap-2 text-amber-900 text-xs font-semibold shadow-xs"
          >
            <span className="text-base">📡</span>
            <span>
              {queueData?.message || 'โหมดออฟไลน์: กำลังแสดงข้อมูลตารางนัดหมายจากแคชในเครื่อง'}
            </span>
          </div>
        )}

        {/* Capacity Indicator Bar (BR-03, REQ-CON-003) */}
        <CapacityIndicatorBar
          current_load_kg={totalLoad}
          job_est_weight_kg={0}
          max_capacity_kg={maxCapacity}
        />

        {/* Route Optimization Bar (UC-04, AC-B04-04) */}
        {jobs.length > 0 && (
          <RouteOptimizationBar
            jobs={jobs}
            total_route_distance_km={queueData?.total_route_distance_km || 0.0}
            total_estimated_duration_min={queueData?.total_estimated_duration_min || 0}
          />
        )}

        {/* Loading Spinner */}
        {isLoading && (
          <div data-testid="queue-loading" className="py-12 text-center text-slate-500 text-sm">
            ⏳ กำลังโหลดรายการคิวงาน...
          </div>
        )}

        {/* Error Alert */}
        {error && !isLoading && (
          <div
            data-testid="queue-error"
            className="p-4 bg-rose-50 border border-rose-200 rounded-2xl text-rose-800 text-sm text-center"
          >
            {error}
          </div>
        )}

        {/* Empty State */}
        {!isLoading && !error && jobs.length === 0 && (
          <div
            data-testid="empty-queue-message"
            className="py-16 text-center text-slate-500 space-y-2 bg-white rounded-2xl border border-slate-200 p-6"
          >
            <div className="text-4xl">📭</div>
            <div className="font-bold text-slate-700">ไม่มีงานในคิวขณะนี้</div>
            <p className="text-xs text-slate-400">
              เมื่อกดรับงานจากหน้ารายการ งานจะมาปรากฏในคิวนี้พร้อมจัดลำดับจุดแวะรับให้อัตโนมัติ
            </p>
          </div>
        )}

        {/* Job Cards List */}
        {!isLoading && jobs.length > 0 && (
          <div className="space-y-3" data-testid="active-jobs-list">
            {jobs.map((job) => (
              <ActiveJobCard
                key={job.order_id}
                job={job}
                isProcessing={isProcessing}
                onStartTransit={handleStartTransit}
                onOpenCancelModal={(selectedJob) => setCancelModalJob(selectedJob)}
              />
            ))}
          </div>
        )}
      </main>

      {/* Collector Cancel Modal (MD-STM-04, AC-B04-06) */}
      <CollectorCancelModal
        isOpen={Boolean(cancelModalJob)}
        job={cancelModalJob}
        isSubmitting={isProcessing}
        onClose={() => setCancelModalJob(null)}
        onConfirm={handleConfirmCancel}
      />

      {/* Claim Conflict Modal (BR-02, CC-04, AC-B04-01) */}
      <ClaimConflictModal
        isOpen={conflictModalOpen}
        message={conflictMessage}
        onAcknowledge={() => setConflictModalOpen(false)}
      />
    </div>
  );
}

