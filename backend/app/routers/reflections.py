from datetime import datetime, timezone
import json
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlmodel import Session, delete, select

from app.database import get_session
from app.llm_client import generate_reflection_report, stream_reflection_report
from app.models import ReflectionRecord, ReflectionReference
from app.rag.retrieval import RetrievedChunk, format_chunks_for_prompt, retrieve_relevant_chunks
from app.schemas import (
    DeleteResponse,
    FeedbackUpdate,
    KnowledgeReference,
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


def create_record_from_report(
    payload: ReflectionCreate,
    ai_report: str,
    session: Session,
    retrieved_chunks: list[RetrievedChunk] | None = None,
) -> ReflectionRecord:
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

    if retrieved_chunks:
        save_references(record, retrieved_chunks, session)

    return record


def save_references(record: ReflectionRecord, retrieved_chunks: list[RetrievedChunk], session: Session) -> None:
    if record.id is None:
        return

    for item in retrieved_chunks:
        if item.chunk.id is None:
            continue
        session.add(
            ReflectionReference(
                reflection_id=record.id,
                knowledge_chunk_id=item.chunk.id,
                source=item.chunk.source,
                title=item.chunk.title,
                content_preview=build_event_summary(item.chunk.content, max_length=160),
                score=item.score,
            )
        )
    session.commit()


def build_reflection_detail(record: ReflectionRecord, session: Session) -> ReflectionDetail:
    if record.id is None:
        references: list[KnowledgeReference] = []
    else:
        reference_records = session.exec(
            select(ReflectionReference)
            .where(ReflectionReference.reflection_id == record.id)
            .order_by(ReflectionReference.score.desc())
        ).all()
        references = [
            KnowledgeReference(
                source=reference.source,
                title=reference.title,
                content_preview=reference.content_preview,
                score=reference.score,
            )
            for reference in reference_records
        ]

    return ReflectionDetail(
        id=record.id or 0,
        session_id=record.session_id,
        event_text=record.event_text,
        emotion_tags=record.emotion_tags,
        emotion_intensity=record.emotion_intensity,
        automatic_thoughts=record.automatic_thoughts,
        body_reaction=record.body_reaction,
        focus_area=record.focus_area,
        ai_report=record.ai_report,
        feedback=record.feedback,
        created_at=record.created_at,
        updated_at=record.updated_at,
        references=references,
    )


def sse_event(event: str, data: dict[str, object]) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.post("", response_model=ReflectionDetail, status_code=status.HTTP_201_CREATED)
async def create_reflection(payload: ReflectionCreate, session: Session = Depends(get_session)) -> ReflectionDetail:
    retrieved_chunks = await retrieve_relevant_chunks(payload, session)
    ai_report = await generate_reflection_report(payload, retrieved_context=format_chunks_for_prompt(retrieved_chunks))
    record = create_record_from_report(payload, ai_report, session, retrieved_chunks)
    return build_reflection_detail(record, session)


@router.post("/stream")
def stream_create_reflection(payload: ReflectionCreate, session: Session = Depends(get_session)) -> StreamingResponse:
    async def event_generator() -> AsyncIterator[str]:
        chunks: list[str] = []
        try:
            retrieved_chunks = await retrieve_relevant_chunks(payload, session)
            retrieved_context = format_chunks_for_prompt(retrieved_chunks)

            async for content in stream_reflection_report(payload, retrieved_context=retrieved_context):
                chunks.append(content)
                yield sse_event("delta", {"content": content})

            ai_report = "".join(chunks).strip()
            if not ai_report:
                yield sse_event("error", {"message": "LLM API returned an empty report."})
                return

            record = create_record_from_report(payload, ai_report, session, retrieved_chunks)
            yield sse_event("done", {"record_id": record.id})
        except HTTPException as exc:
            yield sse_event("error", {"message": exc.detail})
        except Exception:
            yield sse_event("error", {"message": "Reflection stream failed."})

    return StreamingResponse(event_generator(), media_type="text/event-stream")


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
) -> ReflectionDetail:
    record = get_record_for_session(record_id, session_id, session)
    return build_reflection_detail(record, session)


@router.delete("/{record_id}", response_model=DeleteResponse)
def delete_reflection(
    record_id: int,
    session_id: str = Query(..., min_length=1),
    session: Session = Depends(get_session),
) -> DeleteResponse:
    record = get_record_for_session(record_id, session_id, session)
    if record.id is not None:
        session.exec(delete(ReflectionReference).where(ReflectionReference.reflection_id == record.id))
    session.delete(record)
    session.commit()
    return DeleteResponse(deleted=True)


@router.post("/{record_id}/feedback", response_model=ReflectionDetail)
def update_feedback(record_id: int, payload: FeedbackUpdate, session: Session = Depends(get_session)) -> ReflectionDetail:
    record = get_record_for_session(record_id, payload.session_id, session)
    record.feedback = payload.feedback
    record.updated_at = datetime.now(timezone.utc)
    session.add(record)
    session.commit()
    session.refresh(record)
    return build_reflection_detail(record, session)
