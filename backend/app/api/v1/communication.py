"""
FastAPI Router for Communication (In-App Chat & Quick Call)
รองรับ UC-08, REQ-UX-001, REQ-SEC-001, REQ-SEC-002, CC-01, CC-04, CC-06, D-B05-01..06
"""

from fastapi import APIRouter, HTTPException, Query, status
from backend.app.models.communication_models import (
    ChatMessageResponse,
    ChatRoomResponse,
    LogCallRequest,
    LogCallResponse,
    QuickRepliesResponse,
    SendChatMessageRequest,
)
from backend.app.services.communication_service import CommunicationService

router = APIRouter(prefix="/chat", tags=["communication"])


@router.get("/quick-replies", response_model=QuickRepliesResponse)
def get_quick_replies():
    """
    ดึงรายการข้อความด่วนสำเร็จรูป 4 ข้อความมาตรฐาน (AC-B05-02, D-B05-03)
    """
    return CommunicationService.get_quick_replies()


@router.get("/{order_id}/messages", response_model=ChatRoomResponse)
def get_chat_room(
    order_id: str,
    saleng_id: str = Query(..., description="รหัสซาเล้งผู้เข้าใช้งาน"),
):
    """
    ดึงประวัติข้อความแชต ข้อมูลติดต่อผู้ขาย และสถานะห้องแชต (AC-B05-01, AC-B05-04, AC-B05-05)
    """
    try:
        return CommunicationService.get_chat_room(order_id=order_id, saleng_id=saleng_id)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e).strip("'"))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/{order_id}/messages",
    response_model=ChatMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def send_chat_message(
    order_id: str,
    payload: SendChatMessageRequest,
):
    """
    ส่งข้อความแชตใหม่ (ข้อความอิสระ หรือ Quick Reply) (AC-B05-01, AC-B05-02)
    """
    try:
        return CommunicationService.send_message(order_id=order_id, req=payload)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e).strip("'"))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{order_id}/call-log", response_model=LogCallResponse)
def log_quick_call(
    order_id: str,
    payload: LogCallRequest,
):
    """
    บันทึก Audit Log เมื่อซาเล้งกดปุ่มโทรด่วน Native Phone Dialer (AC-B05-03, REQ-SEC-001)
    """
    try:
        return CommunicationService.log_call(order_id=order_id, req=payload)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e).strip("'"))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

