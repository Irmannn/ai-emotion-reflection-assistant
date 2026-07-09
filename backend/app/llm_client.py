import json
from collections.abc import AsyncIterator
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
    return _truncate_upstream_error(text)


def _truncate_upstream_error(text: str) -> str:
    if len(text) <= MAX_UPSTREAM_ERROR_LENGTH:
        return text
    return f"{text[:MAX_UPSTREAM_ERROR_LENGTH]}..."


def _build_chat_request_body(payload: ReflectionCreate, *, stream: bool = False) -> dict[str, Any]:
    return {
        "model": get_settings().llm_model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_reflection_user_prompt(payload)},
        ],
        "temperature": 0.4,
        "stream": stream,
    }


def _authorization_headers() -> dict[str, str]:
    settings = get_settings()
    return {
        "Authorization": f"Bearer {settings.llm_api_key}",
        "Content-Type": "application/json",
    }


def _ensure_api_key_configured() -> None:
    if get_settings().llm_api_key:
        return
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="LLM_API_KEY is not configured on the backend.",
    )


async def generate_reflection_report(payload: ReflectionCreate) -> str:
    """Generate a non-streaming Markdown reflection report with an OpenAI-compatible API."""
    settings = get_settings()

    _ensure_api_key_configured()
    request_body = _build_chat_request_body(payload)

    try:
        async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
            response = await client.post(
                _chat_completions_url(settings.llm_base_url),
                headers=_authorization_headers(),
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


async def stream_reflection_report(payload: ReflectionCreate) -> AsyncIterator[str]:
    """Yield Markdown report chunks from an OpenAI-compatible streaming API."""
    settings = get_settings()
    _ensure_api_key_configured()

    try:
        async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
            async with client.stream(
                "POST",
                _chat_completions_url(settings.llm_base_url),
                headers=_authorization_headers(),
                json=_build_chat_request_body(payload, stream=True),
            ) as response:
                if response.is_error:
                    body = (await response.aread()).decode("utf-8", errors="replace").strip()
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"LLM API request failed with status {response.status_code}: {_truncate_upstream_error(body)}",
                    )

                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue

                    raw_data = line.removeprefix("data: ").strip()
                    if raw_data == "[DONE]":
                        break

                    try:
                        data = json.loads(raw_data)
                        content = data["choices"][0]["delta"].get("content")
                    except (json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
                        raise HTTPException(
                            status_code=status.HTTP_502_BAD_GATEWAY,
                            detail="LLM API returned an unexpected streaming response format.",
                        ) from exc

                    if content:
                        yield content
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="LLM API streaming request failed.",
        ) from exc
