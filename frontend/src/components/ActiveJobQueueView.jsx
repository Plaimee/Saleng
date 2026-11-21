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
  onStartNavigation,
  onOpenChat,
  onOpenBilling,
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
      let targetJob = null;
      setQueueData((prev) => {
        if (!prev) return prev;
        const updatedJobs = prev.jobs.map((j) => {
          if (j.order_id === orderId) {
            targetJob = { ...j, status: 'S4' };
            return targetJob;
          }
          return j;
        });
        return { ...prev, jobs: updatedJobs };
      });

      if (onStartNavigation && targetJob) {
        onStartNavigation(targetJob);
      }
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
      className="w-full flex flex-col space-y-5 font-sans text-black"
    >
      {/* Top Banner: Golden Yellow + Jet Black */}
      <header className="rounded-2xl p-4 bg-yellow-400 border-2 border-black shadow-sm flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          {onBack && (
            <button
              type="button"
              data-testid="back-to-jobs-btn"
              onClick={onBack}
              className="flex items-center gap-1 min-h-[44px] px-3 bg-black text-yellow-400 hover:bg-zinc-800 font-bold text-xs rounded-full transition-colors"
            >
              <span>⬅️</span>
              <span>กลับ</span>
            </button>
          )}
          <div className="w-10 h-10 rounded-xl bg-black text-yellow-400 flex items-center justify-center text-xl flex-shrink-0">
            🛵
          </div>
          <div>
            <h1 className="text-base sm:text-lg font-extrabold text-black">
              คิวงานและเส้นทางวันนี้ ({jobs.length})
            </h1>
            <p className="text-xs text-black/80">
              เริ่มออกเดินทาง แชตผู้ขาย หรือเข้าหน้าชั่งน้ำหนักได้จากแต่ละงานโดยตรง
            </p>
          </div>
        </div>

        <button
          type="button"
          data-testid="refresh-queue-btn"
          onClick={fetchQueue}
          disabled={isLoading || isProcessing}
          className="min-h-[44px] px-4 flex items-center justify-center gap-1.5 bg-black text-yellow-400 hover:bg-zinc-800 text-xs font-bold rounded-full transition-colors shadow"
          title="รีเฟรชข้อมูล"
        >
          <span>🔄</span>
          <span>รีเฟรชคิว</span>
        </button>
      </header>

      {/* Main Content Area */}
      <main className="space-y-4 flex-1">
        {/* Offline Banner (REQ-OP-001, CC-05) */}
        {isOffline && (
          <div
            data-testid="offline-banner"
            className="p-3 bg-amber-100 border border-amber-400 rounded-2xl flex items-center gap-2 text-amber-950 text-xs font-semibold shadow-xs"
          >
            <span className="text-base">📡</span>
            <span>
              {queueData?.message || 'โหมดออฟไลน์: กำลังแสดงข้อมูลตารางนัดหมายจากแคชในเครื่อง'}
            </span>
          </div>
        )}

        {/* Capacity + Route Summary Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="bg-yellow-50/90 rounded-2xl p-3 border border-yellow-300">
            <CapacityIndicatorBar
              current_load_kg={totalLoad}
              job_est_weight_kg={0}
              max_capacity_kg={maxCapacity}
            />
          </div>

          {jobs.length > 0 && (
            <div className="bg-yellow-50/90 rounded-2xl p-3 border border-yellow-300">
              <RouteOptimizationBar
                jobs={jobs}
                total_route_distance_km={queueData?.total_route_distance_km || 0.0}
                total_estimated_duration_min={queueData?.total_estimated_duration_min || 0}
              />
            </div>
          )}
        </div>

        {/* Loading Spinner */}
        {isLoading && (
          <div data-testid="queue-loading" className="py-12 text-center text-zinc-500 text-sm">
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
            className="py-14 text-center text-zinc-600 space-y-2 bg-yellow-50 rounded-2xl border-2 border-dashed border-yellow-400 p-6"
          >
            <div className="text-4xl">📭</div>
            <div className="font-extrabold text-black">ไม่มีงานในคิวขณะนี้</div>
            <p className="text-xs text-zinc-600">
              เมื่อกดรับงานจากหน้าหางานใกล้ฉัน งานจะมาปรากฏในคิวนี้พร้อมจัดลำดับจุดแวะรับให้อัตโนมัติ
            </p>
          </div>
        )}

        {/* Job Cards Grid (2 Columns on Desktop) */}
        {!isLoading && jobs.length > 0 && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4" data-testid="active-jobs-list">
            {jobs.map((job) => (
              <div key={job.order_id} className="space-y-2">
                <ActiveJobCard
                  job={job}
                  isProcessing={isProcessing}
                  onStartTransit={handleStartTransit}
                  onOpenCancelModal={(selectedJob) => setCancelModalJob(selectedJob)}
                />
                {(onOpenChat || onOpenBilling) && (
                  <div className="flex items-center gap-2 px-1">
                    {onOpenChat && (
                      <button
                        type="button"
                        onClick={() => onOpenChat(job)}
                        className="flex-1 py-2 rounded-xl bg-white border-2 border-black text-black text-xs font-bold hover:bg-yellow-100 transition"
                      >
                        💬 แชต & โทรติดต่อผู้ขาย
                      </button>
                    )}
                    {onOpenBilling && (
                      <button
                        type="button"
                        onClick={() => onOpenBilling(job)}
                        className="flex-1 py-2 rounded-xl bg-black text-yellow-400 text-xs font-bold hover:bg-zinc-800 transition"
                      >
                        ⚖️ ชั่งน้ำหนัก & ออกใบเสร็จ
                      </button>
                    )}
                  </div>
                )}
              </div>
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

