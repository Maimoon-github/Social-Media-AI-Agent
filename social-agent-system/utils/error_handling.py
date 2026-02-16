import asyncio
from typing import Callable, Any
from functools import wraps
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger()

def exponential_backoff(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
    """
    Calculate exponential backoff delay.
    
    Args:
        attempt: Attempt number (0-indexed)
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        
    Returns:
        Delay in seconds
    """
    delay = base_delay * (2 ** attempt)
    return min(delay, max_delay)

def with_retry(
    max_attempts: int = 3,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator for automatic retry with exponential backoff.
    
    Args:
        max_attempts: Maximum number of attempts
        backoff_factor: Backoff multiplication factor
        exceptions: Exception types to catch and retry
        
    Usage:
        @with_retry(max_attempts=3, backoff_factor=2)
        async def fetch_data():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                    
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_attempts - 1:
                        delay = exponential_backoff(attempt, base_delay=backoff_factor)
                        logger.warning(
                            f"Attempt {attempt + 1} failed, retrying in {delay}s",
                            function=func.__name__,
                            error=str(e)
                        )
                        await asyncio.sleep(delay)
                    else:
                        logger.error(
                            f"All {max_attempts} attempts failed",
                            function=func.__name__,
                            error=str(e)
                        )
            
            raise last_exception
        
        return wrapper
    return decorator

class CircuitBreaker:
    """
    Circuit breaker pattern for API resilience.
    
    Prevents cascading failures by stopping requests to failing services.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds before attempting recovery
            expected_exception: Exception type to track
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open
    
    async def __aenter__(self):
        """Check circuit state before operation."""
        if self.state == "open":
            # Check if recovery timeout has passed
            if self.last_failure_time:
                elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
                if elapsed >= self.recovery_timeout:
                    logger.info("Circuit breaker: attempting recovery (half-open)")
                    self.state = "half_open"
                else:
                    raise Exception("Circuit breaker is OPEN - service unavailable")
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Record success/failure after operation."""
        if exc_type is None:
            # Success
            if self.state == "half_open":
                logger.info("Circuit breaker: recovery successful (closing)")
                self.state = "closed"
                self.failure_count = 0
        
        elif issubclass(exc_type, self.expected_exception):
            # Failure
            self.failure_count += 1
            self.last_failure_time = datetime.utcnow()
            
            if self.failure_count >= self.failure_threshold:
                logger.error(
                    "Circuit breaker: threshold exceeded (opening)",
                    failures=self.failure_count
                )
                self.state = "open"
            
            if self.state == "half_open":
                # Failed during recovery
                self.state = "open"
        
        return False  # Don't suppress exception