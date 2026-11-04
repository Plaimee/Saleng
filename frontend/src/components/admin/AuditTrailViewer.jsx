import React, { useState, useEffect, useCallback } from 'react';
import {
  getAuditLogs,
  exportAuditLogs,
  verifyAuditIntegrity,
} from '../../services/adminSecurityComplianceApi';

/**
 * คอมโพเนนต์ตรวจสอบประวัติร่องรอยการใช้งาน (Audit Trail Viewer)
 * รองรับ UC-13, REQ-SEC-001, P-07, D-A04-01, D-A04-05, REQ-UX-001, CC-01, CC-03, CC-05
 * ทัชทาร์เก็ตปุ่มกด >= 48px ทุกปุ่ม
 * กำกับ data-req="UC-13"
 */
export default function AuditTrailViewer({ adminRole = 'ADMIN', onNotify }) {
  const [logs, setLogs] = useState([]);
  const [totalRecords, setTotalRecords] = useState(0);
  const [offset, setOffset] = useState(0);
  const limit = 10;

  const [filterAction, setFilterAction] = useState('');
  const [filterRole, setFilterRole] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [integrityStatus, setIntegrityStatus] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');

  const fetchLogs = useCallback(async (currentOffset = 0) => {
    setIsLoading(true);
    setErrorMessage('');
    try {
      const res = await getAuditLogs(
        {
          action: filterAction || undefined,
          actor_role: filterRole || undefined,
          limit,
          offset: currentOffset,
        },
        { customRole: adminRole }
      );
      setLogs(res.logs || []);
      setTotalRecords(res.total_records || 0);
      setOffset(currentOffset);
    } catch (err) {
      setErrorMessage(err.message || 'ไม่สามารถโหลด Audit Trail ได้');
      if (onNotify) onNotify(err.message, 'error');
    } finally {
      setIsLoading(false);
    }
  }, [filterAction, filterRole, adminRole, onNotify]);

  useEffect(() => {
    fetchLogs(0);
  }, [fetchLogs]);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchLogs(0);
  };

  const handleVerifyIntegrity = async () => {
    setIsLoading(true);
    setErrorMessage('');
    try {
      const res = await verifyAuditIntegrity({ customRole: adminRole });
      setIntegrityStatus(res);
      if (onNotify) {
        onNotify(res.message, res.is_valid ? 'success' : 'error');
      }
    } catch (err) {
      setErrorMessage(err.message || 'เกิดข้อผิดพลาดในการตรวจสอบ Integrity');
      if (onNotify) onNotify(err.message, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleExport = async (format) => {
    try {
      const data = await exportAuditLogs(
        { format, action: filterAction || undefined, actor_role: filterRole || undefined },
        { customRole: adminRole }
      );
      const blob = new Blob([data], { type: format === 'json' ? 'application/json' : 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `audit_logs_${Date.now()}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      if (onNotify) onNotify(`ส่งออกไฟล์ ${format.toUpperCase()} สำเร็จ`, 'success');
    } catch (err) {
      if (onNotify) onNotify(err.message || 'ไม่สามารถส่งออกไฟล์ได้', 'error');
    }
  };

  return (
    <div data-req="UC-13" className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 space-y-4">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b pb-4">
        <div>
          <h2 className="text-xl font-bold text-gray-800 flex items-center gap-2">
            <span>🛡️</span> บันทึกร่องรอยการตรวจสอบ (Audit Trail Viewer)
          </h2>
          <p className="text-sm text-gray-500 mt-1">
            เก็บบันทึกประวัติแบบ Append-only พร้อมการคำนวณแฮช SHA-256 ป้องกันการแก้ไข (REQ-SEC-001)
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={handleVerifyIntegrity}
            disabled={isLoading}
            className="min-h-[48px] min-w-[48px] px-4 py-2 bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 text-white font-medium rounded-lg flex items-center justify-center gap-2 transition disabled:opacity-50"
          >
            <span>🔍</span> ตรวจสอบความสมบูรณ์ (SHA-256)
          </button>
          <button
            type="button"
            onClick={() => handleExport('csv')}
            disabled={isLoading}
            className="min-h-[48px] min-w-[48px] px-3 py-2 bg-emerald-600 hover:bg-emerald-700 active:bg-emerald-800 text-white font-medium rounded-lg flex items-center justify-center gap-1 transition disabled:opacity-50"
          >
            <span>📥</span> ส่งออก CSV
          </button>
          <button
            type="button"
            onClick={() => handleExport('json')}
            disabled={isLoading}
            className="min-h-[48px] min-w-[48px] px-3 py-2 bg-gray-600 hover:bg-gray-700 active:bg-gray-800 text-white font-medium rounded-lg flex items-center justify-center gap-1 transition disabled:opacity-50"
          >
            <span>📥</span> ส่งออก JSON
          </button>
        </div>
      </div>

      {/* Integrity Status Alert */}
      {integrityStatus && (
        <div
          className={`p-4 rounded-lg flex items-center justify-between border ${
            integrityStatus.is_valid
              ? 'bg-green-50 border-green-200 text-green-800'
              : 'bg-red-50 border-red-200 text-red-800'
          }`}
        >
          <div className="flex items-center gap-3">
            <span className="text-2xl">{integrityStatus.is_valid ? '✅' : '⚠️'}</span>
            <div>
              <p className="font-semibold text-base">{integrityStatus.message}</p>
              <p className="text-xs opacity-80">
                ตรวจสอบ {integrityStatus.total_checked} ระเบียน เมื่อ {new Date(integrityStatus.verified_at).toLocaleString('th-TH')}
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={() => setIntegrityStatus(null)}
            className="min-h-[48px] min-w-[48px] text-gray-500 hover:text-gray-700 flex items-center justify-center"
          >
            ✕
          </button>
        </div>
      )}

      {/* Error Alert */}
      {errorMessage && (
        <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
          {errorMessage}
        </div>
      )}

      {/* Filters Form */}
      <form onSubmit={handleSearch} className="grid grid-cols-1 md:grid-cols-3 gap-3 bg-gray-50 p-3 rounded-lg border">
        <div>
          <label className="block text-xs font-semibold text-gray-600 mb-1">กรองตามการกระทำ (Action)</label>
          <input
            type="text"
            value={filterAction}
            onChange={(e) => setFilterAction(e.target.value)}
            placeholder="เช่น KYC_APPROVED, DISPATCH_OVERRIDE"
            className="w-full min-h-[48px] px-3 py-2 border rounded-md text-sm focus:ring-2 focus:ring-indigo-500 bg-white"
          />
        </div>
        <div>
          <label className="block text-xs font-semibold text-gray-600 mb-1">กรองตามบทบาท (Role)</label>
          <select
            value={filterRole}
            onChange={(e) => setFilterRole(e.target.value)}
            className="w-full min-h-[48px] px-3 py-2 border rounded-md text-sm focus:ring-2 focus:ring-indigo-500 bg-white"
          >
            <option value="">ทั้งหมดทุกบทบาท</option>
            <option value="ADMIN">ADMIN (ผู้ดูแลระบบ)</option>
            <option value="AUDITOR">AUDITOR (ผู้ตรวจสอบ)</option>
            <option value="COLLECTOR">COLLECTOR (ซาเล้ง)</option>
            <option value="SELLER">SELLER (ผู้ขาย)</option>
            <option value="SYSTEM">SYSTEM (ระบบอัตโนมัติ)</option>
          </select>
        </div>
        <div className="flex items-end">
          <button
            type="submit"
            disabled={isLoading}
            className="w-full min-h-[48px] px-4 py-2 bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white font-medium rounded-md transition flex items-center justify-center gap-2"
          >
            <span>🔍</span> ค้นหาบันทึก
          </button>
        </div>
      </form>

      {/* Logs Table */}
      <div className="overflow-x-auto border rounded-lg">
        <table className="w-full text-left text-sm text-gray-700">
          <thead className="bg-gray-100 text-gray-700 uppercase font-semibold text-xs border-b">
            <tr>
              <th className="p-3">เวลา (Timestamp)</th>
              <th className="p-3">ผู้กระทำ (Actor)</th>
              <th className="p-3">บทบาท</th>
              <th className="p-3">การกระทำ (Action)</th>
              <th className="p-3">รายละเอียด (Details)</th>
              <th className="p-3">Integrity Hash</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {isLoading ? (
              <tr>
                <td colSpan="6" className="p-6 text-center text-gray-500">กำลังโหลดบันทึก Audit Trail...</td>
              </tr>
            ) : logs.length === 0 ? (
              <tr>
                <td colSpan="6" className="p-6 text-center text-gray-500">ไม่พบบันทึกประวัติตามเงื่อนไขที่ค้นหา</td>
              </tr>
            ) : (
              logs.map((log) => (
                <tr key={log.log_id} className="hover:bg-gray-50 transition">
                  <td className="p-3 whitespace-nowrap text-xs text-gray-600">
                    {new Date(log.timestamp).toLocaleString('th-TH')}
                  </td>
                  <td className="p-3 font-mono text-xs text-gray-900 font-semibold">{log.actor_id || '-'}</td>
                  <td className="p-3">
                    <span className="px-2 py-1 text-xs rounded-full font-medium bg-gray-200 text-gray-800">
                      {log.actor_role}
                    </span>
                  </td>
                  <td className="p-3 font-semibold text-indigo-700 text-xs">{log.action}</td>
                  <td className="p-3 text-xs max-w-xs truncate" title={JSON.stringify(log.details)}>
                    {JSON.stringify(log.details)}
                  </td>
                  <td className="p-3 font-mono text-xs text-gray-500 truncate max-w-[120px]" title={log.log_hash}>
                    {log.log_hash ? `${log.log_hash.substring(0, 10)}...` : '-'}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2 text-sm text-gray-600">
        <div>
          แสดง {logs.length > 0 ? offset + 1 : 0} ถึง {Math.min(offset + limit, totalRecords)} จากทั้งหมด {totalRecords} ระเบียน
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            disabled={offset === 0 || isLoading}
            onClick={() => fetchLogs(Math.max(0, offset - limit))}
            className="min-h-[48px] min-w-[48px] px-4 py-2 border rounded-md hover:bg-gray-100 disabled:opacity-40 disabled:hover:bg-white transition"
          >
            ◀ ย้อนกลับ
          </button>
          <button
            type="button"
            disabled={offset + limit >= totalRecords || isLoading}
            onClick={() => fetchLogs(offset + limit)}
            className="min-h-[48px] min-w-[48px] px-4 py-2 border rounded-md hover:bg-gray-100 disabled:opacity-40 disabled:hover:bg-white transition"
          >
            ถัดไป ▶
          </button>
        </div>
      </div>
    </div>
  );
}

