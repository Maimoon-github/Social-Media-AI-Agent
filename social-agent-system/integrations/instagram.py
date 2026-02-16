import aiohttp
from typing import Dict, Any, Optional
import structlog
from config import get_settings
from utils.error_handling import with_retry

logger = structlog.get_logger()

class InstagramClient:
    """
    Instagram Graph API client for media publishing.
    
    Requires Instagram Business Account linked to Facebook Page.
    """
    
    def __init__(
        self,
        app_id: Optional[str] = None,
        app_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        account_id: Optional[str] = None
    ):
        self.settings = get_settings()
        self.app_id = app_id or self.settings.instagram.app_id
        self.app_secret = app_secret or self.settings.instagram.app_secret
        self.access_token = access_token or self.settings.instagram.access_token
        self.account_id = account_id or self.settings.instagram.account_id
        self.base_url = "https://graph.facebook.com/v24.0"
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def connect(self):
        """Initialize HTTP session."""
        if not self.session:
            self.session = aiohttp.ClientSession()
            logger.info("Instagram client connected")
    
    async def disconnect(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def verify_token(self) -> bool:
        """Verify access token is valid."""
        url = f"{self.base_url}/me"
        params = {"access_token": self.access_token}
        
        try:
            async with self.session.get(url, params=params) as response:
                return response.status == 200
        except Exception as e:
            logger.error("Token verification failed", error=str(e))
            return False
    
    @with_retry(max_attempts=3, backoff_factor=2)
    async def create_media_container(
        self,
        image_url: str,
        caption: str
    ) -> str:
        """
        Create Instagram media container.
        
        Args:
            image_url: Publicly accessible image URL
            caption: Post caption (max 2200 characters)
            
        Returns:
            Container ID
        """
        if len(caption) > 2200:
            raise ValueError(f"Caption exceeds 2200 characters: {len(caption)}")
        
        url = f"{self.base_url}/{self.account_id}/media"
        
        payload = {
            "image_url": image_url,
            "caption": caption,
            "access_token": self.access_token
        }
        
        async with self.session.post(url, data=payload) as response:
            if response.status in [200, 201]:
                data = await response.json()
                container_id = data["id"]
                
                logger.info("Media container created", container_id=container_id)
                return container_id
            else:
                error = await response.text()
                raise Exception(f"Container creation failed: {response.status} - {error}")
    
    @with_retry(max_attempts=3, backoff_factor=2)
    async def publish_media_container(
        self,
        container_id: str
    ) -> Dict[str, Any]:
        """
        Publish Instagram media container.
        
        Args:
            container_id: Container ID from create_media_container
            
        Returns:
            Publication response with media ID
        """
        url = f"{self.base_url}/{self.account_id}/media_publish"
        
        payload = {
            "creation_id": container_id,
            "access_token": self.access_token
        }
        
        async with self.session.post(url, data=payload) as response:
            if response.status in [200, 201]:
                data = await response.json()
                media_id = data["id"]
                
                logger.info("Media published", media_id=media_id)
                
                return {
                    "media_id": media_id,
                    "status": "success",
                    "url": f"https://www.instagram.com/p/{media_id}"
                }
            else:
                error = await response.text()
                raise Exception(f"Media publication failed: {response.status} - {error}")
    
    async def create_post(
        self,
        image_url: str,
        caption: str
    ) -> Dict[str, Any]:
        """
        Create and publish Instagram post (convenience method).
        
        Args:
            image_url: Publicly accessible image URL
            caption: Post caption
            
        Returns:
            Publication response
        """
        # Create container
        container_id = await self.create_media_container(image_url, caption)
        
        # Wait a moment for processing
        await asyncio.sleep(2)
        
        # Publish container
        result = await self.publish_media_container(container_id)
        
        return result