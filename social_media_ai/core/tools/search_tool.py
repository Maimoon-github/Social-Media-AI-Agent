"""
core/tools/search_tool.py
Reusable LangChain/CrewAI web search tools.
Primary: DuckDuckGo (free, no key)
Fallback: Serper (Google SERP) if SERPER_API_KEY is configured.

Exposes get_search_tool() and get_website_search_tool() as required by agents.py.
"""

from __future__ import annotations

import os
from typing import Any, Optional, Type

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import Field, create_model

from config.settings import get_settings

# ─────────────────────────────────────────────────────────────────────────────
#  Imports with graceful fallbacks (2026 stable)
# ─────────────────────────────────────────────────────────────────────────────
try:
    from langchain_community.tools import DuckDuckGoSearchRun
    DUCKDUCKGO_AVAILABLE = True
except ImportError:
    DUCKDUCKGO_AVAILABLE = False

try:
    from langchain_community.utilities.google_serper import GoogleSerperAPIWrapper
    SERPER_AVAILABLE = True
except ImportError:
    SERPER_AVAILABLE = False


class _BaseSearchTool(BaseTool):
    """Base class for search tools with smart DuckDuckGo + Serper fallback."""

    max_results: int = Field(default=6, description="Maximum number of results to return")
    args_schema: Type = create_model(  # explicit schema for CrewAI/LangChain agents
        "SearchInput",
        query=(str, Field(..., description="The search query to execute")),
    )

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Execute search with intelligent fallback logic."""
        if not query or len(query.strip()) < 3:
            return "❌ Error: Query too short. Provide a meaningful search query (min 3 chars)."

        settings = get_settings()

        # Prefer Serper if API key is present (higher quality Google results)
        serper_key = (
            getattr(settings, "serper_api_key", None)
            or os.getenv("SERPER_API_KEY")
        )

        if serper_key and SERPER_AVAILABLE:
            try:
                wrapper = GoogleSerperAPIWrapper(
                    serper_api_key=serper_key,
                    k=self.max_results,
                    gl="us",
                    hl="en",
                )
                results = wrapper.results(query)
                if results and isinstance(results, dict) and "organic" in results:
                    formatted = []
                    for item in results["organic"][: self.max_results]:
                        formatted.append(
                            f"• {item.get('title', 'No title')}\n"
                            f"  {item.get('snippet', 'No snippet')}\n"
                            f"  🔗 {item.get('link', 'No link')}\n"
                        )
                    return "\n".join(formatted) or "No results found."
            except Exception:
                # Silent fallback to DuckDuckGo on any Serper issue
                pass

        # DuckDuckGo fallback (free & reliable)
        if DUCKDUCKGO_AVAILABLE:
            try:
                search = DuckDuckGoSearchRun()
                # DuckDuckGoSearchRun respects max_results via run() in current versions
                return search.run(query)
            except Exception as e:
                return f"❌ DuckDuckGo search failed: {str(e)}. Try a more specific query."

        return (
            "❌ No search tools available. "
            "Please install: pip install duckduckgo-search langchain-community"
        )

    async def _arun(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Async support (delegates to sync implementation)."""
        return self._run(query, run_manager)


# ─────────────────────────────────────────────────────────────────────────────
#  Public Factory Functions (exactly as imported in agents.py)
# ─────────────────────────────────────────────────────────────────────────────

def get_search_tool() -> BaseTool:
    """General web search tool for TrendResearcher and SEOHashtagSpecialist."""
    return _BaseSearchTool(
        name="web_search",
        description=(
            "Search the internet for current information, trends, statistics, "
            "news, audience sentiment, and real-time data. "
            "Best for general research and trending angles."
        ),
    )


def get_website_search_tool() -> BaseTool:
    """Specialized tool for deeper research (supports site: operator, etc.)."""
    tool = _BaseSearchTool(
        name="website_research",
        description=(
            "In-depth research tool optimized for specific sites, companies, "
            "or topics. Supports advanced operators (site:example.com, "
            "after:2025, filetype:pdf, etc.). Ideal for competitor analysis "
            "and detailed SEO/hashtag research."
        ),
    )
    tool.max_results = 8  # deeper results for website-focused queries
    return tool
