/**
 * ป๊อปอัปกรอกเอกสารยืนยันตัวตน Thai-ID/DBD-ID (KycSubmissionModal)
 * รองรับ SC-04, D-00-01, REQ-UX-001, CC-01, AC-B01-03, Q-02, P-03
 */

import React, { useState } from 'react';
import { collectorAccountApi } from '../services/collectorAccountApi';

export default function KycSubmissionModal({ salengId, isOpen, onClose, onKycSubmitted }) {
  const [idCardNo, setIdCardNo] = useState('');
  const [fullName, setFullName] = useState('');
  const [idCardPhotoUrl, setIdCardPhotoUrl] = useState('https://storage.saleng.app/mock-kyc/id_card.jpg');
  const [selfiePhotoUrl, setSelfiePhotoUrl] = useState('https://storage.saleng.app/mock-kyc/selfie.jpg');
  const [vehiclePhotoUrl, setVehiclePhotoUrl] = useState('https://storage.saleng.app/mock-kyc/vehicle.jpg');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    const cleanId = idCardNo.replace(/\D/g, '');
    if (cleanId.length !== 13) {
      setError('กรุณากรอกเลขบัตรประชาชนให้ครบ 13 หลัก');
      return;
    }
    if (!fullName.trim()) {
      setError('กรุณาระบุชื่อ-นามสกุลจริงตามบัตรประชาชน');
      return;
    }

    setLoading(true);
    try {
      const res = await collectorAccountApi.submitKyc(salengId, {
        id_card_no: cleanId,
        full_name: fullName.trim(),
        id_card_photo_url: idCardPhotoUrl,
        selfie_photo_url: selfiePhotoUrl,
        vehicle_photo_url: vehiclePhotoUrl || null,
      });
      if (onKycSubmitted) onKycSubmitted(res);
      onClose();
    } catch (err) {
      setError(err.message || 'ส่งเอกสารยืนยันตัวตนไม่สำเร็จ');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      data-req="SC-04"
      className="fixed inset-0 z-50 bg-black/60 flex items-center justify-center p-4 overflow-y-auto"
    >
      <div className="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl border border-gray-100 my-8">
        <div className="flex justify-between items-center mb-4 pb-3 border-b border-gray-100">
          <div className="flex items-center space-x-2">
            <span className="text-2xl">🪪</span>
            <h3 className="text-lg font-bold text-gray-900">ยื่นเอกสารยืนยันตัวตน (KYC)</h3>
          </div>
          <button
            type="button"
            data-testid="close-modal-btn"
            onClick={onClose}
            className="w-10 h-10 flex items-center justify-center text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100 text-lg"
          >
            ✕
          </button>
        </div>

        {error && (
          <div data-testid="kyc-modal-error" className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl flex items-center">
            <span className="mr-1.5">⚠️</span>
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4 text-sm">
          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">
              เลขประจำตัวประชาชน (13 หลัก) *
            </label>
            <input
              type="text"
              data-testid="id-card-input"
              value={idCardNo}
              onChange={(e) => setIdCardNo(e.target.value)}
              placeholder="1100701234561"
              maxLength={17}
              className="w-full h-12 px-3.5 rounded-xl border border-gray-300 focus:ring-2 focus:ring-emerald-500 font-mono tracking-wider"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">
              ชื่อ-นามสกุลจริง (ตามบัตรประชาชน) *
            </label>
            <input
              type="text"
              data-testid="full-name-input"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="สมชาย ใจดี"
              className="w-full h-12 px-3.5 rounded-xl border border-gray-300 focus:ring-2 focus:ring-emerald-500"
              required
            />
          </div>

          {/* อัปโหลดภาพ 4 จุด (Q-02) */}
          <div className="space-y-3 pt-2">
            <p className="text-xs font-semibold text-gray-700">รูปถ่ายหลักฐานยืนยันตัวตน (Q-02)</p>

            <div>
              <label className="block text-xs text-gray-500 mb-1">1. ภาพถ่ายหน้าบัตรประชาชน *</label>
              <input
                type="text"
                data-testid="id-card-photo-input"
                value={idCardPhotoUrl}
                onChange={(e) => setIdCardPhotoUrl(e.target.value)}
                className="w-full h-10 px-3 rounded-lg border border-gray-200 text-xs text-gray-600 bg-gray-50 font-mono"
                required
              />
            </div>

            <div>
              <label className="block text-xs text-gray-500 mb-1">2. ภาพถ่ายหน้าตรงคู่กับบัตรประชาชน (Selfie) *</label>
              <input
                type="text"
                data-testid="selfie-photo-input"
                value={selfiePhotoUrl}
                onChange={(e) => setSelfiePhotoUrl(e.target.value)}
                className="w-full h-10 px-3 rounded-lg border border-gray-200 text-xs text-gray-600 bg-gray-50 font-mono"
                required
              />
            </div>

            <div>
              <label className="block text-xs text-gray-500 mb-1">3. ภาพถ่ายยานพาหนะพร้อมป้ายทะเบียน (ถ้ามี)</label>
              <input
                type="text"
                data-testid="vehicle-photo-input"
                value={vehiclePhotoUrl}
                onChange={(e) => setVehiclePhotoUrl(e.target.value)}
                className="w-full h-10 px-3 rounded-lg border border-gray-200 text-xs text-gray-600 bg-gray-50 font-mono"
              />
            </div>
          </div>

          <div className="pt-4 flex space-x-3">
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              className="w-1/3 min-h-[48px] bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium rounded-xl text-sm transition"
            >
              ยกเลิก
            </button>
            <button
              type="submit"
              data-testid="submit-kyc-btn"
              disabled={loading}
              className="w-2/3 min-h-[48px] bg-emerald-600 hover:bg-emerald-700 text-white font-medium rounded-xl text-sm transition shadow-md flex items-center justify-center space-x-1.5"
            >
              {loading ? 'กำลังส่งข้อมูล...' : 'ส่งเอกสารตรวจสอบ'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

