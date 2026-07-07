from typing import Any

import httpx
from fastapi import HTTPException, status

from app.prompts import SYSTEM_PROMPT, build_reflection_user_prompt
from app.schemas import ReflectionCreate
from app.settings import get_settings

MAX_UPSTREAM_ERROR_LENGTH = 500


def _chat_completions_url(base_url: str) -> str:
    return f"{base_url.rstrip('/')}/chat/completions"


def _safe_response_text(response: httpx.Response) -> str:
    text = response.text.strip()
    if len(text) <= MAX_UPSTREAM_ERROR_LENGTH:
        return text
    return f"{text[:MAX_UPSTREAM_ERROR_LENGTH]}..."


async def generate_reflection_report(payload: ReflectionCreate) -> str:
    """Generate a non-streaming Markdown reflection report with an OpenAI-compatible API."""
    settings = get_settings()

    if not settings.llm_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM_API_KEY is not configured on the backend.",
        )

    request_body: dict[str, Any] = {
        "model": settings.llm_model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_reflection_user_prompt(payload)},
        ],
        "temperature": 0.4,
    }

    try:
        async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
            response = await client.post(
                _chat_completions_url(settings.llm_base_url),
                headers={
                    "Authorization": f"Bearer {settings.llm_api_key}",
                    "Content-Type": "application/json",
                },
                json=request_body,
            )
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPStatusError as exc:
        upstream_error = _safe_response_text(exc.response)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"LLM API request failed with status {exc.response.status_code}: {upstream_error}",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="LLM API request failed.",
        ) from exc

    try:
        report = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="LLM API returned an unexpected response format.",
        ) from exc

    if not isinstance(report, str) or not report.strip():
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="LLM API returned an empty report.",
        )

    return report.strip()
