/**
 * แผงรวมการโพสต์ขายของเก่าของผู้ขาย (ScrapPostingPanel)
 * Mobile-First Single-Page Application (375px–414px)
 * รองรับ UC-02, CC-01, CC-05, REQ-UX-002, Card 03, AC-S02-01..05
 */

import React, { useState, useEffect } from 'react';
import { scrapPostingApi } from '../services/scrapPostingApi';
import VisualScrapGuide from './VisualScrapGuide';
import BulkyItemSelector from './BulkyItemSelector';
import PhotoUploadManager from './PhotoUploadManager';
import LiftingHelpToggle from './LiftingHelpToggle';

export default function ScrapPostingPanel({
  sellerId = 'SEL-DEMO-01',
  pickupLocation = null,
  onPostConfirmed,
}) {
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [selectedSubCategory, setSelectedSubCategory] = useState('');
  const [quantity, setQuantity] = useState(1);
  const [photos, setPhotos] = useState([]);
  const [draftOrder, setDraftOrder] = useState(null);
  const [bulkyError, setBulkyError] = useState('');
  const [loading, setLoading] = useState(false);
  const [needLiftingHelp, setNeedLiftingHelp] = useState(false);
  const [liftingHelpNotes, setLiftingHelpNotes] = useState('');

  // โหลด Categories และเตรียม Draft Order เมื่อเริ่มต้น
  useEffect(() => {
    async function init() {
      try {
        const catRes = await scrapPostingApi.getCategories();
        setCategories(catRes.categories || []);
        if (catRes.categories?.length > 0) {
          setSelectedCategory(catRes.categories[0]);
        }

        // สร้างหรือดึงฉบับร่าง
        const draft = await scrapPostingApi.createDraft(
          sellerId,
          pickupLocation?.location_id || null
        );
        setDraftOrder(draft);
      } catch (e) {
        console.error('Init error', e);
      }
    }
    init();
  }, [sellerId, pickupLocation]);

  const handleAddItem = async (e) => {
    if (e) e.preventDefault();
    if (!draftOrder || !selectedCategory) return;

    // Card 03 Exception Case Guard: หากเป็นของชิ้นใหญ่เหมาจ่าย ต้องเลือกประเภทย่อย
    if (selectedCategory.category_group === 'BULKY_FLAT_RATE') {
      if (!selectedSubCategory || !selectedSubCategory.trim()) {
        setBulkyError('กรุณาระบุประเภทของชิ้นใหญ่ เพื่อให้ผู้รับซื้อจัดสรรพื้นที่รถบรรทุกได้');
        return;
      }
    }
    setBulkyError('');

    setLoading(true);
    try {
      await scrapPostingApi.addItem(draftOrder.order_id, {
        category_code: selectedCategory.category_code,
        sub_category: selectedSubCategory || null,
        quantity: parseFloat(quantity) || 1,
        photo_urls: photos,
      });

      // ดึงฉบับร่างที่อัปเดตแล้ว
      const updated = await scrapPostingApi.getDraft(draftOrder.order_id);
      setDraftOrder(updated);

      // รีเซ็ตฟอร์ม
      setPhotos([]);
      setSelectedSubCategory('');
      setQuantity(1);
    } catch (err) {
      alert(err.message || 'เพิ่มรายการไม่สำเร็จ');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteItem = async (itemId) => {
    if (!draftOrder) return;
    try {
      await scrapPostingApi.deleteItem(draftOrder.order_id, itemId);
      const updated = await scrapPostingApi.getDraft(draftOrder.order_id);
      setDraftOrder(updated);
    } catch (err) {
      alert(err.message || 'ลบรายการไม่สำเร็จ');
    }
  };

  const handleToggleLiftingHelp = async (val) => {
    setNeedLiftingHelp(val);
    if (!draftOrder) return;
    try {
      const updated = await scrapPostingApi.updateLiftingHelp(draftOrder.order_id, {
        needLiftingHelp: val,
        liftingHelpNotes,
      });
      setDraftOrder(updated);
    } catch (e) {
      console.error(e);
    }
  };

  const handleChangeLiftingNotes = async (notes) => {
    setLiftingHelpNotes(notes);
    if (!draftOrder) return;
    try {
      const updated = await scrapPostingApi.updateLiftingHelp(draftOrder.order_id, {
        needLiftingHelp,
        liftingHelpNotes: notes,
      });
      setDraftOrder(updated);
    } catch (e) {
      console.error(e);
    }
  };

  const unitLabel = selectedCategory?.unit === 'kg'
    ? 'กก.'
    : selectedCategory?.unit === 'crate'
    ? 'ลัง'
    : selectedCategory?.unit === 'bag'
    ? 'กระสอบ'
    : 'ชิ้น';

  return (
    <div
      data-req="UC-02"
      className="max-w-md mx-auto min-h-screen bg-gray-50/50 p-4 pb-16 font-sans space-y-4"
    >
      {/* ส่วนหัวแสดงที่อยู่นัดหมายจาก UC-01 */}
      <div className="bg-white rounded-2xl p-4 border border-gray-100 shadow-2xs flex items-center justify-between">
        <div>
          <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full">
            📍 จุดนัดรับของเก่า
          </span>
          <h4 className="text-xs font-bold text-gray-900 mt-1">
            {pickupLocation?.label || 'ที่อยู่นัดหมายเริ่มต้น'}: {pickupLocation?.sub_district || 'กรุงเทพมหานคร'}
          </h4>
          <p className="text-[11px] text-gray-500 line-clamp-1">
            {pickupLocation?.address_text || 'บ้านเลขที่/ซอย (ข้อมูลส่วนตัว PII)'}
          </p>
        </div>
      </div>

      {/* 1. คู่มือภาพเลือกประเภทของเก่า */}
      <div className="bg-white rounded-2xl p-4 border border-gray-100 shadow-2xs">
        <VisualScrapGuide
          categories={categories}
          selectedCategory={selectedCategory}
          onSelectCategory={(cat) => {
            setSelectedCategory(cat);
            setSelectedSubCategory('');
            setBulkyError('');
          }}
        />
      </div>

      {/* 2. หมวดของชิ้นใหญ่เหมาจ่าย (Bulky Selector) */}
      {selectedCategory?.category_group === 'BULKY_FLAT_RATE' && (
        <BulkyItemSelector
          selectedSubCategory={selectedSubCategory}
          onSelectSubCategory={(sub) => {
            setSelectedSubCategory(sub);
            setBulkyError('');
          }}
          errorMessage={bulkyError}
        />
      )}

      {/* 3. ปริมาณและแนบรูป */}
      <div className="bg-white rounded-2xl p-4 border border-gray-100 shadow-2xs space-y-4">
        <div>
          <label className="block text-xs font-semibold text-gray-700 mb-1">
            ปริมาณ ({unitLabel})
          </label>
          <div className="flex items-center space-x-2">
            <input
              type="number"
              min="0.1"
              step="any"
              data-testid="item-quantity-input"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              className="flex-1 px-4 py-2.5 text-sm rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 font-bold"
            />
            <span className="text-xs font-bold text-gray-500">{unitLabel}</span>
          </div>
        </div>

        {/* จัดการรูปถ่าย */}
        <PhotoUploadManager
          photos={photos}
          onAddPhoto={(url) => setPhotos([...photos, url])}
          onRemovePhoto={(idx) => setPhotos(photos.filter((_, i) => i !== idx))}
        />

        <button
          type="button"
          data-testid="add-item-btn"
          onClick={handleAddItem}
          disabled={loading}
          className="w-full py-3 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl transition-colors shadow-sm disabled:opacity-50"
        >
          {loading ? 'กำลังบันทึก...' : '+ เพิ่มลงในรายการขาย'}
        </button>
      </div>

      {/* 4. ตะกร้ารายการของเก่าในคำขอนี้ */}
      {draftOrder?.items && draftOrder.items.length > 0 && (
        <div className="bg-white rounded-2xl p-4 border border-gray-100 shadow-2xs space-y-3">
          <div className="flex items-center justify-between border-b border-gray-100 pb-2">
            <h4 className="text-xs font-bold text-gray-900">
              รายการของเก่าที่จะขาย ({draftOrder.items.length} รายการ)
            </h4>
            <span className="text-[11px] text-emerald-600 font-bold">
              ช่วงราคาประเมินรวม: {draftOrder.total_est_min_price}–{draftOrder.total_est_max_price} บาท
            </span>
          </div>

          <div className="space-y-2">
            {draftOrder.items.map((item) => (
              <div
                key={item.item_id}
                data-testid={`cart-item-${item.item_id}`}
                className="p-3 bg-gray-50 rounded-xl flex items-center justify-between text-xs"
              >
                <div>
                  <div className="font-bold text-gray-800">
                    {item.category_name}
                  </div>
                  <div className="text-[11px] text-gray-500">
                    {item.quantity} {item.unit} (ประเมิน {item.est_min_price}–{item.est_max_price} บ.)
                    {item.photo_urls?.length > 0 && ` • 📷 ${item.photo_urls.length} รูป`}
                  </div>
                </div>

                <button
                  type="button"
                  data-testid={`delete-item-btn-${item.item_id}`}
                  onClick={() => handleDeleteItem(item.item_id)}
                  className="text-red-500 hover:text-red-700 font-bold text-sm px-2 py-1"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 5. ตัวเลือกขอคนช่วยยกของหนัก */}
      <LiftingHelpToggle
        needLiftingHelp={needLiftingHelp}
        liftingHelpNotes={liftingHelpNotes}
        onToggleHelp={handleToggleLiftingHelp}
        onChangeNotes={handleChangeLiftingNotes}
      />

      {/* ปุ่มยืนยันโพสต์งาน */}
      {draftOrder?.items?.length > 0 && (
        <div className="pt-2">
          <button
            type="button"
            data-testid="confirm-post-btn"
            onClick={() => onPostConfirmed && onPostConfirmed(draftOrder)}
            className="w-full py-3.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-2xl text-sm transition-all shadow-md flex items-center justify-center space-x-2"
          >
            <span>ยืนยันโพสต์ขายของเก่า</span>
            <span>({draftOrder.total_est_min_price}–{draftOrder.total_est_max_price} บ.)</span>
          </button>
        </div>
      )}
    </div>
  );
}

