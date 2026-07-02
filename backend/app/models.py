from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ReflectionRecord(SQLModel, table=True):
    __tablename__ = "reflection_records"

    id: int | None = Field(default=None, primary_key=True)
    session_id: str = Field(index=True, nullable=False)
    event_text: str
    emotion_tags: str
    emotion_intensity: int
    automatic_thoughts: str
    body_reaction: str
    focus_area: str
    ai_report: str
    feedback: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
