import aiohttp
from typing import Dict, Any, List, Optional
import structlog
from config import get_settings
from utils.error_handling import with_retry

logger = structlog.get_logger()

class XClient:
    """
    X (Twitter) API v2 client for publishing tweets and threads.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        access_token_secret: Optional[str] = None,
        bearer_token: Optional[str] = None
    ):
        self.settings = get_settings()
        self.api_key = api_key or self.settings.x.api_key
        self.api_secret = api_secret or self.settings.x.api_secret
        self.access_token = access_token or self.settings.x.access_token
        self.access_token_secret = access_token_secret or self.settings.x.access_token_secret
        self.bearer_token = bearer_token or self.settings.x.bearer_token
        self.base_url = "https://api.twitter.com/2"
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def connect(self):
        """Initialize HTTP session."""
        if not self.session:
            headers = {
                "Authorization": f"Bearer {self.bearer_token}",
                "Content-Type": "application/json"
            }
            self.session = aiohttp.ClientSession(headers=headers)
            logger.info("X client connected")
    
    async def disconnect(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def verify_credentials(self) -> bool:
        """Verify API credentials are valid."""
        url = f"{self.base_url}/users/me"
        
        try:
            async with self.session.get(url) as response:
                return response.status == 200
        except Exception as e:
            logger.error("Credentials verification failed", error=str(e))
            return False
    
    @with_retry(max_attempts=3, backoff_factor=2)
    async def create_tweet(
        self,
        text: str,
        reply_to_tweet_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a single tweet.
        
        Args:
            text: Tweet content (max 280 characters)
            reply_to_tweet_id: ID of tweet to reply to (for threading)
            
        Returns:
            Tweet creation response
        """
        if len(text) > 280:
            raise ValueError(f"Tweet text exceeds 280 characters: {len(text)}")
        
        payload = {"text": text}
        
        if reply_to_tweet_id:
            payload["reply"] = {"in_reply_to_tweet_id": reply_to_tweet_id}
        
        url = f"{self.base_url}/tweets"
        
        async with self.session.post(url, json=payload) as response:
            if response.status in [200, 201]:
                data = await response.json()
                tweet_id = data["data"]["id"]
                
                logger.info("Tweet created", tweet_id=tweet_id)
                
                return {
                    "tweet_id": tweet_id,
                    "status": "success",
                    "url": f"https://twitter.com/i/web/status/{tweet_id}"
                }
            else:
                error = await response.text()
                logger.error("Tweet creation failed", status=response.status, error=error)
                raise Exception(f"X API error: {response.status} - {error}")
    
    async def create_thread(
        self,
        tweets: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create a thread of tweets.
        
        Args:
            tweets: List of tweet dictionaries with 'text' and 'order'
            
        Returns:
            Thread creation results
        """
        if len(tweets) > 10:
            raise ValueError(f"Thread exceeds maximum of 10 tweets: {len(tweets)}")
        
        # Sort by order
        sorted_tweets = sorted(tweets, key=lambda t: t["order"])
        
        tweet_ids = []
        previous_tweet_id = None
        
        for tweet in sorted_tweets:
            try:
                result = await self.create_tweet(
                    text=tweet["text"],
                    reply_to_tweet_id=previous_tweet_id
                )
                
                tweet_ids.append(result["tweet_id"])
                previous_tweet_id = result["tweet_id"]
                
            except Exception as e:
                logger.error(
                    "Failed to create tweet in thread",
                    order=tweet["order"],
                    error=str(e)
                )
                # Stop thread creation on error
                break
        
        logger.info("Thread created", tweet_count=len(tweet_ids))
        
        return {
            "tweet_ids": tweet_ids,
            "thread_url": f"https://twitter.com/i/web/status/{tweet_ids[0]}" if tweet_ids else None,
            "status": "success" if len(tweet_ids) == len(sorted_tweets) else "partial"
        }