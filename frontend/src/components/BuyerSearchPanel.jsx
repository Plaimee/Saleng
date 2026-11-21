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
      className="w-full space-y-5 font-sans"
    >
      {/* Header Banner: Golden Yellow + Jet Black */}
      <div className="rounded-2xl p-4 bg-yellow-400 border-2 border-black shadow-sm flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-black text-yellow-400 flex items-center justify-center text-xl flex-shrink-0">
            🛺
          </div>
          <div>
            <h2 className="text-base sm:text-lg font-extrabold text-black leading-tight">
              ค้นหาและเลือกผู้รับซื้อใกล้ฉัน
            </h2>
            <p className="text-xs text-black/80">
              เลือกซาเล้งที่ผ่านการยืนยันตัวตน 100% ในรัศมีของคุณ
            </p>
          </div>
        </div>
        <button
          type="button"
          data-testid="refresh-btn"
          onClick={fetchCollectors}
          className="px-4 py-2 text-xs font-bold text-yellow-400 bg-black rounded-full hover:bg-zinc-800 transition shadow"
        >
          🔄 รีเฟรชรายชื่อ
        </button>
      </div>

      {/* ป้ายเตือนโหมดออฟไลน์ (CC-05, REQ-OP-001) */}
      {isOffline && (
        <div
          data-testid="offline-alert"
          className="p-3 bg-amber-100 border border-amber-400 text-amber-950 rounded-2xl text-xs font-medium flex items-center space-x-2"
        >
          <span>⚠️</span>
          <span>โหมดออฟไลน์: กำลังแสดงรายชื่อผู้รับซื้อล่าสุดที่บันทึกไว้ในอุปกรณ์</span>
        </div>
      )}

      {/* แถบสำเร็จเมื่อส่งคำขอนัดหมายแล้ว (S2 State) */}
      {matchedOrder && (
        <div
          data-testid="matched-success-banner"
          className="p-4 bg-yellow-100 border-2 border-black rounded-2xl space-y-1.5 shadow-sm"
        >
          <div className="flex items-center space-x-2 text-sm font-extrabold text-black">
            <span>🎉</span>
            <span>ส่งคำขอนัดหมายเจาะจงบุคคลสำเร็จ (สถานะ: S2)</span>
          </div>
          <p className="text-xs text-zinc-800 leading-relaxed">
            {matchedOrder.message}
          </p>
          <div className="text-xs text-black font-bold">
            หมดเวลาตอบรับ: {new Date(matchedOrder.direct_request_expires_at).toLocaleTimeString('th-TH')}
          </div>
        </div>
      )}

      {/* แผงตัวกรอง + ซาเล้งประจำ (Warm Yellow Card) */}
      <div className="bg-yellow-50/90 rounded-2xl p-4 border border-yellow-300 space-y-4">
        <FavoriteCollectorPinList
          favorites={favorites}
          onSelect={handleOpenDirectModal}
        />

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
      </div>

      {/* รายการการ์ดซาเล้งแบบ 2 คอลัมน์เต็มพื้นที่ (AC-S03-01) */}
      <div className="space-y-3">
        <div className="flex items-center justify-between text-xs px-1">
          <span className="font-bold text-black">พบผู้รับซื้อ {collectors.length} รายในรัศมี</span>
          <span className="text-[11px] bg-black text-yellow-400 px-2.5 py-0.5 rounded-full font-bold">
            ✓ ยืนยันตัวตน 100%
          </span>
        </div>

        {loading ? (
          <div className="text-center py-8 text-xs text-zinc-500">
            กำลังค้นหาผู้รับซื้อในพื้นที่...
          </div>
        ) : collectors.length === 0 ? (
          <div
            data-testid="no-collectors-msg"
            className="text-center py-10 bg-yellow-50 rounded-2xl border-2 border-dashed border-yellow-400 p-6 space-y-2"
          >
            <span className="text-3xl">📭</span>
            <p className="text-xs font-bold text-black">ไม่พบผู้รับซื้อในเงื่อนไขที่เลือก</p>
            <p className="text-[11px] text-zinc-600">ลองขยายรัศมี หรือปรับตัวกรองยานพาหนะ</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {collectors.map((c) => (
              <SalengProfileCard
                key={c.saleng_id}
                collector={c}
                onSelect={handleOpenDirectModal}
                onToggleFavorite={handleToggleFavorite}
                onStartChat={(col) => alert(`เปิดห้องแชตกับ ${col.display_name}`)}
              />
            ))}
          </div>
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

