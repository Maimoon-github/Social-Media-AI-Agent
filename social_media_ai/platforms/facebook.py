"""
platforms/facebook.py
FacebookPoster implementation using Meta Graph API v25.0.
Supports text posts (/feed) and photo posts (/photos) for Facebook Pages.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

import httpx
from loguru import logger

from config.settings import get_settings
from core.crews.content_crew import PlatformPost
from platforms.base import BasePoster


class FacebookPoster(BasePoster):
    """
    Concrete implementation of BasePoster for Facebook Pages.
    Uses direct Meta Graph API v25.0 calls (/feed and /photos endpoints).
    """

    def __init__(self):
        self.settings = get_settings()
        self._validate_credentials()

        self.base_url = "https://graph.facebook.com/v25.0"
        self.client = httpx.Client(timeout=30.0)
        logger.info("✅ FacebookPoster initialized with Graph API v25.0")

    def _validate_credentials(self) -> None:
        """Ensure Facebook Page credentials are configured."""
        if not self.settings.meta_access_token:
            raise ValueError(
                "Missing META_ACCESS_TOKEN. Please configure in .env."
            )
        if not self.settings.facebook_page_id:
            raise ValueError(
                "Missing FACEBOOK_PAGE_ID. Please configure in .env."
            )

    def post(self, content: PlatformPost) -> Dict[str, Any]:
        """
        Post content to Facebook Page.

        Args:
            content: PlatformPost with final_text and optional image_paths

        Returns:
            Standardized result dict (status, post_id, error, url)
        """
        try:
            caption = content.final_text.strip()
            if not caption:
                return {
                    "status": "failed",
                    "platform": "facebook",
                    "post_id": None,
                    "error": "Empty caption provided",
                }

            image_paths = getattr(content, "image_paths", None) or []

            if image_paths:
                # Prefer photo endpoint for images
                result = self._post_with_photo(caption, image_paths[0])
            else:
                # Text-only via /feed
                result = self._post_text(caption)

            if result.get("status") == "success":
                logger.success(f"✅ Successfully posted to Facebook | Post ID: {result.get('post_id')}")
            return result

        except Exception as e:
            error_msg = f"Facebook Graph API error: {str(e)}"
            logger.error(f"❌ Facebook post failed: {error_msg}")
            return {
                "status": "failed",
                "platform": "facebook",
                "post_id": None,
                "error": error_msg,
            }

    def _post_text(self, caption: str) -> Dict[str, Any]:
        """Text-only post via /feed endpoint."""
        url = f"{self.base_url}/{self.settings.facebook_page_id}/feed"
        params = {
            "access_token": self.settings.meta_access_token,
            "message": caption,
        }

        response = self.client.post(url, params=params)
        response.raise_for_status()
        data = response.json()
        post_id = data.get("id")

        return {
            "status": "success",
            "platform": "facebook",
            "post_id": post_id,
            "error": None,
            "url": f"https://www.facebook.com/{post_id}" if post_id else None,
        }

    def _post_with_photo(self, caption: str, image_path: str) -> Dict[str, Any]:
        """Photo post via /photos endpoint (requires public image_url)."""
        image_url = self._get_public_image_url(image_path)
        if not image_url:
            logger.warning("Could not get public image URL. Falling back to text-only post.")
            return self._post_text(caption)

        url = f"{self.base_url}/{self.settings.facebook_page_id}/photos"
        params = {
            "access_token": self.settings.meta_access_token,
            "url": image_url,
            "caption": caption,
        }

        response = self.client.post(url, params=params)
        response.raise_for_status()
        data = response.json()
        post_id = data.get("post_id") or data.get("id")

        return {
            "status": "success",
            "platform": "facebook",
            "post_id": post_id,
            "error": None,
            "url": f"https://www.facebook.com/{post_id}" if post_id else None,
        }

    def _get_public_image_url(self, image_path: str) -> Optional[str]:
        """Convert local path to public URL (MediaHandler integration point)."""
        if image_path.startswith(("http://", "https://")):
            return image_path
        # TODO: Integrate with utils/media_handler.py for temporary public hosting
        logger.warning(
            f"Facebook requires publicly accessible image URL. "
            f"Local path provided: {image_path}. Use MediaHandler to host it."
        )
        return None


# Clean export for platforms/__init__.py
__all__ = ["FacebookPoster"]