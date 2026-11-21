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
  onOpenLocationPicker,
  onItemsChange,
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
  const [statusMsg, setStatusMsg] = useState('');
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

        // สร้างหรือดึงฉบับร่าง (หากบัญชีผู้ขายเป็นโหมดทดสอบที่ยังไม่ได้สร้างใน Backend ใช้ฉบับร่างในเครื่องแทน)
        try {
          const draft = await scrapPostingApi.createDraft(
            sellerId,
            pickupLocation?.location_id || null
          );
          setDraftOrder(draft);
        } catch {
          setDraftOrder((prev) =>
            prev || {
              order_id: `DRAFT-LOCAL-${Date.now()}`,
              seller_id: sellerId,
              pickup_location_id: pickupLocation?.location_id || null,
              items: [],
              total_est_min_price: 0,
              total_est_max_price: 0,
              is_local: true,
            }
          );
        }
      } catch (e) {
        console.error('Init error', e);
      }
    }
    init();
  }, [sellerId, pickupLocation]);

  // ซิงก์รายการที่เลือกส่งต่อไปยังขั้นตอนที่ 2 (ประเมินราคากลาง) อัตโนมัติ
  useEffect(() => {
    if (!onItemsChange) return;
    const rawItems = draftOrder?.items || [];
    const mapToPricingCode = (code, name) => {
      if (code === 'MAT-PET-BOTTLE') return 'MAT-PLASTIC-BOTTLE';
      if (code === 'BOXED-GLASS') return 'MAT-GLASS-BOTTLE-BAG';
      if (code === 'BOXED-PLASTIC') return 'MAT-PLASTIC-BOTTLE-BAG';
      if (code === 'BULKY-APPLIANCE') {
        if (name?.includes('ตู้เย็น')) return 'BULKY-FRIDGE';
        if (name?.includes('เครื่องซักผ้า')) return 'BULKY-WASHING-MACHINE';
        if (name?.includes('แอร์')) return 'BULKY-AIR-CONDITIONER';
        return 'BULKY-FURNITURE';
      }
      if (code === 'MAT-ALU-CAN' || code === 'MAT-SCRAP-IRON') return 'MAT-CARDBOARD';
      return code || 'MAT-CARDBOARD';
    };

    const normalized = rawItems.map((it) => {
      const mappedCode = mapToPricingCode(it.category_code, it.category_name);
      const u =
        mappedCode.endsWith('-BAG')
          ? 'bag'
          : mappedCode.startsWith('BULKY-')
          ? 'piece'
          : it.unit === 'กระสอบ' || it.unit === 'bag'
          ? 'bag'
          : 'kg';
      return {
        category_code: mappedCode,
        category_name: it.category_name || it.category_code,
        unit: u,
        quantity: Number(it.quantity) || 1,
        est_min_price: Number(it.est_min_price) || 0,
        est_max_price: Number(it.est_max_price) || 0,
      };
    });
    onItemsChange(normalized);
  }, [draftOrder?.items, onItemsChange]);

  const recalcLocalDraft = (items, baseDraft) => {
    const totalMin = items.reduce((sum, it) => sum + (it.est_min_price || 0), 0);
    const totalMax = items.reduce((sum, it) => sum + (it.est_max_price || 0), 0);
    return {
      ...baseDraft,
      items,
      total_est_min_price: Math.round(totalMin * 100) / 100,
      total_est_max_price: Math.round(totalMax * 100) / 100,
    };
  };

  const handleAddItem = async (e) => {
    if (e) e.preventDefault();
    if (!selectedCategory) return;

    // Card 03 Exception Case Guard: หากเป็นของชิ้นใหญ่เหมาจ่าย ต้องเลือกประเภทย่อย
    if (selectedCategory.category_group === 'BULKY_FLAT_RATE') {
      if (!selectedSubCategory || !selectedSubCategory.trim()) {
        setBulkyError('กรุณาระบุประเภทของชิ้นใหญ่ เพื่อให้ผู้รับซื้อจัดสรรพื้นที่รถบรรทุกได้');
        return;
      }
    }
    setBulkyError('');
    setStatusMsg('');

    const parsedQty = Math.max(0.1, parseFloat(quantity) || 1);
    const activeDraft = draftOrder || {
      order_id: `DRAFT-LOCAL-${Date.now()}`,
      seller_id: sellerId,
      items: [],
      total_est_min_price: 0,
      total_est_max_price: 0,
      is_local: true,
    };

    const appendLocalItem = () => {
      const unitText =
        selectedCategory.unit === 'kg'
          ? 'กก.'
          : selectedCategory.unit === 'crate'
          ? 'ลัง'
          : selectedCategory.unit === 'bag'
          ? 'กระสอบ'
          : 'ชิ้น';
      const newItem = {
        item_id: `ITEM-${Date.now()}`,
        category_code: selectedCategory.category_code,
        category_name: selectedSubCategory
          ? `${selectedCategory.name} (${selectedSubCategory})`
          : selectedCategory.name,
        quantity: parsedQty,
        unit: unitText,
        est_min_price: Math.round(parsedQty * (selectedCategory.min_price_per_unit || 0) * 100) / 100,
        est_max_price: Math.round(parsedQty * (selectedCategory.max_price_per_unit || 0) * 100) / 100,
        photo_urls: [...photos],
      };
      const updated = recalcLocalDraft([...(activeDraft.items || []), newItem], activeDraft);
      setDraftOrder(updated);
      setStatusMsg(`เพิ่ม "${newItem.category_name}" (${parsedQty} ${unitText}) ลงในรายการขายแล้ว`);
    };

    setLoading(true);
    try {
      if (activeDraft.is_local) {
        appendLocalItem();
      } else {
        await scrapPostingApi.addItem(activeDraft.order_id, {
          category_code: selectedCategory.category_code,
          sub_category: selectedSubCategory || null,
          quantity: parsedQty,
          photo_urls: photos,
        });
        const updated = await scrapPostingApi.getDraft(activeDraft.order_id);
        setDraftOrder(updated);
        setStatusMsg(`เพิ่ม "${selectedCategory.name}" ลงในรายการขายแล้ว`);
      }

      // รีเซ็ตฟอร์ม
      setPhotos([]);
      setSelectedSubCategory('');
      setQuantity(1);
    } catch {
      appendLocalItem();
      setPhotos([]);
      setSelectedSubCategory('');
      setQuantity(1);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteItem = async (itemId) => {
    if (!draftOrder) return;
    if (draftOrder.is_local) {
      const remaining = (draftOrder.items || []).filter((it) => it.item_id !== itemId);
      setDraftOrder(recalcLocalDraft(remaining, draftOrder));
      return;
    }
    try {
      await scrapPostingApi.deleteItem(draftOrder.order_id, itemId);
      const updated = await scrapPostingApi.getDraft(draftOrder.order_id);
      setDraftOrder(updated);
    } catch {
      const remaining = (draftOrder.items || []).filter((it) => it.item_id !== itemId);
      setDraftOrder(recalcLocalDraft(remaining, draftOrder));
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

  const unitLabel = !selectedCategory
    ? 'หน่วย'
    : selectedCategory.unit === 'kg'
    ? 'กก.'
    : selectedCategory.unit === 'crate'
    ? 'ลัง'
    : selectedCategory.unit === 'bag'
    ? 'กระสอบ'
    : 'ชิ้น';

  return (
    <div
      data-req="UC-02"
      className="w-full space-y-5 font-sans"
    >
      {/* แถบจุดนัดรับของเก่าเดียวครบจบ (Yellow + Black Accent) */}
      <div className="rounded-2xl p-4 bg-yellow-400 border-2 border-black shadow-sm flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 rounded-xl bg-black text-yellow-400 flex items-center justify-center text-lg flex-shrink-0">
            📍
          </div>
          <div>
            <span className="text-[11px] font-bold text-black/80 uppercase tracking-wide">
              จุดนัดรับของเก่า
            </span>
            <h4 className="text-sm font-extrabold text-black leading-tight">
              {pickupLocation?.label || 'ที่อยู่นัดหมายเริ่มต้น'}: {pickupLocation?.sub_district || 'กรุงเทพมหานคร'}
            </h4>
            <p className="text-xs text-black/80 line-clamp-1 mt-0.5">
              {pickupLocation?.address_text || 'ยังไม่ได้ปักหมุด — กดปุ่มด้านขวาเพื่อเลือกตำแหน่งบนแผนที่'}
            </p>
          </div>
        </div>

        {onOpenLocationPicker && (
          <button
            type="button"
            onClick={onOpenLocationPicker}
            className="px-4 py-2 rounded-full bg-black text-yellow-400 text-xs font-bold hover:bg-zinc-800 transition flex items-center gap-1.5 shadow"
          >
            <span>🗺️</span>
            <span>{pickupLocation ? 'เปลี่ยนจุดนัดรับบนแผนที่' : 'เลือกตำแหน่งบนแผนที่'}</span>
          </button>
        )}
      </div>

      {/* Responsive 2-Column Layout (Full-Width, High Contrast Yellow-Black-White) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
        {/* Left Column: คู่มือภาพเลือกประเภท + ของชิ้นใหญ่ */}
        <div className="lg:col-span-7 space-y-4">
          <div className="bg-yellow-50/90 rounded-2xl p-5 border border-yellow-300 shadow-xs">
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
        </div>

        {/* Right Column: กรอกปริมาณ แนบรูป และตะกร้ารายการ */}
        <div className="lg:col-span-5 space-y-4">
          <div className="bg-white rounded-2xl border-2 border-black overflow-hidden shadow-md">
            <div className="bg-black text-yellow-400 px-5 py-3 flex items-center justify-between">
              <span className="text-sm font-extrabold">📝 ระบุปริมาณและรูปถ่าย</span>
              <span className="text-xs font-bold text-white/90">
                {selectedCategory ? selectedCategory.name : 'กรุณาเลือกประเภท'}
              </span>
            </div>

            <div className="p-5 space-y-4">
              <div>
                <label className="block text-xs font-bold text-black mb-1.5">
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
                    className="flex-1 px-4 py-2.5 text-sm rounded-xl border-2 border-zinc-200 focus:outline-none focus:border-black bg-zinc-50 focus:bg-white font-bold text-black"
                  />
                  <span className="px-3 py-2.5 rounded-xl bg-yellow-100 border border-yellow-300 text-xs font-extrabold text-black">
                    {unitLabel}
                  </span>
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
                disabled={loading || !selectedCategory}
                className="w-full py-3 bg-black hover:bg-zinc-800 text-yellow-400 text-sm font-extrabold rounded-full transition-colors shadow-md disabled:opacity-45"
              >
                {loading ? 'กำลังบันทึก...' : '+ เพิ่มลงในรายการขาย'}
              </button>

              {statusMsg && (
                <div className="p-2.5 rounded-xl bg-yellow-100 border border-yellow-400 text-black text-xs font-bold text-center">
                  ✓ {statusMsg}
                </div>
              )}
            </div>
          </div>

          {/* 4. ตะกร้ารายการของเก่าในคำขอนี้ */}
          {draftOrder?.items && draftOrder.items.length > 0 && (
            <div className="bg-yellow-50 rounded-2xl p-4 border-2 border-yellow-400 shadow-xs space-y-3">
              <div className="flex items-center justify-between border-b border-yellow-300 pb-2">
                <h4 className="text-xs font-extrabold text-black">
                  🛒 รายการของเก่าที่จะขาย ({draftOrder.items.length} รายการ)
                </h4>
                <span className="text-xs bg-black text-yellow-400 px-2.5 py-0.5 rounded-full font-bold">
                  {draftOrder.total_est_min_price}–{draftOrder.total_est_max_price} บ.
                </span>
              </div>

              <div className="space-y-2">
                {draftOrder.items.map((item) => (
                  <div
                    key={item.item_id}
                    data-testid={`cart-item-${item.item_id}`}
                    className="p-3 bg-white border border-yellow-200 rounded-xl flex items-center justify-between text-xs"
                  >
                    <div>
                      <div className="font-bold text-black">
                        {item.category_name}
                      </div>
                      <div className="text-[11px] text-zinc-600">
                        {item.quantity} {item.unit} (ประเมิน {item.est_min_price}–{item.est_max_price} บ.)
                        {item.photo_urls?.length > 0 && ` • 📷 ${item.photo_urls.length} รูป`}
                      </div>
                    </div>

                    <button
                      type="button"
                      data-testid={`delete-item-btn-${item.item_id}`}
                      onClick={() => handleDeleteItem(item.item_id)}
                      className="text-red-600 hover:text-red-800 font-bold text-sm px-2 py-1"
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
            <div className="pt-1">
              <button
                type="button"
                data-testid="confirm-post-btn"
                onClick={() => onPostConfirmed && onPostConfirmed(draftOrder)}
                className="w-full py-3.5 bg-yellow-400 hover:bg-yellow-300 text-black border-2 border-black font-extrabold rounded-full text-sm transition-all shadow-md flex items-center justify-center space-x-2"
              >
                <span>✓ ยืนยันโพสต์ขายของเก่า</span>
                <span>({draftOrder.total_est_min_price}–{draftOrder.total_est_max_price} บ.)</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

