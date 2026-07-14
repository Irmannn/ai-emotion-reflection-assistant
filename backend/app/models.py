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


class KnowledgeChunk(SQLModel, table=True):
    __tablename__ = "knowledge_chunks"

    id: int | None = Field(default=None, primary_key=True)
    source: str = Field(index=True, nullable=False)
    title: str = Field(index=True, nullable=False)
    content: str
    embedding: str
    created_at: datetime = Field(default_factory=utc_now)


class ReflectionReference(SQLModel, table=True):
    __tablename__ = "reflection_references"

    id: int | None = Field(default=None, primary_key=True)
    reflection_id: int = Field(index=True, foreign_key="reflection_records.id")
    knowledge_chunk_id: int = Field(index=True, foreign_key="knowledge_chunks.id")
    source: str
    title: str
    content_preview: str
    score: float
    created_at: datetime = Field(default_factory=utc_now)
