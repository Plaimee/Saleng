/**
 * แผงควบคุมระบบบัญชีและการเข้าใช้งานของผู้ขาย (AccountAccessPanel)
 * รวมระบบล็อกอิน โปรไฟล์ และการจัดการที่อยู่นัดหมายแบบ Mobile-First SPA
 * รองรับ UC-01, UC-02, CC-01, CC-05, REQ-UX-001, AC-S01-01..04
 */

import React, { useState, useEffect } from 'react';
import { accountApi } from '../services/accountApi';
import PhoneOtpLoginForm from './PhoneOtpLoginForm';
import SellerProfileCard from './SellerProfileCard';
import PickupLocationList from './PickupLocationList';
import PickupLocationModal from './PickupLocationModal';

export default function AccountAccessPanel({ onSessionReady }) {
  const [session, setSession] = useState(null);
  const [profile, setProfile] = useState(null);
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingLocation, setEditingLocation] = useState(null);

  // ตรวจสอบเซสชันที่บันทึกไว้ในเครื่องเมื่อเริ่มต้น (CC-05, REQ-OP-001)
  useEffect(() => {
    const stored = accountApi.getStoredSession();
    if (stored) {
      setSession(stored);
      setProfile(stored);
      loadLocations(stored.seller_id);
      if (onSessionReady) onSessionReady(stored);
    }
    setLoading(false);
  }, []);

  const loadLocations = async (sellerId) => {
    try {
      const data = await accountApi.listLocations(sellerId);
      setLocations(data.locations || []);
    } catch (e) {
      console.error('Failed to load locations', e);
    }
  };

  const handleLoginSuccess = (authData) => {
    setSession(authData);
    setProfile(authData);
    loadLocations(authData.seller_id);
    if (onSessionReady) onSessionReady(authData);
  };

  const handleLogout = async () => {
    await accountApi.logout();
    setSession(null);
    setProfile(null);
    setLocations([]);
  };

  const handleSaveLocation = async (locData) => {
    try {
      if (editingLocation) {
        await accountApi.updateLocation(
          session.seller_id,
          editingLocation.location_id,
          locData
        );
      } else {
        await accountApi.createLocation(session.seller_id, locData);
      }
      setModalOpen(false);
      setEditingLocation(null);
      await loadLocations(session.seller_id);
    } catch (err) {
      alert(err.message || 'บันทึกที่อยู่ไม่สำเร็จ');
    }
  };

  const handleDeleteLocation = async (locId) => {
    if (!window.confirm('คุณต้องการลบที่อยู่นี้ใช่หรือไม่?')) return;
    try {
      await accountApi.deleteLocation(session.seller_id, locId);
      await loadLocations(session.seller_id);
    } catch (err) {
      alert(err.message || 'ลบที่อยู่ไม่สำเร็จ');
    }
  };

  const handleSetDefault = async (locId) => {
    try {
      await accountApi.setDefaultLocation(session.seller_id, locId);
      await loadLocations(session.seller_id);
    } catch (err) {
      alert(err.message || 'ตั้งค่าที่อยู่เริ่มต้นไม่สำเร็จ');
    }
  };

  if (loading) {
    return (
      <div data-req="UC-01" className="p-6 text-center text-xs text-gray-500">
        กำลังโหลดข้อมูลบัญชี...
      </div>
    );
  }

  return (
    <div
      data-req="UC-01"
      className="max-w-md mx-auto min-h-screen bg-gray-50/50 p-4 pb-12 font-sans"
    >
      {!session ? (
        <PhoneOtpLoginForm onLoginSuccess={handleLoginSuccess} />
      ) : (
        <div className="space-y-4">
          <SellerProfileCard
            profile={profile}
            onProfileUpdated={(updated) => setProfile(updated)}
            onLogout={handleLogout}
          />

          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-4">
            <PickupLocationList
              locations={locations}
              onAddNew={() => {
                setEditingLocation(null);
                setModalOpen(true);
              }}
              onEdit={(loc) => {
                setEditingLocation(loc);
                setModalOpen(true);
              }}
              onDelete={handleDeleteLocation}
              onSetDefault={handleSetDefault}
            />
          </div>

          <PickupLocationModal
            isOpen={modalOpen}
            location={editingLocation}
            onClose={() => {
              setModalOpen(false);
              setEditingLocation(null);
            }}
            onSave={handleSaveLocation}
          />
        </div>
      )}
    </div>
  );
}

