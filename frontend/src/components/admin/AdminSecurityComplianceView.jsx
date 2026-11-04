import React, { useState } from 'react';
import AuditTrailViewer from './AuditTrailViewer';
import CommunityWasteReportView from './CommunityWasteReportView';
import PdpaRetentionPanel from './PdpaRetentionPanel';

/**
 * หน้าจอหลักศูนย์ควบคุมความปลอดภัย ตรวจสอบร่องรอย และ PDPA (Admin Feature 04)
 * รองรับ UC-13, REQ-SEC-001, REQ-SEC-002, CT-01, P-07, D-A04-01..06, CC-01, CC-03, CC-05, REQ-UX-001
 * ทัชทาร์เก็ตปุ่มกด >= 48px ทุกปุ่ม
 * กำกับ data-req="UC-13"
 */
export default function AdminSecurityComplianceView() {
  const [activeTab, setActiveTab] = useState('audit'); // 'audit' | 'waste_report' | 'pdpa'
  const [adminRole, setAdminRole] = useState('ADMIN'); // 'ADMIN' | 'AUDITOR' | 'DPO' | 'SUPPORT'
  const [notification, setNotification] = useState(null); // { message, type }

  const notify = (message, type = 'info') => {
    setNotification({ message, type });
    setTimeout(() => {
      setNotification((curr) => (curr?.message === message ? null : curr));
    }, 4000);
  };

  return (
    <div
      data-testid="admin-security-compliance-view"
      data-req="UC-13"
      className="max-w-7xl mx-auto p-4 sm:p-6 space-y-6"
    >
      {/* Online-only Banner (CC-05) */}
      <div className="bg-blue-50 border border-blue-200 text-blue-900 px-4 py-2.5 rounded-lg flex items-center justify-between text-xs sm:text-sm">
        <div className="flex items-center gap-2">
          <span>🌐</span>
          <span>
            <strong>โหมดออนไลน์ (Online-only):</strong> ระบบความปลอดภัยและบันทึกร่องรอยตรวจสอบทำงานแบบเชื่อมต่อเซิร์ฟเวอร์โดยตรง เพื่อความถูกต้องและเป็นหนึ่งเดียวของข้อมูล (CC-05)
          </span>
        </div>
        <span className="px-2 py-0.5 bg-blue-200 text-blue-800 rounded font-semibold text-xs">
          ONLINE
        </span>
      </div>

      {/* Notification Toast */}
      {notification && (
        <div
          className={`p-4 rounded-lg flex items-center justify-between text-sm border shadow-sm ${
            notification.type === 'error'
              ? 'bg-red-50 border-red-200 text-red-800'
              : notification.type === 'success'
              ? 'bg-green-50 border-green-200 text-green-800'
              : 'bg-indigo-50 border-indigo-200 text-indigo-800'
          }`}
        >
          <div className="flex items-center gap-2">
            <span>{notification.type === 'error' ? '⚠️' : 'ℹ️'}</span>
            <span>{notification.message}</span>
          </div>
          <button
            type="button"
            onClick={() => setNotification(null)}
            className="min-h-[48px] min-w-[48px] text-gray-400 hover:text-gray-600 flex items-center justify-center font-bold"
          >
            ✕
          </button>
        </div>
      )}

      {/* Header & Role Switcher */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-5 rounded-lg shadow-sm border">
        <div>
          <h1 className="text-2xl font-black text-gray-900 flex items-center gap-2">
            <span>🛡️</span> ศูนย์ควบคุมความปลอดภัยและตรวจสอบการปฏิบัติตามกฎหมาย
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            (Admin 04: Audit Trail, Community Waste Reporting & PDPA Compliance — UC-13)
          </p>
        </div>
        <div className="flex items-center gap-2 bg-gray-50 p-2 rounded-lg border">
          <label className="text-xs font-semibold text-gray-600 whitespace-nowrap">บทบาทผู้ใช้งาน:</label>
          <select
            value={adminRole}
            onChange={(e) => setAdminRole(e.target.value)}
            className="min-h-[48px] px-3 py-1.5 border rounded bg-white text-sm font-bold text-indigo-700 focus:ring-2 focus:ring-indigo-500"
          >
            <option value="ADMIN">ADMIN (สิทธิ์เต็มทุกส่วน)</option>
            <option value="AUDITOR">AUDITOR (ตรวจ Audit & รายงาน)</option>
            <option value="DPO">DPO (คุ้มครองข้อมูลส่วนบุคคล & Purge)</option>
            <option value="SUPPORT">SUPPORT (ช่วยเหลือทั่วไป - ถูกจำกัดสิทธิ์)</option>
          </select>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex border-b border-gray-200 gap-2">
        <button
          type="button"
          onClick={() => setActiveTab('audit')}
          className={`min-h-[48px] min-w-[48px] px-5 py-2.5 font-bold text-sm rounded-t-lg transition flex items-center gap-2 ${
            activeTab === 'audit'
              ? 'border-b-2 border-indigo-600 text-indigo-700 bg-white'
              : 'text-gray-500 hover:text-gray-800 hover:bg-gray-50'
          }`}
        >
          <span>🛡️</span> ร่องรอยตรวจสอบ (Audit Trail)
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('waste_report')}
          className={`min-h-[48px] min-w-[48px] px-5 py-2.5 font-bold text-sm rounded-t-lg transition flex items-center gap-2 ${
            activeTab === 'waste_report'
              ? 'border-b-2 border-indigo-600 text-indigo-700 bg-white'
              : 'text-gray-500 hover:text-gray-800 hover:bg-gray-50'
          }`}
        >
          <span>📊</span> รายงานสถิติขยะชุมชน (No PII)
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('pdpa')}
          className={`min-h-[48px] min-w-[48px] px-5 py-2.5 font-bold text-sm rounded-t-lg transition flex items-center gap-2 ${
            activeTab === 'pdpa'
              ? 'border-b-2 border-indigo-600 text-indigo-700 bg-white'
              : 'text-gray-500 hover:text-gray-800 hover:bg-gray-50'
          }`}
        >
          <span>🔐</span> การปฏิบัติตาม PDPA (Data Retention)
        </button>
      </div>

      {/* Tab Panels */}
      <div>
        {activeTab === 'audit' && (
          <AuditTrailViewer adminRole={adminRole} onNotify={notify} />
        )}
        {activeTab === 'waste_report' && (
          <CommunityWasteReportView adminRole={adminRole} onNotify={notify} />
        )}
        {activeTab === 'pdpa' && (
          <PdpaRetentionPanel adminRole={adminRole} onNotify={notify} />
        )}
      </div>
    </div>
  );
}
