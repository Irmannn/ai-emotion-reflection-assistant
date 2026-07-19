import asyncio
import json
from collections.abc import AsyncIterator
from time import perf_counter

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import Session

from app.agent.agent_client import run_agent_chat, stream_agent_chat
from app.agent.conversation_service import (
    build_context_messages,
    complete_assistant_message,
    conversation_view,
    create_conversation,
    create_exchange,
    fail_assistant_message,
    get_conversation_messages,
    get_owned_conversation,
    list_conversations,
    message_view,
)
from app.agent.schemas import (
    AgentChatRequest,
    AgentChatResponse,
    AgentConversationCreate,
    AgentConversationMessagesResponse,
    AgentConversationStreamRequest,
    AgentConversationView,
)
from app.database import get_session
from app.settings import get_settings

router = APIRouter(prefix="/api/agent", tags=["agent"])


@router.post("/chat", response_model=AgentChatResponse)
async def chat_with_agent(payload: AgentChatRequest, session: Session = Depends(get_session)) -> AgentChatResponse:
    """Stage 7 compatibility endpoint. New UI uses the conversation stream endpoint."""
    return await run_agent_chat(payload.message, payload.session_id, session)


@router.post("/conversations", response_model=AgentConversationView)
def create_agent_conversation(
    payload: AgentConversationCreate, session: Session = Depends(get_session)
) -> AgentConversationView:
    return conversation_view(create_conversation(payload.session_id, session))


@router.get("/conversations", response_model=list[AgentConversationView])
def get_agent_conversations(session_id: str, session: Session = Depends(get_session)) -> list[AgentConversationView]:
    return list_conversations(session_id, session)


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=AgentConversationMessagesResponse,
)
def get_agent_conversation_messages(
    conversation_id: str, session_id: str, session: Session = Depends(get_session)
) -> AgentConversationMessagesResponse:
    conversation = get_owned_conversation(conversation_id, session_id, session)
    return AgentConversationMessagesResponse(
        conversation=conversation_view(conversation),
        messages=get_conversation_messages(conversation, session),
    )


@router.post("/conversations/{conversation_id}/stream")
async def stream_agent_conversation(
    conversation_id: str,
    payload: AgentConversationStreamRequest,
    session: Session = Depends(get_session),
) -> StreamingResponse:
    conversation = get_owned_conversation(conversation_id, payload.session_id, session)
    user_message, assistant_message = create_exchange(conversation, payload.message.strip(), session)
    context_messages = build_context_messages(conversation.id, session)

    async def event_generator() -> AsyncIterator[str]:
        started_at = perf_counter()
        answer_parts: list[str] = []
        try:
            yield _sse_event(
                "conversation",
                {
                    "conversation": conversation_view(conversation).model_dump(),
                    "user_message": message_view(user_message, session).model_dump(),
                    "assistant_message": message_view(assistant_message, session).model_dump(),
                },
            )
            async for event in stream_agent_chat(
                messages=context_messages,
                session_id=payload.session_id,
                session=session,
                conversation_id=conversation.id,
                assistant_message_id=assistant_message.id,
            ):
                if event.event == "delta":
                    answer_parts.append(str(event.data["content"]))
                yield _sse_event(event.event, event.data)

            answer = "".join(answer_parts).strip()
            if not answer:
                raise HTTPException(status_code=502, detail="Agent API returned an empty streamed answer.")
            completed_message = complete_assistant_message(
                conversation,
                assistant_message,
                answer,
                get_settings().llm_model,
                _duration_ms(started_at),
                session,
            )
            yield _sse_event(
                "done",
                {
                    "conversation": conversation_view(conversation).model_dump(),
                    "message": message_view(completed_message, session).model_dump(),
                },
            )
        except HTTPException as exc:
            error_message = str(exc.detail)
            fail_assistant_message(
                conversation,
                assistant_message,
                error_message,
                get_settings().llm_model,
                _duration_ms(started_at),
                session,
            )
            yield _sse_event("error", {"message": error_message})
        except asyncio.CancelledError:
            fail_assistant_message(
                conversation,
                assistant_message,
                "Agent stream was cancelled before completion.",
                get_settings().llm_model,
                _duration_ms(started_at),
                session,
            )
            raise
        except Exception as exc:
            error_message = f"Agent stream failed: {type(exc).__name__}."
            fail_assistant_message(
                conversation,
                assistant_message,
                error_message,
                get_settings().llm_model,
                _duration_ms(started_at),
                session,
            )
            yield _sse_event("error", {"message": error_message})

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


def _sse_event(event: str, data: dict[str, object]) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def _duration_ms(started_at: float) -> int:
    return int((perf_counter() - started_at) * 1000)
