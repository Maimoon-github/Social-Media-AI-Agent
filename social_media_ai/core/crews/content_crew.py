"""
core/crews/content_crew.py
Main CrewAI crew that orchestrates the 6-agent content pipeline.
Returns a structured ContentResult with per-platform ready-to-post content.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from crewai import Crew, Process
from loguru import logger

from config.platforms import PlatformConfig, get_platform
from core.crews.agents import (
    build_content_editor,
    build_content_strategist,
    build_copywriter,
    build_quality_gatekeeper,
    build_seo_hashtag_specialist,
    build_trend_researcher,
)
from core.crews.tasks import build_tasks


# ─────────────────────────────────────────────────────────────────────────────
#  Data Models
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class PlatformPost:
    platform: str
    status: str                      # "APPROVED" | "NEEDS_REVISION"
    final_text: str
    char_count: int
    char_limit: int
    issues: list[str] = field(default_factory=list)
    image_description: Optional[str] = None
    b_copy: Optional[str] = None


@dataclass
class ContentResult:
    topic: str
    posts: dict[str, PlatformPost]  # platform_name → PlatformPost
    raw_crew_output: str
    approved_platforms: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.approved_platforms = [
            p for p, post in self.posts.items()
            if post.status == "APPROVED"
        ]

    def get_post(self, platform: str) -> Optional[PlatformPost]:
        return self.posts.get(platform.lower())


# ─────────────────────────────────────────────────────────────────────────────
#  Content Crew
# ─────────────────────────────────────────────────────────────────────────────

class ContentCrew:
    """
    Wraps CrewAI setup and exposes a single `generate()` method.

    Usage:
        crew = ContentCrew()
        result = crew.generate(
            topic="The future of remote work",
            platforms=["twitter", "linkedin", "instagram"],
            brand_voice="confident, data-driven, occasionally humorous",
        )
        for platform, post in result.posts.items():
            print(platform, post.final_text)
    """

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self._agents = {
            "researcher":  build_trend_researcher(),
            "strategist":  build_content_strategist(),
            "writer":      build_copywriter(),
            "editor":      build_content_editor(),
            "seo":         build_seo_hashtag_specialist(),
            "gatekeeper":  build_quality_gatekeeper(),
        }

    def generate(
        self,
        topic: str,
        platforms: list[str],
        extra_context: str = "",
        brand_voice: str = "professional yet approachable",
    ) -> ContentResult:
        """
        Run the full 6-agent content pipeline.

        Parameters
        ----------
        topic        : The content topic or campaign idea.
        platforms    : List of platform names (e.g. ["twitter", "linkedin"]).
        extra_context: Extra briefing text (audience, goals, constraints).
        brand_voice  : Description of desired brand voice.

        Returns
        -------
        ContentResult with per-platform PlatformPost objects.
        """
        platform_configs: list[PlatformConfig] = [
            get_platform(p) for p in platforms
        ]

        logger.info(
            f"🚀 Starting ContentCrew | topic='{topic}' | "
            f"platforms={platforms} | provider=content_crew"
        )

        tasks = build_tasks(
            topic=topic,
            platforms=platform_configs,
            extra_context=extra_context,
            brand_voice=brand_voice,
        )

        crew = Crew(
            agents=list(self._agents.values()),
            tasks=tasks,
            process=Process.sequential,   # researcher → strategist → writer → editor → seo → gatekeeper
            verbose=self.verbose,
            memory=True,                  # agents share memory across tasks
            embedder={
                "provider": "ollama",
                "config": {"model": "nomic-embed-text"},
            } if _is_ollama() else {"provider": "openai"},
        )

        raw_output: str = crew.kickoff(inputs={
            "topic": topic,
            "platforms": ", ".join(p.display_name for p in platform_configs),
            "brand_voice": brand_voice,
            "extra_context": extra_context,
        })

        logger.info("✅ ContentCrew finished. Parsing output…")

        posts = _parse_qa_output(raw_output, platform_configs)

        result = ContentResult(
            topic=topic,
            posts=posts,
            raw_crew_output=str(raw_output),
        )

        logger.info(
            f"📊 ContentResult: approved={result.approved_platforms} | "
            f"total_platforms={len(posts)}"
        )
        return result


# ─────────────────────────────────────────────────────────────────────────────
#  Output Parser
# ─────────────────────────────────────────────────────────────────────────────

def _parse_qa_output(
    raw: str,
    platform_configs: list[PlatformConfig],
) -> dict[str, PlatformPost]:
    """
    Parse the quality-gatekeeper's structured output into PlatformPost objects.

    Expected format per platform:
        STATUS: APPROVED
        CHAR_COUNT: 278/280
        ISSUES: None
        FINAL_POST: <actual post text>
    """
    posts: dict[str, PlatformPost] = {}
    raw_str = str(raw)

    # Build a lookup: display_name → internal name
    name_map = {cfg.display_name.lower(): cfg.name for cfg in platform_configs}
    name_map.update({cfg.name: cfg.name for cfg in platform_configs})
    limit_map = {cfg.name: cfg.char_limit for cfg in platform_configs}

    # Split on === PLATFORM === markers (case-insensitive, flexible spacing)
    sections = re.split(r"===\s*(.+?)\s*===", raw_str, flags=re.IGNORECASE)

    # sections[0] = text before first ===
    # sections[1], sections[2], sections[3], sections[4] …  (alternating name/body)
    for i in range(1, len(sections) - 1, 2):
        section_title = sections[i].strip().lower()
        section_body  = sections[i + 1].strip()

        # Resolve platform name
        platform_name = _resolve_platform(section_title, name_map)
        if not platform_name:
            logger.warning(f"Could not resolve platform from section: '{section_title}'")
            continue

        char_limit = limit_map.get(platform_name, 3000)

        # Extract fields
        status     = _extract_field(section_body, "STATUS", default="NEEDS_REVISION")
        char_str   = _extract_field(section_body, "CHAR_COUNT", default="0")
        issues_str = _extract_field(section_body, "ISSUES", default="None")
        final_post = _extract_field(section_body, "FINAL_POST", default=section_body[:500])

        # Parse char count  e.g. "278/280"
        char_count = _parse_char_count(char_str)

        issues = (
            []
            if issues_str.strip().lower() in ("none", "no issues", "-", "")
            else [i.strip() for i in issues_str.split(";") if i.strip()]
        )

        posts[platform_name] = PlatformPost(
            platform=platform_name,
            status=status.upper(),
            final_text=final_post.strip(),
            char_count=char_count if char_count else len(final_post),
            char_limit=char_limit,
            issues=issues,
        )

    # Fallback: if parser found nothing, create a single generic entry
    if not posts:
        logger.warning("Parser found no structured sections — using raw output as fallback.")
        for cfg in platform_configs:
            posts[cfg.name] = PlatformPost(
                platform=cfg.name,
                status="NEEDS_REVISION",
                final_text=raw_str[:cfg.char_limit],
                char_count=min(len(raw_str), cfg.char_limit),
                char_limit=cfg.char_limit,
                issues=["Auto-parse failed — please review raw output manually."],
            )

    return posts


def _resolve_platform(title: str, name_map: dict[str, str]) -> Optional[str]:
    for key, val in name_map.items():
        if key in title:
            return val
    return None


def _extract_field(text: str, field_name: str, default: str = "") -> str:
    pattern = rf"{field_name}\s*:\s*(.+?)(?=\n[A-Z_]+\s*:|$)"
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return default


def _parse_char_count(char_str: str) -> int:
    """Parse strings like '278/280' or '278' → integer."""
    match = re.search(r"(\d+)", char_str)
    return int(match.group(1)) if match else 0


def _is_ollama() -> bool:
    from config.settings import get_settings
    return get_settings().llm_provider == "ollama"