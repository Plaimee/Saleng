import React, { useState, useEffect, useCallback } from 'react';
import StalledOrdersTable from './StalledOrdersTable';
import DisputeDossierCard from './DisputeDossierCard';
import ArbitrationModal from './ArbitrationModal';
import {
  getStalledOrders,
  manualDispatchOrder,
  expandSearchRadius,
  getDisputes,
  getDisputeDossier,
  resolveDispute,
} from '../../services/adminDispatchDisputeApi';

/**
 * หน้าจอหลักศูนย์ควบคุมการจับคู่งานและข้อพิพาทฝั่งผู้ดูแลระบบ (Admin Feature 03)
 * รองรับ UC-13, REQ-FN-005, REQ-FN-004, REQ-UX-001, CC-01, CC-03, CC-05, D-A03-01..06
 * ทัชทาร์เก็ตปุ่มกด >= 48px ทุกปุ่ม
 * กำกับ data-req="UC-13"
 */
export default function AdminDispatchDisputeView() {
  const [activeTab, setActiveTab] = useState('dispatch'); // 'dispatch' | 'disputes'
  const [stalledOrders, setStalledOrders] = useState([]);
  const [disputes, setDisputes] = useState([]);
  const [selectedDisputeDossier, setSelectedDisputeDossier] = useState(null);
  const [arbitrationTarget, setArbitrationTarget] = useState(null);
  const [isArbitrationModalOpen, setIsArbitrationModalOpen] = useState(false);

  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  // โหลดคิวงานตกค้าง
  const loadStalledOrders = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage('');
    try {
      const data = await getStalledOrders({ min_wait_minutes: 30 });
      setStalledOrders(data || []);
    } catch (err) {
      setErrorMessage(err.message || 'ไม่สามารถโหลดข้อมูลคิวงานตกค้างได้');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // โหลดคิวข้อพิพาท
  const loadDisputes = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage('');
    try {
      const data = await getDisputes({ status: 'ALL' });
      setDisputes(data || []);
    } catch (err) {
      setErrorMessage(err.message || 'ไม่สามารถโหลดข้อมูลข้อพิพาทได้');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (activeTab === 'dispatch') {
      loadStalledOrders();
    } else {
      loadDisputes();
    }
  }, [activeTab, loadStalledOrders, loadDisputes]);

  // Handler มอบหมายงานตรง (Direct Assign -> S3)
  const handleAssignOrder = async (orderId, salengId) => {
    setIsLoading(true);
    setErrorMessage('');
    setSuccessMessage('');
    try {
      await manualDispatchOrder({ order_id: orderId, saleng_id: salengId });
      setSuccessMessage(`มอบหมายงาน ${orderId} ให้ซาเล้งสำเร็จ (สถานะเปลี่ยนเป็น S3)`);
      await loadStalledOrders();
    } catch (err) {
      setErrorMessage(err.message || 'เกิดข้อผิดพลาดในการมอบหมายงาน');
    } finally {
      setIsLoading(false);
    }
  };

  // Handler ขยายรัศมีเป็น 10 กม.
  const handleExpandRadius = async (orderId) => {
    setIsLoading(true);
    setErrorMessage('');
    setSuccessMessage('');
    try {
      await expandSearchRadius({ order_id: orderId, new_radius_km: 10.0 });
      setSuccessMessage(`ขยายรัศมีการค้นหาคำขอ ${orderId} เป็น 10.0 กม. เรียบร้อยแล้ว`);
      await loadStalledOrders();
    } catch (err) {
      setErrorMessage(err.message || 'เกิดข้อผิดพลาดในการขยายรัศมี');
    } finally {
      setIsLoading(false);
    }
  };

  // Handler ดึงสำนวนข้อพิพาท
  const handleFetchDossier = async (disputeId) => {
    try {
      const dossier = await getDisputeDossier(disputeId);
      setSelectedDisputeDossier(dossier);
    } catch (err) {
      setErrorMessage(err.message || 'ไม่สามารถดึงสำนวนข้อพิพาทได้');
    }
  };

  // Handler เปิด Modal ตัดสินชี้ขาด
  const handleOpenArbitration = (disputeOrDossier) => {
    setArbitrationTarget(disputeOrDossier);
    setIsArbitrationModalOpen(true);
  };

  // Handler ยืนยันคำตัดสินชี้ขาด
  const handleSubmitArbitration = async (payload) => {
    if (!arbitrationTarget) return;
    setIsLoading(true);
    setErrorMessage('');
    setSuccessMessage('');
    try {
      const res = await resolveDispute(arbitrationTarget.dispute_id, payload);
      setSuccessMessage(
        `ตัดสินชี้ขาดข้อพิพาท ${arbitrationTarget.dispute_id} สำเร็จ: ${
          res.order_status === 'S7' ? 'ปิดงานและออกใบเสร็จเรียบร้อย' : 'สั่งยกเลิกคำขอเรียบร้อย'
        }`
      );
      setIsArbitrationModalOpen(false);
      setArbitrationTarget(null);
      await loadDisputes();
    } catch (err) {
      setErrorMessage(err.message || 'เกิดข้อผิดพลาดในการตัดสินชี้ขาด');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      data-req="UC-13"
      data-testid="admin-dispatch-dispute-view"
      className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6"
    >
      {/* Header และป้ายกำกับระบบ */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-gray-200 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded text-xs font-bold bg-blue-100 text-blue-800">
              Admin Feature 03
            </span>
            <span className="px-2.5 py-0.5 rounded text-xs font-semibold bg-emerald-100 text-emerald-800 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
              Online-only (CC-05)
            </span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mt-1">
            ศูนย์ควบคุมการจับคู่งานและข้อพิพาท
          </h1>
          <p className="text-sm text-gray-500 mt-0.5">
            จัดการคำขอนัดหมายตกค้างเกินเกณฑ์ (Manual Dispatch Fallback) และระงับข้อพิพาทหน้างาน (Dispute Arbitration)
          </p>
        </div>

        {/* ปุ่มรีเฟรชข้อมูล */}
        <button
          type="button"
          onClick={() => (activeTab === 'dispatch' ? loadStalledOrders() : loadDisputes())}
          disabled={isLoading}
          className="min-h-[48px] px-5 py-2.5 bg-white border border-gray-300 rounded-xl text-xs font-semibold text-gray-700 shadow-sm hover:bg-gray-50 active:scale-95 transition flex items-center justify-center gap-2 disabled:opacity-50"
        >
          <svg className={`w-4 h-4 text-gray-500 ${isLoading ? 'animate-spin' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span>{isLoading ? 'กำลังโหลด...' : 'รีเฟรชคิวงาน'}</span>
        </button>
      </div>

      {/* แถบแจ้งเตือนความสำเร็จและข้อผิดพลาด */}
      {successMessage && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-emerald-800 font-medium flex justify-between items-center animate-in fade-in">
          <span>{successMessage}</span>
          <button onClick={() => setSuccessMessage('')} className="text-emerald-600 hover:text-emerald-800 p-1">✕</button>
        </div>
      )}
      {errorMessage && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-xs text-red-800 font-medium flex justify-between items-center animate-in fade-in">
          <span>{errorMessage}</span>
          <button onClick={() => setErrorMessage('')} className="text-red-600 hover:text-red-800 p-1">✕</button>
        </div>
      )}

      {/* แถบเลือกแท็บการทำงานหลัก */}
      <div className="flex border-b border-gray-200 space-x-2">
        <button
          type="button"
          data-testid="tab-dispatch"
          onClick={() => setActiveTab('dispatch')}
          className={`min-h-[48px] px-5 py-3 text-sm font-semibold border-b-2 transition flex items-center gap-2 ${
            activeTab === 'dispatch'
              ? 'border-emerald-600 text-emerald-700'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          }`}
        >
          <span>1. ศูนย์กระจายงานสำรอง (งานตกค้าง)</span>
          {stalledOrders.length > 0 && (
            <span className="px-2 py-0.5 text-xs rounded-full bg-amber-100 text-amber-800 font-bold">
              {stalledOrders.length}
            </span>
          )}
        </button>

        <button
          type="button"
          data-testid="tab-disputes"
          onClick={() => setActiveTab('disputes')}
          className={`min-h-[48px] px-5 py-3 text-sm font-semibold border-b-2 transition flex items-center gap-2 ${
            activeTab === 'disputes'
              ? 'border-emerald-600 text-emerald-700'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          }`}
        >
          <span>2. ศูนย์ตัดสินข้อพิพาทหน้างาน (S8)</span>
          {disputes.filter((d) => d.status === 'PENDING_ADMIN').length > 0 && (
            <span className="px-2 py-0.5 text-xs rounded-full bg-red-100 text-red-800 font-bold">
              {disputes.filter((d) => d.status === 'PENDING_ADMIN').length}
            </span>
          )}
        </button>
      </div>

      {/* เนื้อหาตามแท็บที่เลือก */}
      {activeTab === 'dispatch' ? (
        <div className="space-y-4">
          <StalledOrdersTable
            orders={stalledOrders}
            onAssign={handleAssignOrder}
            onExpandRadius={handleExpandRadius}
            isLoading={isLoading}
          />
        </div>
      ) : (
        <div className="space-y-4">
          {disputes.length === 0 ? (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center text-gray-500">
              <p className="text-base font-medium text-gray-700">ไม่มีรายการข้อพิพาทในขณะนี้</p>
            </div>
          ) : (
            disputes.map((disp) => (
              <DisputeDossierCard
                key={disp.dispute_id}
                dispute={disp}
                dossier={selectedDisputeDossier?.dispute_id === disp.dispute_id ? selectedDisputeDossier : null}
                onOpenArbitration={handleOpenArbitration}
                onFetchDossier={handleFetchDossier}
                isLoading={isLoading}
              />
            ))
          )}
        </div>
      )}

      {/* Modal ตัดสินชี้ขาดข้อพิพาท */}
      <ArbitrationModal
        dispute={arbitrationTarget}
        isOpen={isArbitrationModalOpen}
        onClose={() => {
          setIsArbitrationModalOpen(false);
          setArbitrationTarget(null);
        }}
        onSubmit={handleSubmitArbitration}
        isLoading={isLoading}
      />
    </div>
  );
}
