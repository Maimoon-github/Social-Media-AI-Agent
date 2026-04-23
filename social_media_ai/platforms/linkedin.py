"""
platforms/linkedin.py
LinkedInPoster implementation using linkedin-api (v2.3.1+ unofficial wrapper).
Supports text-only UGC posts with graceful image upload fallback.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

from linkedin_api import Linkedin
from loguru import logger

from config.settings import get_settings
from core.crews.content_crew import PlatformPost
from platforms.base import BasePoster


class LinkedInPoster(BasePoster):
    """
    Concrete implementation of BasePoster for LinkedIn.
    Uses linkedin-api library for organic UGC posts (text + future media support).
    """

    def __init__(self):
        self.settings = get_settings()
        self._validate_credentials()

        try:
            self.linkedin = Linkedin(
                self.settings.linkedin_email,
                self.settings.linkedin_password,
                # debug=True  # uncomment for verbose API debugging
            )
            logger.info("✅ LinkedInPoster initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize LinkedIn client: {e}")
            raise

    def _validate_credentials(self) -> None:
        """Ensure LinkedIn credentials are configured."""
        if not self.settings.linkedin_email or not self.settings.linkedin_password:
            raise ValueError(
                "Missing LinkedIn credentials. Please set LINKEDIN_EMAIL and "
                "LINKEDIN_PASSWORD in your .env file."
            )

    def post(self, content: PlatformPost) -> Dict[str, Any]:
        """
        Post content to LinkedIn as a UGC post.

        Args:
            content: PlatformPost with final_text and optional image_paths

        Returns:
            Standardized result dict (status, post_id, error, url)
        """
        try:
            text = content.final_text.strip()
            if not text:
                return {
                    "status": "failed",
                    "platform": "linkedin",
                    "post_id": None,
                    "error": "Empty post text provided",
                }

            # Image support (linkedin-api upload + UGC attachment)
            image_paths = getattr(content, "image_paths", None) or []
            media_urns = []

            if image_paths:
                for path in image_paths[:4]:  # LinkedIn practical limit
                    if os.path.exists(path):
                        try:
                            # linkedin-api provides upload_image which returns URN
                            urn = self.linkedin.upload_image(path)
                            if urn:
                                media_urns.append(urn)
                                logger.info(f"✅ Uploaded image to LinkedIn: {path}")
                        except Exception as upload_err:
                            logger.warning(f"Image upload failed for {path}: {upload_err}")
                    else:
                        logger.warning(f"Image path not found: {path}")

            # Build UGC payload (text + optional media)
            post_data = {
                "commentary": text,
                "visibility": "PUBLIC",  # or "CONNECTIONS" based on preference
            }

            # Attach media if available (library handles URNs in payload)
            if media_urns:
                post_data["media"] = [{"media": urn} for urn in media_urns]

            # Post via library
            response = self.linkedin.post_ugc(post_data)

            # Extract post identifier (library returns URN or dict)
            post_urn = None
            if isinstance(response, dict):
                post_urn = response.get("urn") or str(response)
            else:
                post_urn = str(response)

            post_id = post_urn.split(":")[-1] if post_urn else None

            logger.success(f"✅ Successfully posted to LinkedIn | URN: {post_urn}")

            return {
                "status": "success",
                "platform": "linkedin",
                "post_id": post_id,
                "urn": post_urn,
                "error": None,
                "url": f"https://www.linkedin.com/feed/update/{post_urn}" if post_urn else None,
            }

        except Exception as e:
            error_msg = f"LinkedIn API error: {str(e)}"
            logger.error(f"❌ LinkedIn post failed: {error_msg}")
            return {
                "status": "failed",
                "platform": "linkedin",
                "post_id": None,
                "error": error_msg,
            }


# Clean export for platforms/__init__.py
__all__ = ["LinkedInPoster"]