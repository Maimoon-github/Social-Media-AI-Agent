import aiohttp
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import structlog
from config import get_settings
from utils.error_handling import with_retry, CircuitBreaker
from persistence.cache import CacheManager

logger = structlog.get_logger()

class GitHubClient:
    """
    Async GitHub API client with rate limiting and caching.
    
    Uses GitHub REST API v3 with personal access token authentication.
    """
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize GitHub client.
        
        Args:
            token: GitHub personal access token (reads from config if not provided)
        """
        self.settings = get_settings()
        self.token = token or self.settings.github.token
        self.base_url = self.settings.github.api_base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60
        )
        self.cache = CacheManager()
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
    
    async def connect(self):
        """Initialize HTTP session."""
        if not self.session:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "SocialAgentSystem/1.0"
            }
            timeout = aiohttp.ClientTimeout(total=self.settings.github.timeout)
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=timeout
            )
            await self.cache.connect()
            logger.info("GitHub client connected")
    
    async def disconnect(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
            await self.cache.disconnect()
            logger.info("GitHub client disconnected")
    
    @with_retry(max_attempts=3, backoff_factor=2)
    async def get_repository(self, repo_identifier: str) -> Dict[str, Any]:
        """
        Fetch repository metadata.
        
        Args:
            repo_identifier: "owner/repo" or full URL
            
        Returns:
            Repository metadata dictionary
        """
        # Parse identifier
        if "/" in repo_identifier and not repo_identifier.startswith("http"):
            owner, repo = repo_identifier.split("/", 1)
        else:
            # Extract from URL
            parts = repo_identifier.rstrip("/").split("/")
            owner, repo = parts[-2], parts[-1]
        
        cache_key = f"github:repo:{owner}/{repo}"
        
        # Check cache
        cached = await self.cache.get(cache_key)
        if cached:
            logger.debug("Cache hit for repository", repo=f"{owner}/{repo}")
            return cached
        
        # Fetch from API
        url = f"{self.base_url}/repos/{owner}/{repo}"
        
        async with self.circuit_breaker:
            async with self.session.get(url) as response:
                await self._check_rate_limit(response)
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Structure the response
                    result = {
                        "name": data["name"],
                        "full_name": data["full_name"],
                        "description": data.get("description"),
                        "url": data["html_url"],
                        "stars": data["stargazers_count"],
                        "forks": data["forks_count"],
                        "watchers": data["watchers_count"],
                        "open_issues": data["open_issues_count"],
                        "language": data.get("language"),
                        "created_at": data["created_at"],
                        "updated_at": data["updated_at"],
                        "pushed_at": data["pushed_at"],
                        "size": data["size"],
                        "default_branch": data["default_branch"],
                        "license": data.get("license", {}).get("name") if data.get("license") else None,
                        "topics": data.get("topics", []),
                        "has_wiki": data["has_wiki"],
                        "has_pages": data["has_pages"],
                        "archived": data["archived"]
                    }
                    
                    # Cache for 1 hour
                    await self.cache.set(cache_key, result, ttl=3600)
                    
                    logger.info("Repository fetched", repo=f"{owner}/{repo}")
                    return result
                    
                elif response.status == 404:
                    raise ValueError(f"Repository not found: {owner}/{repo}")
                else:
                    error = await response.text()
                    raise Exception(f"GitHub API error: {response.status} - {error}")
    
    @with_retry(max_attempts=3, backoff_factor=2)
    async def get_languages(self, repo_identifier: str) -> Dict[str, int]:
        """
        Fetch repository language breakdown.
        
        Args:
            repo_identifier: "owner/repo" format
            
        Returns:
            Dictionary mapping language names to byte counts
        """
        owner, repo = self._parse_repo_identifier(repo_identifier)
        cache_key = f"github:languages:{owner}/{repo}"
        
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        
        url = f"{self.base_url}/repos/{owner}/{repo}/languages"
        
        async with self.circuit_breaker:
            async with self.session.get(url) as response:
                await self._check_rate_limit(response)
                
                if response.status == 200:
                    data = await response.json()
                    await self.cache.set(cache_key, data, ttl=3600)
                    return data
                else:
                    raise Exception(f"Failed to fetch languages: {response.status}")
    
    @with_retry(max_attempts=3, backoff_factor=2)
    async def get_commits(
        self,
        repo_identifier: str,
        limit: int = 10,
        since: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch recent commits.
        
        Args:
            repo_identifier: "owner/repo" format
            limit: Maximum number of commits to fetch
            since: Only commits after this date
            
        Returns:
            List of commit dictionaries
        """
        owner, repo = self._parse_repo_identifier(repo_identifier)
        
        params = {"per_page": limit}
        if since:
            params["since"] = since.isoformat()
        
        url = f"{self.base_url}/repos/{owner}/{repo}/commits"
        
        async with self.circuit_breaker:
            async with self.session.get(url, params=params) as response:
                await self._check_rate_limit(response)
                
                if response.status == 200:
                    data = await response.json()
                    
                    commits = []
                    for commit in data:
                        commits.append({
                            "sha": commit["sha"],
                            "message": commit["commit"]["message"],
                            "author": commit["commit"]["author"]["name"],
                            "date": commit["commit"]["author"]["date"],
                            "url": commit["html_url"]
                        })
                    
                    return commits
                else:
                    raise Exception(f"Failed to fetch commits: {response.status}")
    
    @with_retry(max_attempts=3, backoff_factor=2)
    async def get_user(self, username: str) -> Dict[str, Any]:
        """
        Fetch user profile.
        
        Args:
            username: GitHub username
            
        Returns:
            User profile dictionary
        """
        cache_key = f"github:user:{username}"
        
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        
        url = f"{self.base_url}/users/{username}"
        
        async with self.circuit_breaker:
            async with self.session.get(url) as response:
                await self._check_rate_limit(response)
                
                if response.status == 200:
                    data = await response.json()
                    
                    result = {
                        "username": data["login"],
                        "name": data.get("name"),
                        "bio": data.get("bio"),
                        "location": data.get("location"),
                        "company": data.get("company"),
                        "blog": data.get("blog"),
                        "email": data.get("email"),
                        "avatar_url": data["avatar_url"],
                        "followers": data["followers"],
                        "following": data["following"],
                        "public_repos": data["public_repos"],
                        "public_gists": data["public_gists"],
                        "created_at": data["created_at"],
                        "updated_at": data["updated_at"]
                    }
                    
                    await self.cache.set(cache_key, result, ttl=3600)
                    return result
                    
                elif response.status == 404:
                    raise ValueError(f"User not found: {username}")
                else:
                    error = await response.text()
                    raise Exception(f"GitHub API error: {response.status} - {error}")
    
    @with_retry(max_attempts=3, backoff_factor=2)
    async def get_user_repos(
        self,
        username: str,
        limit: int = 20,
        sort: str = "updated"
    ) -> List[Dict[str, Any]]:
        """
        Fetch user's repositories.
        
        Args:
            username: GitHub username
            limit: Maximum number of repos to fetch
            sort: Sort order (created, updated, pushed, full_name)
            
        Returns:
            List of repository dictionaries
        """
        params = {
            "per_page": limit,
            "sort": sort,
            "direction": "desc"
        }
        
        url = f"{self.base_url}/users/{username}/repos"
        
        async with self.circuit_breaker:
            async with self.session.get(url, params=params) as response:
                await self._check_rate_limit(response)
                
                if response.status == 200:
                    data = await response.json()
                    
                    repos = []
                    for repo in data:
                        repos.append({
                            "name": repo["name"],
                            "full_name": repo["full_name"],
                            "description": repo.get("description"),
                            "url": repo["html_url"],
                            "stars": repo["stargazers_count"],
                            "forks": repo["forks_count"],
                            "language": repo.get("language"),
                            "updated_at": repo["updated_at"]
                        })
                    
                    return repos
                else:
                    raise Exception(f"Failed to fetch user repos: {response.status}")
    
    async def get_rate_limit(self) -> Dict[str, Any]:
        """
        Check current rate limit status.
        
        Returns:
            Rate limit information
        """
        url = f"{self.base_url}/rate_limit"
        
        async with self.session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data["rate"]
            else:
                raise Exception(f"Failed to check rate limit: {response.status}")
    
    async def _check_rate_limit(self, response: aiohttp.ClientResponse):
        """Check rate limit from response headers."""
        remaining = response.headers.get("X-RateLimit-Remaining")
        reset_time = response.headers.get("X-RateLimit-Reset")
        
        if remaining and int(remaining) < 100:
            logger.warning(
                "GitHub rate limit low",
                remaining=remaining,
                reset_time=reset_time
            )
        
        if remaining and int(remaining) == 0:
            # Calculate wait time
            reset_timestamp = int(reset_time)
            wait_time = reset_timestamp - int(datetime.now().timestamp())
            logger.error(
                "GitHub rate limit exceeded",
                wait_seconds=wait_time
            )
            raise Exception(f"Rate limit exceeded. Reset in {wait_time} seconds.")
    
    def _parse_repo_identifier(self, identifier: str) -> tuple:
        """Parse repository identifier into owner and repo."""
        if "/" in identifier and not identifier.startswith("http"):
            return identifier.split("/", 1)
        else:
            parts = identifier.rstrip("/").split("/")
            return parts[-2], parts[-1]