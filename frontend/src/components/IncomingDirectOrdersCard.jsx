/**
 * การ์ดแสดงคำขอเรียกตรงจากผู้ขายที่รอซาเล้งกดตอบรับ (IncomingDirectOrdersCard)
 * แสดงเมื่อผู้ขายเลือกซาเล้งท่านนี้โดยตรงในขั้นที่ 3 (S2 Direct Request)
 * ซาเล้งสามารถกดรับออเดอร์ (S2 -> S3) หรือปฏิเสธได้ทันที
 */

import React, { useState, useEffect, useCallback } from 'react';
import { jobRouteApi } from '../services/jobRouteApi';

export default function IncomingDirectOrdersCard({
  salengId = 'saleng-01',
  onAccepted,
}) {
  const [requests, setRequests] = useState([]);
  const [busyId, setBusyId] = useState(null);
  const [error, setError] = useState('');

  const fetchIncoming = useCallback(async () => {
    if (!salengId) return;
    try {
      const res = await fetch(
        `/api/v1/collectors/${encodeURIComponent(salengId)}/incoming-requests`
      );
      if (!res.ok) return;
      const data = await res.json();
      setRequests(data.requests || []);
    } catch {
      // ignore background poll errors
    }
  }, [salengId]);

  useEffect(() => {
    fetchIncoming();
    const timer = setInterval(fetchIncoming, 5000);
    return () => clearInterval(timer);
  }, [fetchIncoming]);

  const handleAccept = async (req) => {
    setBusyId(req.order_id);
    setError('');
    try {
      await jobRouteApi.claimJob(req.order_id, {
        saleng_id: salengId,
        expected_version: req.version || 1,
      });
      await fetchIncoming();
      if (onAccepted) onAccepted(req);
    } catch (err) {
      setError(err.message || 'ไม่สามารถรับออเดอร์ได้ (ตรวจสอบว่าผ่านการยืนยันตัวตน KYC แล้ว)');
    } finally {
      setBusyId(null);
    }
  };

  const handleDecline = async (req) => {
    setBusyId(req.order_id);
    setError('');
    try {
      await fetch(
        `/api/v1/collectors/jobs/${encodeURIComponent(req.order_id)}/decline-direct?saleng_id=${encodeURIComponent(salengId)}`,
        { method: 'POST' }
      );
      await fetchIncoming();
    } catch {
      setError('ปฏิเสธคำขอไม่สำเร็จ');
    } finally {
      setBusyId(null);
    }
  };

  if (requests.length === 0) return null;

  return (
    <div
      data-testid="incoming-direct-orders"
      className="rounded-2xl p-4 bg-black text-white border-2 border-yellow-400 shadow-lg space-y-3 mb-5"
    >
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="text-xl animate-bounce">🔔</span>
          <div>
            <h3 className="text-sm sm:text-base font-extrabold text-yellow-400">
              มีคำขอเรียกตรงถึงคุณ ({requests.length} ออเดอร์)
            </h3>
            <p className="text-xs text-zinc-300">
              ผู้ขายเจาะจงเลือกคุณมารับซื้อ กรุณาตอบรับภายใน 15 นาที
            </p>
          </div>
        </div>
        <span className="text-xs font-extrabold px-3 py-1 rounded-full bg-yellow-400 text-black">
          รอตอบรับ (S2)
        </span>
      </div>

      {error && (
        <div className="p-2.5 rounded-xl bg-red-900/60 border border-red-400 text-red-100 text-xs">
          ⚠️ {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {requests.map((req) => (
          <div
            key={req.order_id}
            className="rounded-xl p-3.5 bg-zinc-900 border border-yellow-400/50 space-y-2.5"
          >
            <div className="flex items-start justify-between gap-2">
              <div>
                <div className="text-[11px] font-mono text-zinc-400">
                  รหัสคำขอ: {req.order_id.slice(0, 12)}...
                </div>
                <div className="text-sm font-bold text-white mt-0.5">
                  {req.items_count} รายการ • ~{req.total_est_weight_kg} กก.
                </div>
              </div>
              <div className="text-right">
                <div className="text-xs font-extrabold text-yellow-400">
                  ฿{req.total_est_min_price.toFixed(0)} – ฿{req.total_est_max_price.toFixed(0)}
                </div>
                <div className="text-[10px] text-zinc-400">ราคาประเมิน</div>
              </div>
            </div>

            {req.appointment_notes && (
              <div className="text-xs text-yellow-200 bg-zinc-800 px-3 py-1.5 rounded-lg">
                💬 &ldquo;{req.appointment_notes}&rdquo;
              </div>
            )}

            <div className="flex items-center gap-2 pt-1">
              <button
                type="button"
                disabled={busyId === req.order_id}
                onClick={() => handleAccept(req)}
                className="flex-1 py-2.5 rounded-full bg-yellow-400 hover:bg-yellow-300 text-black text-xs font-extrabold transition disabled:opacity-50"
              >
                {busyId === req.order_id ? 'กำลังรับงาน...' : '✅ กดรับออเดอร์นี้'}
              </button>
              <button
                type="button"
                disabled={busyId === req.order_id}
                onClick={() => handleDecline(req)}
                className="px-4 py-2.5 rounded-full bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-bold border border-zinc-600 transition disabled:opacity-50"
              >
                ปฏิเสธ
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
