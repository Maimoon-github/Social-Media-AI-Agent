import asyncio
from typing import Optional
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger()

class RateLimiter:
    """
    Token bucket rate limiter for API calls.
    
    Ensures requests don't exceed specified rate limits.
    """
    
    def __init__(self, requests_per_second: float = 1.0):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_second: Maximum requests per second
        """
        self.requests_per_second = requests_per_second
        self.min_interval = 1.0 / requests_per_second
        self.last_request = None
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire permission to make a request (blocks if needed)."""
        async with self._lock:
            now = datetime.utcnow()
            
            if self.last_request:
                elapsed = (now - self.last_request).total_seconds()
                if elapsed < self.min_interval:
                    wait_time = self.min_interval - elapsed
                    logger.debug(f"Rate limiting: waiting {wait_time:.2f}s")
                    await asyncio.sleep(wait_time)
            
            self.last_request = datetime.utcnow()

class Semaphore:
    """
    Async semaphore for limiting concurrent operations.
    """
    
    def __init__(self, value: int = 5):
        """
        Initialize semaphore.
        
        Args:
            value: Maximum concurrent operations
        """
        self._semaphore = asyncio.Semaphore(value)
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._semaphore.acquire()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        self._semaphore.release()

async def gather_with_concurrency(n: int, *tasks):
    """
    Execute tasks with limited concurrency.
    
    Args:
        n: Maximum concurrent tasks
        *tasks: Coroutines to execute
        
    Returns:
        List of results
    """
    semaphore = asyncio.Semaphore(n)
    
    async def sem_task(task):
        async with semaphore:
            return await task
    
    return await asyncio.gather(*(sem_task(task) for task in tasks))