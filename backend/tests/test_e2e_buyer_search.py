"""
E2E Integration Test สำหรับระบบค้นหาและเลือกผู้รับซื้อ (Buyer Search & Selection Lifecycle)
รองรับ UC-03, REQ-FN-001, REQ-QA-001, REQ-UX-001, REQ-SEC-001, Card 03, AC-S03-01..05, P-01..P-06
"""

from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


def test_e2e_buyer_search_and_selection_lifecycle():
    """
    ทดสอบวงจรชีวิตของ UC-03 แบบครบวงจร:
    1. สร้างคำขอฉบับร่าง S1 พร้อมของเก่าชิ้นใหญ่ (ตู้เย็น Card 03)
    2. ค้นหารายชื่อซาเล้งในพื้นที่ -> ตรวจสอบป้าย KYC 100% และตรวจจับของชิ้นใหญ่
    3. กรองเฉพาะรถกระบะ (PICKUP_TRUCK) เพื่อให้รองรับตู้เย็น
    4. สลับสถานะบันทึกเป็นคนโปรด (Favorite Collector)
    5. ส่งคำขอนัดหมายเจาะจงบุคคล (Direct Request) -> เปลี่ยนสถานะเป็น S2
    6. ตรวจสอบ Audit Log และเวลานับถอยหลัง 15 นาที
    """
    seller_id = "seller-e2e-buyer-search"
    order_id = "order-e2e-s03"

    # ขั้นตอนที่ 1: เตรียมคำขอฉบับร่าง S1 พร้อมของชิ้นใหญ่
    supabase_store.orders[order_id] = {
        "order_id": order_id,
        "seller_id": seller_id,
        "status": "S1",
    }
    supabase_store.items["item-e2e-fridge"] = {
        "item_id": "item-e2e-fridge",
        "order_id": order_id,
        "category_code": "BULKY-APPLIANCE",
        "sub_category": "ตู้เย็น",
        "quantity": 1,
    }

    # ขั้นตอนที่ 2: ค้นหาซาเล้งในพื้นที่
    search_res = client.get(
        f"/api/v1/buyer-search/collectors?seller_id={seller_id}&order_id={order_id}"
    )
    assert search_res.status_code == 200
    search_data = search_res.json()

    assert search_data["has_bulky_items"] is True
    assert search_data["total_count"] >= 2
    # ทุกคนที่แสดงต้อง verified = True
    for c in search_data["collectors"]:
        assert c["verified"] is True
        assert c["is_online"] is True

    # ขั้นตอนที่ 3: กรองเฉพาะรถกระบะ
    filter_res = client.get(
        f"/api/v1/buyer-search/collectors?seller_id={seller_id}&order_id={order_id}&vehicle_type=PICKUP_TRUCK"
    )
    assert filter_res.status_code == 200
    filtered_collectors = filter_res.json()["collectors"]
    assert len(filtered_collectors) >= 1
    selected_collector = filtered_collectors[0]
    assert selected_collector["vehicle_type"] == "PICKUP_TRUCK"
    saleng_id = selected_collector["saleng_id"]

    # ขั้นตอนที่ 4: บันทึกเป็นคนโปรด
    fav_res = client.post(
        f"/api/v1/buyer-search/favorites/{saleng_id}/toggle?seller_id={seller_id}"
    )
    assert fav_res.status_code == 200
    assert fav_res.json()["is_favorite"] is True

    # ค้นหาใหม่ -> ซาเล้งคนนี้ต้องถูกตรึงไว้บนสุด
    re_search = client.get(
        f"/api/v1/buyer-search/collectors?seller_id={seller_id}&order_id={order_id}"
    )
    assert re_search.json()["collectors"][0]["saleng_id"] == saleng_id
    assert re_search.json()["collectors"][0]["is_favorite"] is True

    # ขั้นตอนที่ 5: ส่งคำขอนัดหมายเจาะจงบุคคล (Direct Request)
    direct_req_res = client.post(
        f"/api/v1/buyer-search/orders/{order_id}/direct-request?seller_id={seller_id}",
        json={"saleng_id": saleng_id, "notes": "มีตู้เย็น 1 เครื่อง ต้องการรถกระบะ"},
    )
    assert direct_req_res.status_code == 200
    direct_data = direct_req_res.json()
    assert direct_data["status"] == "S2"
    assert direct_data["assigned_saleng"]["saleng_id"] == saleng_id
    assert "direct_request_expires_at" in direct_data

    # ขั้นตอนที่ 6: ตรวจสอบสถานะในฐานข้อมูลและ Audit Log
    updated_order = supabase_store.get_order(order_id)
    assert updated_order is not None
    assert updated_order["status"] == "S2"
    assert updated_order["assigned_saleng_id"] == saleng_id

    logs = [
        l for l in supabase_store.audit_logs
        if l.get("action") == "COLLECTOR_DIRECT_REQUESTED" and l.get("entity_id") == order_id
    ]
    assert len(logs) >= 1
    assert logs[-1]["actor_id"] == seller_id

