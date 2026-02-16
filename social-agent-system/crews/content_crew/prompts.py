"""
Prompt templates and fragments for content generation.
"""

from typing import Dict, Any

# Platform-specific guidelines
LINKEDIN_GUIDELINES = """
LinkedIn Content Guidelines:
- Professional tone but approachable
- Focus on value and insights
- Character limit: 3000 (optimal: 150-300)
- Hashtags: 3-5 relevant tags
- Structure: Hook → Value → Insights → CTA
- Target: Developers, tech leaders, CTOs
"""

X_GUIDELINES = """
X (Twitter) Content Guidelines:
- Concise and punchy
- Character limit: 280 per tweet
- Thread limit: 10 tweets max
- Hashtags: 1-2 maximum
- Format: Thread-aware storytelling
- Target: Developer community
"""

INSTAGRAM_GUIDELINES = """
Instagram Content Guidelines:
- Visual-first thinking
- Caption limit: 2200 characters
- Hashtags: 10-15 relevant tags
- Tone: Authentic and inspiring
- Must include image description
- Target: Broader tech audience
"""

def get_platform_prompt(platform: str) -> str:
    """Get platform-specific guidelines."""
    prompts = {
        "linkedin": LINKEDIN_GUIDELINES,
        "twitter": X_GUIDELINES,
        "x": X_GUIDELINES,
        "instagram": INSTAGRAM_GUIDELINES
    }
    return prompts.get(platform, "")

# Common prompt fragments
TECH_STACK_CONTEXT = """
Technology Stack Context:
{tech_stack}

Use this to:
- Identify target audience (developers using these technologies)
- Choose relevant hashtags
- Frame technical insights appropriately
"""

DEVELOPER_CONTEXT = """
Developer Profile Context:
- Username: {username}
- Expertise: {expertise}
- Notable Projects: {projects}

Use this to:
- Position the developer's credibility
- Reference their expertise naturally
- Build narrative around their work
"""

def format_tech_stack_context(tech_stack: list) -> str:
    """Format technology stack for prompts."""
    return TECH_STACK_CONTEXT.format(
        tech_stack=", ".join(tech_stack) if tech_stack else "Not specified"
    )

def format_developer_context(profile: Dict[str, Any]) -> str:
    """Format developer profile for prompts."""
    expertise = ", ".join([
        e.get("area") for e in profile.get("expertise_areas", [])
    ])
    projects = ", ".join([
        p.get("name") for p in profile.get("notable_projects", [])[:3]
    ])
    
    return DEVELOPER_CONTEXT.format(
        username=profile.get("username", "Unknown"),
        expertise=expertise or "General development",
        projects=projects or "Various projects"
    )