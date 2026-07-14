from typing import Any

import httpx
from fastapi import HTTPException, status

from app.settings import get_settings


def _embeddings_url(base_url: str) -> str:
    return f"{base_url.rstrip('/')}/embeddings"


def _ensure_embedding_configured() -> None:
    if get_settings().embedding_api_key:
        return
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="EMBEDDING_API_KEY is not configured on the backend.",
    )


async def generate_embedding(text: str) -> list[float]:
    settings = get_settings()
    _ensure_embedding_configured()

    request_body: dict[str, Any] = {
        "model": settings.embedding_model,
        "input": text,
        "encoding_format": "float",
    }
    if settings.embedding_dimensions:
        request_body["dimensions"] = settings.embedding_dimensions

    try:
        async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
            response = await client.post(
                _embeddings_url(settings.embedding_base_url),
                headers={
                    "Authorization": f"Bearer {settings.embedding_api_key}",
                    "Content-Type": "application/json",
                },
                json=request_body,
            )
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Embedding API request failed with status {exc.response.status_code}.",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Embedding API request failed.",
        ) from exc

    try:
        embedding = data["data"][0]["embedding"]
    except (KeyError, IndexError, TypeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Embedding API returned an unexpected response format.",
        ) from exc

    if not isinstance(embedding, list):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Embedding API returned an invalid embedding.",
        )

    return [float(value) for value in embedding]
