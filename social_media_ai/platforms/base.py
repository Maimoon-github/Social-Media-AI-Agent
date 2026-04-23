"""
platforms/base.py
Abstract BasePoster interface for all social media platforms.
Enforces the standardized post() contract used by ContentCrew → LangGraph workflow.
"""

from __future__ import annotations

import abc
from typing import Any, Dict

from core.crews.content_crew import PlatformPost


class BasePoster(abc.ABC):
    """
    Abstract base class for all platform-specific posters.

    Every concrete poster (TwitterPoster, LinkedInPoster, etc.)
    MUST implement the post() method with this exact signature.

    This ensures consistent behavior across the entire posting pipeline.
    """

    @abc.abstractmethod
    def post(self, content: PlatformPost) -> Dict[str, Any]:
        """
        Post content to the target platform.

        Args:
            content: PlatformPost object containing:
                - final_text (required)
                - image_paths / video_path (optional, depending on platform)
                - Any platform-specific metadata

        Returns:
            Standardized dictionary with:
            {
                "status": "success" | "failed",
                "platform": str,
                "post_id": str | None,
                "error": str | None,
                "url": str | None,
                ... (platform-specific fields like tweet_id, urn, etc.)
            }
        """
        raise NotImplementedError("Subclasses must implement post()")

    def __str__(self) -> str:
        """Helpful string representation for logging/debugging."""
        return f"{self.__class__.__name__}()"

    def __repr__(self) -> str:
        return self.__str__()
