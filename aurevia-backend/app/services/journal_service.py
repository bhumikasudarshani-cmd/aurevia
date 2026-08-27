from sqlalchemy.orm import Session

from app.models.journal import JournalEntry
from app.schemas.journal import JournalEntryCreate


def create_entry(db: Session, user_id: str, payload: JournalEntryCreate) -> JournalEntry:
    entry = JournalEntry(user_id=user_id, content=payload.content, mood_score=payload.mood_score)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def list_entries(db: Session, user_id: str, limit: int = 50) -> list[JournalEntry]:
    return (
        db.query(JournalEntry)
        .filter(JournalEntry.user_id == user_id)
        .order_by(JournalEntry.created_at.desc())
        .limit(limit)
        .all()
    )


def get_entry(db: Session, user_id: str, entry_id: str) -> JournalEntry | None:
    return (
        db.query(JournalEntry)
        .filter(JournalEntry.id == entry_id, JournalEntry.user_id == user_id)
        .first()
    )


def delete_entry(db: Session, user_id: str, entry_id: str) -> bool:
    entry = get_entry(db, user_id, entry_id)
    if not entry:
        return False
    db.delete(entry)
    db.commit()
    return True
