import json
from collections.abc import AsyncIterator
from typing import Any

import httpx
from fastapi import HTTPException, status
from sqlmodel import Session

from app.agent.schemas import AgentChatResponse, AgentStreamEvent, AgentToolCallView, ToolExecutionResult
from app.agent.tool_runner import execute_tool_call
from app.agent.tools import TOOL_DEFINITIONS
from app.settings import get_settings

MAX_AGENT_TOOL_ROUNDS = 3
MAX_UPSTREAM_ERROR_LENGTH = 500

AGENT_SYSTEM_PROMPT = """你是一个情绪复盘行动助手。

你的能力：
1. 可以回答用户关于情绪复盘的普通问题。
2. 可以通过工具查询当前用户 session 下的历史复盘。
3. 可以基于历史复盘和用户目标，整理低风险、可执行的行动建议。

边界：
- 不提供医学诊断、治疗建议或危机干预。
- 如果用户表达自伤、自杀或紧急危机，请建议立即联系身边可信任的人或当地专业机构。
- 只能基于工具返回的当前 session 数据回答，不要声称看到了未提供的数据。
- 写操作、删除操作、外部网络访问都不可用。
"""


async def run_agent_chat(message: str, session_id: str, session: Session) -> AgentChatResponse:
    """Keep the Stage 7 endpoint available while Stage 8 uses the stream API."""
    tool_call_views: list[AgentToolCallView] = []
    answer_parts: list[str] = []
    async for event in stream_agent_chat(
        messages=[{"role": "user", "content": message}],
        session_id=session_id,
        session=session,
    ):
        if event.event == "delta":
            answer_parts.append(str(event.data["content"]))
        if event.event == "tool_completed":
            tool_call_views.append(AgentToolCallView(**event.data))
    answer = "".join(answer_parts).strip()
    if not answer:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Agent API returned an empty answer.")
    return AgentChatResponse(answer=answer, tool_calls=tool_call_views)


async def stream_agent_chat(
    messages: list[dict[str, str]],
    session_id: str,
    session: Session,
    conversation_id: str | None = None,
    assistant_message_id: int | None = None,
) -> AsyncIterator[AgentStreamEvent]:
    """Run the tool loop, then stream the model's final natural-language answer."""
    settings = get_settings()
    _ensure_api_key_configured()
    request_messages: list[dict[str, Any]] = [
        {"role": "system", "content": AGENT_SYSTEM_PROMPT},
        *messages,
    ]
    tool_rounds = 0

    async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
        while True:
            data = await _post_tool_decision(client, request_messages)
            assistant_message = _extract_assistant_message(data)
            tool_calls = assistant_message.get("tool_calls") or []

            if not tool_calls:
                async for content in _stream_final_answer(client, request_messages):
                    yield AgentStreamEvent(event="delta", data={"content": content})
                return

            if tool_rounds >= MAX_AGENT_TOOL_ROUNDS:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Agent reached the maximum tool call rounds.",
                )
            tool_rounds += 1
            request_messages.append(_assistant_tool_call_message(assistant_message))

            for tool_call in tool_calls:
                tool_name, arguments = _tool_call_identity(tool_call)
                yield AgentStreamEvent(
                    event="tool_started",
                    data={"tool_name": tool_name, "arguments": arguments},
                )
                execution_result = _execute_native_tool_call(
                    tool_call,
                    session_id,
                    session,
                    conversation_id,
                    assistant_message_id,
                )
                tool_view = _to_tool_call_view(execution_result)
                yield AgentStreamEvent(event="tool_completed", data=tool_view.model_dump())
                request_messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.get("id"),
                        "content": json.dumps(execution_result.content, ensure_ascii=False),
                    }
                )


async def _post_tool_decision(client: httpx.AsyncClient, messages: list[dict[str, Any]]) -> dict[str, Any]:
    settings = get_settings()
    request_body = {
        "model": settings.llm_model,
        "messages": messages,
        "tools": TOOL_DEFINITIONS,
        "tool_choice": "auto",
        "temperature": 0.3,
    }
    try:
        response = await client.post(
            f"{settings.llm_base_url.rstrip('/')}/chat/completions",
            headers=_authorization_headers(),
            json=request_body,
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Agent API request failed with status {exc.response.status_code}: {_safe_response_text(exc.response)}",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Agent API request failed: {type(exc).__name__}.",
        ) from exc
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Agent API returned invalid JSON.",
        ) from exc


async def _stream_final_answer(client: httpx.AsyncClient, messages: list[dict[str, Any]]) -> AsyncIterator[str]:
    settings = get_settings()
    request_body = {
        "model": settings.llm_model,
        "messages": messages,
        "tools": TOOL_DEFINITIONS,
        "tool_choice": "none",
        "temperature": 0.3,
        "stream": True,
    }
    try:
        async with client.stream(
            "POST",
            f"{settings.llm_base_url.rstrip('/')}/chat/completions",
            headers=_authorization_headers(),
            json=request_body,
        ) as response:
            if response.is_error:
                text = (await response.aread()).decode("utf-8", errors="replace").strip()
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Agent API streaming request failed with status {response.status_code}: {_truncate(text)}",
                )
            async for line in response.aiter_lines():
                if not line.startswith("data: "):
                    continue
                payload = line[6:]
                if payload == "[DONE]":
                    return
                try:
                    data = json.loads(payload)
                except json.JSONDecodeError as exc:
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail="Agent API streaming response contained invalid JSON.",
                    ) from exc
                content = data.get("choices", [{}])[0].get("delta", {}).get("content")
                if isinstance(content, str) and content:
                    yield content
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Agent API streaming request failed: {type(exc).__name__}.",
        ) from exc


def _extract_assistant_message(data: dict[str, Any]) -> dict[str, Any]:
    try:
        message = data["choices"][0]["message"]
    except (KeyError, IndexError, TypeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Agent API returned an unexpected response format.",
        ) from exc
    if not isinstance(message, dict):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Agent API returned an invalid assistant message.",
        )
    return message


def _assistant_tool_call_message(message: dict[str, Any]) -> dict[str, Any]:
    return {
        "role": "assistant",
        "content": message.get("content"),
        "tool_calls": message.get("tool_calls", []),
    }


def _tool_call_identity(tool_call: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    function = tool_call.get("function") or {}
    tool_name = function.get("name")
    raw_arguments = function.get("arguments") or "{}"
    if not isinstance(tool_name, str):
        tool_name = "unknown"
    if not isinstance(raw_arguments, str):
        raw_arguments = "{}"
    try:
        arguments = json.loads(raw_arguments)
    except json.JSONDecodeError:
        arguments = {}
    return tool_name, arguments if isinstance(arguments, dict) else {}


def _execute_native_tool_call(
    tool_call: dict[str, Any],
    session_id: str,
    session: Session,
    conversation_id: str | None,
    assistant_message_id: int | None,
) -> ToolExecutionResult:
    function = tool_call.get("function") or {}
    tool_name = function.get("name")
    raw_arguments = function.get("arguments") or "{}"
    if not isinstance(tool_name, str):
        tool_name = "unknown"
    if not isinstance(raw_arguments, str):
        raw_arguments = "{}"
    return execute_tool_call(
        tool_name,
        raw_arguments,
        session_id,
        session,
        conversation_id,
        assistant_message_id,
    )


def _to_tool_call_view(result: ToolExecutionResult) -> AgentToolCallView:
    return AgentToolCallView(
        tool_name=result.tool_name,
        arguments=result.arguments,
        result_summary=result.result_summary,
        status=result.status,
        error_message=result.error_message,
    )


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


def _safe_response_text(response: httpx.Response) -> str:
    return _truncate(response.text.strip())


def _truncate(text: str) -> str:
    if len(text) <= MAX_UPSTREAM_ERROR_LENGTH:
        return text
    return f"{text[:MAX_UPSTREAM_ERROR_LENGTH]}..."
