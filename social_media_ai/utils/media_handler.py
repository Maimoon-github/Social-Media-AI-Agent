"""
utils/media_handler.py
Centralized media handling for all platforms.
Saves, resizes (per PlatformConfig aspect ratios), optimizes with Pillow,
and provides local paths + public URL placeholders for Graph API / TikTok / etc.
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from PIL import Image, ImageOps

from config.platforms import get_platform
from config.settings import get_settings
from loguru import logger


class MediaHandler:
    """Singleton-style media handler for saving and preparing platform-ready media."""

    @staticmethod
    def _ensure_media_dir() -> Path:
        """Create MEDIA_UPLOAD_DIR if missing."""
        media_dir = Path(get_settings().media_upload_dir)
        media_dir.mkdir(parents=True, exist_ok=True)
        return media_dir

    @staticmethod
    def save_image(
        image_bytes_or_path: bytes | str | Path,
        platform: str,
        aspect_ratio: Optional[str] = None,
        prefix: str = "generated",
    ) -> tuple[str, Optional[str]]:
        """
        Save and optimize image for a specific platform.
        Returns (absolute_local_path, public_url_or_None)
        """
        media_dir = MediaHandler._ensure_media_dir()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{prefix}_{platform}_{timestamp}.png"
        output_path = media_dir / filename

        try:
            # Load image
            if isinstance(image_bytes_or_path, (bytes, bytearray)):
                img = Image.open(io.BytesIO(image_bytes_or_path))  # type: ignore
            else:
                img = Image.open(image_bytes_or_path)

            # Resize to platform-specific aspect ratio
            if aspect_ratio:
                cfg = get_platform(platform)
                if aspect_ratio in cfg.image_aspect_ratios or aspect_ratio == "auto":
                    target_w, target_h = MediaHandler._get_dimensions(aspect_ratio)
                    img = ImageOps.fit(img, (target_w, target_h), Image.Resampling.LANCZOS)

            # Optimize and save
            img.save(output_path, format="PNG", optimize=True, compress_level=9)
            logger.success(f"✅ Media saved: {output_path} | platform={platform}")

            # TODO: Replace with real public URL service (S3, Cloudinary, Imgix, etc.)
            public_url = None  # placeholder — update when MediaHandler is extended

            return str(output_path.absolute()), public_url

        except Exception as e:
            logger.error(f"❌ Media save failed for {platform}: {e}")
            raise

    @staticmethod
    def _get_dimensions(aspect_ratio: str) -> tuple[int, int]:
        """Platform-friendly dimensions (matches PlatformConfig)."""
        ratios = {
            "1:1": (1080, 1080),
            "16:9": (1920, 1080),
            "9:16": (1080, 1920),
            "1.91:1": (1200, 630),
            "4:5": (1080, 1350),
        }
        return ratios.get(aspect_ratio, (1080, 1080))

    @staticmethod
    def save_video(video_path: str, platform: str) -> str:
        """Placeholder for future video handling (copy + validate)."""
        # For now just validate and return path (full processing in future)
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video not found: {video_path}")
        logger.info(f"✅ Video ready for {platform}: {video_path}")
        return video_path


# Global instance for easy import
media_handler = MediaHandler()

