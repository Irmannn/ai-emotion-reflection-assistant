import re
from typing import Any

from sqlmodel import Session, select

from app.models import ReflectionRecord, ReflectionReference
from app.rag.retriever import KnowledgeBaseRetriever

MAX_TOOL_RESULT_TEXT_LENGTH = 1200
MAX_KNOWLEDGE_CONTENT_LENGTH = 1600


def list_reflections_tool(session_id: str, session: Session, limit: int = 5) -> dict[str, Any]:
    safe_limit = _clamp_limit(limit)
    records = session.exec(
        select(ReflectionRecord)
        .where(ReflectionRecord.session_id == session_id)
        .order_by(ReflectionRecord.created_at.desc())
        .limit(safe_limit)
    ).all()
    return {
        "records": [_reflection_summary(record) for record in records],
        "count": len(records),
    }


def search_reflections_tool(session_id: str, session: Session, query: str, limit: int = 5) -> dict[str, Any]:
    safe_limit = _clamp_limit(limit)
    terms = _search_terms(query)
    if not terms:
        return {"records": [], "count": 0}

    records = session.exec(
        select(ReflectionRecord)
        .where(ReflectionRecord.session_id == session_id)
        .order_by(ReflectionRecord.created_at.desc())
    ).all()

    matched: list[tuple[int, ReflectionRecord, str]] = []
    for record in records:
        matched_reason, matched_count = _matched_reason(record, terms)
        if not matched_reason:
            continue

        matched.append((matched_count, record, matched_reason))

    matched.sort(key=lambda item: (item[0], item[1].created_at), reverse=True)
    result_records: list[dict[str, Any]] = []
    for _, record, matched_reason in matched[:safe_limit]:
        item = _reflection_summary(record)
        item["matched_reason"] = matched_reason
        result_records.append(item)

    return {
        "records": result_records,
        "count": len(result_records),
        "query": query,
    }


def get_reflection_detail_tool(session_id: str, session: Session, record_id: int) -> dict[str, Any]:
    record = session.exec(
        select(ReflectionRecord).where(
            ReflectionRecord.id == record_id,
            ReflectionRecord.session_id == session_id,
        )
    ).first()
    if record is None:
        return {"record": None, "message": "Reflection record not found in current session."}

    references = session.exec(
        select(ReflectionReference)
        .where(ReflectionReference.reflection_id == record.id)
        .order_by(ReflectionReference.score.desc())
    ).all()

    return {
        "record": {
            **_reflection_summary(record),
            "event_text": record.event_text,
            "automatic_thoughts": record.automatic_thoughts,
            "body_reaction": record.body_reaction,
            "focus_area": record.focus_area,
            "ai_report": _truncate_text(record.ai_report),
            "feedback": record.feedback,
            "references": [
                {
                    "source": reference.source,
                    "title": reference.title,
                    "content_preview": reference.content_preview,
                    "score": reference.score,
                }
                for reference in references
            ],
        }
    }


async def search_knowledge_base_tool(
    session_id: str,
    session: Session,
    query: str,
    limit: int = 3,
) -> dict[str, Any]:
    """Search shared built-in materials without accessing private reflection records."""
    del session_id
    safe_limit = min(max(limit, 1), 5)
    normalized_query = query.strip()
    if not normalized_query:
        return {"references": [], "count": 0, "query": query}

    retriever = KnowledgeBaseRetriever(session=session, top_k=safe_limit)
    await retriever.ainvoke(normalized_query)
    return {
        "references": [
            {
                "source": item.chunk.source,
                "title": item.chunk.title,
                "content": _truncate_knowledge_content(item.chunk.content),
                "score": item.score,
            }
            for item in retriever.latest_chunks
        ],
        "count": len(retriever.latest_chunks),
        "query": normalized_query,
    }


def _reflection_summary(record: ReflectionRecord) -> dict[str, Any]:
    return {
        "id": record.id,
        "event_summary": _build_event_summary(record.event_text),
        "emotion_tags": record.emotion_tags.split(",") if record.emotion_tags else [],
        "emotion_intensity": record.emotion_intensity,
        "focus_area": record.focus_area,
        "created_at": record.created_at.isoformat(),
    }


def _search_terms(query: str) -> list[str]:
    normalized_query = query.strip().lower()
    if not normalized_query:
        return []

    terms = re.split(r"[\s,，、;；。！？!?]+", normalized_query)
    return list(dict.fromkeys(term for term in terms if term))


def _matched_reason(record: ReflectionRecord, terms: list[str]) -> tuple[str, int]:
    fields = {
        "事件描述": record.event_text,
        "情绪标签": record.emotion_tags,
        "分析方向": record.focus_area,
        "自动想法": record.automatic_thoughts,
        "身体反应": record.body_reaction,
        "AI 报告": record.ai_report,
    }
    matched_reasons: list[str] = []
    for term in terms:
        for label, value in fields.items():
            if term in (value or "").lower():
                matched_reasons.append(f"{label}匹配 {term}")
                break
    return "；".join(matched_reasons), len(matched_reasons)


def _build_event_summary(event_text: str, max_length: int = 40) -> str:
    text = event_text.strip()
    if len(text) <= max_length:
        return text
    return f"{text[:max_length]}..."


def _truncate_text(text: str) -> str:
    if len(text) <= MAX_TOOL_RESULT_TEXT_LENGTH:
        return text
    return f"{text[:MAX_TOOL_RESULT_TEXT_LENGTH]}..."


def _truncate_knowledge_content(text: str) -> str:
    if len(text) <= MAX_KNOWLEDGE_CONTENT_LENGTH:
        return text
    return f"{text[:MAX_KNOWLEDGE_CONTENT_LENGTH]}..."


def _clamp_limit(limit: int) -> int:
    return min(max(limit, 1), 10)
