import React, { useState, useEffect, useCallback } from 'react';
import {
  getCommunityWasteReport,
  exportCommunityWasteCsv,
} from '../../services/adminSecurityComplianceApi';

/**
 * คอมโพเนนต์รายงานสถิติปริมาณขยะรีไซเคิลชุมชนรายเขต (Anonymized Community Waste Report)
 * รองรับ UC-13, D-A04-03, REQ-SEC-002, AC-A04-05, REQ-UX-001, CC-01, CC-03, CC-05, CC-06 (No PII)
 * ทัชทาร์เก็ตปุ่มกด >= 48px ทุกปุ่ม
 * กำกับ data-req="UC-13"
 */
export default function CommunityWasteReportView({ adminRole = 'ADMIN', onNotify }) {
  const [reportData, setReportData] = useState(null);
  const [filterPeriod, setFilterPeriod] = useState('2026-11');
  const [filterDistrict, setFilterDistrict] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const fetchReport = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage('');
    try {
      const res = await getCommunityWasteReport(
        {
          period: filterPeriod || undefined,
          district: filterDistrict || undefined,
        },
        { customRole: adminRole }
      );
      setReportData(res);
    } catch (err) {
      setErrorMessage(err.message || 'ไม่สามารถโหลดรายงานสถิติขยะชุมชนได้');
      if (onNotify) onNotify(err.message, 'error');
    } finally {
      setIsLoading(false);
    }
  }, [filterPeriod, filterDistrict, adminRole, onNotify]);

  useEffect(() => {
    fetchReport();
  }, [fetchReport]);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchReport();
  };

  const handleExportCsv = async () => {
    try {
      const csvText = await exportCommunityWasteCsv(
        { period: filterPeriod || undefined, district: filterDistrict || undefined },
        { customRole: adminRole }
      );
      const blob = new Blob([csvText], { type: 'text/csv;charset=utf-8;' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `community_waste_report_${filterPeriod || 'all'}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      if (onNotify) onNotify('ส่งออกไฟล์รายงานขยะชุมชน CSV สำเร็จ', 'success');
    } catch (err) {
      if (onNotify) onNotify(err.message || 'ไม่สามารถส่งออก CSV ได้', 'error');
    }
  };

  const summaryItems = reportData?.summary_items || [];

  return (
    <div data-req="UC-13" className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 space-y-4">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-gray-800">
              📊 รายงานสถิติขยะรีไซเคิลชุมชนรายเขต (Community Waste Report)
            </h2>
            <span className="px-2 py-1 text-xs rounded-full font-bold bg-green-100 text-green-800 border border-green-300">
              🔒 No PII (ปลอดข้อมูลส่วนบุคคล 100%)
            </span>
          </div>
          <p className="text-sm text-gray-500 mt-1">
            สรุปปริมาณและมูลค่าการรับซื้อแยกตามเขต/แขวง สำหรับส่งต่อสำนักสิ่งแวดล้อม กทม. และเทศบาล
          </p>
        </div>
        <div>
          <button
            type="button"
            onClick={handleExportCsv}
            disabled={isLoading || summaryItems.length === 0}
            className="min-h-[48px] min-w-[48px] px-4 py-2 bg-emerald-600 hover:bg-emerald-700 active:bg-emerald-800 text-white font-medium rounded-lg flex items-center justify-center gap-2 transition disabled:opacity-50"
          >
            <span>📥</span> ส่งออก CSV (สำหรับ กทม./เทศบาล)
          </button>
        </div>
      </div>

      {/* Filter Form */}
      <form onSubmit={handleSearch} className="grid grid-cols-1 md:grid-cols-3 gap-3 bg-gray-50 p-3 rounded-lg border">
        <div>
          <label className="block text-xs font-semibold text-gray-600 mb-1">ช่วงเวลา (รอบเดือน YYYY-MM)</label>
          <input
            type="text"
            value={filterPeriod}
            onChange={(e) => setFilterPeriod(e.target.value)}
            placeholder="2026-11"
            className="w-full min-h-[48px] px-3 py-2 border rounded-md text-sm focus:ring-2 focus:ring-emerald-500 bg-white"
          />
        </div>
        <div>
          <label className="block text-xs font-semibold text-gray-600 mb-1">กรองเฉพาะเขต</label>
          <input
            type="text"
            value={filterDistrict}
            onChange={(e) => setFilterDistrict(e.target.value)}
            placeholder="เช่น ปทุมวัน, คลองเตย"
            className="w-full min-h-[48px] px-3 py-2 border rounded-md text-sm focus:ring-2 focus:ring-emerald-500 bg-white"
          />
        </div>
        <div className="flex items-end">
          <button
            type="submit"
            disabled={isLoading}
            className="w-full min-h-[48px] px-4 py-2 bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white font-medium rounded-md transition flex items-center justify-center gap-2"
          >
            <span>🔍</span> ประมวลผลรายงาน
          </button>
        </div>
      </form>

      {/* Error Message */}
      {errorMessage && (
        <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
          {errorMessage}
        </div>
      )}

      {/* KPI Cards */}
      {reportData && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4">
            <span className="text-xs font-semibold text-emerald-700 uppercase">น้ำหนักรวมทั้งสิ้น</span>
            <div className="text-2xl font-black text-emerald-900 mt-1">
              {reportData.grand_total_weight_kg.toLocaleString()} <span className="text-sm font-normal">กก.</span>
            </div>
          </div>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <span className="text-xs font-semibold text-blue-700 uppercase">มูลค่าหมุนเวียนรวม</span>
            <div className="text-2xl font-black text-blue-900 mt-1">
              ฿{reportData.grand_total_amount_thb.toLocaleString()} <span className="text-sm font-normal">บาท</span>
            </div>
          </div>
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
            <span className="text-xs font-semibold text-purple-700 uppercase">รอบเก็บขยะสำเร็จ</span>
            <div className="text-2xl font-black text-purple-900 mt-1">
              {reportData.total_completed_trips.toLocaleString()} <span className="text-sm font-normal">เที่ยว</span>
            </div>
          </div>
        </div>
      )}

      {/* Report Table */}
      <div className="overflow-x-auto border rounded-lg">
        <table className="w-full text-left text-sm text-gray-700">
          <thead className="bg-gray-100 text-gray-700 uppercase font-semibold text-xs border-b">
            <tr>
              <th className="p-3">เขต (District)</th>
              <th className="p-3">แขวง (Subdistrict)</th>
              <th className="p-3">หมวดหมู่วัสดุ</th>
              <th className="p-3 text-right">น้ำหนักรวม (กก.)</th>
              <th className="p-3 text-right">มูลค่ารวม (บาท)</th>
              <th className="p-3 text-center">รอบสำเร็จ (เที่ยว)</th>
              <th className="p-3 text-center">รอบเวลา</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {isLoading ? (
              <tr>
                <td colSpan="7" className="p-6 text-center text-gray-500">กำลังประมวลผลรายงานสถิติ...</td>
              </tr>
            ) : summaryItems.length === 0 ? (
              <tr>
                <td colSpan="7" className="p-6 text-center text-gray-500">ไม่พบสถิติการรับซื้อขยะในรอบเวลานี้</td>
              </tr>
            ) : (
              summaryItems.map((item, idx) => (
                <tr key={`${item.district}-${item.subdistrict}-${item.category_code}-${idx}`} className="hover:bg-gray-50 transition">
                  <td className="p-3 font-semibold text-gray-900">{item.district}</td>
                  <td className="p-3 text-gray-600">{item.subdistrict}</td>
                  <td className="p-3 font-medium text-indigo-700">{item.category_name}</td>
                  <td className="p-3 text-right font-mono font-semibold">{item.total_weight_kg.toLocaleString()}</td>
                  <td className="p-3 text-right font-mono font-semibold text-emerald-600">฿{item.total_amount_thb.toLocaleString()}</td>
                  <td className="p-3 text-center font-mono">{item.completed_trips_count}</td>
                  <td className="p-3 text-center text-xs text-gray-500">{item.period_month}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

