from datetime import datetime

from pydantic import BaseModel, Field


class JournalEntryCreate(BaseModel):
    content: str = Field(min_length=1, max_length=10_000)
    mood_score: int | None = Field(default=None, ge=1, le=10)


class JournalEntryOut(BaseModel):
    id: str
    content: str
    mood_score: int | None
    created_at: datetime

    class Config:
        from_attributes = True
