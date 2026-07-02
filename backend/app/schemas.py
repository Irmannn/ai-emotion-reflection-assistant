from datetime import datetime
from typing import Literal

from pydantic import Field
from sqlmodel import SQLModel


class ReflectionCreate(SQLModel):
    session_id: str = Field(min_length=1)
    event_text: str = Field(min_length=1)
    emotion_tags: list[str] = Field(min_length=1)
    emotion_intensity: int = Field(ge=1, le=10)
    automatic_thoughts: str = ""
    body_reaction: str = ""
    focus_area: str = Field(min_length=1)
    ai_report: str = ""


class ReflectionListItem(SQLModel):
    id: int
    event_summary: str
    emotion_tags: str
    emotion_intensity: int
    feedback: str | None
    created_at: datetime


class ReflectionDetail(SQLModel):
    id: int
    session_id: str
    event_text: str
    emotion_tags: str
    emotion_intensity: int
    automatic_thoughts: str
    body_reaction: str
    focus_area: str
    ai_report: str
    feedback: str | None
    created_at: datetime
    updated_at: datetime


class FeedbackUpdate(SQLModel):
    session_id: str = Field(min_length=1)
    feedback: Literal["helpful", "not_helpful"]


class DeleteResponse(SQLModel):
    deleted: bool
