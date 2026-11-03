"""
FastAPI Router for Buyer Job Search & Map Discovery (UC-04)
รองรับ REQ-FN-002, REQ-QA-002, REQ-SEC-002, REQ-OP-002, D-00-01, D-00-02, CC-03, CC-06
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status
from backend.app.models.job_search_models import (
    JobSearchQueryParams,
    NearbyJobListResponse,
    NearbyJobSummaryResponse,
    SimulateOrderRequest,
)
from backend.app.services.job_search_service import JobSearchService

router = APIRouter(prefix="/collectors/jobs", tags=["Buyer Job Discovery & Map"])


@router.get("/nearby", response_model=NearbyJobListResponse)
def get_nearby_jobs(
    saleng_lat: Optional[float] = Query(None, description="พิกัดละติจูดปัจจุบันของซาเล้ง"),
    saleng_lng: Optional[float] = Query(None, description="พิกัดลองจิจูดปัจจุบันของซาเล้ง"),
    radius_km: float = Query(5.0, ge=1.0, le=50.0, description="รัศมีการค้นหา (กม.)"),
    category: Optional[str] = Query(None, description="หมวดหมู่วัสดุที่ต้องการกรอง"),
    weight_range: Optional[str] = Query("ALL", description="ช่วงน้ำหนัก (ALL, SMALL, MEDIUM, LARGE)"),
    sort_by: Optional[str] = Query("DISTANCE", description="การจัดเรียง (DISTANCE, PRICE_DESC)"),
    force_fallback: bool = Query(False, description="บังคับใช้โหมดสำรอง Haversine * 1.35"),
    collector_id: Optional[str] = Query("saleng-01", description="รหัสซาเล้ง"),
):
    """
    ค้นหาคำขอขายสถานะ S2 ในรัศมี 5.0 หรือ 10.0 กม. พร้อม Fuzzing พิกัดและตัวกรอง
    (REQ-FN-002, REQ-QA-002, REQ-SEC-002, AC-B02-01, AC-B02-02, AC-B02-04)
    """
    # ตรวจสอบว่า GPS เปิดอยู่หรือไม่ (AC-B02-04, E1)
    if saleng_lat is None or saleng_lng is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="กรุณาเปิด GPS เพื่อค้นหางานใกล้เคียง (GPS Disabled/Denied)",
        )

    # ตรวจสอบความถูกต้องของพิกัด
    if not (-90.0 <= saleng_lat <= 90.0) or not (-180.0 <= saleng_lng <= 180.0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="พิกัด GPS ไม่อยู่ในช่วงที่ถูกต้อง",
        )

    try:
        query_params = JobSearchQueryParams(
            saleng_lat=saleng_lat,
            saleng_lng=saleng_lng,
            radius_km=radius_km,
            category=category,
            weight_range=weight_range,
            sort_by=sort_by,
        )
        return JobSearchService.search_nearby_jobs(
            params=query_params,
            actor_id=collector_id or "saleng-01",
            force_fallback=force_fallback,
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"เกิดข้อผิดพลาดในการค้นหางาน: {str(e)}",
        )


@router.get("/{order_id}/summary", response_model=NearbyJobSummaryResponse)
def get_job_summary(
    order_id: str,
    saleng_lat: Optional[float] = Query(None, description="พิกัดละติจูดซาเล้งสำหรับคำนวณระยะทาง"),
    saleng_lng: Optional[float] = Query(None, description="พิกัดลองจิจูดซาเล้งสำหรับคำนวณระยะทาง"),
    force_fallback: bool = Query(False, description="บังคับใช้โหมดสำรอง Haversine"),
):
    """
    ดึงข้อมูลสรุปคำขอขายก่อนรับงาน โดยซ่อน PII และพิกัดจริง (REQ-SEC-002, D-00-02, AC-B02-03)
    """
    try:
        return JobSearchService.get_job_summary(
            order_id=order_id,
            saleng_lat=saleng_lat,
            saleng_lng=saleng_lng,
            force_fallback=force_fallback,
        )
    except KeyError as ke:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ke))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"เกิดข้อผิดพลาดในการดึงข้อมูลคำขอ: {str(e)}",
        )


@router.post("/simulate-new-order", status_code=status.HTTP_201_CREATED)
def simulate_new_order(req: SimulateOrderRequest):
    """
    จำลองคำขอขายใหม่สถานะ S2 เพื่อทดสอบ Polling & Live Alert (Q-02)
    """
    try:
        created = JobSearchService.simulate_order(req)
        return {
            "success": True,
            "message": "จำลองคำขอขายใหม่สถานะ S2 สำเร็จ",
            "order": created,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"ไม่สามารถจำลองคำขอขายได้: {str(e)}",
        )

