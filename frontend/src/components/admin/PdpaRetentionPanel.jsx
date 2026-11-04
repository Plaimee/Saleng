import React, { useState, useEffect, useCallback } from 'react';
import {
  getPdpaRetentionStatus,
  purgeExpiredPdpaData,
} from '../../services/adminSecurityComplianceApi';

/**
 * แผงควบคุมการจัดเก็บและทำลายข้อมูลตามกฎหมาย PDPA (PDPA Retention & Purge Panel)
 * รองรับ UC-13, REQ-SEC-002, CT-01, D-A04-04, REQ-UX-001, CC-01, CC-03, CC-05
 * ทัชทาร์เก็ตปุ่มกด >= 48px ทุกปุ่ม
 * กำกับ data-req="UC-13"
 */
export default function PdpaRetentionPanel({ adminRole = 'DPO', onNotify }) {
  const [retentionStatus, setRetentionStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isPurging, setIsPurging] = useState(false);
  const [confirmPurge, setConfirmPurge] = useState(false);
  const [purgeResult, setPurgeResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');

  const fetchRetentionStatus = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage('');
    try {
      const res = await getPdpaRetentionStatus({ customRole: adminRole });
      setRetentionStatus(res);
    } catch (err) {
      setErrorMessage(err.message || 'ไม่สามารถโหลดสถานะ PDPA Retention ได้');
      if (onNotify) onNotify(err.message, 'error');
    } finally {
      setIsLoading(false);
    }
  }, [adminRole, onNotify]);

  useEffect(() => {
    fetchRetentionStatus();
  }, [fetchRetentionStatus]);

  const handleExecutePurge = async () => {
    if (!confirmPurge) {
      if (onNotify) onNotify('กรุณาทำเครื่องหมายยืนยันก่อนสั่งล้างข้อมูล', 'error');
      return;
    }

    setIsPurging(true);
    setErrorMessage('');
    try {
      const res = await purgeExpiredPdpaData(
        { admin_id: 'dpo-compliance-01', confirm_purge: true },
        { customRole: adminRole }
      );
      setPurgeResult(res);
      setConfirmPurge(false);
      if (onNotify) {
        onNotify(res.message || 'ล้างข้อมูลและ Mask ข้อมูลเรียบร้อยแล้ว', 'success');
      }
      // รีเฟรชสถานะหลัง Purge
      await fetchRetentionStatus();
    } catch (err) {
      setErrorMessage(err.message || 'เกิดข้อผิดพลาดในการล้างข้อมูล');
      if (onNotify) onNotify(err.message, 'error');
    } finally {
      setIsPurging(false);
    }
  };

  const expiredGps = retentionStatus?.expired_gps_coordinates_count || 0;
  const unmaskedOrders = retentionStatus?.unmasked_completed_orders_count || 0;
  const hasExpiredData = expiredGps > 0 || unmaskedOrders > 0;

  return (
    <div data-req="UC-13" className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 space-y-6">
      {/* Header */}
      <div className="border-b pb-4">
        <div className="flex items-center gap-2">
          <h2 className="text-xl font-bold text-gray-800">
            🔐 การปฏิบัติตามกฎหมาย PDPA และการทำลายข้อมูล (Data Retention & Purge)
          </h2>
          <span className="px-2 py-1 text-xs rounded-full font-bold bg-indigo-100 text-indigo-800 border border-indigo-300">
            CT-01 / REQ-SEC-002
          </span>
        </div>
        <p className="text-sm text-gray-500 mt-1">
          ควบคุมการเก็บพิกัด GPS ซาเล้งไม่เกิน 90 วัน และ Mask ข้อมูลที่อยู่ผู้ขายหลังจบงานเกิน 24 ชม. ถาวร
        </p>
      </div>

      {/* Error Message */}
      {errorMessage && (
        <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
          {errorMessage}
        </div>
      )}

      {/* Retention Policy Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Card 1: GPS Retention */}
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-bold text-amber-900 flex items-center gap-1">
              <span>📍</span> พิกัด GPS ซาเล้ง (Collector GPS)
            </span>
            <span className="text-xs px-2 py-0.5 rounded bg-amber-200 text-amber-900 font-semibold">
              เกณฑ์ไม่เกิน 90 วัน
            </span>
          </div>
          <p className="text-xs text-amber-800">
            เก็บประวัติเส้นทางเพื่อความปลอดภัยและคำนวณเส้นทาง เมื่อเกิน 90 วันจะถูกทำลายถาวร
          </p>
          <div className="pt-2 flex items-baseline justify-between border-t border-amber-200">
            <span className="text-xs text-amber-800">พิกัดที่ครบกำหนดต้องทำลาย:</span>
            <span className="text-2xl font-black text-amber-900 font-mono">
              {expiredGps} <span className="text-xs font-normal">จุด</span>
            </span>
          </div>
        </div>

        {/* Card 2: Seller Address Masking */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-bold text-blue-900 flex items-center gap-1">
              <span>🏠</span> ที่อยู่บ้านเลขที่ผู้ขาย (Seller Address)
            </span>
            <span className="text-xs px-2 py-0.5 rounded bg-blue-200 text-blue-900 font-semibold">
              Mask หลังจบงาน 24 ชม.
            </span>
          </div>
          <p className="text-xs text-blue-800">
            เปิดเผยบ้านเลขที่เฉพาะขณะเดินทางรับซื้อ และคืนสถานะ Masked ถาวรเมื่อจบงานเกิน 24 ชม.
          </p>
          <div className="pt-2 flex items-baseline justify-between border-t border-blue-200">
            <span className="text-xs text-blue-800">รายการที่รอ Mask ถาวร:</span>
            <span className="text-2xl font-black text-blue-900 font-mono">
              {unmaskedOrders} <span className="text-xs font-normal">คำขอ</span>
            </span>
          </div>
        </div>
      </div>

      {/* Purge Success Result */}
      {purgeResult && (
        <div className="p-4 bg-green-50 border border-green-200 text-green-900 rounded-lg space-y-1">
          <div className="flex items-center gap-2 font-bold text-base">
            <span>✅</span> {purgeResult.message}
          </div>
          <p className="text-xs text-green-700">
            ล้างพิกัด GPS: {purgeResult.purged_gps_points_count} จุด | Mask ที่อยู่: {purgeResult.masked_orders_count} คำขอ | ดำเนินการโดย: {purgeResult.purged_by}
          </p>
        </div>
      )}

      {/* Purge Action Control */}
      <div className="bg-gray-50 border rounded-lg p-5 space-y-4">
        <h3 className="text-base font-bold text-gray-800 flex items-center gap-2">
          <span>⚙️</span> ดำเนินการล้างและทำลายข้อมูลหมดอายุ (Execute Purge Job)
        </h3>
        <p className="text-xs text-gray-600">
          ระบบจะบันทึกประวัติกิจกรรมนี้ลงใน Audit Trail เพื่อเป็นหลักฐานต่อคณะกรรมการคุ้มครองข้อมูลส่วนบุคคล (สคส.)
        </p>

        <label className="flex items-center gap-3 cursor-pointer select-none">
          <input
            type="checkbox"
            checked={confirmPurge}
            onChange={(e) => setConfirmPurge(e.target.checked)}
            className="w-5 h-5 text-indigo-600 rounded border-gray-300 focus:ring-indigo-500"
          />
          <span className="text-sm font-medium text-gray-700">
            ข้าพเจ้ายืนยันความประสงค์ในการสั่งล้างพิกัด GPS ที่เกิน 90 วัน และ Mask ข้อมูลที่อยู่งานเก่าถาวร
          </span>
        </label>

        <div>
          <button
            type="button"
            onClick={handleExecutePurge}
            disabled={!confirmPurge || isPurging || isLoading}
            className="min-h-[48px] min-w-[48px] px-6 py-2.5 bg-red-600 hover:bg-red-700 active:bg-red-800 text-white font-bold rounded-lg flex items-center justify-center gap-2 transition disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <span>🗑️</span> {isPurging ? 'กำลังประมวลผลการล้างข้อมูล...' : 'ดำเนินการล้างข้อมูลตามนโยบาย PDPA ทันที'}
          </button>
        </div>
      </div>
    </div>
  );
}

