/**
 * แผงควบคุมระบบบัญชีและการยืนยันตัวตนซาเล้ง (CollectorAccountPanel)
 * รวมระบบล็อกอิน, โปรไฟล์, ยานพาหนะ, KYC และ Job Claim Gate ตามกฎ D-00-01
 * รองรับ UC-01, REQ-UX-001, CC-01, CC-05, REQ-OP-001, D-00-01, AC-B01-01..05, P-01..P-06
 */

import React, { useState, useEffect } from 'react';
import { collectorAccountApi } from '../services/collectorAccountApi';
import CollectorPhoneLoginForm from './CollectorPhoneLoginForm';
import CollectorProfileCard from './CollectorProfileCard';
import VehicleConfigCard from './VehicleConfigCard';
import KycStatusBanner from './KycStatusBanner';
import KycSubmissionModal from './KycSubmissionModal';

export default function CollectorAccountPanel() {
  const [session, setSession] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isKycModalOpen, setIsKycModalOpen] = useState(false);
  const [gateModalInfo, setGateModalInfo] = useState(null); // { open: bool, allowed: bool, message: str }
  const [testActionMsg, setTestActionMsg] = useState('');

  // ตรวจสอบเซสชันที่บันทึกไว้เมื่อโหลดคอมโพเนนต์ (CC-05, REQ-OP-001)
  useEffect(() => {
    const stored = collectorAccountApi.getStoredSession();
    if (stored && stored.saleng_id) {
      setSession(stored);
      loadProfile(stored.saleng_id);
    } else {
      setLoading(false);
    }
  }, []);

  const loadProfile = async (salengId) => {
    setLoading(true);
    try {
      const data = await collectorAccountApi.getProfile(salengId);
      setProfile(data);
    } catch (err) {
      console.error('Failed to load collector profile:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLoginSuccess = (authData) => {
    setSession(authData);
    setProfile(authData);
    loadProfile(authData.saleng_id);
  };

  const handleLogout = async () => {
    await collectorAccountApi.logout();
    setSession(null);
    setProfile(null);
    setGateModalInfo(null);
  };

  const handleTestClaimJob = async () => {
    if (!profile) return;
    setTestActionMsg('');
    try {
      const res = await collectorAccountApi.checkJobClaimGate(profile.saleng_id);
      if (res.can_claim_job) {
        setGateModalInfo({
          open: true,
          allowed: true,
          message: 'ผ่านการตรวจสอบสิทธิ์เรียบร้อย สามารถกดรับงานในเส้นทางได้ทันที',
        });
      } else {
        setGateModalInfo({
          open: true,
          allowed: false,
          message: res.error_detail || 'ท่านยังไม่ผ่านการยืนยันตัวตน ไม่สามารถรับงานได้ตามกฎ D-00-01',
        });
      }
    } catch (err) {
      setGateModalInfo({
        open: true,
        allowed: false,
        message: err.message || 'ระบบบล็อกการรับงาน (403 Forbidden)',
      });
    }
  };

  const handleMockApprove = async () => {
    if (!profile) return;
    try {
      const updated = await collectorAccountApi.mockApproveKyc(profile.saleng_id);
      setProfile((prev) => ({ ...prev, ...updated }));
      setTestActionMsg('จำลองการอนุมัติ KYC (VERIFIED) สำเร็จ');
      loadProfile(profile.saleng_id);
    } catch (err) {
      setTestActionMsg(`Error: ${err.message}`);
    }
  };

  const handleMockReject = async () => {
    if (!profile) return;
    try {
      const updated = await collectorAccountApi.mockRejectKyc(
        profile.saleng_id,
        'รูปถ่ายบัตรประชาชนไม่ชัดเจนและสะท้อนแสง'
      );
      setProfile((prev) => ({ ...prev, ...updated }));
      setTestActionMsg('จำลองการปฏิเสธ KYC (REJECTED) สำเร็จ');
      loadProfile(profile.saleng_id);
    } catch (err) {
      setTestActionMsg(`Error: ${err.message}`);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-12 text-emerald-700">
        <span className="animate-spin text-3xl mr-3">⏳</span>
        <span className="font-medium">กำลังโหลดข้อมูลบัญชีซาเล้ง...</span>
      </div>
    );
  }

  // หากยังไม่ได้เข้าสู่ระบบ
  if (!session || !profile) {
    return (
      <div className="p-4">
        <CollectorPhoneLoginForm onLoginSuccess={handleLoginSuccess} />
      </div>
    );
  }

  return (
    <div data-req="UC-01" className="max-w-md mx-auto p-4 space-y-4">
      {/* 1. ข้อมูลส่วนตัวและป้ายสถานะ */}
      <CollectorProfileCard
        profile={profile}
        onProfileUpdated={(updated) => setProfile(updated)}
        onLogout={handleLogout}
      />

      {/* 2. แบนเนอร์แจ้งสถานะ KYC */}
      <KycStatusBanner
        profile={profile}
        onOpenKycModal={() => setIsKycModalOpen(true)}
      />

      {/* 3. การตั้งค่ายานพาหนะและความจุ (BR-03) */}
      <VehicleConfigCard
        profile={profile}
        onVehicleUpdated={(updated) => setProfile(updated)}
      />

      {/* 4. ปุ่มทดสอบการรับงาน (Unverified Gate D-00-01) */}
      <div className="bg-white rounded-2xl border border-gray-100 p-4 shadow-sm">
        <h4 className="text-sm font-bold text-gray-900 mb-1">ทดสอบการรับงาน (D-00-01 Gate Check)</h4>
        <p className="text-xs text-gray-500 mb-3">
          ทดสอบการทำงานของระบบความปลอดภัย บล็อกผู้ที่ยังไม่ผ่าน KYC
        </p>
        <button
          type="button"
          data-testid="test-claim-job-btn"
          onClick={handleTestClaimJob}
          className="w-full min-h-[48px] bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-xl text-sm transition shadow-sm flex items-center justify-center space-x-2"
        >
          <span>🎯</span>
          <span>ทดสอบกดรับงาน (Claim Job)</span>
        </button>
      </div>

      {/* 5. กล่องเครื่องมือสำหรับทดสอบ (Q-06 Mock Helpers) */}
      <div className="bg-slate-50 border border-dashed border-slate-300 rounded-2xl p-4 text-xs text-slate-700">
        <div className="flex justify-between items-center mb-2">
          <span className="font-bold text-slate-900">🛠️ เครื่องมือทดสอบ KYC (Q-06)</span>
          <span className="bg-slate-200 text-slate-600 px-2 py-0.5 rounded text-[10px]">Dev / Test</span>
        </div>
        {testActionMsg && (
          <p className="mb-2 p-1.5 bg-white border rounded text-emerald-700 font-medium">{testActionMsg}</p>
        )}
        <div className="grid grid-cols-2 gap-2">
          <button
            type="button"
            data-testid="mock-approve-btn"
            onClick={handleMockApprove}
            className="min-h-[40px] bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition"
          >
            จำลองอนุมัติ (VERIFIED)
          </button>
          <button
            type="button"
            data-testid="mock-reject-btn"
            onClick={handleMockReject}
            className="min-h-[40px] bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition"
          >
            จำลองปฏิเสธ (REJECTED)
          </button>
        </div>
      </div>

      {/* Pop-up Modal ยื่นเอกสาร KYC */}
      <KycSubmissionModal
        salengId={profile.saleng_id}
        isOpen={isKycModalOpen}
        onClose={() => setIsKycModalOpen(false)}
        onKycSubmitted={(res) => {
          setProfile((prev) => ({ ...prev, ...res, kyc_status: 'PENDING_REVIEW' }));
          loadProfile(profile.saleng_id);
        }}
      />

      {/* Gate Modal แจ้งเตือนสิทธิ์การรับงาน (D-00-01) */}
      {gateModalInfo && gateModalInfo.open && (
        <div
          data-testid="unverified-gate-modal"
          className="fixed inset-0 z-50 bg-black/60 flex items-center justify-center p-4"
        >
          <div className="bg-white rounded-3xl max-w-sm w-full p-6 text-center shadow-2xl">
            <div className={`w-16 h-16 rounded-full mx-auto flex items-center justify-center text-3xl mb-4 ${
              gateModalInfo.allowed ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'
            }`}>
              {gateModalInfo.allowed ? '✓' : '🚫'}
            </div>
            <h3 className="text-lg font-bold text-gray-900 mb-2">
              {gateModalInfo.allowed ? 'สามารถรับงานได้' : 'ไม่สามารถรับงานได้'}
            </h3>
            <p className="text-xs text-gray-600 mb-5 leading-relaxed">
              {gateModalInfo.message}
            </p>
            <div className="space-y-2">
              {!gateModalInfo.allowed && (
                <button
                  type="button"
                  data-testid="modal-goto-kyc-btn"
                  onClick={() => {
                    setGateModalInfo(null);
                    setIsKycModalOpen(true);
                  }}
                  className="w-full min-h-[48px] bg-emerald-600 hover:bg-emerald-700 text-white font-medium rounded-xl text-sm transition"
                >
                  ยื่นเอกสารยืนยันตัวตนเลย
                </button>
              )}
              <button
                type="button"
                data-testid="close-gate-modal-btn"
                onClick={() => setGateModalInfo(null)}
                className="w-full min-h-[44px] bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium rounded-xl text-sm transition"
              >
                ปิดหน้าต่าง
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

