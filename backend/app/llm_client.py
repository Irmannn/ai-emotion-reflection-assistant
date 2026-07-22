from collections.abc import AsyncIterator
from typing import Any

from fastapi import HTTPException, status
from langchain_core.messages import BaseMessage

from app.langchain.chat_model import get_chat_model
from app.langchain.prompts import REFLECTION_PROMPT
from app.prompts import build_reflection_user_prompt
from app.schemas import ReflectionCreate
from app.settings import get_settings

MAX_UPSTREAM_ERROR_LENGTH = 500


def _ensure_api_key_configured() -> None:
    if get_settings().llm_api_key:
        return
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="LLM_API_KEY is not configured on the backend.",
    )


def _reflection_messages(payload: ReflectionCreate, retrieved_context: str) -> list[BaseMessage]:
    user_prompt = build_reflection_user_prompt(payload, retrieved_context=retrieved_context)
    return REFLECTION_PROMPT.format_messages(user_prompt=user_prompt)


async def generate_reflection_report(payload: ReflectionCreate, retrieved_context: str = "") -> str:
    """Generate a non-streaming reflection report through LangChain ChatOpenAI."""
    _ensure_api_key_configured()
    try:
        response = await get_chat_model("report").bind(temperature=0.4).ainvoke(
            _reflection_messages(payload, retrieved_context)
        )
    except Exception as exc:
        _raise_model_error(exc, streaming=False)

    report = _message_text(response)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="LLM API returned an empty report.",
        )
    return report


async def stream_reflection_report(payload: ReflectionCreate, retrieved_context: str = "") -> AsyncIterator[str]:
    """Yield report text chunks through LangChain's normalized streaming interface."""
    _ensure_api_key_configured()
    try:
        async for chunk in get_chat_model("report").bind(temperature=0.4).astream(
            _reflection_messages(payload, retrieved_context)
        ):
            content = _message_text(chunk)
            if content:
                yield content
    except Exception as exc:
        _raise_model_error(exc, streaming=True)


def _message_text(message: Any) -> str:
    content = getattr(message, "content", "")
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""

    parts: list[str] = []
    for block in content:
        if isinstance(block, str):
            parts.append(block)
        elif isinstance(block, dict) and isinstance(block.get("text"), str):
            parts.append(block["text"])
    return "".join(parts)


def _raise_model_error(exc: Exception, *, streaming: bool) -> None:
    prefix = "LLM API streaming request failed" if streaming else "LLM API request failed"
    status_code = getattr(exc, "status_code", None)
    if isinstance(status_code, int):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"{prefix} with status {status_code}: {_truncate_error(str(exc))}",
        ) from exc
    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=f"{prefix}: {type(exc).__name__}.",
    ) from exc


def _truncate_error(text: str) -> str:
    if len(text) <= MAX_UPSTREAM_ERROR_LENGTH:
        return text
    return f"{text[:MAX_UPSTREAM_ERROR_LENGTH]}..."
