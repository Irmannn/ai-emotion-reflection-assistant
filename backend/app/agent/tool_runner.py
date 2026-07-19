import json
from typing import Any, Callable

from sqlmodel import Session

from app.agent.schemas import ToolExecutionResult
from app.agent.tools import get_reflection_detail_tool, list_reflections_tool, search_reflections_tool
from app.models import AgentToolCallLog

MAX_ARGUMENTS_LOG_LENGTH = 1000
MAX_RESULT_SUMMARY_LENGTH = 240

ToolFunction = Callable[..., dict[str, Any]]

TOOL_REGISTRY: dict[str, ToolFunction] = {
    "list_reflections": list_reflections_tool,
    "search_reflections": search_reflections_tool,
    "get_reflection_detail": get_reflection_detail_tool,
}


def execute_tool_call(
    tool_name: str,
    raw_arguments: str,
    session_id: str,
    session: Session,
    conversation_id: str | None = None,
    assistant_message_id: int | None = None,
) -> ToolExecutionResult:
    arguments = _parse_arguments(raw_arguments)
    tool = TOOL_REGISTRY.get(tool_name)

    if tool is None:
        result = ToolExecutionResult(
            tool_name=tool_name,
            arguments=arguments,
            content={"error": f"Unknown tool: {tool_name}"},
            result_summary=f"未知工具：{tool_name}",
            status="error",
            error_message=f"Unknown tool: {tool_name}",
        )
        _save_tool_call_log(session_id, result, session, conversation_id, assistant_message_id)
        return result

    try:
        content = tool(session_id=session_id, session=session, **arguments)
        result = ToolExecutionResult(
            tool_name=tool_name,
            arguments=arguments,
            content=content,
            result_summary=_summarize_tool_result(tool_name, content),
            status="success",
        )
    except TypeError as exc:
        result = ToolExecutionResult(
            tool_name=tool_name,
            arguments=arguments,
            content={"error": "Invalid tool arguments."},
            result_summary="工具参数不符合要求",
            status="error",
            error_message=str(exc),
        )
    except Exception as exc:
        result = ToolExecutionResult(
            tool_name=tool_name,
            arguments=arguments,
            content={"error": "Tool execution failed."},
            result_summary="工具执行失败",
            status="error",
            error_message=type(exc).__name__,
        )

    _save_tool_call_log(session_id, result, session, conversation_id, assistant_message_id)
    return result


def _parse_arguments(raw_arguments: str) -> dict[str, Any]:
    if not raw_arguments:
        return {}
    try:
        data = json.loads(raw_arguments)
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}
    return data


def _summarize_tool_result(tool_name: str, content: dict[str, Any]) -> str:
    if tool_name in {"list_reflections", "search_reflections"}:
        return f"查询到 {content.get('count', 0)} 条复盘记录"
    if tool_name == "get_reflection_detail":
        return "已读取复盘详情" if content.get("record") else "未找到复盘详情"
    return "工具执行完成"


def _save_tool_call_log(
    session_id: str,
    result: ToolExecutionResult,
    session: Session,
    conversation_id: str | None,
    assistant_message_id: int | None,
) -> None:
    session.add(
        AgentToolCallLog(
            session_id=session_id,
            conversation_id=conversation_id,
            assistant_message_id=assistant_message_id,
            tool_name=result.tool_name,
            arguments_json=_truncate(json.dumps(result.arguments, ensure_ascii=False), MAX_ARGUMENTS_LOG_LENGTH),
            result_summary=_truncate(result.result_summary, MAX_RESULT_SUMMARY_LENGTH),
            status=result.status,
            error_message=_truncate(result.error_message or "", MAX_RESULT_SUMMARY_LENGTH) or None,
        )
    )
    session.commit()


def _truncate(text: str, max_length: int) -> str:
    if len(text) <= max_length:
        return text
    return f"{text[:max_length]}..."
