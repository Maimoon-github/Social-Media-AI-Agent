"""
utils/logger.py
Centralized structured logging using loguru (0.7.3+).
Configured once with settings.LOG_LEVEL, JSON serialization, file rotation,
and trace ID support for multi-agent CrewAI/LangGraph observability.
"""

from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger

from config.settings import get_settings


def configure_logger() -> None:
    """Configure the global logger once (idempotent)."""
    settings = get_settings()

    # Remove default handlers
    logger.remove()

    # Console sink (human-readable)
    logger.add(
        sys.stdout,
        level=settings.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level> | {extra}",
        colorize=True,
    )

    # JSON file sink (structured, searchable, LangSmith-friendly)
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    logger.add(
        str(log_dir / "social_media_ai_{time:YYYY-MM-DD}.log"),
        level=settings.log_level,
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        serialize=True,  # full JSON with context
        enqueue=True,    # thread-safe for async crews
    )

    logger.info("🚀 Logger configured | level={} | structured JSON enabled", settings.log_level)


# Global singleton logger (auto-configured on first import)
configure_logger() 