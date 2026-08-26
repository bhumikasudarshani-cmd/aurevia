from datetime import datetime

from pydantic import BaseModel, Field


class ChatMessageIn(BaseModel):
    session_id: str | None = None  # omit to start a new session
    message: str = Field(min_length=1, max_length=4_000)


class ChatMessageOut(BaseModel):
    session_id: str
    reply: str
    flagged_for_safety: bool = False


class ChatMessageHistoryItem(BaseModel):
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
