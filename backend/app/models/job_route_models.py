"""
Pydantic Models and Navigation Protocol for Job & Route Management (UC-04, UC-09, UC-12, Buyer 04)
รองรับ REQ-BR-002, REQ-SEC-002, REQ-OP-001, CC-01, CC-04, CC-05, BR-02, BR-03, D-B04-01..06
"""

from typing import List, Optional
from pydantic import BaseModel, Field


def build_google_maps_navigation_url(lat: float, lng: float) -> str:
    """
    สร้าง Deep Link URL Scheme สำหรับเปิดระบบนำทางภายนอก (Google Maps / Apple Maps)
    ตามข้อกำหนด D-B04-03 และ Non-goals ของ SPEC-ROUTE
    """
    return f"https://www.google.com/maps/dir/?api=1&destination={lat:.6f},{lng:.6f}&travelmode=driving"


class ClaimJobRequest(BaseModel):
    """คำขอกดรับงานของซาเล้ง (BR-02, CC-04)"""
    saleng_id: str = Field(..., description="รหัสประจำตัวซาเล้ง")
    expected_version: int = Field(1, ge=1, description="OCC Version ของคำขอขายที่อ่านได้ล่าสุด")


class ClaimJobResponse(BaseModel):
    """ข้อมูลตอบกลับเมื่อกดรับงานสำเร็จ (เปิดเผย PII ตาม REQ-SEC-002, D-00-02)"""
    order_id: str = Field(..., description="รหัสคำขอขาย")
    status: str = Field("S3", description="สถานะใหม่ (S3: มีผู้รับงานแล้ว)")
    collector_id: str = Field(..., description="รหัสซาเล้งผู้รับผิดชอบงาน")
    address_text: str = Field(..., description="บ้านเลขที่และซอยฉบับเต็ม (เปิดเผยหลังรับงาน)")
    dest_lat: float = Field(..., description="พิกัดละติจูดแท้จริงของผู้ขาย")
    dest_lng: float = Field(..., description="พิกัดลองจิจูดแท้จริงของผู้ขาย")
    seller_phone: str = Field(..., description="เบอร์โทรศัพท์ผู้ขายสำหรับติดต่อ")
    seller_name: str = Field(..., description="ชื่อผู้ขาย")
    subdistrict_name: str = Field(..., description="ชื่อแขวง/ตำบล")
    district_name: str = Field(..., description="ชื่อเขต/อำเภอ")
    total_est_weight_kg: float = Field(..., ge=0.0, description="น้ำหนักประเมินรวมของงาน (กก.)")
    total_est_price_min: float = Field(..., ge=0.0, description="ราคาประเมินต่ำสุดรวม (บาท)")
    total_est_price_max: float = Field(..., ge=0.0, description="ราคาประเมินสูงสุดรวม (บาท)")
    claimed_at: str = Field(..., description="วันเวลาที่กดรับงานสำเร็จ (ISO-8601)")
    version: int = Field(..., description="Version ใหม่หลัง Atomic OCC update")
    navigation_url: str = Field(..., description="URL Scheme นำทางผ่าน Google Maps")


class ActiveJobSummary(BaseModel):
    """สรุปข้อมูลงานที่อยู่ในคิวปฏิบัติการของซาเล้ง (S3 หรือ S4)"""
    order_id: str = Field(..., description="รหัสคำขอขาย")
    status: str = Field(..., description="สถานะงาน (S3: Assigned หรือ S4: In-Transit)")
    pickup_slot_time: str = Field("09:00 - 11:00", description="ช่วงเวลานัดหมาย")
    address_text: str = Field(..., description="บ้านเลขที่และซอยฉบับเต็ม")
    dest_lat: float = Field(..., description="พิกัดละติจูดจริง")
    dest_lng: float = Field(..., description="พิกัดลองจิจูดจริง")
    seller_name: str = Field(..., description="ชื่อผู้ขาย")
    seller_phone: str = Field(..., description="เบอร์โทรศัพท์ผู้ขาย")
    total_est_weight_kg: float = Field(..., ge=0.0, description="น้ำหนักประเมิน (กก.)")
    total_est_price_min: float = Field(..., ge=0.0, description="ราคาประเมินต่ำสุด (บาท)")
    total_est_price_max: float = Field(..., ge=0.0, description="ราคาประเมินสูงสุด (บาท)")
    road_distance_km: float = Field(..., ge=0.0, description="ระยะทางถนนจริง (กม.)")
    estimated_arrival_minutes: int = Field(15, ge=0, description="เวลาถึงโดยประมาณ (นาที)")
    sequence_order: int = Field(1, ge=1, description="ลำดับจุดแวะรับตาม Route Optimization")
    need_lifting_help: bool = Field(False, description="ต้องการคนช่วยยกของหนักหรือไม่")
    navigation_url: str = Field(..., description="ลิงก์นำทาง Google Maps")


class ActiveQueueResponse(BaseModel):
    """รายการคิวงานและตารางนัดหมายสะสมของซาเล้ง (BR-03, D-B04-02)"""
    saleng_id: str = Field(..., description="รหัสซาเล้ง")
    total_active_jobs: int = Field(..., ge=0, description="จำนวนงานที่กำลังดูแลอยู่ในคิว")
    current_load_kg: float = Field(..., ge=0.0, description="น้ำหนักบรรทุกสะสมรวมในรถปัจจุบัน (กก.)")
    max_capacity_kg: float = Field(200.0, description="ความจุสูงสุดของรถซาเล้ง (200 กก. ตาม BR-03)")
    remaining_capacity_kg: float = Field(..., ge=0.0, description="ความจุรถที่เหลือรับได้อีก (กก.)")
    capacity_percentage: float = Field(..., ge=0.0, description="เปอร์เซ็นต์ความจุรถที่ใช้ไป (%)")
    total_route_distance_km: float = Field(..., ge=0.0, description="ระยะทางรวมของทุกจุดแวะในคิว (กม.)")
    jobs: List[ActiveJobSummary] = Field(default_factory=list, description="รายการงานที่เรียงลำดับแล้ว")


class StartTransitRequest(BaseModel):
    """คำขอยืนยันออกเดินทางไปยังจุดนัดรับ (UC-09, S3 -> S4)"""
    saleng_id: str = Field(..., description="รหัสซาเล้ง")
    current_lat: Optional[float] = Field(None, description="พิกัดละติจูดล่าสุดขณะออกเดินทาง")
    current_lng: Optional[float] = Field(None, description="พิกัดลองจิจูดล่าสุดขณะออกเดินทาง")


class StartTransitResponse(BaseModel):
    """ผลการยืนยันออกเดินทาง"""
    order_id: str = Field(..., description="รหัสคำขอขาย")
    status: str = Field("S4", description="สถานะใหม่: S4 (กำลังเดินทาง / In-Transit)")
    started_at: str = Field(..., description="วันเวลาที่เริ่มออกเดินทาง")
    seller_notified: bool = Field(True, description="ส่งแจ้งเตือนให้ผู้ขายแล้ว")
    seller_cancel_locked: bool = Field(True, description="ล็อกปุ่มยกเลิกผู้ขายตาม BR-03")
    navigation_url: str = Field(..., description="URL Scheme นำทางผ่าน Google Maps")


class CollectorCancelJobRequest(BaseModel):
    """คำขอยกเลิกงานของซาเล้ง (D-B04-04)"""
    saleng_id: str = Field(..., description="รหัสซาเล้ง")
    reason: str = Field(..., description="เหตุผลการยกเลิก (VEHICLE_BREAKDOWN, ACCIDENT, PERSONAL_EMERGENCY, OTHER)")
    note: Optional[str] = Field(None, description="คำอธิบายเพิ่มเติม")


class CollectorCancelJobResponse(BaseModel):
    """ผลการยกเลิกงานและคืนสถานะ"""
    order_id: str = Field(..., description="รหัสคำขอขาย")
    status: str = Field("S2", description="คืนสถานะกลับเป็น S2: รอผู้รับงาน เพื่อให้ซาเล้งอื่นรับต่อ")
    message: str = Field(..., description="ข้อความแจ้งผลการดำเนินการ")
    cancelled_at: str = Field(..., description="วันเวลาที่ยกเลิก")
    reverted_to_pending: bool = Field(True, description="ยืนยันการคืนสถานะกลับเป็น S2 สำเร็จ")

