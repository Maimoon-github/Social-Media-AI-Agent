"""
platforms/__init__.py
Aggregates all platform poster implementations for easy importing.
"""

from platforms.base import BasePoster

from platforms.twitter import TwitterPoster
from platforms.linkedin import LinkedInPoster
from platforms.instagram import InstagramPoster
from platforms.facebook import FacebookPoster
from platforms.threads import ThreadsPoster
from platforms.youtube import YouTubePoster
from platforms.tiktok import TikTokPoster      # Correct spelling

__all__ = [
    "BasePoster",
    "TwitterPoster",
    "LinkedInPoster",
    "InstagramPoster",
    "FacebookPoster",
    "ThreadsPoster",
    "YouTubePoster",
    "TikTokPoster",
]