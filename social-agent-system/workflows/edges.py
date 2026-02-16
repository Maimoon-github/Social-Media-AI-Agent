from typing import Literal
from .state import WorkflowState
from config import get_settings
import structlog

logger = structlog.get_logger()

class WorkflowEdges:
    """Conditional edge routing logic."""
    
    def __init__(self):
        self.settings = get_settings()
    
    def route_after_initialize(
        self,
        state: WorkflowState
    ) -> Literal["analyze", "error"]:
        """Route after initialization."""
        if state["phase"] == "failed":
            return "error"
        return "analyze"
    
    def route_after_analysis(
        self,
        state: WorkflowState
    ) -> Literal["generate", "retry", "error"]:
        """Route after GitHub analysis."""
        if state["analysis_status"] == "completed":
            return "generate"
        
        elif state["analysis_status"] == "failed":
            if state["analysis_retry_count"] < self.settings.workflow.max_retries:
                logger.info(
                    "Retrying GitHub analysis",
                    retry_count=state["analysis_retry_count"]
                )
                return "retry"
            else:
                logger.error("Max retries exceeded for GitHub analysis")
                return "error"
        
        return "error"
    
    def route_after_generation(
        self,
        state: WorkflowState
    ) -> Literal["validate", "retry", "error"]:
        """Route after content generation."""
        if state["generation_status"] in ["completed", "partial"]:
            # Proceed even with partial content
            return "validate"
        
        elif state["generation_status"] == "failed":
            if state["generation_retry_count"] < self.settings.workflow.max_retries:
                logger.info(
                    "Retrying content generation",
                    retry_count=state["generation_retry_count"]
                )
                return "retry"
            else:
                logger.error("Max retries exceeded for content generation")
                return "error"
        
        return "error"
    
    def route_after_validation(
        self,
        state: WorkflowState
    ) -> Literal["check_limits", "error"]:
        """Route after content validation."""
        if state["validation_status"] == "completed":
            return "check_limits"
        return "error"
    
    def route_after_rate_check(
        self,
        state: WorkflowState
    ) -> Literal["publish", "queue"]:
        """Route after rate limit check."""
        if state["queued_for_later"]:
            logger.info("Workflow queued due to rate limits")
            return "queue"
        return "publish"
    
    def route_after_publishing(
        self,
        state: WorkflowState
    ) -> Literal["calculate", "retry", "error"]:
        """Route after publishing attempt."""
        if state["publishing_status"] in ["completed", "partial"]:
            # Proceed to metrics even if some platforms failed
            return "calculate"
        
        elif state["publishing_status"] == "failed":
            # Check if all platforms failed
            all_failed = all(
                p["status"] == "failed"
                for p in state["published_posts"]
            )
            
            if all_failed:
                logger.error("All platform publishing failed")
                return "error"
            else:
                # At least one succeeded
                return "calculate"
        
        return "calculate"