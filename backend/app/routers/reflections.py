from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from app.database import get_session
from app.llm_client import generate_reflection_report
from app.models import ReflectionRecord
from app.schemas import (
    DeleteResponse,
    FeedbackUpdate,
    ReflectionCreate,
    ReflectionDetail,
    ReflectionListItem,
)

router = APIRouter(prefix="/api/reflections", tags=["reflections"])


def build_event_summary(event_text: str, max_length: int = 40) -> str:
    text = event_text.strip()
    if len(text) <= max_length:
        return text
    return f"{text[:max_length]}..."


def get_record_for_session(record_id: int, session_id: str, session: Session) -> ReflectionRecord:
    statement = select(ReflectionRecord).where(
        ReflectionRecord.id == record_id,
        ReflectionRecord.session_id == session_id,
    )
    record = session.exec(statement).first()
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reflection record not found")
    return record


@router.post("", response_model=ReflectionDetail, status_code=status.HTTP_201_CREATED)
async def create_reflection(payload: ReflectionCreate, session: Session = Depends(get_session)) -> ReflectionRecord:
    ai_report = await generate_reflection_report(payload)
    record = ReflectionRecord(
        session_id=payload.session_id,
        event_text=payload.event_text,
        emotion_tags=",".join(payload.emotion_tags),
        emotion_intensity=payload.emotion_intensity,
        automatic_thoughts=payload.automatic_thoughts,
        body_reaction=payload.body_reaction,
        focus_area=payload.focus_area,
        ai_report=ai_report,
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


@router.get("", response_model=list[ReflectionListItem])
def list_reflections(
    session_id: str = Query(..., min_length=1),
    session: Session = Depends(get_session),
) -> list[ReflectionListItem]:
    statement = (
        select(ReflectionRecord)
        .where(ReflectionRecord.session_id == session_id)
        .order_by(ReflectionRecord.created_at.desc())
    )
    records = session.exec(statement).all()
    return [
        ReflectionListItem(
            id=record.id or 0,
            event_summary=build_event_summary(record.event_text),
            emotion_tags=record.emotion_tags,
            emotion_intensity=record.emotion_intensity,
            feedback=record.feedback,
            created_at=record.created_at,
        )
        for record in records
    ]


@router.get("/{record_id}", response_model=ReflectionDetail)
def get_reflection(
    record_id: int,
    session_id: str = Query(..., min_length=1),
    session: Session = Depends(get_session),
) -> ReflectionRecord:
    return get_record_for_session(record_id, session_id, session)


@router.delete("/{record_id}", response_model=DeleteResponse)
def delete_reflection(
    record_id: int,
    session_id: str = Query(..., min_length=1),
    session: Session = Depends(get_session),
) -> DeleteResponse:
    record = get_record_for_session(record_id, session_id, session)
    session.delete(record)
    session.commit()
    return DeleteResponse(deleted=True)


@router.post("/{record_id}/feedback", response_model=ReflectionDetail)
def update_feedback(record_id: int, payload: FeedbackUpdate, session: Session = Depends(get_session)) -> ReflectionRecord:
    record = get_record_for_session(record_id, payload.session_id, session)
    record.feedback = payload.feedback
    record.updated_at = datetime.now(timezone.utc)
    session.add(record)
    session.commit()
    session.refresh(record)
    return record
