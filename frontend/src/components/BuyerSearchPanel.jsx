/**
 * แผงหลักระบบค้นหาและเลือกผู้รับซื้อ (BuyerSearchPanel)
 * รองรับ UC-03, CC-01, CC-05, REQ-QA-001, REQ-UX-001, REQ-FN-001, AC-S03-01..05
 */

import React, { useState, useEffect } from 'react';
import { buyerSearchApi } from '../services/buyerSearchApi.js';
import FavoriteCollectorPinList from './FavoriteCollectorPinList.jsx';
import CollectorFilterPanel from './CollectorFilterPanel.jsx';
import SalengProfileCard from './SalengProfileCard.jsx';
import DirectRequestModal from './DirectRequestModal.jsx';

export default function BuyerSearchPanel({
  sellerId = 'seller-01',
  orderId = null,
  onOrderMatched,
}) {
  const [collectors, setCollectors] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isOffline, setIsOffline] = useState(false);
  const [hasBulkyItems, setHasBulkyItems] = useState(false);
  const [bulkyWarningMessage, setBulkyWarningMessage] = useState('');

  // Filters
  const [radiusKm, setRadiusKm] = useState(5.0);
  const [vehicleType, setVehicleType] = useState(null);
  const [minRating, setMinRating] = useState(null);

  // Modal State
  const [selectedCollector, setSelectedCollector] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [sendingRequest, setSendingRequest] = useState(false);
  const [matchedOrder, setMatchedOrder] = useState(null);

  const fetchCollectors = async () => {
    setLoading(true);
    try {
      const data = await buyerSearchApi.searchCollectors({
        sellerId,
        orderId,
        radiusKm,
        vehicleType,
        minRating,
      });
      setCollectors(data.collectors || []);
      setHasBulkyItems(data.has_bulky_items || false);
      setBulkyWarningMessage(data.bulky_warning_message || '');
      setIsOffline(data.is_offline || false);

      // ดึงรายชื่อคนโปรดแยก
      const favList = await buyerSearchApi.getFavorites(sellerId);
      setFavorites(favList || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCollectors();
  }, [radiusKm, vehicleType, minRating]);

  const handleToggleFavorite = async (salengId) => {
    try {
      await buyerSearchApi.toggleFavorite(salengId, sellerId);
      await fetchCollectors();
    } catch (err) {
      alert(err.message);
    }
  };

  const handleOpenDirectModal = (collector) => {
    setSelectedCollector(collector);
    setIsModalOpen(true);
  };

  const handleConfirmDirectRequest = async (salengId, notes) => {
    if (!orderId) {
      alert('กรุณาระบุรหัสคำขอก่อนส่งนัดหมาย');
      return;
    }
    setSendingRequest(true);
    try {
      const result = await buyerSearchApi.sendDirectRequest(
        orderId,
        salengId,
        sellerId,
        notes
      );
      setMatchedOrder(result);
      setIsModalOpen(false);
      if (onOrderMatched) {
        onOrderMatched(result);
      }
    } catch (err) {
      alert(err.message);
    } finally {
      setSendingRequest(false);
    }
  };

  return (
    <div
      data-req="UC-03"
      data-testid="buyer-search-panel"
      className="max-w-md mx-auto p-4 space-y-4 bg-gray-50/50 min-h-screen"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-base font-extrabold text-gray-900 flex items-center gap-1.5">
            <span>🔍</span>
            <span>ค้นหาและเลือกผู้รับซื้อ</span>
          </h2>
          <p className="text-[11px] text-gray-500">
            เลือกซาเล้งที่ผ่านการยืนยันตัวตนในรัศมีของคุณ
          </p>
        </div>
        <button
          type="button"
          data-testid="refresh-btn"
          onClick={fetchCollectors}
          className="p-2 text-xs text-gray-600 bg-white border border-gray-200 rounded-xl hover:bg-gray-50"
        >
          🔄 รีเฟรช
        </button>
      </div>

      {/* ป้ายเตือนโหมดออฟไลน์ (CC-05, REQ-OP-001) */}
      {isOffline && (
        <div
          data-testid="offline-alert"
          className="p-2.5 bg-amber-500/10 border border-amber-300 text-amber-900 rounded-2xl text-[11px] flex items-center space-x-2"
        >
          <span>⚠️</span>
          <span>โหมดออฟไลน์: กำลังแสดงรายชื่อผู้รับซื้อล่าสุดที่บันทึกไว้ในอุปกรณ์</span>
        </div>
      )}

      {/* แถบสำเร็จเมื่อส่งคำขอนัดหมายแล้ว (S2 State) */}
      {matchedOrder && (
        <div
          data-testid="matched-success-banner"
          className="p-3.5 bg-emerald-50 border border-emerald-300 rounded-2xl space-y-1.5 animate-fade-in"
        >
          <div className="flex items-center space-x-2 text-xs font-bold text-emerald-900">
            <span>🎉</span>
            <span>ส่งคำขอนัดหมายเจาะจงบุคคลสำเร็จ (สถานะ: S2)</span>
          </div>
          <p className="text-[11px] text-emerald-800 leading-relaxed">
            {matchedOrder.message}
          </p>
          <div className="text-[10px] text-emerald-600 font-semibold">
            หมดเวลาตอบรับ: {new Date(matchedOrder.direct_request_expires_at).toLocaleTimeString('th-TH')}
          </div>
        </div>
      )}

      {/* แถบตรึงซาเล้งที่เคยใช้บริการไว้บนสุด (AC-S03-02) */}
      <FavoriteCollectorPinList
        favorites={favorites}
        onSelect={handleOpenDirectModal}
      />

      {/* แผงตัวกรองหลายมิติ (AC-S03-03) */}
      <CollectorFilterPanel
        radiusKm={radiusKm}
        onChangeRadius={setRadiusKm}
        vehicleType={vehicleType}
        onChangeVehicleType={setVehicleType}
        minRating={minRating}
        onChangeMinRating={setMinRating}
        hasBulkyItems={hasBulkyItems}
        bulkyWarningMessage={bulkyWarningMessage}
      />

      {/* รายการการ์ดซาเล้ง (AC-S03-01) */}
      <div className="space-y-3 pt-1">
        <div className="flex items-center justify-between text-xs text-gray-500 px-1">
          <span>พบผู้รับซื้อ {collectors.length} รายในรัศมี</span>
          <span className="text-[10px] text-emerald-700 font-semibold">✓ ยืนยันตัวตน 100%</span>
        </div>

        {loading ? (
          <div className="text-center py-8 text-xs text-gray-400">
            กำลังค้นหาผู้รับซื้อในพื้นที่...
          </div>
        ) : collectors.length === 0 ? (
          <div
            data-testid="no-collectors-msg"
            className="text-center py-10 bg-white rounded-3xl border border-dashed border-gray-200 p-6 space-y-2"
          >
            <span className="text-3xl">📭</span>
            <p className="text-xs font-bold text-gray-700">ไม่พบผู้รับซื้อในเงื่อนไขที่เลือก</p>
            <p className="text-[11px] text-gray-400">ลองขยายรัศมี หรือปรับตัวกรองยานพาหนะ</p>
          </div>
        ) : (
          collectors.map((c) => (
            <SalengProfileCard
              key={c.saleng_id}
              collector={c}
              onSelect={handleOpenDirectModal}
              onToggleFavorite={handleToggleFavorite}
              onStartChat={(col) => alert(`เปิดห้องแชตกับ ${col.display_name}`)}
            />
          ))
        )}
      </div>

      {/* โมดัลยืนยันนัดหมายเจาะจงบุคคล (AC-S03-05) */}
      <DirectRequestModal
        collector={selectedCollector}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onConfirm={handleConfirmDirectRequest}
        loading={sendingRequest}
      />
    </div>
  );
}

