"""
Pydantic Models and Schemas for Buyer Job Discovery & Map View (UC-04)
รองรับ REQ-FN-002, REQ-QA-002, REQ-SEC-002, CC-03, CC-06, D-00-02, P-01
"""

from typing import List, Optional, Dict, Any, Tuple
from pydantic import BaseModel, Field, field_validator
import hashlib
import math


def fuzz_coordinates(
    lat: float,
    lng: float,
    seed: Optional[str] = None,
    min_dist_m: float = 300.0,
    max_dist_m: float = 500.0,
) -> Tuple[float, float]:
    """
    สร้างพิกัดจำลอง (Fuzzed Coordinates) สุ่มเบี่ยงเบน 300–500 เมตร (REQ-SEC-002, D-00-02, CC-06, P-01)
    ใช้ seed คงที่ต่อ Order เพื่อให้พิกัดจำลองคงที่ตลอดวงจรชีวิตคำขอขายก่อนรับงาน
    """
    if seed:
        hasher = hashlib.sha256(seed.encode("utf-8"))
        digest = hasher.digest()
        angle_ratio = int.from_bytes(digest[:4], "big") / 0xFFFFFFFF
        dist_ratio = int.from_bytes(digest[4:8], "big") / 0xFFFFFFFF
    else:
        # Default seed based on original coordinates
        hasher = hashlib.sha256(f"{lat:.6f},{lng:.6f}".encode("utf-8"))
        digest = hasher.digest()
        angle_ratio = int.from_bytes(digest[:4], "big") / 0xFFFFFFFF
        dist_ratio = int.from_bytes(digest[4:8], "big") / 0xFFFFFFFF

    angle_rad = angle_ratio * 2 * math.pi
    distance_m = min_dist_m + (max_dist_m - min_dist_m) * dist_ratio

    # 1 deg lat ~ 111,139 meters
    # 1 deg lng ~ 111,139 * cos(lat) meters
    delta_lat = (distance_m * math.cos(angle_rad)) / 111139.0
    lat_rad = math.radians(lat)
    cos_lat = math.cos(lat_rad) if abs(math.cos(lat_rad)) > 1e-6 else 1.0
    delta_lng = (distance_m * math.sin(angle_rad)) / (111139.0 * cos_lat)

    fuzzed_lat = round(lat + delta_lat, 6)
    fuzzed_lng = round(lng + delta_lng, 6)
    return (fuzzed_lat, fuzzed_lng)


class JobSearchQueryParams(BaseModel):
    """พารามิเตอร์การค้นหาคำขอขายใกล้เคียง (UC-04, REQ-FN-002)"""
    saleng_lat: float = Field(..., description="พิกัดละติจูดปัจจุบันของซาเล้ง (-90 ถึง 90)")
    saleng_lng: float = Field(..., description="พิกัดลองจิจูดปัจจุบันของซาเล้ง (-180 ถึง 180)")
    radius_km: float = Field(5.0, ge=1.0, le=50.0, description="รัศมีการค้นหา (เริ่มต้น 5.0 กม., ขยายได้ 10.0 กม.)")
    category: Optional[str] = Field(None, description="หมวดหมู่วัสดุที่ต้องการกรอง (เช่น MAT-CARDBOARD, BULKY-APPLIANCE)")
    weight_range: Optional[str] = Field("ALL", description="ช่วงน้ำหนัก (ALL, SMALL, MEDIUM, LARGE)")
    sort_by: Optional[str] = Field("DISTANCE", description="การจัดเรียง (DISTANCE, PRICE_DESC)")

    @field_validator("saleng_lat")
    @classmethod
    def validate_lat(cls, v: float) -> float:
        if not (-90.0 <= v <= 90.0):
            raise ValueError("พิกัดละติจูดต้องอยู่ระหว่าง -90 และ 90 องศา")
        return v

    @field_validator("saleng_lng")
    @classmethod
    def validate_lng(cls, v: float) -> float:
        if not (-180.0 <= v <= 180.0):
            raise ValueError("พิกัดลองจิจูดต้องอยู่ระหว่าง -180 และ 180 องศา")
        return v


class NearbyJobSummaryResponse(BaseModel):
    """
    ข้อมูลย่อของคำขอขายที่ส่งกลับหน้าจอ
    ตัด PII (บ้านเลขที่, พิกัดจริง, เบอร์โทรศัพท์) ออกตาม REQ-SEC-002, D-00-02, CC-06
    """
    order_id: str = Field(..., description="รหัสคำขอขาย")
    status: str = Field("S2", description="สถานะคำขอขาย (S2: Pending)")
    subdistrict_name: str = Field(..., description="ชื่อแขวง/ตำบล")
    district_name: str = Field(..., description="ชื่อเขต/อำเภอ")
    approximate_lat: float = Field(..., description="พิกัดละติจูดจำลอง (Fuzzed)")
    approximate_lng: float = Field(..., description="พิกัดลองจิจูดจำลอง (Fuzzed)")
    road_distance_km: float = Field(..., description="ระยะทางคำนวณตามถนนจริง (กม.)")
    estimated_price_min: float = Field(..., description="ราคาประเมินต่ำสุด (บาท)")
    estimated_price_max: float = Field(..., description="ราคาประเมินสูงสุด (บาท)")
    estimated_weight_kg: float = Field(..., description="น้ำหนักประเมินรวม (กก.)")
    categories: List[str] = Field(default_factory=list, description="รายการหมวดหมู่วัสดุ")
    item_count: int = Field(1, description="จำนวนรายการ")
    need_lifting_help: bool = Field(False, description="ต้องการคนช่วยยกหรือไม่")
    is_fallback_distance: bool = Field(False, description="คำนวณจากสูตร Haversine Fallback หรือไม่ (REQ-OP-002)")
    created_at: str = Field(..., description="วันเวลาที่ส่งคำขอ (ISO 8601)")


class NearbyJobListResponse(BaseModel):
    """รายการคำขอขายในรัศมีพร้อมข้อความแนะนำการขยายระยะทาง (AC-B02-01, AC-B02-02)"""
    total_count: int = Field(..., description="จำนวนงานที่พบ")
    radius_km: float = Field(..., description="รัศมีการค้นหาที่ใช้ (กม.)")
    jobs: List[NearbyJobSummaryResponse] = Field(default_factory=list, description="รายการคำขอขาย")
    active_filters: Dict[str, Any] = Field(default_factory=dict, description="ตัวกรองที่กำลังใช้งาน")
    message: Optional[str] = Field(None, description="ข้อความแจ้งเตือน (เช่น 'ยังไม่มีงานในเส้นทาง')")
    can_expand_radius: bool = Field(False, description="แนะนำให้ขยายรัศมีเป็น 10 กม. หรือไม่")


class SimulateOrderRequest(BaseModel):
    """คำขอจำลองสร้าง Order ใหม่สถานะ S2 เพื่อทดสอบ Polling & Live Alert (Q-02)"""
    seller_id: str = Field("seller-sim-01", description="รหัสผู้ขายจำลอง")
    lat: float = Field(..., description="พิกัดละติจูดจริง")
    lng: float = Field(..., description="พิกัดลองจิจูดจริง")
    subdistrict: str = Field(..., description="ชื่อแขวง/ตำบล")
    district: str = Field("เขตห้วยขวาง", description="ชื่อเขต/อำเภอ")
    categories: List[str] = Field(default_factory=lambda: ["MAT-CARDBOARD"], description="หมวดหมู่วัสดุ")
    estimated_weight_kg: float = Field(25.0, ge=1.0, description="น้ำหนักประเมินรวม (กก.)")
    estimated_price_min: float = Field(100.0, ge=0.0, description="ราคาประเมินต่ำสุด")
    estimated_price_max: float = Field(150.0, ge=0.0, description="ราคาประเมินสูงสุด")
    need_lifting_help: bool = Field(False, description="ต้องการคนช่วยยก")

