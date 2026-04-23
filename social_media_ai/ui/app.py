"""Auto-generated stub."""


class UIApp:
    pass
from scheduler.scheduler import scheduler
scheduler.start()

# Daily LinkedIn + Twitter post
scheduler.add_pipeline_job(
    topic="AI agents in 2026",
    platforms=["linkedin", "twitter"],
    brand_voice="confident, data-driven, witty",
    hour=9,
    minute=0
)