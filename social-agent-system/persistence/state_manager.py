from langgraph.checkpoint.postgres import PostgresSaver
from typing import Dict, Any, Optional
import structlog
from .database import DatabaseManager

logger = structlog.get_logger()

class StateManager:
    """
    Manages workflow state persistence for LangGraph.
    
    Integrates with LangGraph's PostgresSaver for checkpoint storage
    and provides additional state management capabilities.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize state manager.
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
        self.checkpointer: Optional[PostgresSaver] = None
    
    async def initialize(self):
        """Initialize checkpointer."""
        # Create PostgresSaver instance for LangGraph
        self.checkpointer = PostgresSaver.from_conn_string(
            self.db_manager.database_url
        )
        await self.checkpointer.setup()
        logger.info("State manager initialized with PostgreSQL checkpointer")
    
    def get_checkpointer(self) -> PostgresSaver:
        """
        Get LangGraph checkpointer instance.
        
        Returns:
            PostgresSaver for use with LangGraph workflows
        """
        if not self.checkpointer:
            raise RuntimeError("State manager not initialized. Call initialize() first.")
        return self.checkpointer
    
    async def save_checkpoint(
        self,
        workflow_id: str,
        state: Dict[str, Any],
        checkpoint_name: str
    ):
        """
        Save a named checkpoint (in addition to automatic LangGraph checkpoints).
        
        Args:
            workflow_id: Workflow identifier
            state: Current workflow state
            checkpoint_name: Human-readable checkpoint name
        """
        # Save to workflow_runs table
        await self.db_manager.update_workflow_run(
            workflow_id=workflow_id,
            updates={
                "phase": state.get("phase"),
                "analysis_results": state.get("analysis_results"),
                "content_drafts": state.get("content_drafts"),
                "published_posts": state.get("published_posts"),
                "execution_metrics": state.get("execution_metrics")
            }
        )
        
        logger.info(
            "Checkpoint saved",
            workflow_id=workflow_id,
            checkpoint=checkpoint_name
        )
    
    async def load_checkpoint(
        self,
        workflow_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Load the latest checkpoint for a workflow.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            Workflow state if found, None otherwise
        """
        workflow_data = await self.db_manager.get_workflow_run(workflow_id)
        
        if workflow_data:
            logger.info("Checkpoint loaded", workflow_id=workflow_id)
            return workflow_data
        
        logger.warning("No checkpoint found", workflow_id=workflow_id)
        return None
    
    async def list_checkpoints(self, workflow_id: str) -> list:
        """
        List all checkpoints for a workflow.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            List of checkpoint metadata
        """
        # Query checkpointer for all checkpoints
        # Implementation depends on PostgresSaver API
        pass
    
    async def cleanup_old_checkpoints(self, days: int = 30):
        """
        Clean up checkpoints older than specified days.
        
        Args:
            days: Number of days to retain checkpoints
        """
        # Implementation for cleanup
        logger.info(f"Cleaning up checkpoints older than {days} days")