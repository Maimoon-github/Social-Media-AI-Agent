import pytest
import asyncio
from crews.github_crew import GitHubAnalysisCrew
from crews.async_crew import AsyncCrewExecutor
from unittest.mock import Mock, patch, AsyncMock

@pytest.fixture
def github_crew():
    """Create GitHub analysis crew instance."""
    return GitHubAnalysisCrew()

@pytest.fixture
def async_executor():
    """Create async crew executor."""
    return AsyncCrewExecutor(max_workers=2)

@pytest.mark.asyncio
async def test_crew_initialization(github_crew):
    """Test that crew initializes correctly."""
    assert github_crew.llm is not None
    assert github_crew.tools is not None
    assert "researcher" in github_crew.agents
    assert "profile_analyzer" in github_crew.agents

@pytest.mark.asyncio
async def test_create_crew(github_crew):
    """Test crew creation with specific inputs."""
    crew = github_crew.create_crew(
        github_repo_url="https://github.com/test/repo",
        github_username="testuser"
    )
    
    assert crew is not None
    assert len(crew.agents) == 2
    assert len(crew.tasks) == 2

@pytest.mark.asyncio
@patch('crews.github_crew.crew.Crew.kickoff')
async def test_crew_execution(mock_kickoff, github_crew, async_executor):
    """Test crew execution through async executor."""
    # Mock crew output
    mock_output = """
    Repository Analysis:
    - Name: test-repo
    - Stars: 100
    - Health Score: 85
    
    Profile Analysis:
    - Username: testuser
    - Expertise: Python, Machine Learning
    """
    mock_kickoff.return_value = mock_output
    
    crew = github_crew.create_crew(
        github_repo_url="https://github.com/test/repo",
        github_username="testuser"
    )
    
    result = await async_executor.execute_crew(
        crew=crew,
        inputs={
            "repo_url": "https://github.com/test/repo",
            "username": "testuser"
        }
    )
    
    assert result is not None
    mock_kickoff.assert_called_once()

@pytest.mark.asyncio
async def test_parse_results(github_crew):
    """Test parsing of crew output."""
    raw_output = """
    {
        "repository": {
            "name": "test-repo",
            "health_score": 85,
            "tech_stack": ["Python", "FastAPI"]
        },
        "profile": {
            "username": "testuser",
            "expertise_areas": [{"area": "Python", "confidence": "high"}]
        }
    }
    """
    
    results = github_crew.parse_results(raw_output)
    
    assert results is not None
    assert "repository" in results
    assert "profile" in results

@pytest.mark.asyncio
async def test_crew_error_handling(github_crew, async_executor):
    """Test error handling in crew execution."""
    crew = github_crew.create_crew(
        github_repo_url="https://github.com/invalid/repo",
        github_username="invaliduser"
    )
    
    # This should handle the error gracefully
    with pytest.raises(Exception):
        await async_executor.execute_crew(
            crew=crew,
            inputs={
                "repo_url": "https://github.com/invalid/repo",
                "username": "invaliduser"
            }
        )

def test_agent_configuration(github_crew):
    """Test that agents are properly configured."""
    researcher = github_crew.agents["researcher"]
    profile_analyzer = github_crew.agents["profile_analyzer"]
    
    assert researcher.role == "Senior GitHub Repository Analyst"
    assert profile_analyzer.role == "GitHub Profile Intelligence Specialist"
    assert researcher.llm is not None
    assert len(researcher.tools) > 0