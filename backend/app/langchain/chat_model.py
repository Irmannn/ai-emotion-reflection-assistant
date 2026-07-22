from functools import lru_cache
from typing import Literal

from langchain_openai import ChatOpenAI

from app.settings import get_settings

ModelPurpose = Literal["agent", "report", "summary"]


def get_model_name(purpose: ModelPurpose) -> str:
    settings = get_settings()
    configured_models = {
        "agent": settings.llm_agent_model,
        "report": settings.llm_report_model,
        "summary": settings.llm_summary_model,
    }
    return configured_models[purpose] or settings.llm_model


@lru_cache
def get_chat_model(purpose: ModelPurpose) -> ChatOpenAI:
    settings = get_settings()
    return ChatOpenAI(
        model=get_model_name(purpose),
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        timeout=settings.llm_timeout_seconds,
    )
