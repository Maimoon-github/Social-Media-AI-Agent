"""
scheduler/scheduler.py
APScheduler + RedisJobStore for persistent, distributed cron/interval scheduling.
Schedules full ContentCrew → LangGraph → multi-platform posting pipelines.
"""

from __future__ import annotations

from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from loguru import logger

from config.settings import get_settings
from scheduler.queue import queue


class SocialMediaScheduler:
    """Persistent APScheduler with Redis backend."""

    def __init__(self):
        self.settings = get_settings()

        # Redis-backed job store for persistence across restarts
        jobstores = {
            "default": RedisJobStore(
                jobs_key="social_media_jobs",
                run_times_key="social_media_run_times",
                host=self.settings.redis_url.split("://")[-1].split(":")[0],
                port=6379,
                db=0,
            )
        }

        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            timezone=self.settings.timezone,
        )

        logger.info("✅ SocialMediaScheduler initialized with RedisJobStore")

    def start(self) -> None:
        """Start the scheduler (idempotent)."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.success("🚀 APScheduler started with Redis persistence")

    def shutdown(self) -> None:
        """Graceful shutdown."""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=True)
            logger.info("🛑 APScheduler shutdown gracefully")

    def add_pipeline_job(
        self,
        topic: str,
        platforms: list[str],
        brand_voice: str = "professional yet approachable",
        schedule: str = "cron",  # "cron" or "interval"
        **cron_kwargs,
    ) -> str:
        """Schedule a full ContentCrew + posting pipeline."""
        from core.graph.workflow import run_pipeline  # lazy import to avoid circular

        job_id = f"pipeline_{topic.replace(' ', '_')}_{platforms[0]}"

        if schedule == "cron":
            self.scheduler.add_job(
                run_pipeline,
                "cron",
                id=job_id,
                replace_existing=True,
                kwargs={
                    "topic": topic,
                    "platforms": platforms,
                    "brand_voice": brand_voice,
                },
                **cron_kwargs,  # e.g. hour=9, minute=0
            )
        else:
            self.scheduler.add_job(
                run_pipeline,
                "interval",
                id=job_id,
                replace_existing=True,
                kwargs={...},
                **cron_kwargs,
            )

        logger.success(f"📅 Pipeline job scheduled | ID: {job_id} | topic: {topic}")
        return job_id


# Global singleton scheduler
scheduler = SocialMediaScheduler()

__all__ = ["SocialMediaScheduler", "scheduler"]