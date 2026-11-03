/**
 * คอมโพเนนต์แสดงข้อมูลโปรไฟล์และสถานะของซาเล้ง (CollectorProfileCard)
 * รองรับ UC-01, REQ-UX-001, REQ-SEC-002, CC-01, AC-B01-01, P-01
 */

import React, { useState } from 'react';
import { collectorAccountApi } from '../services/collectorAccountApi';

export default function CollectorProfileCard({ profile, onProfileUpdated, onLogout }) {
  const [isEditing, setIsEditing] = useState(false);
  const [displayName, setDisplayName] = useState(profile?.display_name || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  if (!profile) return null;

  const handleUpdateName = async (e) => {
    e.preventDefault();
    if (!displayName.trim()) {
      setError('กรุณาระบุชื่อ');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const updated = await collectorAccountApi.updateProfile(profile.saleng_id, displayName.trim());
      setIsEditing(false);
      if (onProfileUpdated) onProfileUpdated(updated);
    } catch (err) {
      setError(err.message || 'บันทึกชื่อไม่สำเร็จ');
    } finally {
      setLoading(false);
    }
  };

  const getKycBadge = () => {
    switch (profile.kyc_status) {
      case 'VERIFIED':
        return (
          <span
            data-testid="kyc-badge-verified"
            className="px-2.5 py-1 bg-green-100 text-green-800 text-xs font-semibold rounded-full border border-green-200"
          >
            ✓ ยืนยันตัวตนแล้ว
          </span>
        );
      case 'PENDING_REVIEW':
        return (
          <span
            data-testid="kyc-badge-pending"
            className="px-2.5 py-1 bg-amber-100 text-amber-800 text-xs font-semibold rounded-full border border-amber-200"
          >
            ⏳ รอตรวจสอบ KYC
          </span>
        );
      case 'REJECTED':
        return (
          <span
            data-testid="kyc-badge-rejected"
            className="px-2.5 py-1 bg-red-100 text-red-800 text-xs font-semibold rounded-full border border-red-200"
          >
            ✕ KYC ไม่ผ่าน
          </span>
        );
      default:
        return (
          <span
            data-testid="kyc-badge-unverified"
            className="px-2.5 py-1 bg-gray-100 text-gray-700 text-xs font-semibold rounded-full border border-gray-200"
          >
            ⚠️ ยังไม่ยืนยัน KYC
          </span>
        );
    }
  };

  return (
    <div
      data-req="UC-01"
      className="w-full max-w-md mx-auto bg-white rounded-2xl shadow-md border border-gray-100 p-5 my-3"
    >
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-3.5">
          <div className="w-14 h-14 rounded-full bg-emerald-100 border-2 border-emerald-500 overflow-hidden flex items-center justify-center text-emerald-800 font-bold text-xl shadow-inner">
            {profile.avatar_url ? (
              <img src={profile.avatar_url} alt={profile.display_name} className="w-full h-full object-cover" />
            ) : (
              <span>🛵</span>
            )}
          </div>
          <div>
            {!isEditing ? (
              <div className="flex items-center space-x-2">
                <h3 data-testid="collector-display-name" className="text-lg font-bold text-gray-900">
                  {profile.display_name}
                </h3>
                <button
                  type="button"
                  data-testid="edit-name-btn"
                  onClick={() => setIsEditing(true)}
                  className="text-gray-400 hover:text-emerald-600 min-h-[36px] min-w-[36px] flex items-center justify-center p-1 rounded-lg"
                  title="แก้ไขชื่อ"
                >
                  ✏️
                </button>
              </div>
            ) : (
              <form onSubmit={handleUpdateName} className="flex items-center space-x-1.5 mt-1">
                <input
                  type="text"
                  data-testid="edit-name-input"
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  className="px-2 py-1 text-sm border rounded-lg focus:ring-1 focus:ring-emerald-500 w-36"
                  autoFocus
                />
                <button
                  type="submit"
                  data-testid="save-name-btn"
                  disabled={loading}
                  className="px-2 py-1 bg-emerald-600 text-white text-xs rounded-lg min-h-[32px]"
                >
                  บันทึก
                </button>
                <button
                  type="button"
                  onClick={() => setIsEditing(false)}
                  className="px-2 py-1 bg-gray-200 text-gray-700 text-xs rounded-lg min-h-[32px]"
                >
                  ยกเลิก
                </button>
              </form>
            )}

            <p data-testid="collector-phone-masked" className="text-sm text-gray-500">
              เบอร์โทร: <span className="font-mono">{profile.phone_masked}</span>
            </p>
          </div>
        </div>

        <div>{getKycBadge()}</div>
      </div>

      {error && <p className="text-xs text-red-600 mt-2">{error}</p>}

      {/* สถิติการรับงาน */}
      <div className="grid grid-cols-2 gap-3 mt-4 pt-3 border-t border-gray-100 text-center">
        <div className="bg-emerald-50/60 p-2.5 rounded-xl">
          <p className="text-xs text-gray-500">คะแนนความพึงพอใจ</p>
          <p data-testid="collector-rating" className="text-base font-bold text-emerald-800">
            ★ {Number(profile.rating || 5.0).toFixed(1)}
          </p>
        </div>
        <div className="bg-blue-50/60 p-2.5 rounded-xl">
          <p className="text-xs text-gray-500">งานที่สำเร็จแล้ว</p>
          <p data-testid="collector-jobs-count" className="text-base font-bold text-blue-900">
            {profile.completed_jobs_count || 0} งาน
          </p>
        </div>
      </div>

      {/* ปุ่มออกจากระบบ */}
      {onLogout && (
        <div className="mt-4 pt-2">
          <button
            type="button"
            data-testid="logout-btn"
            onClick={onLogout}
            className="w-full min-h-[48px] bg-gray-50 hover:bg-gray-100 border border-gray-200 text-gray-700 font-medium rounded-xl text-sm transition flex items-center justify-center space-x-2"
          >
            <span>🚪</span>
            <span>ออกจากระบบ</span>
          </button>
        </div>
      )}
    </div>
  );
}

