import React, { useState, useEffect, useCallback } from 'react';
import BenchmarkPriceTable from './BenchmarkPriceTable';
import BulkyItemPriceTable from './BulkyItemPriceTable';
import QualityGradingRuleCard from './QualityGradingRuleCard';
import {
  getBenchmarkPrices,
  updateBenchmarkPrice,
  getGradingRules,
  updateGradingRules,
} from '../../services/adminBenchmarkApi';

/**
 * หน้าจอหลักระบบจัดการราคากลางและหมวดหมู่วัสดุฝั่งผู้ดูแลระบบ (Admin Feature 02)
 * รองรับ UC-03, UC-05, REQ-DAT-001, REQ-FN-003, REQ-UX-001, CC-01, CC-03, CC-05
 * ทัชทาร์เก็ตปุ่มกด >= 48px ทุกปุ่ม
 */
export default function AdminBenchmarkGradingView() {
  const [activeTab, setActiveTab] = useState('prices'); // 'prices' | 'grading'
  const [prices, setPrices] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  // โหลดรายการราคากลางทั้งหมด
  const loadPrices = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage('');
    try {
      const data = await getBenchmarkPrices();
      setPrices(data || []);
    } catch (err) {
      setErrorMessage(err.message || 'ไม่สามารถโหลดข้อมูลราคากลางได้');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadPrices();
  }, [loadPrices]);

  // Handler สำหรับการอัปเดตราคากลาง (ทั้งแบบ kg และ piece)
  const handleUpdatePrice = async (categoryCode, payload) => {
    setIsLoading(true);
    setErrorMessage('');
    setSuccessMessage('');
    try {
      const res = await updateBenchmarkPrice(categoryCode, payload);
      setSuccessMessage(`อัปเดตราคาหมวด ${categoryCode} เรียบร้อยแล้ว${res.warning ? ` (${res.warning})` : ''}`);
      await loadPrices();
    } catch (err) {
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  // Handler สำหรับดึงเกณฑ์คุณภาพ
  const handleFetchRules = useCallback(async (categoryCode) => {
    return await getGradingRules(categoryCode);
  }, []);

  // Handler สำหรับอัปเดตเกณฑ์คุณภาพ
  const handleUpdateRules = async (categoryCode, payload) => {
    setIsLoading(true);
    setErrorMessage('');
    setSuccessMessage('');
    try {
      const res = await updateGradingRules(categoryCode, payload);
      setSuccessMessage(`ปรับปรุงเกณฑ์คุณภาพหมวด ${categoryCode} สำเร็จ`);
      return res;
    } catch (err) {
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8"
      data-req="UC-03"
      data-testid="admin-benchmark-grading-view"
    >
      {/* ส่วนหัวหน้าจอ */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 pb-6 border-b border-slate-200 mb-6">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-black text-slate-900 tracking-tight">
              ระบบจัดการราคากลางและเกณฑ์คุณภาพ
            </h1>
            <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300">
              Admin 02
            </span>
          </div>
          <p className="text-sm text-slate-500 mt-1">
            ควบคุมการเผยแพร่ราคากลางรายวัน (UC-03) และราคาเหมาจ่ายขยะชิ้นใหญ่ (UC-05) พร้อมเกณฑ์คุณภาพ 3 ระดับ
          </p>
        </div>

        {/* Badge โหมด Online-only ตาม CC-05 */}
        <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-50 text-emerald-800 text-xs font-semibold rounded-xl border border-emerald-200">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span>โหมด Online-only (CC-05)</span>
        </div>
      </div>

      {/* แถบแจ้งเตือนความสำเร็จและข้อผิดพลาด */}
      {successMessage && (
        <div className="p-4 mb-6 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl flex items-center justify-between text-sm" role="alert">
          <div className="flex items-center gap-2">
            <span className="text-lg">✓</span>
            <span>{successMessage}</span>
          </div>
          <button
            type="button"
            onClick={() => setSuccessMessage('')}
            className="text-emerald-600 hover:text-emerald-800 p-1"
          >
            ✕
          </button>
        </div>
      )}

      {errorMessage && (
        <div className="p-4 mb-6 bg-rose-50 border border-rose-200 text-rose-800 rounded-xl flex items-center justify-between text-sm" role="alert">
          <div className="flex items-center gap-2">
            <span className="text-lg">⚠️</span>
            <span>{errorMessage}</span>
          </div>
          <button
            type="button"
            onClick={() => setErrorMessage('')}
            className="text-rose-600 hover:text-rose-800 p-1"
          >
            ✕
          </button>
        </div>
      )}

      {/* แท็บสลับหน้าจอ (ปุ่ม >= 48px ตาม REQ-UX-001, CC-01) */}
      <div className="flex gap-2 border-b border-slate-200 mb-6 pb-px">
        <button
          type="button"
          onClick={() => setActiveTab('prices')}
          className={`min-h-[48px] px-6 py-2.5 font-bold text-sm rounded-t-xl transition-all border-b-2 flex items-center gap-2 ${
            activeTab === 'prices'
              ? 'border-emerald-600 text-emerald-800 bg-emerald-50/50'
              : 'border-transparent text-slate-500 hover:text-slate-700 hover:bg-slate-50'
          }`}
          data-testid="tab-prices"
        >
          <span>⚖️</span> ราคากลางรายวันและขยะชิ้นใหญ่
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('grading')}
          className={`min-h-[48px] px-6 py-2.5 font-bold text-sm rounded-t-xl transition-all border-b-2 flex items-center gap-2 ${
            activeTab === 'grading'
              ? 'border-emerald-600 text-emerald-800 bg-emerald-50/50'
              : 'border-transparent text-slate-500 hover:text-slate-700 hover:bg-slate-50'
          }`}
          data-testid="tab-grading"
        >
          <span>🏷️</span> เกณฑ์คุณภาพและการหักสิ่งปนเปื้อน
        </button>
      </div>

      {/* เนื้อหาตามแท็บที่เลือก */}
      {activeTab === 'prices' && (
        <div>
          <BenchmarkPriceTable
            prices={prices}
            onUpdatePrice={handleUpdatePrice}
            isLoading={isLoading}
          />
          <BulkyItemPriceTable
            prices={prices}
            onUpdatePrice={handleUpdatePrice}
            isLoading={isLoading}
          />
        </div>
      )}

      {activeTab === 'grading' && (
        <div>
          <QualityGradingRuleCard
            categories={prices}
            onFetchRules={handleFetchRules}
            onUpdateRules={handleUpdateRules}
            isLoading={isLoading}
          />
        </div>
      )}
    </div>
  );
}

