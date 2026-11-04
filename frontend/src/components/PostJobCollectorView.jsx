import React, { useState, useEffect, useCallback } from 'react';
import { postJobApi } from '../services/postJobApi.js';
import PurchaseHistoryCard from './PurchaseHistoryCard.jsx';
import RegularCustomerList from './RegularCustomerList.jsx';
import DigitalReceiptCard from './DigitalReceiptCard.jsx';
import { billingReceiptApi } from '../services/billingReceiptApi.js';

/**
 * PostJobCollectorView Component
 * หน้าจอหลักระบบหลังจบงานฝั่งซาเล้ง: ประวัติการรับซื้อ, สถิติสะสม, และลูกค้าประจำ
 * รองรับ UC-10, REQ-FN-005, REQ-SEC-002, CC-01, CC-05, CC-06, REQ-OP-001, D-B07-01..06
 */
export default function PostJobCollectorView({
  salengId = 'saleng-01',
  onBack,
}) {
  const [activeTab, setActiveTab] = useState('history'); // 'history' | 'regular'
  const [period, setPeriod] = useState('all'); // 'all' | 'today' | 'month'

  const [historyData, setHistoryData] = useState(null);
  const [regularCustomers, setRegularCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isOffline, setIsOffline] = useState(
    typeof navigator !== 'undefined' ? navigator.onLine === false : false
  );

  // สำหรับเปิดดูใบเสร็จดิจิทัล
  const [activeReceipt, setActiveReceipt] = useState(null);
  const [loadingReceipt, setLoadingReceipt] = useState(false);

  const loadHistory = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await postJobApi.getPurchaseHistory(salengId, period);
      setHistoryData(data);
    } catch (err) {
      setError(err.message || 'ไม่สามารถโหลดประวัติการรับซื้อได้');
    } finally {
      setLoading(false);
    }
  }, [salengId, period]);

  const loadRegularCustomers = useCallback(async () => {
    try {
      const data = await postJobApi.getRegularCustomers(salengId);
      setRegularCustomers(data);
    } catch {
      // ignore
    }
  }, [salengId]);

  useEffect(() => {
    loadHistory();
    loadRegularCustomers();

    const handleOnline = () => setIsOffline(false);
    const handleOffline = () => setIsOffline(true);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [loadHistory, loadRegularCustomers]);

  const handleToggleCustomer = async (item) => {
    try {
      await postJobApi.toggleRegularCustomer(salengId, {
        seller_id: item.seller_id || item.order_id,
        seller_name: item.seller_name,
        seller_phone_masked: item.seller_phone_masked,
      });
      await loadHistory();
      await loadRegularCustomers();
    } catch (err) {
      setError(err.message || 'ไม่สามารถสลับสถานะลูกค้าประจำได้');
    }
  };

  const handleRemoveCustomer = async (sellerId) => {
    try {
      await postJobApi.toggleRegularCustomer(salengId, { seller_id: sellerId });
      await loadRegularCustomers();
      await loadHistory();
    } catch (err) {
      setError(err.message || 'ไม่สามารถลบลูกค้าประจำได้');
    }
  };

  const handleViewReceipt = async (orderId) => {
    setLoadingReceipt(true);
    try {
      const receipt = await billingReceiptApi.getReceipt(orderId, salengId);
      setActiveReceipt(receipt);
    } catch (err) {
      setError(err.message || 'ไม่สามารถดึงใบเสร็จดิจิทัลได้');
    } finally {
      setLoadingReceipt(false);
    }
  };

  const summary = historyData?.summary || {
    total_expense_baht: 0,
    total_weight_kg: 0,
    total_completed_jobs: 0,
  };
  const items = historyData?.items || [];

  return (
    <div
      className="max-w-md mx-auto bg-gray-50 min-h-screen pb-12"
      data-req="UC-10"
      data-testid="post-job-collector-view"
    >
      {/* ส่วนหัวหน้าจอ */}
      <header className="bg-emerald-700 text-white p-4 sticky top-0 z-10 shadow-md">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {onBack && (
              <button
                type="button"
                onClick={onBack}
                className="w-10 h-10 min-h-[48px] min-w-[48px] rounded-full hover:bg-emerald-800 flex items-center justify-center text-lg"
                data-testid="header-back-btn"
              >
                ←
              </button>
            )}
            <div>
              <h1 className="text-base font-bold">สรุปหลังจบงานและลูกค้าประจำ</h1>
              <span className="text-xs text-emerald-100">ซาเล้ง: {salengId}</span>
            </div>
          </div>
        </div>

        {/* แถบสลับแท็บ (ทัชทาร์เก็ต >= 48px ตาม REQ-UX-001, CC-01) */}
        <div className="grid grid-cols-2 gap-1 bg-emerald-800/60 p-1 rounded-xl mt-3">
          <button
            type="button"
            onClick={() => setActiveTab('history')}
            className={`min-h-[48px] rounded-lg text-xs font-bold transition flex items-center justify-center gap-1.5 ${
              activeTab === 'history'
                ? 'bg-white text-emerald-900 shadow-sm'
                : 'text-emerald-100 hover:text-white'
            }`}
            data-testid="tab-history-btn"
          >
            <span>📜</span> ประวัติการรับซื้อ
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('regular')}
            className={`min-h-[48px] rounded-lg text-xs font-bold transition flex items-center justify-center gap-1.5 ${
              activeTab === 'regular'
                ? 'bg-white text-emerald-900 shadow-sm'
                : 'text-emerald-100 hover:text-white'
            }`}
            data-testid="tab-regular-btn"
          >
            <span>⭐</span> ลูกค้าประจำ ({regularCustomers.length})
          </button>
        </div>
      </header>

      {/* แถบเตือนออฟไลน์ (CC-05, REQ-OP-001) */}
      {isOffline && (
        <div
          className="bg-amber-100 border-b border-amber-200 px-4 py-2 text-xs text-amber-900 flex items-center gap-1.5"
          data-testid="offline-banner"
        >
          <span>📶</span>
          <span>โหมดออฟไลน์: กำลังแสดงข้อมูลประวัติที่บันทึกไว้ในเครื่อง</span>
        </div>
      )}

      <main className="p-4 space-y-4">
        {error && (
          <div
            className="bg-red-50 border border-red-200 rounded-xl p-3 text-xs text-red-700 flex justify-between items-center"
            data-testid="error-banner"
          >
            <span>⚠️ {error}</span>
            <button
              type="button"
              onClick={() => setError(null)}
              className="text-red-500 font-bold px-2"
            >
              ✕
            </button>
          </div>
        )}

        {/* แท็บที่ 1: ประวัติการรับซื้อ */}
        {activeTab === 'history' && (
          <div className="space-y-4" data-testid="history-tab-content">
            {/* ตัวกรองช่วงเวลา */}
            <div className="flex gap-2">
              {[
                { id: 'all', label: 'ทั้งหมด' },
                { id: 'today', label: 'วันนี้' },
                { id: 'month', label: 'เดือนนี้' },
              ].map((f) => (
                <button
                  key={f.id}
                  type="button"
                  onClick={() => setPeriod(f.id)}
                  className={`min-h-[48px] flex-1 rounded-xl text-xs font-bold border transition ${
                    period === f.id
                      ? 'bg-emerald-600 text-white border-emerald-600 shadow-sm'
                      : 'bg-white text-gray-700 border-gray-200 hover:bg-gray-50'
                  }`}
                  data-testid={`filter-${f.id}-btn`}
                >
                  {f.label}
                </button>
              ))}
            </div>

            {/* การ์ดสรุปสะสม 3 มิติ (D-B07-05) */}
            <div className="grid grid-cols-3 gap-2" data-testid="summary-cards">
              <div className="bg-white rounded-2xl border border-gray-200 p-3 text-center shadow-sm">
                <span className="text-[11px] text-gray-400 block">รายจ่ายรวม</span>
                <span className="text-base font-black text-emerald-700 block mt-0.5" data-testid="summary-expense">
                  ฿{summary.total_expense_baht.toFixed(0)}
                </span>
              </div>
              <div className="bg-white rounded-2xl border border-gray-200 p-3 text-center shadow-sm">
                <span className="text-[11px] text-gray-400 block">น้ำหนักรวม</span>
                <span className="text-base font-black text-gray-800 block mt-0.5" data-testid="summary-weight">
                  {summary.total_weight_kg.toFixed(0)} <span className="text-xs font-normal">กก.</span>
                </span>
              </div>
              <div className="bg-white rounded-2xl border border-gray-200 p-3 text-center shadow-sm">
                <span className="text-[11px] text-gray-400 block">งานสำเร็จ</span>
                <span className="text-base font-black text-blue-600 block mt-0.5" data-testid="summary-jobs">
                  {summary.total_completed_jobs} <span className="text-xs font-normal">งาน</span>
                </span>
              </div>
            </div>

            {/* รายการคำขอสำเร็จ */}
            {loading ? (
              <div className="text-center py-10 text-xs text-gray-500">กำลังโหลดข้อมูล...</div>
            ) : items.length === 0 ? (
              <div className="bg-white rounded-2xl border border-gray-200 p-8 text-center text-xs text-gray-500">
                ไม่มีประวัติการรับซื้อในช่วงเวลานี้
              </div>
            ) : (
              <div className="space-y-3" data-testid="history-list">
                {items.map((it) => (
                  <PurchaseHistoryCard
                    key={it.order_id}
                    item={it}
                    onViewReceipt={handleViewReceipt}
                    onToggleRegularCustomer={handleToggleCustomer}
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {/* แท็บที่ 2: ลูกค้าประจำ */}
        {activeTab === 'regular' && (
          <div data-testid="regular-tab-content">
            <RegularCustomerList
              customers={regularCustomers}
              onRemoveCustomer={handleRemoveCustomer}
            />
          </div>
        )}
      </main>

      {/* โมดอลเปิดดูใบเสร็จดิจิทัล */}
      {activeReceipt && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="max-w-sm w-full">
            <DigitalReceiptCard
              receipt={activeReceipt}
              onBackToHome={() => setActiveReceipt(null)}
            />
          </div>
        </div>
      )}
    </div>
  );
}

