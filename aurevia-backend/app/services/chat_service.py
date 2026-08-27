from sqlalchemy.orm import Session

from app.models.chat import ChatSession, ChatMessage
from app.services import ai_service


def get_or_create_session(db: Session, user_id: str, session_id: str | None) -> ChatSession:
    if session_id:
        session = (
            db.query(ChatSession)
            .filter(ChatSession.id == session_id, ChatSession.user_id == user_id)
            .first()
        )
        if session:
            return session

    session = ChatSession(user_id=user_id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_history(db: Session, session: ChatSession, limit: int = 20) -> list[dict]:
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.created_at.asc())
        .limit(limit)
        .all()
    )
    return [{"role": m.role, "content": m.content} for m in messages]


async def send_message(db: Session, user_id: str, session_id: str | None, message: str):
    session = get_or_create_session(db, user_id, session_id)
    history = get_history(db, session)

    reply_text, flagged = await ai_service.get_ai_reply(message, history)

    db.add(ChatMessage(session_id=session.id, role="user", content=message))
    db.add(ChatMessage(session_id=session.id, role="assistant", content=reply_text))
    db.commit()

    return session.id, reply_text, flagged
