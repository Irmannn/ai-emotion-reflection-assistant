from typing import Any

from pydantic import Field
from sqlmodel import SQLModel


class AgentChatRequest(SQLModel):
    session_id: str = Field(min_length=1)
    message: str = Field(min_length=1)


class AgentToolCallView(SQLModel):
    tool_name: str
    arguments: dict[str, Any]
    result_summary: str
    status: str
    error_message: str | None = None


class AgentChatResponse(SQLModel):
    answer: str
    tool_calls: list[AgentToolCallView] = Field(default_factory=list)


class ToolExecutionResult(SQLModel):
    tool_name: str
    arguments: dict[str, Any]
    content: dict[str, Any]
    result_summary: str
    status: str = "success"
    error_message: str | None = None

