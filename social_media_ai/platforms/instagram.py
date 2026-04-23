"""
platforms/instagram.py
InstagramPoster implementation using official Meta Graph API v20.0.
Uses container → publish flow for Business/Creator accounts (image posts).
"""

from __future__ import annotations

import os
import time
from typing import Any, Dict, Optional

import httpx
from loguru import logger

from config.settings import get_settings
from core.crews.content_crew import PlatformPost
from platforms.base import BasePoster


class InstagramPoster(BasePoster):
    """
    Concrete implementation of BasePoster for Instagram.
    Uses Meta Graph API v20.0 container → publish workflow.
    """

    def __init__(self):
        self.settings = get_settings()
        self._validate_credentials()

        self.base_url = "https://graph.instagram.com/v20.0"
        self.client = httpx.Client(timeout=30.0)
        logger.info("✅ InstagramPoster initialized with Graph API v20.0")

    def _validate_credentials(self) -> None:
        """Ensure Instagram Business credentials are configured."""
        if not self.settings.meta_access_token:
            raise ValueError(
                "Missing META_ACCESS_TOKEN. Please configure in .env."
            )
        if not self.settings.instagram_business_account_id:
            raise ValueError(
                "Missing INSTAGRAM_BUSINESS_ACCOUNT_ID. "
                "Please configure in .env (Instagram Business/Creator account ID)."
            )

    def post(self, content: PlatformPost) -> Dict[str, Any]:
        """
        Post content to Instagram via container → publish flow.

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
                    "platform": "instagram",
                    "post_id": None,
                    "error": "Empty caption provided",
                }

            # Image handling (Graph API requires public image_url)
            image_paths = getattr(content, "image_paths", None) or []
            media_container_id = None

            if image_paths:
                # Use first image (Instagram single image post; carousel extension possible later)
                image_path = image_paths[0]
                image_url = self._get_public_image_url(image_path)

                if image_url:
                    media_container_id = self._create_media_container(caption, image_url)
                else:
                    logger.warning(f"Could not resolve public URL for image: {image_path}")
            else:
                logger.warning("Instagram requires media for feed posts. Posting text-only may fail.")

            if not media_container_id:
                return {
                    "status": "failed",
                    "platform": "instagram",
                    "post_id": None,
                    "error": "No valid media container created (image required for Instagram feed)",
                }

            # Poll container status
            status = self._poll_container_status(media_container_id)
            if status != "FINISHED":
                return {
                    "status": "failed",
                    "platform": "instagram",
                    "post_id": None,
                    "error": f"Container processing failed or timed out (status: {status})",
                }

            # Publish the container
            post_id = self._publish_container(media_container_id)

            logger.success(f"✅ Successfully posted to Instagram | Post ID: {post_id}")

            return {
                "status": "success",
                "platform": "instagram",
                "post_id": post_id,
                "error": None,
                "url": f"https://www.instagram.com/p/{post_id}/" if post_id else None,
            }

        except Exception as e:
            error_msg = f"Instagram Graph API error: {str(e)}"
            logger.error(f"❌ Instagram post failed: {error_msg}")
            return {
                "status": "failed",
                "platform": "instagram",
                "post_id": None,
                "error": error_msg,
            }

    def _get_public_image_url(self, image_path: str) -> Optional[str]:
        """Convert local path or return URL (MediaHandler integration point)."""
        if image_path.startswith(("http://", "https://")):
            return image_path
        # TODO: Integrate with utils/media_handler.py for public hosting (S3/Imgur/etc.)
        # For now, log warning and return None (requires public URL)
        logger.warning(
            f"Instagram requires publicly accessible image_url. "
            f"Local path provided: {image_path}. Use MediaHandler to host it."
        )
        return None

    def _create_media_container(self, caption: str, image_url: str) -> Optional[str]:
        """Create media container (Step 1)."""
        url = f"{self.base_url}/{self.settings.instagram_business_account_id}/media"
        params = {
            "access_token": self.settings.meta_access_token,
            "image_url": image_url,
            "caption": caption,
        }

        response = self.client.post(url, params=params)
        response.raise_for_status()
        data = response.json()
        container_id = data.get("id")
        logger.info(f"✅ Media container created: {container_id}")
        return container_id

    def _poll_container_status(self, container_id: str, max_attempts: int = 30) -> str:
        """Poll until container is FINISHED (Step 2)."""
        url = f"{self.base_url}/{container_id}"
        params = {"access_token": self.settings.meta_access_token, "fields": "status"}

        for attempt in range(max_attempts):
            response = self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            status = data.get("status", "UNKNOWN")

            if status == "FINISHED":
                logger.info(f"✅ Container ready: {container_id}")
                return status
            if status in ("ERROR", "EXPIRED"):
                raise RuntimeError(f"Container error: {status}")

            logger.info(f"⏳ Container status: {status} (attempt {attempt+1}/{max_attempts})")
            time.sleep(2)  # exponential backoff can be added later

        raise TimeoutError("Container processing timed out")

    def _publish_container(self, container_id: str) -> Optional[str]:
        """Publish the container (Step 3)."""
        url = f"{self.base_url}/{self.settings.instagram_business_account_id}/media_publish"
        params = {
            "access_token": self.settings.meta_access_token,
            "creation_id": container_id,
        }

        response = self.client.post(url, params=params)
        response.raise_for_status()
        data = response.json()
        post_id = data.get("id")
        return post_id