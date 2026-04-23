"""
config/settings.py
Centralised, validated configuration via pydantic-settings.
All values are read from environment / .env file.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Literal, Optional

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── LLM Backend ──────────────────────────────────────────────────
    llm_provider: Literal["ollama", "groq", "openai", "together", "anthropic"] = "ollama"

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    ollama_embed_model: str = "nomic-embed-text"

    # Groq
    groq_api_key: Optional[str] = None
    groq_model: str = "llama-3.3-70b-versatile"

    # OpenAI
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"

    # Together
    together_api_key: Optional[str] = None
    together_model: str = "meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo"

    # Anthropic
    anthropic_api_key: Optional[str] = None

    # ── LangSmith ────────────────────────────────────────────────────
    langchain_tracing_v2: bool = True
    langchain_api_key: Optional[str] = None
    langchain_project: str = "social-media-ai"
    langchain_endpoint: str = "https://api.smith.langchain.com"

    # ── Twitter ──────────────────────────────────────────────────────
    twitter_api_key: Optional[str] = None
    twitter_api_secret: Optional[str] = None
    twitter_access_token: Optional[str] = None
    twitter_access_token_secret: Optional[str] = None
    twitter_bearer_token: Optional[str] = None

    # ── LinkedIn ─────────────────────────────────────────────────────
    linkedin_email: Optional[str] = None
    linkedin_password: Optional[str] = None

    # ── Meta (Instagram / Facebook / Threads) ────────────────────────
    meta_app_id: Optional[str] = None
    meta_app_secret: Optional[str] = None
    meta_access_token: Optional[str] = None
    instagram_business_account_id: Optional[str] = None
    facebook_page_id: Optional[str] = None
    threads_user_id: Optional[str] = None

    # ── YouTube ──────────────────────────────────────────────────────
    youtube_client_id: Optional[str] = None
    youtube_client_secret: Optional[str] = None
    youtube_refresh_token: Optional[str] = None

    # ── TikTok ───────────────────────────────────────────────────────
    tiktok_session_id: Optional[str] = None
    tiktok_csrf_token: Optional[str] = None

    # ── Infrastructure ───────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # ── App ──────────────────────────────────────────────────────────
    database_url: str = "sqlite:///./social_media_ai.db"
    media_upload_dir: str = "./media/uploads"
    log_level: str = "INFO"
    timezone: str = "UTC"

    # ── Image Generation ─────────────────────────────────────────────
    image_gen_provider: Literal["dalle", "stable_diffusion", "none"] = "none"
    stable_diffusion_url: str = "http://localhost:7860"

    @model_validator(mode="after")
    def _validate_llm_keys(self) -> "Settings":
        """Ensure the selected provider has the necessary key."""
        required: dict[str, Optional[str]] = {
            "groq": self.groq_api_key,
            "openai": self.openai_api_key,
            "together": self.together_api_key,
            "anthropic": self.anthropic_api_key,
        }
        if self.llm_provider != "ollama":
            key = required.get(self.llm_provider)
            if not key:
                import warnings
                warnings.warn(
                    f"LLM_PROVIDER={self.llm_provider} but no API key found. "
                    "Set the corresponding *_API_KEY environment variable."
                )
        return self

    @field_validator("log_level")
    @classmethod
    def _upper_log(cls, v: str) -> str:
        return v.upper()

    def enabled_platforms(self) -> list[str]:
        """Return list of platforms that have credentials configured."""
        platforms = []
        if all([self.twitter_api_key, self.twitter_access_token]):
            platforms.append("twitter")
        if all([self.linkedin_email, self.linkedin_password]):
            platforms.append("linkedin")
        if all([self.meta_access_token, self.instagram_business_account_id]):
            platforms.append("instagram")
        if all([self.meta_access_token, self.facebook_page_id]):
            platforms.append("facebook")
        if all([self.meta_access_token, self.threads_user_id]):
            platforms.append("threads")
        if all([self.youtube_client_id, self.youtube_refresh_token]):
            platforms.append("youtube")
        if self.tiktok_session_id:
            platforms.append("tiktok")
        return platforms


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cached singleton settings instance."""
    return Settings()