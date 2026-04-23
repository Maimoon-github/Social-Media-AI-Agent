"""
scheduler/queue.py
Redis-backed job queue for async execution of ContentCrew → posting pipelines.
Complements APScheduler for fire-and-forget / high-throughput jobs.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Callable

import redis
from loguru import logger

from config.settings import get_settings


class JobQueue:
    """Simple, reliable Redis queue for immediate async task execution."""

    def __init__(self):
        self.settings = get_settings()
        self.redis = redis.from_url(self.settings.redis_url, decode_responses=True)
        self.queue_name = "social_media_ai_jobs"
        logger.info("✅ JobQueue initialized with Redis backend")

    def enqueue(self, func: Callable, *args, **kwargs) -> str:
        """Enqueue a job (e.g. run_pipeline) for async execution."""
        job_data = {
            "function": func.__name__,
            "args": args,
            "kwargs": kwargs,
            "timestamp": datetime.now().isoformat(),
        }

        job_id = str(self.redis.incr("job_counter"))
        self.redis.rpush(self.queue_name, json.dumps(job_data))

        logger.info(f"📤 Job enqueued | ID: {job_id} | func: {func.__name__}")
        return job_id

    def get_next_job(self) -> dict | None:
        """Pop next job from queue (used by worker)."""
        job_json = self.redis.lpop(self.queue_name)
        if job_json:
            return json.loads(job_json)
        return None


# Global singleton
queue = JobQueue()

__all__ = ["JobQueue", "queue"]