from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres import PostgresSaver
from typing import Dict, Any
from .state import WorkflowState, WorkflowPhase, create_initial_state
from .nodes import WorkflowNodes
from .edges import WorkflowEdges
from config import get_settings
import structlog

logger = structlog.get_logger()

class SocialAgentWorkflow:
    """
    LangGraph workflow orchestration for the social agent system.
    
    This class defines the complete workflow graph including nodes,
    edges, and checkpointing configuration.
    """
    
    def __init__(self, checkpointer: PostgresSaver):
        """
        Initialize workflow.
        
        Args:
            checkpointer: PostgreSQL checkpointer for state persistence
        """
        self.settings = get_settings()
        self.checkpointer = checkpointer
        self.nodes = WorkflowNodes()
        self.edges = WorkflowEdges()
        self.graph = self._build_graph()
        
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow.
        
        Returns:
            Configured StateGraph instance
        """
        # Create graph with state schema
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("initialize", self.nodes.initialize_node)
        workflow.add_node("analyze_github", self.nodes.analyze_github_node)
        workflow.add_node("generate_content", self.nodes.generate_content_node)
        workflow.add_node("validate_content", self.nodes.validate_content_node)
        workflow.add_node("check_rate_limits", self.nodes.check_rate_limits_node)
        workflow.add_node("publish_content", self.nodes.publish_content_node)
        workflow.add_node("calculate_metrics", self.nodes.calculate_metrics_node)
        workflow.add_node("handle_error", self.nodes.handle_error_node)
        
        # Set entry point
        workflow.set_entry_point("initialize")
        
        # Add edges
        # Initialize → Analyze (or Error if init fails)
        workflow.add_conditional_edges(
            "initialize",
            self.edges.route_after_initialize,
            {
                "analyze": "analyze_github",
                "error": "handle_error"
            }
        )
        
        # Analyze → Generate (or Retry or Error)
        workflow.add_conditional_edges(
            "analyze_github",
            self.edges.route_after_analysis,
            {
                "generate": "generate_content",
                "retry": "analyze_github",
                "error": "handle_error"
            }
        )
        
        # Generate → Validate (or Retry or Error)
        workflow.add_conditional_edges(
            "generate_content",
            self.edges.route_after_generation,
            {
                "validate": "validate_content",
                "retry": "generate_content",
                "error": "handle_error"
            }
        )
        
        # Validate → Check Rate Limits (or Error)
        workflow.add_conditional_edges(
            "validate_content",
            self.edges.route_after_validation,
            {
                "check_limits": "check_rate_limits",
                "error": "handle_error"
            }
        )
        
        # Check Rate Limits → Publish or Queue
        workflow.add_conditional_edges(
            "check_rate_limits",
            self.edges.route_after_rate_check,
            {
                "publish": "publish_content",
                "queue": END  # Queue for later, end workflow
            }
        )
        
        # Publish → Calculate Metrics (or Retry)
        workflow.add_conditional_edges(
            "publish_content",
            self.edges.route_after_publishing,
            {
                "calculate": "calculate_metrics",
                "retry": "publish_content",
                "error": "handle_error"
            }
        )
        
        # Calculate Metrics → END
        workflow.add_edge("calculate_metrics", END)
        
        # Error Handler → END
        workflow.add_edge("handle_error", END)
        
        return workflow.compile(checkpointer=self.checkpointer)
    
    async def execute(
        self,
        github_repo_url: str,
        github_username: str,
        platforms: List[str],
        dry_run: bool = False,
        workflow_id: Optional[str] = None
    ) -> WorkflowState:
        """
        Execute the workflow.
        
        Args:
            github_repo_url: GitHub repository URL
            github_username: GitHub username
            platforms: Target platforms for publishing
            dry_run: Skip actual publishing if True
            workflow_id: Resume existing workflow if provided
            
        Returns:
            Final workflow state
        """
        # Create or resume workflow state
        if workflow_id:
            logger.info("Resuming workflow", workflow_id=workflow_id)
            # Load state from checkpoint
            state = await self._load_checkpoint(workflow_id)
        else:
            # Create new workflow
            import uuid
            workflow_id = str(uuid.uuid4())
            logger.info("Starting new workflow", workflow_id=workflow_id)
            
            state = create_initial_state(
                workflow_id=workflow_id,
                github_repo_url=github_repo_url,
                github_username=github_username,
                platforms=platforms,
                dry_run=dry_run
            )
        
        try:
            # Execute graph
            final_state = await self.graph.ainvoke(
                state,
                config={
                    "configurable": {
                        "thread_id": workflow_id
                    }
                }
            )
            
            logger.info(
                "Workflow completed",
                workflow_id=workflow_id,
                phase=final_state["phase"],
                success_rate=final_state["success_rate"]
            )
            
            return final_state
            
        except Exception as e:
            logger.error(
                "Workflow execution failed",
                workflow_id=workflow_id,
                error=str(e)
            )
            raise
    
    async def _load_checkpoint(self, workflow_id: str) -> WorkflowState:
        """Load workflow state from checkpoint."""
        # Implementation depends on PostgresSaver API
        # This should retrieve the latest checkpoint for the workflow
        pass