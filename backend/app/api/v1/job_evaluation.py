"""
FastAPI Router for Buyer Pre-Acceptance Job Evaluation & Fuel Cost (UC-04, Buyer 03)
รองรับ REQ-FN-002, REQ-QA-002, REQ-OP-002, REQ-CON-003, REQ-SEC-002, BR-03, D-00-01, D-00-02
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status
from backend.app.models.job_evaluation_models import (
    JobEvaluationResponse,
    CollectorStatusToggleRequest,
    CollectorCapacityResponse,
)
from backend.app.services.job_evaluation_service import JobEvaluationService

router = APIRouter(prefix="/collectors", tags=["Buyer Pre-Acceptance Job Evaluation"])


@router.get("/jobs/{order_id}/evaluate", response_model=JobEvaluationResponse)
def evaluate_job(
    order_id: str,
    saleng_id: Optional[str] = Query("saleng-01", description="รหัสซาเล้ง"),
    saleng_lat: Optional[float] = Query(None, description="พิกัดละติจูดซาเล้ง"),
    saleng_lng: Optional[float] = Query(None, description="พิกัดลองจิจูดซาเล้ง"),
    force_fallback: bool = Query(False, description="บังคับใช้โหมดสำรอง Haversine * 1.35"),
):
    """
    ประเมินรายละเอียดคำขอขาย คำนวณระยะทาง ค่าน้ำมันตามประเภทรถ และตรวจความจุรถก่อนรับ
    (Card 02, REQ-FN-002, REQ-QA-002, REQ-CON-003, AC-B03-01..05)
    """
    try:
        return JobEvaluationService.evaluate_job(
            order_id=order_id,
            saleng_id=saleng_id or "saleng-01",
            saleng_lat=saleng_lat,
            saleng_lng=saleng_lng,
            force_fallback=force_fallback,
        )
    except KeyError as ke:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ke))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"เกิดข้อผิดพลาดในการประเมินคำขอขาย: {str(e)}",
        )


@router.patch("/{saleng_id}/status")
def toggle_online_status(saleng_id: str, req: CollectorStatusToggleRequest):
    """
    สลับสถานะความพร้อมรับงาน Online / Offline และซิงก์พิกัดล่าสุด (CC-02, AC-B03-03)
    """
    if req.saleng_id != saleng_id:
        req.saleng_id = saleng_id

    try:
        updated = JobEvaluationService.toggle_online_status(req)
        return {
            "success": True,
            "message": f"สลับสถานะเป็น {'Online (พร้อมรับงาน)' if req.is_online else 'Offline (พักรับงาน)'} สำเร็จ",
            "profile": updated,
        }
    except KeyError as ke:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ke))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"ไม่สามารถสลับสถานะได้: {str(e)}",
        )


@router.get("/{saleng_id}/capacity", response_model=CollectorCapacityResponse)
def get_collector_capacity(saleng_id: str):
    """
    ดึงข้อมูลความจุรถและน้ำหนักสะสมปัจจุบันของซาเล้งตามกฎ BR-03 (REQ-CON-003)
    """
    try:
        return JobEvaluationService.get_collector_capacity(saleng_id)
    except KeyError as ke:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ke))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"เกิดข้อผิดพลาดในการดึงข้อมูลความจุรถ: {str(e)}",
        )

