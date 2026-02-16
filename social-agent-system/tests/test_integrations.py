import pytest
from integrations.github import GitHubClient
from integrations.linkedin import LinkedInClient
from integrations.x_twitter import XClient
from integrations.instagram import InstagramClient
from unittest.mock import Mock, patch, AsyncMock
import aiohttp

@pytest.fixture
async def github_client():
    """Create GitHub client."""
    client = GitHubClient(token="test_token")
    await client.connect()
    yield client
    await client.disconnect()

@pytest.mark.asyncio
@patch('aiohttp.ClientSession.get')
async def test_github_get_repository(mock_get, github_client):
    """Test GitHub repository fetching."""
    # Mock response
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={
        "name": "test-repo",
        "full_name": "owner/test-repo",
        "stargazers_count": 100,
        "forks_count": 20
    })
    mock_response.headers = {"X-RateLimit-Remaining": "5000"}
    mock_get.return_value.__aenter__.return_value = mock_response
    
    result = await github_client.get_repository("owner/test-repo")
    
    assert result["name"] == "test-repo"
    assert result["stars"] == 100
    assert result["forks"] == 20

@pytest.mark.asyncio
@patch('aiohttp.ClientSession.get')
async def test_github_rate_limit_warning(mock_get, github_client):
    """Test GitHub rate limit warning."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={})
    mock_response.headers = {"X-RateLimit-Remaining": "50"}  # Low
    mock_get.return_value.__aenter__.return_value = mock_response
    
    # Should log warning but not raise exception
    result = await github_client.get_repository("owner/test-repo")

@pytest.mark.asyncio
async def test_linkedin_client_initialization():
    """Test LinkedIn client initialization."""
    client = LinkedInClient(
        client_id="test_id",
        client_secret="test_secret",
        access_token="test_token"
    )
    
    await client.connect()
    assert client.session is not None
    await client.disconnect()

@pytest.mark.asyncio
@patch('aiohttp.ClientSession.post')
async def test_linkedin_create_post(mock_post):
    """Test LinkedIn post creation."""
    client = LinkedInClient(
        client_id="test_id",
        client_secret="test_secret",
        access_token="test_token"
    )
    await client.connect()
    
    # Mock response
    mock_response = AsyncMock()
    mock_response.status = 201
    mock_response.json = AsyncMock(return_value={"id": "post123"})
    mock_post.return_value.__aenter__.return_value = mock_response
    
    result = await client.create_post(text="Test post")
    
    assert result["post_id"] == "post123"
    assert result["status"] == "success"
    
    await client.disconnect()

@pytest.mark.asyncio
async def test_x_client_initialization():
    """Test X/Twitter client initialization."""
    client = XClient(
        api_key="test_key",
        api_secret="test_secret",
        access_token="test_token",
        access_token_secret="test_token_secret",
        bearer_token="test_bearer"
    )
    
    await client.connect()
    assert client.session is not None
    await client.disconnect()

@pytest.mark.asyncio
@patch('aiohttp.ClientSession.post')
async def test_x_create_thread(mock_post):
    """Test X thread creation."""
    client = XClient(
        api_key="test_key",
        api_secret="test_secret",
        access_token="test_token",
        access_token_secret="test_token_secret",
        bearer_token="test_bearer"
    )
    await client.connect()
    
    # Mock response for each tweet
    mock_response = AsyncMock()
    mock_response.status = 201
    call_count = [0]
    
    async def mock_json():
        call_count[0] += 1
        return {"data": {"id": f"tweet{call_count[0]}"}}
    
    mock_response.json = mock_json
    mock_post.return_value.__aenter__.return_value = mock_response
    
    tweets = [
        {"text": "Tweet 1", "order": 1},
        {"text": "Tweet 2", "order": 2}
    ]
    
    result = await client.create_thread(tweets=tweets)
    
    assert len(result["tweet_ids"]) == 2
    assert result["status"] == "success"
    
    await client.disconnect()