"""
platforms/youtube.py
YouTubePoster implementation using official YouTube Data API v3.
Supports resumable video upload with title, description, tags, privacy, and thumbnail.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from loguru import logger

from config.settings import get_settings
from core.crews.content_crew import PlatformPost
from platforms.base import BasePoster


class YouTubePoster(BasePoster):
    """
    Concrete implementation of BasePoster for YouTube.
    Uses YouTube Data API v3 with OAuth2 refresh token + resumable upload.
    """

    def __init__(self):
        self.settings = get_settings()
        self._validate_credentials()

        # Build OAuth2 credentials from refresh token (official pattern)
        self.credentials = Credentials(
            None,
            refresh_token=self.settings.youtube_refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.settings.youtube_client_id,
            client_secret=self.settings.youtube_client_secret,
        )

        self.youtube = build("youtube", "v3", credentials=self.credentials)
        logger.info("✅ YouTubePoster initialized with Data API v3")

    def _validate_credentials(self) -> None:
        """Ensure YouTube OAuth credentials are configured."""
        missing = []
        if not self.settings.youtube_client_id:
            missing.append("YOUTUBE_CLIENT_ID")
        if not self.settings.youtube_client_secret:
            missing.append("YOUTUBE_CLIENT_SECRET")
        if not self.settings.youtube_refresh_token:
            missing.append("YOUTUBE_REFRESH_TOKEN")

        if missing:
            raise ValueError(
                f"Missing YouTube credentials: {', '.join(missing)}. "
                "Please configure them in .env (OAuth2 refresh token flow required)."
            )

    def post(self, content: PlatformPost) -> Dict[str, Any]:
        """
        Upload video to YouTube with metadata.

        Args:
            content: PlatformPost with final_text (title + description), video_path, optional image_paths (thumbnail)

        Returns:
            Standardized result dict (status, post_id, error, url)
        """
        try:
            video_path = getattr(content, "video_path", None)
            if not video_path or not os.path.exists(video_path):
                return {
                    "status": "failed",
                    "platform": "youtube",
                    "post_id": None,
                    "error": "YouTube requires a valid local video file (video_path in PlatformPost)",
                }

            # Split final_text: first line = title, rest = description
            lines = content.final_text.strip().split("\n", 1)
            title = lines[0][:70] if lines else "Untitled Video"
            description = lines[1] if len(lines) > 1 else content.final_text

            # Prepare request body
            body = {
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": getattr(content, "tags", ["AI", "content", "socialmedia"]),
                    "categoryId": getattr(content, "category_id", "22"),  # 22 = People & Blogs
                },
                "status": {
                    "privacyStatus": getattr(content, "privacy_status", "unlisted"),
                    "embeddable": True,
                    "license": "youtube",
                },
            }

            # Resumable video upload
            media_body = MediaFileUpload(
                video_path,
                chunksize=10 * 1024 * 1024,  # 10MB chunks
                resumable=True,
            )

            request = self.youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media_body,
            )

            logger.info(f"🚀 Starting resumable YouTube upload: {os.path.basename(video_path)}")
            response = request.execute()

            video_id = response["id"]
            logger.success(f"✅ Successfully uploaded to YouTube | Video ID: {video_id}")

            # Optional thumbnail upload (after video is created)
            thumbnail_paths = getattr(content, "image_paths", None) or []
            if thumbnail_paths and os.path.exists(thumbnail_paths[0]):
                try:
                    thumb_media = MediaFileUpload(thumbnail_paths[0])
                    self.youtube.thumbnails().set(
                        videoId=video_id,
                        media_body=thumb_media,
                    ).execute()
                    logger.info(f"✅ Thumbnail attached: {thumbnail_paths[0]}")
                except Exception as thumb_err:
                    logger.warning(f"Thumbnail upload failed (non-critical): {thumb_err}")

            return {
                "status": "success",
                "platform": "youtube",
                "post_id": video_id,
                "error": None,
                "url": f"https://youtube.com/watch?v={video_id}",
            }

        except Exception as e:
            error_msg = f"YouTube Data API error: {str(e)}"
            logger.error(f"❌ YouTube upload failed: {error_msg}")
            return {
                "status": "failed",
                "platform": "youtube",
                "post_id": None,
                "error": error_msg,
            }


# Clean export for platforms/__init__.py
__all__ = ["YouTubePoster"]