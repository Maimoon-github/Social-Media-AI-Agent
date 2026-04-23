"""
platforms/twitter.py
Twitter/X Poster implementation using Tweepy v4.16+ (hybrid OAuth 1.0a + v2).
Supports text-only and image-attached posts via verified media_upload + create_tweet pattern.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import tweepy
from loguru import logger

from config.settings import get_settings
from core.crews.content_crew import PlatformPost
from platforms.base import BasePoster


class TwitterPoster(BasePoster):
    """
    Concrete implementation of BasePoster for Twitter/X.
    Uses hybrid auth pattern required for media uploads in Tweepy v4+.
    """

    def __init__(self):
        self.settings = get_settings()
        self._validate_credentials()

        # OAuth 1.0a handler for media uploads (v1.1 endpoint)
        auth = tweepy.OAuth1UserHandler(
            consumer_key=self.settings.twitter_api_key,
            consumer_secret=self.settings.twitter_api_secret,
            access_token=self.settings.twitter_access_token,
            access_token_secret=self.settings.twitter_access_token_secret,
        )
        self.api = tweepy.API(auth, wait_on_rate_limit=True)

        # v2 Client for posting tweets
        self.client = tweepy.Client(
            consumer_key=self.settings.twitter_api_key,
            consumer_secret=self.settings.twitter_api_secret,
            access_token=self.settings.twitter_access_token,
            access_token_secret=self.settings.twitter_access_token_secret,
            wait_on_rate_limit=True,
        )

        logger.info("✅ TwitterPoster initialized with hybrid Tweepy auth")

    def _validate_credentials(self) -> None:
        """Ensure all required Twitter credentials are configured."""
        missing = []
        if not self.settings.twitter_api_key:
            missing.append("TWITTER_API_KEY")
        if not self.settings.twitter_api_secret:
            missing.append("TWITTER_API_SECRET")
        if not self.settings.twitter_access_token:
            missing.append("TWITTER_ACCESS_TOKEN")
        if not self.settings.twitter_access_token_secret:
            missing.append("TWITTER_ACCESS_TOKEN_SECRET")

        if missing:
            raise ValueError(
                f"Missing Twitter credentials: {', '.join(missing)}. "
                "Please configure them in .env file."
            )

    def post(self, content: PlatformPost) -> Dict[str, Any]:
        """
        Post content to Twitter/X.

        Args:
            content: PlatformPost containing final_text and optional image_paths

        Returns:
            Dict with status, tweet_id, media_ids, error
        """
        try:
            text = content.final_text.strip()
            media_ids: List[str] = []

            # Handle image uploads (up to 4 per tweet)
            image_paths = getattr(content, 'image_paths', None) or []
            if image_paths:
                for path in image_paths[:4]:  # Twitter limit
                    if os.path.exists(path):
                        try:
                            media = self.api.media_upload(filename=str(path))
                            media_ids.append(media.media_id_string)
                            logger.info(f"✅ Uploaded media for Twitter: {path}")
                        except Exception as upload_err:
                            logger.warning(f"Failed to upload image {path}: {upload_err}")
                    else:
                        logger.warning(f"Image path not found: {path}")

            # Post the tweet
            response = self.client.create_tweet(
                text=text,
                media_ids=media_ids if media_ids else None,
            )

            tweet_id = str(response.data['id']) if response.data and 'id' in response.data else None

            logger.success(f"✅ Successfully posted to Twitter | Tweet ID: {tweet_id}")

            return {
                "status": "success",
                "platform": "twitter",
                "tweet_id": tweet_id,
                "media_ids": media_ids,
                "error": None,
                "url": f"https://x.com/i/web/status/{tweet_id}" if tweet_id else None,
            }

        except tweepy.TweepyException as e:
            error_msg = f"Tweepy error: {str(e)}"
            logger.error(f"❌ Twitter post failed: {error_msg}")
            return {
                "status": "failed",
                "platform": "twitter",
                "tweet_id": None,
                "media_ids": None,
                "error": error_msg,
            }

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"❌ Twitter posting exception: {error_msg}")
            return {
                "status": "failed",
                "platform": "twitter",
                "tweet_id": None,
                "media_ids": None,
                "error": error_msg,
            }