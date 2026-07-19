from datetime import datetime, timezone
from uuid import uuid4

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


class AgentToolCallLog(SQLModel, table=True):
    __tablename__ = "agent_tool_calls"

    id: int | None = Field(default=None, primary_key=True)
    session_id: str = Field(index=True, nullable=False)
    conversation_id: str | None = Field(default=None, index=True)
    assistant_message_id: int | None = Field(default=None, index=True)
    tool_name: str = Field(index=True, nullable=False)
    arguments_json: str
    result_summary: str
    status: str = Field(index=True, nullable=False)
    error_message: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=utc_now)


class AgentConversation(SQLModel, table=True):
    __tablename__ = "agent_conversations"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    session_id: str = Field(index=True, nullable=False)
    title: str = Field(default="新对话", nullable=False)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now, index=True)


class AgentMessage(SQLModel, table=True):
    __tablename__ = "agent_messages"

    id: int | None = Field(default=None, primary_key=True)
    conversation_id: str = Field(index=True, foreign_key="agent_conversations.id")
    role: str = Field(index=True, nullable=False)
    content: str = Field(default="", nullable=False)
    status: str = Field(default="completed", index=True, nullable=False)
    model: str | None = Field(default=None)
    duration_ms: int | None = Field(default=None)
    error_message: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=utc_now, index=True)
