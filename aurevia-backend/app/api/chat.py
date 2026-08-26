from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.chat import ChatMessageIn, ChatMessageOut
from app.services import chat_service
from app.services.ai_service import AIServiceError

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatMessageOut)
async def send_message(
    payload: ChatMessageIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        session_id, reply, flagged = await chat_service.send_message(
            db, current_user.id, payload.session_id, payload.message
        )
    except AIServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))

    return ChatMessageOut(session_id=session_id, reply=reply, flagged_for_safety=flagged)
