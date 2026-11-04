"""
FastAPI Router สำหรับระบบจัดการงานและเส้นทางของซาเล้ง (UC-04, UC-09, UC-12, Buyer 04)
รองรับ REQ-BR-002, REQ-SEC-002, REQ-OP-001, CC-01, CC-04, CC-05, BR-02, BR-03, D-B04-01..06
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, status, Query

from backend.app.models.job_route_models import (
    ClaimJobRequest,
    ClaimJobResponse,
    ActiveQueueResponse,
    StartTransitRequest,
    StartTransitResponse,
    CollectorCancelJobRequest,
    CollectorCancelJobResponse,
)
from backend.app.services.job_route_service import JobRouteManagementService

router = APIRouter(prefix="", tags=["Buyer Job & Route Management"])


@router.post("/jobs/{order_id}/claim", response_model=ClaimJobResponse)
def claim_job(order_id: str, req: ClaimJobRequest):
    """
    กดรับงานแบบ Single Collector Atomic Claim ด้วย Optimistic Concurrency Control (OCC)
    (BR-02, REQ-BR-002, CC-04, AC-B04-01, D-B04-01)
    """
    try:
        return JobRouteManagementService.claim_job(order_id=order_id, req=req)
    except KeyError as ke:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ke))
    except PermissionError as pe:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))
    except ValueError as ve:
        err_msg = str(ve)
        if "มีผู้รับงานนี้แล้ว" in err_msg or "version mismatch" in err_msg:
            # 409 Conflict เมื่อมีคนรับตัดหน้า หรือ OCC version ชนกัน (AC-B04-01)
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="มีผู้รับงานนี้แล้ว")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"เกิดข้อผิดพลาดในการกดรับงาน: {str(e)}",
        )


@router.post("/jobs/{order_id}/skip")
def skip_job(order_id: str, saleng_id: str = Query("saleng-01")):
    """
    ข้ามงาน ปิดหน้ารายละเอียด และคงสถานะคำขอขายเป็น S2 (Extension A2, AC-B04-02)
    """
    try:
        return JobRouteManagementService.skip_job(order_id=order_id, saleng_id=saleng_id)
    except KeyError as ke:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ke))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"เกิดข้อผิดพลาดในการข้ามงาน: {str(e)}",
        )


@router.get("/{saleng_id}/active-jobs", response_model=ActiveQueueResponse)
def get_active_queue(
    saleng_id: str,
    saleng_lat: Optional[float] = Query(None, description="พิกัดละติจูดปัจจุบัน"),
    saleng_lng: Optional[float] = Query(None, description="พิกัดลองจิจูดปัจจุบัน"),
):
    """
    ดึงรายการคิวงานสะสมในสถานะ S3 และ S4 พร้อมจัดลำดับเส้นทางและคำนวณน้ำหนักสะสม (BR-03, AC-B04-04)
    """
    try:
        return JobRouteManagementService.get_active_queue(
            saleng_id=saleng_id,
            saleng_lat=saleng_lat,
            saleng_lng=saleng_lng,
        )
    except KeyError as ke:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ke))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"เกิดข้อผิดพลาดในการดึงรายการคิวงาน: {str(e)}",
        )


@router.post("/jobs/{order_id}/start-transit", response_model=StartTransitResponse)
def start_transit(order_id: str, req: StartTransitRequest):
    """
    ยืนยันออกเดินทาง เปลี่ยนสถานะเป็น S4: กำลังเดินทาง และล็อกปุ่มยกเลิกผู้ขาย (UC-09, BR-03, AC-B04-05)
    """
    try:
        return JobRouteManagementService.start_transit(order_id=order_id, req=req)
    except KeyError as ke:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ke))
    except PermissionError as pe:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"เกิดข้อผิดพลาดในการเริ่มออกเดินทาง: {str(e)}",
        )


@router.post("/jobs/{order_id}/cancel", response_model=CollectorCancelJobResponse)
def cancel_job(order_id: str, req: CollectorCancelJobRequest):
    """
    สละสิทธิ์/ยกเลิกงานในสถานะ S3 และคืนสถานะคำขอกลับเป็น S2: รอผู้รับงาน (D-B04-04, MD-STM-04, AC-B04-06)
    """
    try:
        return JobRouteManagementService.cancel_job(order_id=order_id, req=req)
    except KeyError as ke:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ke))
    except PermissionError as pe:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"เกิดข้อผิดพลาดในการยกเลิกงาน: {str(e)}",
        )

