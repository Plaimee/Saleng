import React, { useState, useEffect } from "react";
import SalesSummaryCards from "../components/SalesSummaryCards";
import SalesOrderCard from "../components/SalesOrderCard";
import DigitalReceiptCard from "../components/DigitalReceiptCard";
import {
  fetchSalesHistory,
  toggleFavorite,
  fetchReceipt,
} from "../services/postTransactionApi";

/**
 * SalesHistoryPage Component (Main Mobile SPA Page)
 * หน้าจอหลักรวมประวัติการขายของเก่าย้อนหลังของผู้ขาย พร้อมสรุปสถิติสะสมและดูใบเสร็จดิจิทัล
 * รองรับ UC-10, REQ-FN-005, REQ-SEC-002, CC-01, CC-05, REQ-OP-001, AC-S07-03, AC-S07-04
 */
export default function SalesHistoryPage({ sellerId = "SELLER-001", onBack }) {
  const [historyData, setHistoryData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState("");
  const [selectedReceipt, setSelectedReceipt] = useState(null);
  const [receiptLoading, setReceiptLoading] = useState(false);
  const [isReceiptModalOpen, setIsReceiptModalOpen] = useState(false);

  const loadHistory = async () => {
    setLoading(true);
    setErrorMsg("");
    try {
      const data = await fetchSalesHistory(sellerId);
      setHistoryData(data);
    } catch (err) {
      setErrorMsg("ไม่สามารถโหลดประวัติการขายได้ กรุณาลองใหม่อีกครั้ง");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, [sellerId]);

  const handleToggleFavorite = async (collectorId) => {
    try {
      await toggleFavorite(sellerId, collectorId);
      // รีโหลดข้อมูลเพื่ออัปเดตสถานะ is_favorite
      await loadHistory();
    } catch (e) {
      // ignore
    }
  };

  const handleOpenReceipt = async (orderId) => {
    setReceiptLoading(true);
    try {
      const receipt = await fetchReceipt(orderId);
      setSelectedReceipt(receipt);
      setIsReceiptModalOpen(true);
    } catch (err) {
      alert("ไม่สามารถเปิดใบเสร็จได้ กรุณาลองใหม่อีกครั้ง");
    } finally {
      setReceiptLoading(false);
    }
  };

  const summary = historyData?.summary || {
    total_sales_amount: 0,
    total_weight_kg: 0,
    total_completed_orders: 0,
  };
  const orders = historyData?.orders || [];
  const isOffline = historyData?.is_offline_cached || false;

  return (
    <div
      className="min-h-screen bg-gray-50 max-w-md mx-auto pb-12 font-sans text-gray-900 border-x border-gray-200"
      data-testid="sales-history-page"
      data-req="UC-10"
    >
      {/* Top Navbar */}
      <header className="sticky top-0 z-30 bg-white/95 backdrop-blur-md border-b border-gray-100 px-4 py-3 flex items-center justify-between shadow-xs">
        <div className="flex items-center gap-2">
          {onBack && (
            <button
              onClick={onBack}
              className="p-1.5 -ml-1.5 text-gray-600 hover:text-gray-900 rounded-lg hover:bg-gray-100 text-sm"
              data-testid="back-button"
            >
              ←
            </button>
          )}
          <h1 className="text-base font-bold text-gray-800">
            ประวัติการขายของเก่า
          </h1>
        </div>
        <button
          onClick={loadHistory}
          className="text-xs text-emerald-600 font-medium hover:underline p-1"
          data-testid="refresh-btn"
        >
          รีเฟรช
        </button>
      </header>

      {/* Main Content */}
      <main className="p-4">
        {/* ป้ายเตือนออฟไลน์แคช (CC-05, REQ-OP-001) */}
        {isOffline && (
          <div
            className="bg-amber-50 border border-amber-200 text-amber-800 px-3 py-2 rounded-xl text-xs mb-4 flex items-center justify-between"
            data-testid="offline-history-banner"
          >
            <span>📡 แสดงข้อมูลจากแคชออฟไลน์ในเครื่อง</span>
            <span className="text-[10px] text-amber-600">ออฟไลน์</span>
          </div>
        )}

        {/* สรุปสถิติสะสม (AC-S07-03) */}
        <SalesSummaryCards summary={summary} isOffline={isOffline} />

        {/* รายการคำขอย้อนหลัง */}
        <div className="mb-3 flex justify-between items-center">
          <h2 className="text-xs font-bold text-gray-700 uppercase tracking-wider">
            รายการที่สำเร็จ ({orders.length})
          </h2>
        </div>

        {loading ? (
          <div className="text-center py-12 text-xs text-gray-400" data-testid="loading-indicator">
            กำลังโหลดข้อมูลประวัติการขาย...
          </div>
        ) : errorMsg ? (
          <div className="bg-red-50 text-red-600 text-xs p-4 rounded-xl text-center border border-red-200">
            {errorMsg}
          </div>
        ) : orders.length === 0 ? (
          <div className="bg-white rounded-2xl border border-dashed border-gray-200 p-8 text-center text-gray-400 text-xs">
            ยังไม่มีประวัติการขายของเก่าที่สำเร็จ
          </div>
        ) : (
          <div data-testid="orders-list-container">
            {orders.map((order) => (
              <SalesOrderCard
                key={order.order_id}
                order={order}
                onToggleFavorite={handleToggleFavorite}
                onOpenReceipt={handleOpenReceipt}
              />
            ))}
          </div>
        )}
      </main>

      {/* Modal เปิดดูใบเสร็จดิจิทัล (AC-S07-04, REQ-FN-005) */}
      {isReceiptModalOpen && selectedReceipt && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
          data-testid="receipt-modal-backdrop"
        >
          <div className="bg-white w-full max-w-sm rounded-3xl p-4 max-h-[90vh] overflow-y-auto shadow-2xl">
            <div className="flex justify-between items-center pb-2 mb-2 border-b border-gray-100">
              <span className="text-xs font-bold text-gray-700">ใบเสร็จดิจิทัล</span>
              <button
                onClick={() => setIsReceiptModalOpen(false)}
                className="text-gray-400 hover:text-gray-600 text-lg leading-none p-1"
                data-testid="close-receipt-modal-btn"
              >
                ✕
              </button>
            </div>
            <DigitalReceiptCard
              receipt={selectedReceipt}
              isOffline={selectedReceipt.is_offline_cached}
              onBackToHome={() => setIsReceiptModalOpen(false)}
            />
          </div>
        </div>
      )}
    </div>
  );
}

