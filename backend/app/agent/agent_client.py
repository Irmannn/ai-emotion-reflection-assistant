import json
from collections.abc import AsyncIterator
from typing import Any

from fastapi import HTTPException, status
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from sqlmodel import Session

from app.agent.schemas import AgentChatResponse, AgentStreamEvent, AgentToolCallView, ToolExecutionResult
from app.agent.tool_runner import execute_tool_call_async
from app.langchain.chat_model import get_chat_model
from app.langchain.messages import to_conversation_messages
from app.langchain.tools import get_agent_tools
from app.settings import get_settings

MAX_AGENT_TOOL_ROUNDS = 3
MAX_UPSTREAM_ERROR_LENGTH = 500

AGENT_SYSTEM_PROMPT = """你是一个情绪复盘行动助手。

你的能力：
1. 可以回答用户关于情绪复盘的普通问题。
2. 可以通过工具查询当前用户 session 下的历史复盘。
3. 可以按需检索内置知识库，获取情绪复盘相关的理论、练习和行动建议依据。
4. 可以基于历史复盘和用户目标，整理低风险、可执行的行动建议。

边界：
- 不提供医学诊断、治疗建议或危机干预。
- 如果用户表达自伤、自杀或紧急危机，请建议立即联系身边可信任的人或当地专业机构。
- 只能基于工具返回的当前 session 数据回答，不要声称看到了未提供的数据。
- 当用户的问题需要理论解释、练习方法或资料依据时，可以使用 search_knowledge_base；不需要资料时不要强制调用。
- 内置知识库是共享资料，不等于用户的历史复盘；不要将二者混为一谈。
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
    """Use LangChain messages and tools while retaining the project's execution boundary."""
    _ensure_api_key_configured()
    request_messages = to_conversation_messages(messages, AGENT_SYSTEM_PROMPT)
    tools = get_agent_tools()
    tool_model = get_chat_model("agent").bind_tools(tools, tool_choice="auto").bind(temperature=0.3)
    final_model = get_chat_model("agent").bind_tools(tools, tool_choice="none").bind(temperature=0.3)
    tool_rounds = 0

    while True:
        assistant_message = await _invoke_tool_decision(tool_model, request_messages)
        tool_calls = assistant_message.tool_calls

        if not tool_calls:
            async for content in _stream_final_answer(final_model, request_messages):
                yield AgentStreamEvent(event="delta", data={"content": content})
            return

        if tool_rounds >= MAX_AGENT_TOOL_ROUNDS:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Agent reached the maximum tool call rounds.",
            )
        tool_rounds += 1
        request_messages.append(assistant_message)

        for tool_call in tool_calls:
            tool_name = tool_call.get("name")
            arguments = tool_call.get("args")
            tool_call_id = tool_call.get("id")
            if not isinstance(tool_name, str):
                tool_name = "unknown"
            if not isinstance(arguments, dict):
                arguments = {}
            if not isinstance(tool_call_id, str):
                tool_call_id = "unknown"

            yield AgentStreamEvent(
                event="tool_started",
                data={"tool_name": tool_name, "arguments": arguments},
            )
            execution_result = await execute_tool_call_async(
                tool_name,
                json.dumps(arguments, ensure_ascii=False),
                session_id,
                session,
                conversation_id,
                assistant_message_id,
            )
            tool_view = _to_tool_call_view(execution_result)
            yield AgentStreamEvent(event="tool_completed", data=tool_view.model_dump())
            request_messages.append(
                ToolMessage(
                    content=json.dumps(execution_result.content, ensure_ascii=False),
                    tool_call_id=tool_call_id,
                )
            )


async def _invoke_tool_decision(model: Any, messages: list[BaseMessage]) -> AIMessage:
    try:
        response = await model.ainvoke(messages)
    except Exception as exc:
        _raise_agent_error(exc, streaming=False)
    if not isinstance(response, AIMessage):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Agent API returned an invalid assistant message.",
        )
    return response


async def _stream_final_answer(model: Any, messages: list[BaseMessage]) -> AsyncIterator[str]:
    try:
        async for chunk in model.astream(messages):
            content = _message_text(chunk)
            if content:
                yield content
    except Exception as exc:
        _raise_agent_error(exc, streaming=True)


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


def _to_tool_call_view(result: ToolExecutionResult) -> AgentToolCallView:
    return AgentToolCallView(
        tool_name=result.tool_name,
        arguments=result.arguments,
        result_summary=result.result_summary,
        status=result.status,
        error_message=result.error_message,
    )


def _ensure_api_key_configured() -> None:
    if get_settings().llm_api_key:
        return
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="LLM_API_KEY is not configured on the backend.",
    )


def _raise_agent_error(exc: Exception, *, streaming: bool) -> None:
    prefix = "Agent API streaming request failed" if streaming else "Agent API request failed"
    upstream_status = getattr(exc, "status_code", None)
    if isinstance(upstream_status, int):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"{prefix} with status {upstream_status}: {_truncate_error(str(exc))}",
        ) from exc
    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=f"{prefix}: {type(exc).__name__}.",
    ) from exc


def _truncate_error(text: str) -> str:
    if len(text) <= MAX_UPSTREAM_ERROR_LENGTH:
        return text
    return f"{text[:MAX_UPSTREAM_ERROR_LENGTH]}..."
