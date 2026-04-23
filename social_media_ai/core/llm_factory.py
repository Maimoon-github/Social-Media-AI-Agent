"""
core/llm_factory.py
Factory that returns the correct LangChain ChatModel and CrewAI LLM
based on the LLM_PROVIDER setting.

Supported backends:
  - ollama     → local, free, via langchain-ollama
  - groq       → cloud, free tier, fastest inference
  - openai     → cloud, paid
  - together   → cloud, free tier available
  - anthropic  → cloud, paid
"""
from __future__ import annotations

import os
from functools import lru_cache
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel

from config.settings import get_settings


# ─────────────────────────────────────────────────────────────────────────────
#  LangChain ChatModel
# ─────────────────────────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def get_chat_model(temperature: float = 0.7) -> BaseChatModel:
    """Return the configured LangChain chat model (singleton)."""
    s = get_settings()
    _apply_langsmith_env(s)

    provider = s.llm_provider.lower()

    if provider == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model=s.ollama_model,
            base_url=s.ollama_base_url,
            temperature=temperature,
        )

    elif provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            model=s.groq_model,
            api_key=s.groq_api_key,
            temperature=temperature,
        )

    elif provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=s.openai_model,
            api_key=s.openai_api_key,
            temperature=temperature,
        )

    elif provider == "together":
        # Together AI is OpenAI-API-compatible
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=s.together_model,
            api_key=s.together_api_key,
            base_url="https://api.together.xyz/v1",
            temperature=temperature,
        )

    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model="claude-sonnet-4-20250514",
            api_key=s.anthropic_api_key,
            temperature=temperature,
        )

    else:
        raise ValueError(f"Unknown LLM_PROVIDER: '{provider}'")


# ─────────────────────────────────────────────────────────────────────────────
#  CrewAI LLM
# ─────────────────────────────────────────────────────────────────────────────

def get_crewai_llm(temperature: float = 0.7) -> Any:
    """
    Return a CrewAI-compatible LLM object.
    CrewAI uses LiteLLM under the hood, so we pass model strings in
    LiteLLM format: "ollama/llama3.2", "groq/llama-3.3-70b-versatile", etc.
    """
    s = get_settings()
    from crewai import LLM

    provider = s.llm_provider.lower()

    if provider == "ollama":
        return LLM(
            model=f"ollama/{s.ollama_model}",
            base_url=s.ollama_base_url,
            temperature=temperature,
        )

    elif provider == "groq":
        return LLM(
            model=f"groq/{s.groq_model}",
            api_key=s.groq_api_key,
            temperature=temperature,
        )

    elif provider == "openai":
        return LLM(
            model=f"openai/{s.openai_model}",
            api_key=s.openai_api_key,
            temperature=temperature,
        )

    elif provider == "together":
        return LLM(
            model=f"together_ai/{s.together_model}",
            api_key=s.together_api_key,
            temperature=temperature,
        )

    elif provider == "anthropic":
        return LLM(
            model="anthropic/claude-sonnet-4-20250514",
            api_key=s.anthropic_api_key,
            temperature=temperature,
        )

    else:
        raise ValueError(f"Unknown LLM_PROVIDER: '{provider}'")


# ─────────────────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _apply_langsmith_env(s: Any) -> None:
    """Inject LangSmith env vars so LangChain picks them up automatically."""
    if s.langchain_tracing_v2 and s.langchain_api_key:
        os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
        os.environ.setdefault("LANGCHAIN_API_KEY", s.langchain_api_key)
        os.environ.setdefault("LANGCHAIN_PROJECT", s.langchain_project)
        os.environ.setdefault("LANGCHAIN_ENDPOINT", s.langchain_endpoint)


def model_info() -> dict[str, str]:
    """Return a summary of the currently configured LLM."""
    s = get_settings()
    model_map = {
        "ollama": s.ollama_model,
        "groq": s.groq_model,
        "openai": s.openai_model,
        "together": s.together_model,
        "anthropic": "claude-sonnet-4-20250514",
    }
    return {
        "provider": s.llm_provider,
        "model": model_map.get(s.llm_provider, "unknown"),
        "tracing": str(s.langchain_tracing_v2 and bool(s.langchain_api_key)),
    }