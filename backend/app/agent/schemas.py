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


class AgentConversationCreate(SQLModel):
    session_id: str = Field(min_length=1)


class AgentConversationView(SQLModel):
    id: str
    title: str
    created_at: str
    updated_at: str


class AgentMessageView(SQLModel):
    id: int
    role: str
    content: str
    status: str
    model: str | None = None
    duration_ms: int | None = None
    error_message: str | None = None
    created_at: str
    tool_calls: list[AgentToolCallView] = Field(default_factory=list)


class AgentConversationMessagesResponse(SQLModel):
    conversation: AgentConversationView
    messages: list[AgentMessageView]


class AgentConversationStreamRequest(SQLModel):
    session_id: str = Field(min_length=1)
    message: str = Field(min_length=1)


class AgentStreamEvent(SQLModel):
    event: str
    data: dict[str, Any]


class ToolExecutionResult(SQLModel):
    tool_name: str
    arguments: dict[str, Any]
    content: dict[str, Any]
    result_summary: str
    status: str = "success"
    error_message: str | None = None
