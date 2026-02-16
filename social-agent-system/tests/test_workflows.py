import pytest
from workflows.graph import SocialAgentWorkflow
from workflows.state import create_initial_state, WorkflowPhase
from workflows.nodes import WorkflowNodes
from workflows.edges import WorkflowEdges
from unittest.mock import Mock, AsyncMock, patch

@pytest.fixture
def workflow_state():
    """Create initial workflow state for testing."""
    return create_initial_state(
        workflow_id="test-workflow-123",
        github_repo_url="https://github.com/test/repo",
        github_username="testuser",
        platforms=["linkedin", "twitter"],
        dry_run=True
    )

def test_initial_state_creation(workflow_state):
    """Test initial state is created correctly."""
    assert workflow_state["workflow_id"] == "test-workflow-123"
    assert workflow_state["phase"] == WorkflowPhase.IDLE
    assert workflow_state["platforms"] == ["linkedin", "twitter"]
    assert workflow_state["dry_run"] is True
    assert workflow_state["analysis_status"] == "pending"

def test_workflow_nodes_initialization():
    """Test workflow nodes are initialized."""
    nodes = WorkflowNodes()
    
    assert nodes.github_crew is not None
    assert nodes.content_crew is not None
    assert nodes.crew_executor is not None

@pytest.mark.asyncio
async def test_initialize_node(workflow_state):
    """Test initialization node."""
    nodes = WorkflowNodes()
    
    result_state = await nodes.initialize_node(workflow_state)
    
    assert result_state["phase"] == WorkflowPhase.INITIALIZING

def test_workflow_edges_routing():
    """Test conditional edge routing logic."""
    edges = WorkflowEdges()
    
    # Test successful initialization routing
    state = {"phase": WorkflowPhase.INITIALIZING, "analysis_status": "pending"}
    route = edges.route_after_initialize(state)
    assert route == "analyze"
    
    # Test failed initialization routing
    state = {"phase": "failed"}
    route = edges.route_after_initialize(state)
    assert route == "error"

def test_workflow_edges_retry_logic():
    """Test retry logic in edges."""
    edges = WorkflowEdges()
    
    # Test retry when under max retries
    state = {
        "analysis_status": "failed",
        "analysis_retry_count": 1
    }
    route = edges.route_after_analysis(state)
    assert route == "retry"
    
    # Test error when max retries exceeded
    state = {
        "analysis_status": "failed",
        "analysis_retry_count": 3
    }
    route = edges.route_after_analysis(state)
    assert route == "error"

@pytest.mark.asyncio
@patch('workflows.nodes.WorkflowNodes._publish_linkedin')
@patch('workflows.nodes.WorkflowNodes._publish_x')
async def test_publish_content_node(mock_x, mock_linkedin, workflow_state):
    """Test publishing node."""
    nodes = WorkflowNodes()
    
    # Setup state with content
    workflow_state["content_drafts"] = {
        "drafts": {
            "linkedin": {"text": "Test post", "hashtags": ["test"]},
            "twitter": {"tweets": [{"text": "Test tweet", "order": 1}]}
        }
    }
    workflow_state["phase"] = WorkflowPhase.PUBLISHING
    
    # Mock successful publishing
    mock_linkedin.return_value = {
        "status": "success",
        "post_id": "linkedin123"
    }
    mock_x.return_value = {
        "status": "success",
        "tweet_ids": ["tweet123"]
    }
    
    result_state = await nodes.publish_content_node(workflow_state)
    
    assert result_state["publishing_status"] in ["completed", "partial"]
    assert len(result_state["published_posts"]) > 0