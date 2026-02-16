import aiohttp
from typing import Dict, Any, Optional
import structlog
from config import get_settings
from utils.error_handling import with_retry

logger = structlog.get_logger()

class LinkedInClient:
    """
    LinkedIn API client for publishing posts.
    
    Uses LinkedIn API v202501 with OAuth 2.0 authentication.
    """
    
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None
    ):
        self.settings = get_settings()
        self.client_id = client_id or self.settings.linkedin.client_id
        self.client_secret = client_secret or self.settings.linkedin.client_secret
        self.access_token = access_token or self.settings.linkedin.access_token
        self.refresh_token = refresh_token or self.settings.linkedin.refresh_token
        self.base_url = "https://api.linkedin.com/v2"
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def connect(self):
        """Initialize HTTP session."""
        if not self.session:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            self.session = aiohttp.ClientSession(headers=headers)
            logger.info("LinkedIn client connected")
    
    async def disconnect(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def verify_token(self) -> bool:
        """Verify access token is valid."""
        url = f"{self.base_url}/me"
        
        try:
            async with self.session.get(url) as response:
                return response.status == 200
        except Exception as e:
            logger.error("Token verification failed", error=str(e))
            return False
    
    @with_retry(max_attempts=3, backoff_factor=2)
    async def create_post(
        self,
        text: str,
        visibility: str = "PUBLIC"
    ) -> Dict[str, Any]:
        """
        Create a LinkedIn post.
        
        Args:
            text: Post content
            visibility: Post visibility (PUBLIC, CONNECTIONS)
            
        Returns:
            Post creation response with post ID
        """
        # Get user URN
        user_urn = await self._get_user_urn()
        
        # Construct post payload
        payload = {
            "author": user_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility
            }
        }
        
        url = f"{self.base_url}/ugcPosts"
        
        async with self.session.post(url, json=payload) as response:
            if response.status in [200, 201]:
                data = await response.json()
                post_id = data.get("id")
                
                logger.info("LinkedIn post created", post_id=post_id)
                
                return {
                    "post_id": post_id,
                    "status": "success",
                    "url": f"https://www.linkedin.com/feed/update/{post_id}"
                }
            else:
                error = await response.text()
                logger.error("LinkedIn post failed", status=response.status, error=error)
                raise Exception(f"LinkedIn API error: {response.status} - {error}")
    
    async def _get_user_urn(self) -> str:
        """Get user URN for API calls."""
        url = f"{self.base_url}/me"
        
        async with self.session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return f"urn:li:person:{data['id']}"
            else:
                raise Exception("Failed to get user URN")
    
    async def refresh_access_token(self) -> str:
        """
        Refresh the access token using refresh token.
        
        Returns:
            New access token
        """
        url = "https://www.linkedin.com/oauth/v2/accessToken"
        
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    new_token = data["access_token"]
                    self.access_token = new_token
                    
                    # Update session headers
                    if self.session:
                        self.session.headers["Authorization"] = f"Bearer {new_token}"
                    
                    logger.info("LinkedIn access token refreshed")
                    return new_token
                else:
                    error = await response.text()
                    raise Exception(f"Token refresh failed: {error}")