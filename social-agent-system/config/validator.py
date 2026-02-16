from typing import Dict, List, Tuple
import asyncio
import aiohttp
from .settings import Settings
from integrations.github import GitHubClient
from integrations.linkedin import LinkedInClient
from integrations.x_twitter import XClient
from integrations.instagram import InstagramClient
from persistence.database import DatabaseManager
from persistence.cache import CacheManager

class ValidationError(Exception):
    """Configuration validation error."""
    pass

class ConfigValidator:
    """Validates system configuration and external dependencies."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.validation_results: Dict[str, bool] = {}
        
    async def validate_all(self) -> Tuple[bool, List[str]]:
        """
        Run all validation checks.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Run validations concurrently
        results = await asyncio.gather(
            self._validate_github(),
            self._validate_linkedin(),
            self._validate_x(),
            self._validate_instagram(),
            self._validate_llm(),
            self._validate_database(),
            self._validate_redis(),
            return_exceptions=True
        )
        
        # Collect errors
        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                errors.append(str(result))
                
        is_valid = len(errors) == 0
        return is_valid, errors
    
    async def _validate_github(self) -> bool:
        """Validate GitHub API credentials."""
        try:
            client = GitHubClient(token=self.settings.github.token)
            # Test API call
            await client.get_rate_limit()
            self.validation_results["github"] = True
            return True
        except Exception as e:
            raise ValidationError(f"GitHub validation failed: {e}")
    
    async def _validate_linkedin(self) -> bool:
        """Validate LinkedIn API credentials."""
        try:
            client = LinkedInClient(
                client_id=self.settings.linkedin.client_id,
                client_secret=self.settings.linkedin.client_secret,
                access_token=self.settings.linkedin.access_token
            )
            # Test API call
            await client.verify_token()
            self.validation_results["linkedin"] = True
            return True
        except Exception as e:
            raise ValidationError(f"LinkedIn validation failed: {e}")
    
    async def _validate_x(self) -> bool:
        """Validate X (Twitter) API credentials."""
        try:
            client = XClient(
                api_key=self.settings.x.api_key,
                api_secret=self.settings.x.api_secret,
                access_token=self.settings.x.access_token,
                access_token_secret=self.settings.x.access_token_secret
            )
            # Test API call
            await client.verify_credentials()
            self.validation_results["x"] = True
            return True
        except Exception as e:
            raise ValidationError(f"X validation failed: {e}")
    
    async def _validate_instagram(self) -> bool:
        """Validate Instagram API credentials."""
        try:
            client = InstagramClient(
                app_id=self.settings.instagram.app_id,
                app_secret=self.settings.instagram.app_secret,
                access_token=self.settings.instagram.access_token
            )
            # Test API call
            await client.verify_token()
            self.validation_results["instagram"] = True
            return True
        except Exception as e:
            raise ValidationError(f"Instagram validation failed: {e}")
    
    async def _validate_llm(self) -> bool:
        """Validate LLM service availability."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.settings.llm.ollama_base_url}/api/tags"
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Check if required models are available
                        available_models = [m["name"] for m in data.get("models", [])]
                        if self.settings.llm.analysis_model not in available_models:
                            raise ValidationError(f"Analysis model {self.settings.llm.analysis_model} not found")
                        if self.settings.llm.content_model not in available_models:
                            raise ValidationError(f"Content model {self.settings.llm.content_model} not found")
                        
                        self.validation_results["llm"] = True
                        return True
                    else:
                        raise ValidationError(f"Ollama service returned status {response.status}")
        except Exception as e:
            raise ValidationError(f"LLM validation failed: {e}")
    
    async def _validate_database(self) -> bool:
        """Validate database connectivity."""
        try:
            db_manager = DatabaseManager(self.settings.database.url)
            await db_manager.connect()
            await db_manager.disconnect()
            self.validation_results["database"] = True
            return True
        except Exception as e:
            raise ValidationError(f"Database validation failed: {e}")
    
    async def _validate_redis(self) -> bool:
        """Validate Redis connectivity."""
        try:
            cache_manager = CacheManager(self.settings.redis.url)
            await cache_manager.connect()
            await cache_manager.ping()
            await cache_manager.disconnect()
            self.validation_results["redis"] = True
            return True
        except Exception as e:
            raise ValidationError(f"Redis validation failed: {e}")