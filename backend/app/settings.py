from functools import lru_cache

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    """Runtime configuration loaded from backend environment variables."""

    llm_api_key: str = Field(default="", alias="LLM_API_KEY")
    llm_base_url: str = Field(default="https://api.openai.com/v1", alias="LLM_BASE_URL")
    llm_model: str = Field(default="gpt-4o-mini", alias="LLM_MODEL")
    llm_timeout_seconds: int = Field(default=60, alias="LLM_TIMEOUT_SECONDS")

    model_config = SettingsConfigDict(extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
