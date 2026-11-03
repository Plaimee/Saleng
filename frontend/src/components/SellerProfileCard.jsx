/**
 * คอมโพเนนต์แสดงและแก้ไขโปรไฟล์ผู้ขาย (SellerProfileCard)
 * รองรับ UC-01, REQ-SEC-002, EV-09, AC-S01-03
 */

import React, { useState } from 'react';
import { accountApi } from '../services/accountApi';

export default function SellerProfileCard({ profile, onProfileUpdated, onLogout }) {
  const [isEditing, setIsEditing] = useState(false);
  const [name, setName] = useState(profile?.display_name || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSave = async () => {
    if (!name.trim()) return;
    setLoading(true);
    setError('');
    try {
      const updated = await accountApi.updateProfile(profile.seller_id, name.trim());
      setIsEditing(false);
      if (onProfileUpdated) onProfileUpdated(updated);
    } catch (err) {
      setError(err.message || 'บันทึกชื่อไม่สำเร็จ');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      data-req="UC-01"
      className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 mb-4"
    >
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 rounded-full bg-emerald-500 text-white flex items-center justify-center font-bold text-lg shadow-sm">
            {profile?.display_name ? profile.display_name.charAt(0) : 'ผ'}
          </div>
          <div>
            {isEditing ? (
              <div className="flex items-center space-x-2">
                <input
                  type="text"
                  data-testid="edit-name-input"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="px-2 py-1 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
                <button
                  type="button"
                  data-testid="save-name-btn"
                  onClick={handleSave}
                  disabled={loading}
                  className="px-3 py-1 bg-emerald-600 text-white text-xs rounded-lg font-medium hover:bg-emerald-700"
                >
                  {loading ? '...' : 'บันทึก'}
                </button>
                <button
                  type="button"
                  onClick={() => setIsEditing(false)}
                  className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-lg"
                >
                  ยกเลิก
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <h3 data-testid="profile-name" className="text-base font-bold text-gray-900">
                  {profile?.display_name || 'ผู้ขาย'}
                </h3>
                <button
                  type="button"
                  data-testid="edit-profile-btn"
                  onClick={() => {
                    setName(profile?.display_name || '');
                    setIsEditing(true);
                  }}
                  className="text-xs text-emerald-600 hover:underline"
                >
                  แก้ไข
                </button>
              </div>
            )}

            <div className="flex items-center space-x-2 mt-1">
              <span
                data-testid="profile-phone-masked"
                className="text-xs font-mono text-gray-600 bg-gray-50 px-2 py-0.5 rounded"
              >
                {profile?.phone_masked || '08X-XXX-XXXX'}
              </span>
              <span className="text-[10px] bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full font-semibold">
                ยืนยันแล้ว
              </span>
            </div>
          </div>
        </div>

        <button
          type="button"
          data-testid="logout-btn"
          onClick={onLogout}
          className="text-xs text-red-500 hover:text-red-700 font-medium px-2 py-1 rounded hover:bg-red-50 transition-colors"
        >
          ออกจากระบบ
        </button>
      </div>

      {error && (
        <div className="mt-2 text-xs text-red-600 bg-red-50 p-2 rounded-lg">
          {error}
        </div>
      )}
    </div>
  );
}

