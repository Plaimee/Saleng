import React, { useState, useEffect, useCallback } from 'react';
import { billingReceiptApi, OFFLINE_QUEUE_KEY } from '../services/billingReceiptApi.js';
import WeighingInputForm from './WeighingInputForm.jsx';
import SellerConfirmationGate from './SellerConfirmationGate.jsx';
import PaymentMethodSelector from './PaymentMethodSelector.jsx';
import DigitalReceiptCard from './DigitalReceiptCard.jsx';

/**
 * BillingReceiptView Component
 * หน้าจอหลักระบบคิดเงินและออกใบเสร็จฝั่งซาเล้ง (Buyer 06)
 * รองรับ UC-05, UC-06, UC-07, REQ-FN-002, REQ-FN-004, REQ-FN-005, REQ-BR-002, REQ-SEC-002, CC-01, CC-04, CC-05, CC-06, REQ-OP-001, D-B06-01..06
 */
export default function BillingReceiptView({
  orderId = 'order-01',
  salengId = 'saleng-01',
  onBack,
}) {
  const [sheet, setSheet] = useState(null);
  const [receipt, setReceipt] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [isOffline, setIsOffline] = useState(
    typeof navigator !== 'undefined' ? navigator.onLine === false : false
  );
  const [pendingQueueCount, setPendingQueueCount] = useState(0);

  // ตรวจสอบจำนวนรายการในคิวออฟไลน์
  const updatePendingCount = useCallback(() => {
    if (typeof localStorage !== 'undefined') {
      try {
        const queue = JSON.parse(localStorage.getItem(OFFLINE_QUEUE_KEY) || '[]');
        setPendingQueueCount(queue.length);
      } catch {
        setPendingQueueCount(0);
      }
    }
  }, []);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await billingReceiptApi.getWeighingSheet(orderId, salengId);
      setSheet(data);

      // หากสถานะเป็น S7 ให้โหลดใบเสร็จทันที
      if (data.order_status === 'S7') {
        const receiptData = await billingReceiptApi.getReceipt(orderId, salengId);
        setReceipt(receiptData);
      }
    } catch (err) {
      setError(err.message || 'ไม่สามารถโหลดข้อมูลคำขอขายได้');
    } finally {
      setLoading(false);
      updatePendingCount();
    }
  }, [orderId, salengId, updatePendingCount]);

  useEffect(() => {
    loadData();

    const handleOnline = () => {
      setIsOffline(false);
      handleSyncQueue();
    };
    const handleOffline = () => setIsOffline(true);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [loadData]);

  // ซิงก์คิวออฟไลน์
  const handleSyncQueue = async () => {
    try {
      const res = await billingReceiptApi.syncOfflineWeighingQueue();
      if (res.syncedCount > 0) {
        await loadData();
      }
      updatePendingCount();
    } catch {
      // ignore
    }
  };

  // จัดการการส่งผลชั่งน้ำหนัก (S4 -> S5)
  const handleSubmitWeighing = async ({ scalePhotoUrl, items }) => {
    setSubmitting(true);
    setError(null);
    try {
      const res = await billingReceiptApi.submitWeighing(orderId, {
        salengId,
        scalePhotoUrl,
        items,
      });

      if (res.is_offline) {
        updatePendingCount();
        setSheet((prev) => ({
          ...prev,
          order_status: 'S5',
          scale_photo_url: scalePhotoUrl,
        }));
      } else {
        await loadData();
      }
    } catch (err) {
      setError(err.message || 'บันทึกผลการชั่งไม่สำเร็จ');
    } finally {
      setSubmitting(false);
    }
  };

  // จัดการเลือกช่องทางชำระเงิน (S6)
  const handleSelectPaymentMethod = async (paymentMethod) => {
    setSubmitting(true);
    setError(null);
    try {
      await billingReceiptApi.selectPaymentMethod(orderId, {
        salengId,
        paymentMethod,
      });
      await loadData();
    } catch (err) {
      setError(err.message || 'ไม่สามารถบันทึกช่องทางชำระเงินได้');
    } finally {
      setSubmitting(false);
    }
  };

  const currentStatus = sheet?.order_status || 'S4';
  const sellerConfirmed = sheet?.seller_confirmed_weight || false;

  return (
    <div
      className="max-w-md mx-auto bg-gray-50 min-h-screen pb-12"
      data-req="UC-07"
      data-testid="billing-receipt-view"
    >
      {/* ส่วนหัวหน้าจอ */}
      <header className="bg-emerald-700 text-white p-4 sticky top-0 z-10 shadow-md">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {onBack && (
              <button
                type="button"
                onClick={onBack}
                className="w-10 h-10 min-h-[48px] min-w-[48px] rounded-full hover:bg-emerald-800 flex items-center justify-center text-lg"
                data-testid="header-back-btn"
              >
                ←
              </button>
            )}
            <div>
              <h1 className="text-base font-bold">ระบบคิดเงินและออกใบเสร็จ</h1>
              <span className="text-xs text-emerald-100 font-mono">
                คำขอ: {orderId}
              </span>
            </div>
          </div>
          <span className="text-xs bg-emerald-800 text-emerald-100 font-bold px-2.5 py-1 rounded-full border border-emerald-600">
            {currentStatus}
          </span>
        </div>
      </header>

      {/* แถบเตือนออฟไลน์ & ซิงก์คิว (CC-05, REQ-OP-001) */}
      {isOffline && (
        <div
          className="bg-amber-100 border-b border-amber-200 px-4 py-2.5 text-xs text-amber-900 flex justify-between items-center"
          data-testid="offline-banner"
        >
          <div className="flex items-center gap-1.5">
            <span>📶</span>
            <span>โหมดออฟไลน์: บันทึกข้อมูลลงเครื่อง</span>
          </div>
          {pendingQueueCount > 0 && (
            <span className="bg-amber-200 font-bold px-2 py-0.5 rounded text-[11px]">
              ค้าง {pendingQueueCount} รายการ
            </span>
          )}
        </div>
      )}

      {/* แถบซิงก์คิวเมื่อกลับมาออนไลน์ */}
      {!isOffline && pendingQueueCount > 0 && (
        <div
          className="bg-blue-50 border-b border-blue-200 px-4 py-2 text-xs text-blue-900 flex justify-between items-center"
          data-testid="sync-pending-banner"
        >
          <span>มีรายการชั่งน้ำหนักรอซิงก์ {pendingQueueCount} รายการ</span>
          <button
            type="button"
            onClick={handleSyncQueue}
            className="bg-blue-600 hover:bg-blue-700 text-white font-bold px-3 py-1 rounded-lg text-xs"
            data-testid="sync-now-btn"
          >
            ซิงก์เดี๋ยวนี้
          </button>
        </div>
      )}

      <main className="p-4 space-y-4">
        {/* ข้อความแจ้งเตือนข้อผิดพลาด */}
        {error && (
          <div
            className="bg-red-50 border border-red-200 rounded-xl p-3 text-xs text-red-700 flex justify-between items-center"
            data-testid="global-error-banner"
          >
            <span>⚠️ {error}</span>
            <button
              type="button"
              onClick={() => setError(null)}
              className="text-red-500 font-bold text-sm px-2"
            >
              ✕
            </button>
          </div>
        )}

        {/* ข้อมูลสรุปคู่ค้าและ Masking (REQ-SEC-002, CC-06) */}
        {sheet && (
          <div
            className="bg-white rounded-2xl border border-gray-200 p-4 shadow-sm text-xs space-y-2"
            data-testid="seller-info-card"
          >
            <div className="flex justify-between items-center">
              <span className="text-gray-500">ผู้ขาย:</span>
              <span className="font-bold text-gray-800">{sheet.seller_name}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-500">เบอร์โทรศัพท์ (Masked):</span>
              <span className="font-mono font-medium text-gray-700" data-testid="masked-phone">
                {sheet.seller_phone_masked}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-500">สถานะขั้นตอน:</span>
              <span className="font-bold text-emerald-700">
                {currentStatus === 'S4' && '1. กำลังชั่งน้ำหนักหน้างาน'}
                {currentStatus === 'S5' && (sellerConfirmed ? '2. รอเลือกชำระเงิน' : '2. รอผู้ขายยืนยันน้ำหนัก')}
                {currentStatus === 'S6' && '3. ยืนยันน้ำหนักแล้ว / รอยืนยันรับเงิน'}
                {currentStatus === 'S7' && '4. ซื้อขายสำเร็จ / ออกใบเสร็จดิจิทัล'}
              </span>
            </div>
          </div>
        )}

        {loading ? (
          <div className="text-center py-12 text-sm text-gray-500" data-testid="loading-state">
            กำลังโหลดข้อมูล...
          </div>
        ) : (
          <>
            {/* ขั้นตอนที่ 1: กรอกน้ำหนักจริง (S4 หรือ S5 ก่อนยืนยัน) */}
            {currentStatus === 'S4' && (
              <WeighingInputForm
                orderId={orderId}
                items={sheet?.items || []}
                initialScalePhotoUrl={sheet?.scale_photo_url || ''}
                onSubmitWeighing={handleSubmitWeighing}
                isLoading={submitting}
              />
            )}

            {/* ขั้นตอนที่ 2: 100% Confirmation Gate (S5) */}
            {currentStatus === 'S5' && !sellerConfirmed && (
              <SellerConfirmationGate
                orderId={orderId}
                sellerConfirmed={false}
                orderStatus="S5"
                totalAmount={sheet?.total_settled_amount || 0}
                onCheckStatus={loadData}
                isLoading={loading}
              />
            )}

            {/* ขั้นตอนที่ 3: เลือกช่องทางชำระเงิน (S6 หรือ S5 ที่ sellerConfirmed แล้ว) */}
            {(currentStatus === 'S6' || (currentStatus === 'S5' && sellerConfirmed)) && (
              <PaymentMethodSelector
                orderId={orderId}
                totalAmount={sheet?.total_settled_amount || 0}
                sellerPhoneMasked={sheet?.seller_phone_masked}
                selectedMethod={sheet?.payment_method}
                onSelectPaymentMethod={handleSelectPaymentMethod}
                isLoading={submitting}
              />
            )}

            {/* ขั้นตอนที่ 4: ใบเสร็จดิจิทัล (S7) */}
            {currentStatus === 'S7' && receipt && (
              <DigitalReceiptCard
                receipt={receipt}
                isOffline={isOffline}
                onBackToHome={onBack}
              />
            )}
          </>
        )}
      </main>
    </div>
  );
}

