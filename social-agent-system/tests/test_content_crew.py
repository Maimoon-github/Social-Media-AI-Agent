import pytest
from crews.content_crew import ContentGenerationCrew
from unittest.mock import Mock, patch

@pytest.fixture
def content_crew():
    """Create content generation crew instance."""
    return ContentGenerationCrew()

@pytest.fixture
def sample_analysis():
    """Sample GitHub analysis results for testing."""
    return {
        "repository": {
            "name": "test-repo",
            "description": "A test repository",
            "tech_stack": ["Python", "FastAPI"],
            "health_score": 85,
            "key_insights": ["Well structured", "Good documentation"]
        },
        "profile": {
            "username": "testuser",
            "expertise_areas": [
                {"area": "Python", "confidence": "high"},
                {"area": "Backend", "confidence": "medium"}
            ],
            "professional_positioning": "Backend developer"
        }
    }

def test_crew_initialization(content_crew):
    """Test content crew initialization."""
    assert content_crew.llm is not None
    assert "linkedin" in content_crew.agents
    assert "x" in content_crew.agents
    assert "instagram" in content_crew.agents

def test_create_crew_all_platforms(content_crew, sample_analysis):
    """Test crew creation for all platforms."""
    platforms = ["linkedin", "twitter", "instagram"]
    crew = content_crew.create_crew(
        analysis_results=sample_analysis,
        platforms=platforms
    )
    
    assert crew is not None
    assert len(crew.agents) == 3
    assert len(crew.tasks) == 3

def test_create_crew_single_platform(content_crew, sample_analysis):
    """Test crew creation for single platform."""
    platforms = ["linkedin"]
    crew = content_crew.create_crew(
        analysis_results=sample_analysis,
        platforms=platforms
    )
    
    assert len(crew.agents) == 1
    assert len(crew.tasks) == 1

def test_content_validation_linkedin(content_crew):
    """Test LinkedIn content validation."""
    content = {
        "text": "Test post content",
        "hashtags": ["python", "github", "opensource"]
    }
    
    result = content_crew._validate_content(content, "linkedin")
    
    assert result["valid"] is True
    assert len(result["errors"]) == 0

def test_content_validation_linkedin_too_long(content_crew):
    """Test LinkedIn content validation with too long text."""
    content = {
        "text": "x" * 3001,  # Exceeds 3000 char limit
        "hashtags": ["python", "github", "opensource"]
    }
    
    result = content_crew._validate_content(content, "linkedin")
    
    assert result["valid"] is False
    assert len(result["errors"]) > 0

def test_content_validation_x_thread(content_crew):
    """Test X/Twitter thread validation."""
    content = {
        "tweets": [
            {"text": "Tweet 1", "order": 1},
            {"text": "Tweet 2", "order": 2}
        ],
        "hashtags": ["github"]
    }
    
    result = content_crew._validate_content(content, "x")
    
    assert result["valid"] is True

def test_content_validation_x_too_many_tweets(content_crew):
    """Test X validation with too many tweets."""
    content = {
        "tweets": [
            {"text": f"Tweet {i}", "order": i}
            for i in range(1, 12)  # 11 tweets, exceeds limit of 10
        ],
        "hashtags": ["github"]
    }
    
    result = content_crew._validate_content(content, "x")
    
    assert result["valid"] is False

def test_content_validation_instagram(content_crew):
    """Test Instagram content validation."""
    content = {
        "caption": "Test caption",
        "hashtags": ["coding"] * 15,  # 15 hashtags
        "image_description": "Test image"
    }
    
    result = content_crew._validate_content(content, "instagram")
    
    assert result["valid"] is True

def test_content_validation_instagram_missing_image(content_crew):
    """Test Instagram validation without image description."""
    content = {
        "caption": "Test caption",
        "hashtags": ["coding"] * 15,
        "image_description": ""  # Missing
    }
    
    result = content_crew._validate_content(content, "instagram")
    
    assert result["valid"] is False