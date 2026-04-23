"""
platforms/__init__.py
Aggregates all platform poster implementations for easy importing.
"""

from platforms.base import BasePoster
from platforms.linkedin import LinkedInPoster
from platforms.twitter import TwitterPoster
from platforms.youtube import YouTubePoster
from platforms.tiktok import TiktokPoster
from platforms.instagram import InstagranPoster
from platforms.facebook import FacebookPoster
from platforms.threads import ThreadsPoster


__all__ = [
    "BasePoster",
    "LinkedInPoster",
    "TwitterPoster",
    "YouTubePoster",
    "TiktokPoster",
    "InstagranPoster",
    "FacebookPoster",
    "ThreadsPoster",
]