from typing import TypedDict, List, Dict, Any, Optional, Literal
from datetime import datetime
from enum import Enum

class WorkflowPhase(str, Enum):
    """Workflow execution phases."""
    IDLE = "idle"
    INITIALIZING = "initializing"
    ANALYZING = "analyzing"
    GENERATING = "generating"
    VALIDATING = "validating"
    PUBLISHING = "publishing"
    COMPLETED = "completed"
    FAILED = "failed"

class PlatformStatus(TypedDict):
    """Status for individual platform publishing."""
    platform: str
    status: Literal["pending", "success", "failed", "skipped"]
    post_id: Optional[str]
    error: Optional[str]
    timestamp: Optional[str]
    retry_count: int

class WorkflowState(TypedDict):
    """
    Complete workflow state schema.
    
    This state is persisted at each checkpoint and enables pause/resume functionality.
    """
    # Workflow metadata
    workflow_id: str
    phase: WorkflowPhase
    created_at: str
    updated_at: str
    
    # Input parameters
    github_repo_url: str
    github_username: str
    platforms: List[str]
    dry_run: bool
    
    # GitHub Analysis Phase
    analysis_status: Literal["pending", "in_progress", "completed", "failed"]
    analysis_results: Optional[Dict[str, Any]]
    analysis_error: Optional[str]
    analysis_retry_count: int
    
    # Content Generation Phase
    generation_status: Literal["pending", "in_progress", "completed", "partial", "failed"]
    content_drafts: Optional[Dict[str, Any]]
    generation_error: Optional[str]
    generation_retry_count: int
    
    # Validation Phase
    validation_status: Literal["pending", "completed", "failed"]
    validation_results: Optional[Dict[str, Any]]
    
    # Publishing Phase
    publishing_status: Literal["pending", "in_progress", "completed", "partial", "failed"]
    published_posts: List[PlatformStatus]
    publishing_errors: List[str]
    
    # Rate Limiting
    rate_limit_status: Dict[str, Any]  # Platform-specific rate limit info
    queued_for_later: bool
    
    # Metrics
    execution_metrics: Dict[str, Any]
    success_rate: float
    total_duration: Optional[float]
    
    # Error tracking
    errors: List[Dict[str, Any]]
    warnings: List[str]
    
    # Checkpointing
    last_checkpoint: str
    checkpoint_count: int

# Initial state factory
def create_initial_state(
    workflow_id: str,
    github_repo_url: str,
    github_username: str,
    platforms: List[str],
    dry_run: bool = False
) -> WorkflowState:
    """
    Create initial workflow state.
    
    Args:
        workflow_id: Unique workflow identifier
        github_repo_url: GitHub repository URL
        github_username: GitHub username
        platforms: List of target platforms
        dry_run: Whether to skip actual publishing
        
    Returns:
        Initial workflow state
    """
    now = datetime.utcnow().isoformat()
    
    return WorkflowState(
        # Metadata
        workflow_id=workflow_id,
        phase=WorkflowPhase.IDLE,
        created_at=now,
        updated_at=now,
        
        # Inputs
        github_repo_url=github_repo_url,
        github_username=github_username,
        platforms=platforms,
        dry_run=dry_run,
        
        # Analysis
        analysis_status="pending",
        analysis_results=None,
        analysis_error=None,
        analysis_retry_count=0,
        
        # Generation
        generation_status="pending",
        content_drafts=None,
        generation_error=None,
        generation_retry_count=0,
        
        # Validation
        validation_status="pending",
        validation_results=None,
        
        # Publishing
        publishing_status="pending",
        published_posts=[],
        publishing_errors=[],
        
        # Rate Limiting
        rate_limit_status={},
        queued_for_later=False,
        
        # Metrics
        execution_metrics={},
        success_rate=0.0,
        total_duration=None,
        
        # Errors
        errors=[],
        warnings=[],
        
        # Checkpointing
        last_checkpoint=now,
        checkpoint_count=0
    )

# State update helpers
def update_phase(state: WorkflowState, new_phase: WorkflowPhase) -> WorkflowState:
    """Update workflow phase and timestamp."""
    state["phase"] = new_phase
    state["updated_at"] = datetime.utcnow().isoformat()
    return state

def add_error(state: WorkflowState, error: Dict[str, Any]) -> WorkflowState:
    """Add error to state tracking."""
    state["errors"].append({
        **error,
        "timestamp": datetime.utcnow().isoformat()
    })
    return state

def increment_checkpoint(state: WorkflowState) -> WorkflowState:
    """Increment checkpoint counter."""
    state["checkpoint_count"] += 1
    state["last_checkpoint"] = datetime.utcnow().isoformat()
    return state