import asyncio
from typing import Dict, Any, List, Optional
import structlog
from .linkedin import LinkedInClient
from .x_twitter import XClient
from .instagram import InstagramClient
from config import get_settings
from persistence.cache import CacheManager

logger = structlog.get_logger()

class MultiPlatformPublisher:
    """
    Coordinates content publishing across multiple social media platforms.
    
    Publishes to LinkedIn, X (Twitter), and Instagram in parallel while
    handling errors and rate limits per platform.
    """
    
    def __init__(self, platforms: List[str], dry_run: bool = False):
        """
        Initialize multi-platform publisher.
        
        Args:
            platforms: List of platforms to publish to
            dry_run: If True, skip actual API calls
        """
        self.settings = get_settings()
        self.platforms = platforms
        self.dry_run = dry_run
        self.clients: Dict[str, Any] = {}
        self.cache = CacheManager()
        
    async def initialize(self):
        """Initialize platform clients."""
        await self.cache.connect()
        
        if "linkedin" in self.platforms:
            self.clients["linkedin"] = LinkedInClient()
            await self.clients["linkedin"].connect()
        
        if "twitter" in self.platforms or "x" in self.platforms:
            self.clients["x"] = XClient()
            await self.clients["x"].connect()
        
        if "instagram" in self.platforms:
            self.clients["instagram"] = InstagramClient()
            await self.clients["instagram"].connect()
        
        logger.info("Multi-platform publisher initialized", platforms=self.platforms)
    
    async def cleanup(self):
        """Cleanup platform clients."""
        for client in self.clients.values():
            await client.disconnect()
        
        await self.cache.disconnect()
        logger.info("Multi-platform publisher cleaned up")
    
    async def check_rate_limits_all(self) -> Dict[str, Any]:
        """
        Check rate limits for all platforms.
        
        Returns:
            Dictionary of rate limit status per platform
        """
        rate_limits = {}
        
        for platform in self.platforms:
            try:
                usage = await self._get_rate_limit_usage(platform)
                remaining = await self._get_remaining_quota(platform)
                
                rate_limits[platform] = {
                    "usage_today": usage,
                    "remaining_today": remaining,
                    "would_exceed": remaining <= 0
                }
                
            except Exception as e:
                logger.error(f"Failed to check {platform} rate limit", error=str(e))
                rate_limits[platform] = {
                    "error": str(e),
                    "would_exceed": False  # Assume OK if check fails
                }
        
        return rate_limits
    
    async def publish_all(
        self,
        content_drafts: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Publish content to all platforms in parallel.
        
        Args:
            content_drafts: Dictionary of platform-specific content
            
        Returns:
            Publishing results for all platforms
        """
        if self.dry_run:
            logger.info("DRY RUN: Skipping actual publishing")
            return self._mock_publish_results(content_drafts)
        
        # Create publishing tasks
        tasks = {}
        
        if "linkedin" in content_drafts:
            tasks["linkedin"] = self._publish_linkedin(content_drafts["linkedin"])
        
        if "twitter" in content_drafts or "x" in content_drafts:
            content = content_drafts.get("twitter") or content_drafts.get("x")
            tasks["x"] = self._publish_x(content)
        
        if "instagram" in content_drafts:
            tasks["instagram"] = self._publish_instagram(content_drafts["instagram"])
        
        # Execute all publishing tasks in parallel
        results = await asyncio.gather(
            *tasks.values(),
            return_exceptions=True
        )
        
        # Aggregate results
        posts = []
        errors = []
        
        for platform, result in zip(tasks.keys(), results):
            if isinstance(result, Exception):
                logger.error(f"{platform} publishing failed", error=str(result))
                errors.append(f"{platform}: {str(result)}")
                posts.append({
                    "platform": platform,
                    "status": "failed",
                    "error": str(result),
                    "post_id": None,
                    "timestamp": None,
                    "retry_count": 0
                })
            else:
                posts.append({
                    "platform": platform,
                    "status": result["status"],
                    "post_id": result.get("post_id") or result.get("tweet_ids", [None])[0],
                    "url": result.get("url") or result.get("thread_url"),
                    "timestamp": datetime.utcnow().isoformat(),
                    "retry_count": 0,
                    "error": None
                })
        
        logger.info(
            "Publishing completed",
            successful=len([p for p in posts if p["status"] == "success"]),
            failed=len(errors)
        )
        
        return {
            "posts": posts,
            "errors": errors
        }
    
    async def _publish_linkedin(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Publish to LinkedIn."""
        logger.info("Publishing to LinkedIn")
        
        client = self.clients["linkedin"]
        
        # Construct post text with hashtags
        text = content["text"]
        hashtags = " ".join(f"#{tag}" for tag in content.get("hashtags", []))
        full_text = f"{text}\n\n{hashtags}"
        
        result = await client.create_post(text=full_text)
        
        # Update rate limit tracking
        await self._increment_rate_limit_usage("linkedin")
        
        return result
    
    async def _publish_x(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Publish to X (Twitter)."""
        logger.info("Publishing to X")
        
        client = self.clients["x"]
        
        tweets = content["tweets"]
        
        if len(tweets) == 1:
            # Single tweet
            result = await client.create_tweet(text=tweets[0]["text"])
        else:
            # Thread
            result = await client.create_thread(tweets=tweets)
        
        # Update rate limit tracking
        await self._increment_rate_limit_usage("x")
        
        return result
    
    async def _publish_instagram(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Publish to Instagram."""
        logger.info("Publishing to Instagram")
        
        client = self.clients["instagram"]
        
        # Instagram requires an image URL
        # In production, this would be generated from image_description
        # For now, we'll need to handle image generation separately
        
        # Placeholder: This should be replaced with actual image generation/upload
        image_url = "https://placeholder.com/instagram-post.jpg"
        
        caption = content["caption"]
        hashtags = " ".join(f"#{tag}" for tag in content.get("hashtags", []))
        full_caption = f"{caption}\n\n{hashtags}"
        
        result = await client.create_post(
            image_url=image_url,
            caption=full_caption
        )
        
        # Update rate limit tracking
        await self._increment_rate_limit_usage("instagram")
        
        return result
    
    async def _get_rate_limit_usage(self, platform: str) -> int:
        """Get today's API usage count for platform."""
        date_key = datetime.utcnow().strftime("%Y-%m-%d")
        cache_key = f"rate_limit:{platform}:{date_key}"
        
        usage = await self.cache.get(cache_key)
        return int(usage) if usage else 0
    
    async def _get_remaining_quota(self, platform: str) -> int:
        """Get remaining quota for platform today."""
        limits = {
            "linkedin": self.settings.linkedin.rate_limit_requests,
            "x": self.settings.x.rate_limit_posts,
            "instagram": self.settings.instagram.rate_limit_posts
        }
        
        limit = limits.get(platform, 100)
        usage = await self._get_rate_limit_usage(platform)
        
        return max(0, limit - usage)
    
    async def _increment_rate_limit_usage(self, platform: str):
        """Increment rate limit usage counter."""
        date_key = datetime.utcnow().strftime("%Y-%m-%d")
        cache_key = f"rate_limit:{platform}:{date_key}"
        
        # Increment with expiry of 24 hours
        await self.cache.incr(cache_key, ttl=86400)
    
    def _mock_publish_results(self, content_drafts: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock results for dry run mode."""
        posts = []
        
        for platform in content_drafts.keys():
            posts.append({
                "platform": platform,
                "status": "success",
                "post_id": f"mock-{platform}-{datetime.utcnow().timestamp()}",
                "url": f"https://mock-url.com/{platform}",
                "timestamp": datetime.utcnow().isoformat(),
                "retry_count": 0,
                "error": None
            })
        
        return {
            "posts": posts,
            "errors": []
        }