import redis.asyncio as aioredis
from typing import Optional, Any
import json
import structlog
from config import get_settings

logger = structlog.get_logger()

class CacheManager:
    """
    Redis cache manager for rate limiting and data caching.
    
    Provides async Redis operations with automatic serialization.
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize cache manager.
        
        Args:
            redis_url: Redis connection URL (uses config if not provided)
        """
        self.settings = get_settings()
        self.redis_url = redis_url or self.settings.redis.url
        self.client: Optional[aioredis.Redis] = None
    
    async def connect(self):
        """Connect to Redis."""
        if not self.client:
            self.client = await aioredis.from_url(
                self.redis_url,
                max_connections=self.settings.redis.max_connections,
                decode_responses=self.settings.redis.decode_responses
            )
            logger.info("Redis cache connected")
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.client:
            await self.client.close()
            self.client = None
            logger.info("Redis cache disconnected")
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        value = await self.client.get(key)
        
        if value:
            try:
                # Try to deserialize JSON
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                # Return as string if not JSON
                return value
        
        return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ):
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None for no expiry)
        """
        # Serialize value
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        elif not isinstance(value, (str, bytes)):
            value = str(value)
        
        if ttl:
            await self.client.setex(key, ttl, value)
        else:
            await self.client.set(key, value)
    
    async def delete(self, key: str):
        """Delete key from cache."""
        await self.client.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        return bool(await self.client.exists(key))
    
    async def incr(self, key: str, ttl: Optional[int] = None) -> int:
        """
        Increment counter.
        
        Args:
            key: Counter key
            ttl: Set expiry if this is the first increment
            
        Returns:
            New counter value
        """
        value = await self.client.incr(key)
        
        # Set TTL on first increment
        if value == 1 and ttl:
            await self.client.expire(key, ttl)
        
        return value
    
    async def ping(self) -> bool:
        """Ping Redis to check connectivity."""
        try:
            return await self.client.ping()
        except Exception as e:
            logger.error("Redis ping failed", error=str(e))
            return False
    
    async def flush_pattern(self, pattern: str):
        """
        Delete all keys matching pattern.
        
        Args:
            pattern: Key pattern (e.g., "rate_limit:*")
        """
        keys = []
        async for key in self.client.scan_iter(match=pattern):
            keys.append(key)
        
        if keys:
            await self.client.delete(*keys)
            logger.info(f"Flushed {len(keys)} keys matching pattern", pattern=pattern)