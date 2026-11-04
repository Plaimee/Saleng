"""
Pydantic Models and Fuel Calculation for Pre-Acceptance Evaluation (UC-04, Buyer 03)
รองรับ REQ-FN-002, REQ-QA-002, REQ-CON-003, REQ-SEC-002, BR-03, D-B03-01..06
"""

from typing import List, Optional
from pydantic import BaseModel, Field

# อัตราค่าน้ำมันอ้างอิงตามประเภทยานพาหนะ (บาท/กม.) ตาม D-B03-01 (Card 02)
FUEL_RATE_MAP = {
    "TRICYCLE": 0.00,       # รถซาเล้งปั่น ไม่ใช้น้ำมัน
    "MOTORCYCLE": 2.50,     # รถซาเล้งพ่วงข้าง / มอเตอร์ไซค์
    "PICKUP": 4.50,         # รถกระบะรับซื้อ
    "DEFAULT": 2.50,        # ค่าเริ่มต้น
}


def calculate_fuel_cost(road_distance_km: float, vehicle_type: Optional[str] = None) -> float:
    """
    คำนวณค่าน้ำมันโดยประมาณ (Card 02, D-B03-01, AC-B03-01):
    estimated_fuel_cost = round(road_distance_km * fuel_rate_per_km, 2)
    """
    normalized_vtype = (vehicle_type or "DEFAULT").upper()
    rate = FUEL_RATE_MAP.get(normalized_vtype, FUEL_RATE_MAP["DEFAULT"])
    return round(road_distance_km * rate, 2)


class EvaluatedItemSummary(BaseModel):
    """ข้อมูลสิ่งของที่จะรับซื้อในคำขอ (REQ-FN-003, REQ-FN-004)"""
    item_id: str = Field(..., description="รหัสรายการของเก่า")
    category_code: str = Field(..., description="รหัสหมวดหมู่วัสดุ")
    category_name: str = Field(..., description="ชื่อหมวดหมู่วัสดุ")
    category_group: str = Field(..., description="กลุ่มหมวดหมู่ (GENERAL_WEIGHT, BULKY_FLAT_RATE, BOXED_PACKAGING)")
    est_weight_kg: float = Field(..., ge=0.0, description="น้ำหนักประเมิน (กก.)")
    est_min_price: float = Field(..., ge=0.0, description="ราคาประเมินต่ำสุด (บาท)")
    est_max_price: float = Field(..., ge=0.0, description="ราคาประเมินสูงสุด (บาท)")
    sub_category: Optional[str] = Field(None, description="ประเภทย่อย เช่น ตู้เย็น, แอร์")
    photo_urls: List[str] = Field(default_factory=list, description="รายการรูปถ่ายของเก่า")


class JobEvaluationResponse(BaseModel):
    """
    ข้อมูลประเมินรายละเอียดคำขอขายส่งกลับหน้าจอซาเล้งก่อนรับงาน (Card 02, AC-B03-01..05)
    ตัด PII (บ้านเลขที่, เบอร์โทร, พิกัดแท้จริง) ออกตาม REQ-SEC-002, D-00-02
    """
    order_id: str = Field(..., description="รหัสคำขอขาย")
    status: str = Field("S2", description="สถานะคำขอ (S2: Pending)")
    subdistrict_name: str = Field(..., description="ชื่อแขวง/ตำบล")
    district_name: str = Field(..., description="ชื่อเขต/อำเภอ")
    approximate_lat: float = Field(..., description="พิกัดละติจูดจำลอง (Fuzzed)")
    approximate_lng: float = Field(..., description="พิกัดลองจิจูดจำลอง (Fuzzed)")
    road_distance_km: float = Field(..., description="ระยะทางถนนจริง (กม.)")
    is_fallback_distance: bool = Field(False, description="คำนวณจากสูตรสำรอง Haversine หรือไม่")
    vehicle_type: str = Field("MOTORCYCLE", description="ประเภทยานพาหนะของซาเล้ง")
    fuel_rate_per_km: float = Field(2.50, description="อัตราค่าน้ำมันต่อกิโลเมตร (บาท)")
    estimated_fuel_cost: float = Field(..., description="ค่าน้ำมันโดยประมาณ (บาท)")
    total_est_min_price: float = Field(..., description="ราคาประเมินต่ำสุดรวม (บาท)")
    total_est_max_price: float = Field(..., description="ราคาประเมินสูงสุดรวม (บาท)")
    total_est_weight_kg: float = Field(..., description="น้ำหนักประเมินรวมของงานนี้ (กก.)")
    need_lifting_help: bool = Field(False, description="ต้องการคนช่วยยกของหนักหรือไม่")
    items: List[EvaluatedItemSummary] = Field(default_factory=list, description="รายการสิ่งของ")
    collector_current_load_kg: float = Field(0.0, description="น้ำหนักบรรทุกปัจจุบันในรถซาเล้ง (กก.)")
    collector_max_capacity_kg: float = Field(200.0, description="ความจุสูงสุดของรถซาเล้ง (กก.)")
    projected_total_load_kg: float = Field(..., description="น้ำหนักสะสมรวมหากรับงานนี้ (กก.)")
    is_capacity_exceeded: bool = Field(False, description="น้ำหนักเกินความจุรถหรือไม่ (BR-03)")
    remaining_capacity_kg: float = Field(..., description="ความจุรถที่เหลืออยู่ (กก.)")
    can_claim_job: bool = Field(True, description="สามารถกดรับงานได้หรือไม่")
    claim_block_reason: Optional[str] = Field(None, description="เหตุผลที่บล็อกปุ่มรับงาน")
    collector_is_online: bool = Field(True, description="สถานะความพร้อมรับงาน (Online)")
    collector_is_verified: bool = Field(True, description="สถานะการยืนยันตัวตน KYC")
    created_at: str = Field(..., description="วันเวลาที่ส่งคำขอขาย")


class CollectorStatusToggleRequest(BaseModel):
    """คำขอสลับสถานะ Online/Offline (CC-02)"""
    saleng_id: str = Field(..., description="รหัสซาเล้ง")
    is_online: bool = Field(..., description="สถานะใหม่ (True = Online, False = Offline)")
    current_lat: Optional[float] = Field(None, description="พิกัดละติจูดล่าสุด")
    current_lng: Optional[float] = Field(None, description="พิกัดลองจิจูดล่าสุด")


class CollectorCapacityResponse(BaseModel):
    """ข้อมูลการตรวจสอบความจุรถของซาเล้ง (BR-03, REQ-CON-003)"""
    saleng_id: str = Field(..., description="รหัสซาเล้ง")
    current_load_kg: float = Field(..., description="น้ำหนักบรรทุกปัจจุบัน (กก.)")
    max_capacity_kg: float = Field(..., description="ความจุสูงสุดของรถ (กก.)")
    remaining_capacity_kg: float = Field(..., description="ความจุที่เหลืออยู่ (กก.)")
    vehicle_type: str = Field(..., description="ประเภทยานพาหนะ")
    load_percentage: float = Field(..., description="เปอร์เซ็นต์การบรรทุกปัจจุบัน (%)")

