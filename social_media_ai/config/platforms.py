"""
config/platforms.py
Per-platform constraints, character limits, content rules,
and tone/format hints used by the AI content crew.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class PlatformConfig:
    name: str
    display_name: str
    char_limit: int
    supports_images: bool
    supports_video: bool
    supports_hashtags: bool
    supports_links: bool
    ideal_hashtag_count: int
    tone_hint: str
    format_hint: str
    best_post_times: list[str]        # e.g. ["09:00", "17:00"] UTC
    video_max_seconds: Optional[int] = None
    image_aspect_ratios: list[str] = field(default_factory=list)

    def truncate(self, text: str) -> str:
        """Hard-truncate content to platform limit."""
        if len(text) <= self.char_limit:
            return text
        return text[: self.char_limit - 3] + "..."


PLATFORMS: dict[str, PlatformConfig] = {
    "twitter": PlatformConfig(
        name="twitter",
        display_name="Twitter / X",
        char_limit=280,
        supports_images=True,
        supports_video=True,
        supports_hashtags=True,
        supports_links=True,
        ideal_hashtag_count=2,
        tone_hint=(
            "Punchy, conversational, witty. Hook in the first line. "
            "Opinion-driven. End with a call-to-action or question."
        ),
        format_hint=(
            "Max 280 chars. 1-2 hashtags at the end. No em-dash walls. "
            "Short paragraphs or single sentences."
        ),
        best_post_times=["09:00", "12:00", "17:00", "20:00"],
        video_max_seconds=140,
        image_aspect_ratios=["16:9", "1:1"],
    ),
    "linkedin": PlatformConfig(
        name="linkedin",
        display_name="LinkedIn",
        char_limit=3000,
        supports_images=True,
        supports_video=True,
        supports_hashtags=True,
        supports_links=True,
        ideal_hashtag_count=5,
        tone_hint=(
            "Professional but personal. Storytelling with a lesson. "
            "Lead with a bold statement or counterintuitive insight. "
            "End with a question to drive comments."
        ),
        format_hint=(
            "Use line breaks between every 1-2 sentences. "
            "3-7 short paragraphs. 3-5 hashtags at the bottom. "
            "Emojis sparingly as bullet points are fine."
        ),
        best_post_times=["07:30", "12:00", "17:30"],
        video_max_seconds=600,
        image_aspect_ratios=["1:1", "1.91:1"],
    ),
    "instagram": PlatformConfig(
        name="instagram",
        display_name="Instagram",
        char_limit=2200,
        supports_images=True,
        supports_video=True,
        supports_hashtags=True,
        supports_links=False,  # links not clickable in captions
        ideal_hashtag_count=15,
        tone_hint=(
            "Visual storytelling. Lifestyle-driven. Aspirational yet authentic. "
            "Caption should complement the image, not describe it."
        ),
        format_hint=(
            "First 125 chars are visible before 'more'. Start strong. "
            "Up to 30 hashtags (15 ideal). Use \\n\\n breaks. "
            "Emojis are welcome and increase engagement."
        ),
        best_post_times=["08:00", "11:00", "14:00", "19:00"],
        video_max_seconds=60,
        image_aspect_ratios=["1:1", "4:5", "9:16"],
    ),
    "facebook": PlatformConfig(
        name="facebook",
        display_name="Facebook",
        char_limit=63206,
        supports_images=True,
        supports_video=True,
        supports_hashtags=True,
        supports_links=True,
        ideal_hashtag_count=3,
        tone_hint=(
            "Community-focused. Warm and conversational. "
            "Stories and personal anecdotes perform well. "
            "Ask questions to boost organic reach."
        ),
        format_hint=(
            "Keep it under 500 chars for best reach. "
            "Use links naturally in the body. 1-3 hashtags only. "
            "Images and videos dramatically increase engagement."
        ),
        best_post_times=["09:00", "13:00", "19:00"],
        video_max_seconds=14400,
        image_aspect_ratios=["1:1", "1.91:1", "16:9"],
    ),
    "threads": PlatformConfig(
        name="threads",
        display_name="Threads",
        char_limit=500,
        supports_images=True,
        supports_video=True,
        supports_hashtags=True,
        supports_links=True,
        ideal_hashtag_count=3,
        tone_hint=(
            "Casual, conversational, low-pressure. "
            "Raw opinions, questions, behind-the-scenes moments. "
            "Authenticity > polish."
        ),
        format_hint=(
            "Max 500 chars. Very short is fine — even 1-2 sentences. "
            "Threads rewards replies, so end with a hook. "
            "1-3 hashtags max."
        ),
        best_post_times=["09:00", "12:00", "20:00"],
        video_max_seconds=300,
        image_aspect_ratios=["1:1", "9:16"],
    ),
    "youtube": PlatformConfig(
        name="youtube",
        display_name="YouTube",
        char_limit=5000,  # description
        supports_images=False,  # thumbnail only
        supports_video=True,
        supports_hashtags=True,
        supports_links=True,
        ideal_hashtag_count=5,
        tone_hint=(
            "Educational or entertaining. "
            "Title: curiosity gap or clear value promise. "
            "Description: expand on the video, include timestamps, links."
        ),
        format_hint=(
            "Title max 70 chars. Description 500-1000 chars for SEO. "
            "First 2 lines visible before 'Show more'. "
            "Include chapter timestamps if video > 5 min."
        ),
        best_post_times=["15:00", "17:00", "20:00"],
        video_max_seconds=None,
        image_aspect_ratios=["16:9"],
    ),
    "tiktok": PlatformConfig(
        name="tiktok",
        display_name="TikTok",
        char_limit=2200,
        supports_images=False,
        supports_video=True,
        supports_hashtags=True,
        supports_links=False,
        ideal_hashtag_count=5,
        tone_hint=(
            "Trendy, energetic, authentic. Hook viewers in the first 2 seconds. "
            "Script should feel spontaneous, not corporate. "
            "Incorporate trending sounds/formats when relevant."
        ),
        format_hint=(
            "Caption 100-150 chars is ideal. 3-5 hashtags. "
            "Mix niche hashtags (#YourNiche) with broad ones (#FYP). "
            "No links — direct people to bio."
        ),
        best_post_times=["06:00", "10:00", "19:00", "21:00"],
        video_max_seconds=600,
        image_aspect_ratios=["9:16"],
    ),
}


def get_platform(name: str) -> PlatformConfig:
    config = PLATFORMS.get(name.lower())
    if not config:
        raise ValueError(
            f"Unknown platform: '{name}'. "
            f"Available: {list(PLATFORMS.keys())}"
        )
    return config