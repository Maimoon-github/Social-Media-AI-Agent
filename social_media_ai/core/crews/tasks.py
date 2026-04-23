"""
core/crews/tasks.py
CrewAI Task definitions.  Each task maps to one step in the
content-generation pipeline.
"""
from __future__ import annotations

from crewai import Task

from config.platforms import PlatformConfig
from core.crews.agents import (
    build_content_editor,
    build_content_strategist,
    build_copywriter,
    build_quality_gatekeeper,
    build_seo_hashtag_specialist,
    build_trend_researcher,
)


def build_tasks(
    topic: str,
    platforms: list[PlatformConfig],
    extra_context: str = "",
    brand_voice: str = "professional yet approachable",
) -> list[Task]:
    """
    Build the full ordered task list for the content pipeline.

    Parameters
    ----------
    topic        : The subject / campaign idea.
    platforms    : List of PlatformConfig objects to generate content for.
    extra_context: Any additional briefing (target audience, campaign goals…).
    brand_voice  : Description of the brand's tone of voice.
    """
    platform_names = ", ".join(p.display_name for p in platforms)
    platform_details = "\n".join(
        f"- {p.display_name}: {p.format_hint} | Tone: {p.tone_hint}"
        for p in platforms
    )

    researcher = build_trend_researcher()
    strategist = build_content_strategist()
    writer     = build_copywriter()
    editor     = build_content_editor()
    seo        = build_seo_hashtag_specialist()
    gatekeeper = build_quality_gatekeeper()

    # ── Task 1: Trend Research ────────────────────────────────────────────
    task_research = Task(
        description=f"""
Research the current landscape for the following topic:

TOPIC: {topic}
TARGET PLATFORMS: {platform_names}
EXTRA CONTEXT: {extra_context or "None provided."}

Your research must cover:
1. Top 5 trending angles / sub-topics related to "{topic}" right now.
2. Audience sentiment — what are people saying, feeling, asking?
3. Competitors or industry leaders who are posting about this — what's working for them?
4. Specific data points, statistics, or recent news that would add credibility.
5. Recommended content angle that feels fresh, not overdone.

Deliver a concise research brief (max 600 words) with bullet points.
""",
        expected_output=(
            "A structured research brief with: trending angles (numbered list), "
            "audience insights, competitor analysis, supporting data points, "
            "and a recommended content angle."
        ),
        agent=researcher,
    )

    # ── Task 2: Content Strategy ──────────────────────────────────────────
    task_strategy = Task(
        description=f"""
Using the research brief, develop a content strategy for all platforms.

BRAND VOICE: {brand_voice}
TARGET PLATFORMS WITH REQUIREMENTS:
{platform_details}

For each platform, define:
1. Core message (1 sentence)
2. Emotional hook (what feeling should the audience have after reading?)
3. Content format (e.g., story, list, question, stat-lead, how-to)
4. Call-to-action
5. Unique angle for this platform vs others (avoid copy-pasting!)

Output a strategy brief for each platform.
""",
        expected_output=(
            "Per-platform strategy briefs, each containing: core message, "
            "emotional hook, content format, call-to-action, and unique platform angle."
        ),
        agent=strategist,
        context=[task_research],
    )

    # ── Task 3: Copywriting ───────────────────────────────────────────────
    task_write = Task(
        description=f"""
Write the actual social media posts based on the content strategy.

BRAND VOICE: {brand_voice}
PLATFORMS AND THEIR STRICT CHARACTER/FORMAT RULES:
{platform_details}

For each platform, write:
- The complete post text (respecting character limits strictly)
- A suggested image/video description (1-2 sentences for the creative team)
- An alternative variation (B-copy) for A/B testing

Format your output clearly with platform headers:
===TWITTER===
[post content]
[image description]
[b-copy variation]

===LINKEDIN===
[post content]
...etc.
""",
        expected_output=(
            "Complete post copy for each platform with main copy, "
            "visual description, and B-copy variation. "
            "Platform sections clearly delimited with === PLATFORM === headers."
        ),
        agent=writer,
        context=[task_strategy],
    )

    # ── Task 4: Editing ───────────────────────────────────────────────────
    task_edit = Task(
        description=f"""
Edit and refine all platform posts.

BRAND VOICE: {brand_voice}
CHARACTER LIMITS per platform:
{chr(10).join(f'  - {p.display_name}: {p.char_limit} chars max' for p in platforms)}

Review each post for:
1. Hook strength — does the opening sentence demand attention?
2. Clarity — remove jargon, passive voice, filler words.
3. Brand voice consistency — does it sound like {brand_voice}?
4. Correct character count — flag if over limit and trim.
5. Grammar and punctuation.
6. Platform-native feel — would a native user of this platform write this way?

Return the full edited version maintaining the === PLATFORM === section format.
Include brief editor notes in [brackets] explaining key changes.
""",
        expected_output=(
            "Edited posts for all platforms maintaining the === PLATFORM === "
            "format. Editor notes in [brackets]. Character count noted per post."
        ),
        agent=editor,
        context=[task_write],
    )

    # ── Task 5: SEO & Hashtags ────────────────────────────────────────────
    task_seo = Task(
        description=f"""
Add SEO optimisation and hashtags to all platform posts.

TOPIC: {topic}
PLATFORMS: {platform_names}
IDEAL HASHTAG COUNTS:
{chr(10).join(f'  - {p.display_name}: {p.ideal_hashtag_count} hashtags' for p in platforms)}

For each platform:
1. Append the ideal number of hashtags (mix of broad + niche).
2. For YouTube: write an SEO-optimised title (max 70 chars) and 
   add 5-10 relevant search keywords to the description.
3. For all platforms: suggest a primary keyword to use naturally in the copy.
4. Verify no hashtags are banned or shadowlisted.

Return the complete posts with hashtags appended (maintaining === PLATFORM === format).
""",
        expected_output=(
            "Complete posts with hashtags integrated. YouTube entries include "
            "SEO title and keyword list. === PLATFORM === format maintained."
        ),
        agent=seo,
        context=[task_edit],
    )

    # ── Task 6: Quality Gate ──────────────────────────────────────────────
    task_qa = Task(
        description=f"""
Perform the final quality check on all platform posts.

CHARACTER LIMITS (HARD LIMITS):
{chr(10).join(f'  - {p.display_name}: {p.char_limit} chars' for p in platforms)}

Check each post for:
1. ✅ Character count within limit
2. ✅ No factual errors or unverifiable claims
3. ✅ No hate speech, discriminatory language, or policy violations
4. ✅ No copyright issues (no quoted lyrics, brand names misused, etc.)
5. ✅ Correct hashtag format (# before each)
6. ✅ CTA present and clear
7. ✅ Brand voice: {brand_voice}

Output format per platform:
STATUS: APPROVED / NEEDS_REVISION
CHAR_COUNT: [n]/{p.char_limit}
ISSUES: [list any issues, or "None"]
FINAL_POST: [the final ready-to-publish post text]

Be STRICT on character limits. Trim if needed. Approve good content quickly.
""",
        expected_output=(
            "Quality report and final post text for each platform. "
            "STATUS field must be APPROVED or NEEDS_REVISION. "
            "FINAL_POST contains the exact text to be published."
        ),
        agent=gatekeeper,
        context=[task_seo],
    )

    return [
        task_research,
        task_strategy,
        task_write,
        task_edit,
        task_seo,
        task_qa,
    ]