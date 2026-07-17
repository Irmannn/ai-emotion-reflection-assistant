from typing import Any

from sqlmodel import Session, select

from app.models import ReflectionRecord, ReflectionReference

MAX_TOOL_RESULT_TEXT_LENGTH = 1200


TOOL_DEFINITIONS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "list_reflections",
            "description": "List recent emotion reflection records for the current session.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of records to return. Use 5 if unsure.",
                        "minimum": 1,
                        "maximum": 10,
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_reflections",
            "description": "Search current session reflection records by keyword, emotion tag, focus area, or report content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Keyword to search, for example 焦虑, 拖延, 直播, 人际关系.",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of matching records to return. Use 5 if unsure.",
                        "minimum": 1,
                        "maximum": 10,
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_reflection_detail",
            "description": "Get full detail for one reflection record in the current session.",
            "parameters": {
                "type": "object",
                "properties": {
                    "record_id": {
                        "type": "integer",
                        "description": "Reflection record ID returned by list_reflections or search_reflections.",
                    }
                },
                "required": ["record_id"],
            },
        },
    },
]


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
    normalized_query = query.strip().lower()
    if not normalized_query:
        return {"records": [], "count": 0}

    records = session.exec(
        select(ReflectionRecord)
        .where(ReflectionRecord.session_id == session_id)
        .order_by(ReflectionRecord.created_at.desc())
    ).all()

    matched: list[dict[str, Any]] = []
    for record in records:
        matched_reason = _matched_reason(record, normalized_query)
        if not matched_reason:
            continue
        item = _reflection_summary(record)
        item["matched_reason"] = matched_reason
        matched.append(item)
        if len(matched) >= safe_limit:
            break

    return {
        "records": matched,
        "count": len(matched),
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


def _reflection_summary(record: ReflectionRecord) -> dict[str, Any]:
    return {
        "id": record.id,
        "event_summary": _build_event_summary(record.event_text),
        "emotion_tags": record.emotion_tags.split(",") if record.emotion_tags else [],
        "emotion_intensity": record.emotion_intensity,
        "focus_area": record.focus_area,
        "created_at": record.created_at.isoformat(),
    }


def _matched_reason(record: ReflectionRecord, query: str) -> str:
    fields = {
        "事件描述": record.event_text,
        "情绪标签": record.emotion_tags,
        "分析方向": record.focus_area,
        "自动想法": record.automatic_thoughts,
        "身体反应": record.body_reaction,
        "AI 报告": record.ai_report,
    }
    for label, value in fields.items():
        if query in (value or "").lower():
            return f"{label}匹配 {query}"
    return ""


def _build_event_summary(event_text: str, max_length: int = 40) -> str:
    text = event_text.strip()
    if len(text) <= max_length:
        return text
    return f"{text[:max_length]}..."


def _truncate_text(text: str) -> str:
    if len(text) <= MAX_TOOL_RESULT_TEXT_LENGTH:
        return text
    return f"{text[:MAX_TOOL_RESULT_TEXT_LENGTH]}..."


def _clamp_limit(limit: int) -> int:
    return min(max(limit, 1), 10)

