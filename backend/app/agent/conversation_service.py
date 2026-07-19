from datetime import datetime

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.agent.schemas import AgentConversationView, AgentMessageView, AgentToolCallView
from app.models import AgentConversation, AgentMessage, AgentToolCallLog, utc_now

CONTEXT_MESSAGE_LIMIT = 12
TITLE_MAX_LENGTH = 28


def create_conversation(session_id: str, session: Session) -> AgentConversation:
    conversation = AgentConversation(session_id=session_id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation


def list_conversations(session_id: str, session: Session) -> list[AgentConversationView]:
    conversations = session.exec(
        select(AgentConversation)
        .where(AgentConversation.session_id == session_id)
        .order_by(AgentConversation.updated_at.desc())
    ).all()
    return [_conversation_view(conversation) for conversation in conversations]


def get_owned_conversation(conversation_id: str, session_id: str, session: Session) -> AgentConversation:
    conversation = session.exec(
        select(AgentConversation).where(
            AgentConversation.id == conversation_id,
            AgentConversation.session_id == session_id,
        )
    ).first()
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent conversation was not found.")
    return conversation


def get_conversation_messages(
    conversation: AgentConversation, session: Session
) -> list[AgentMessageView]:
    messages = session.exec(
        select(AgentMessage)
        .where(AgentMessage.conversation_id == conversation.id)
        .order_by(AgentMessage.created_at.asc(), AgentMessage.id.asc())
    ).all()
    return [_message_view(message, session) for message in messages]


def build_context_messages(conversation_id: str, session: Session) -> list[dict[str, str]]:
    messages = session.exec(
        select(AgentMessage)
        .where(
            AgentMessage.conversation_id == conversation_id,
            AgentMessage.status == "completed",
            AgentMessage.role.in_(["user", "assistant"]),
        )
        .order_by(AgentMessage.created_at.desc(), AgentMessage.id.desc())
        .limit(CONTEXT_MESSAGE_LIMIT)
    ).all()
    return [
        {"role": message.role, "content": message.content}
        for message in reversed(messages)
        if message.content.strip()
    ]


def create_exchange(
    conversation: AgentConversation, user_content: str, session: Session
) -> tuple[AgentMessage, AgentMessage]:
    user_message = AgentMessage(
        conversation_id=conversation.id,
        role="user",
        content=user_content,
    )
    assistant_message = AgentMessage(
        conversation_id=conversation.id,
        role="assistant",
        status="pending",
    )
    if conversation.title == "新对话":
        conversation.title = _build_title(user_content)
    conversation.updated_at = utc_now()
    session.add(user_message)
    session.add(assistant_message)
    session.add(conversation)
    session.commit()
    session.refresh(user_message)
    session.refresh(assistant_message)
    return user_message, assistant_message


def complete_assistant_message(
    conversation: AgentConversation,
    message: AgentMessage,
    content: str,
    model: str,
    duration_ms: int,
    session: Session,
) -> AgentMessage:
    message.content = content
    message.status = "completed"
    message.model = model
    message.duration_ms = duration_ms
    message.error_message = None
    conversation.updated_at = utc_now()
    session.add(message)
    session.add(conversation)
    session.commit()
    session.refresh(message)
    return message


def fail_assistant_message(
    conversation: AgentConversation,
    message: AgentMessage,
    error_message: str,
    model: str,
    duration_ms: int,
    session: Session,
) -> AgentMessage:
    message.status = "failed"
    message.model = model
    message.duration_ms = duration_ms
    message.error_message = error_message
    conversation.updated_at = utc_now()
    session.add(message)
    session.add(conversation)
    session.commit()
    session.refresh(message)
    return message


def message_view(message: AgentMessage, session: Session) -> AgentMessageView:
    return _message_view(message, session)


def conversation_view(conversation: AgentConversation) -> AgentConversationView:
    return _conversation_view(conversation)


def _conversation_view(conversation: AgentConversation) -> AgentConversationView:
    return AgentConversationView(
        id=conversation.id,
        title=conversation.title,
        created_at=_to_isoformat(conversation.created_at),
        updated_at=_to_isoformat(conversation.updated_at),
    )


def _message_view(message: AgentMessage, session: Session) -> AgentMessageView:
    tool_logs = session.exec(
        select(AgentToolCallLog)
        .where(AgentToolCallLog.assistant_message_id == message.id)
        .order_by(AgentToolCallLog.id.asc())
    ).all()
    return AgentMessageView(
        id=message.id or 0,
        role=message.role,
        content=message.content,
        status=message.status,
        model=message.model,
        duration_ms=message.duration_ms,
        error_message=message.error_message,
        created_at=_to_isoformat(message.created_at),
        tool_calls=[
            AgentToolCallView(
                tool_name=log.tool_name,
                arguments={},
                result_summary=log.result_summary,
                status=log.status,
                error_message=log.error_message,
            )
            for log in tool_logs
        ],
    )


def _build_title(content: str) -> str:
    normalized = " ".join(content.split())
    if len(normalized) <= TITLE_MAX_LENGTH:
        return normalized or "新对话"
    return f"{normalized[:TITLE_MAX_LENGTH]}..."


def _to_isoformat(value: datetime) -> str:
    return value.isoformat()
