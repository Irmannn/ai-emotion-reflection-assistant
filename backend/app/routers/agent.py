from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.agent.agent_client import run_agent_chat
from app.agent.schemas import AgentChatRequest, AgentChatResponse
from app.database import get_session

router = APIRouter(prefix="/api/agent", tags=["agent"])


@router.post("/chat", response_model=AgentChatResponse)
async def chat_with_agent(payload: AgentChatRequest, session: Session = Depends(get_session)) -> AgentChatResponse:
    return await run_agent_chat(payload.message, payload.session_id, session)

