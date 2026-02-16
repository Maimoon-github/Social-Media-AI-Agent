from typing import Dict, Any
from datetime import datetime
import structlog
from .state import WorkflowState, WorkflowPhase, update_phase, add_error
from crews import GitHubAnalysisCrew, ContentGenerationCrew, AsyncCrewExecutor
from integrations.publisher import MultiPlatformPublisher
from config import get_settings

logger = structlog.get_logger()

class WorkflowNodes:
    """Implementations of workflow graph nodes."""
    
    def __init__(self):
        self.settings = get_settings()
        self.crew_executor = AsyncCrewExecutor()
        self.github_crew = GitHubAnalysisCrew()
        self.content_crew = ContentGenerationCrew()
        self.publisher = None  # Initialized in initialize_node
        
    async def initialize_node(self, state: WorkflowState) -> WorkflowState:
        """
        Initialize workflow resources.
        
        - Validate configuration
        - Initialize publishers
        - Setup tracing
        """
        logger.info("Initializing workflow", workflow_id=state["workflow_id"])
        state = update_phase(state, WorkflowPhase.INITIALIZING)
        
        try:
            # Initialize publishers
            self.publisher = MultiPlatformPublisher(
                platforms=state["platforms"],
                dry_run=state["dry_run"]
            )
            await self.publisher.initialize()
            
            logger.info("Workflow initialized successfully")
            return state
            
        except Exception as e:
            logger.error("Initialization failed", error=str(e))
            state = add_error(state, {
                "phase": "initialization",
                "error": str(e)
            })
            state["phase"] = WorkflowPhase.FAILED
            return state
    
    async def analyze_github_node(self, state: WorkflowState) -> WorkflowState:
        """
        Execute GitHub analysis using GitHubAnalysisCrew.
        """
        logger.info("Starting GitHub analysis", workflow_id=state["workflow_id"])
        state = update_phase(state, WorkflowPhase.ANALYZING)
        state["analysis_status"] = "in_progress"
        
        try:
            # Create crew for this specific analysis
            crew = self.github_crew.create_crew(
                github_repo_url=state["github_repo_url"],
                github_username=state["github_username"]
            )
            
            # Execute crew asynchronously
            raw_output = await self.crew_executor.execute_crew(
                crew=crew,
                inputs={
                    "repo_url": state["github_repo_url"],
                    "username": state["github_username"]
                },
                crew_id=f"{state['workflow_id']}-github-analysis"
            )
            
            # Parse and structure results
            analysis_results = self.github_crew.parse_results(raw_output)
            
            state["analysis_results"] = analysis_results
            state["analysis_status"] = "completed"
            
            logger.info(
                "GitHub analysis completed",
                health_score=analysis_results.get("repository", {}).get("health_score")
            )
            
            return state
            
        except Exception as e:
            logger.error("GitHub analysis failed", error=str(e))
            
            state["analysis_error"] = str(e)
            state["analysis_retry_count"] += 1
            
            if state["analysis_retry_count"] >= self.settings.workflow.max_retries:
                state["analysis_status"] = "failed"
                state["phase"] = WorkflowPhase.FAILED
                state = add_error(state, {
                    "phase": "analysis",
                    "error": str(e),
                    "retry_count": state["analysis_retry_count"]
                })
            
            return state
    
    async def generate_content_node(self, state: WorkflowState) -> WorkflowState:
        """
        Generate platform-specific content using ContentGenerationCrew.
        """
        logger.info("Starting content generation", workflow_id=state["workflow_id"])
        state = update_phase(state, WorkflowPhase.GENERATING)
        state["generation_status"] = "in_progress"
        
        try:
            # Ensure analysis results are available
            if not state["analysis_results"]:
                raise ValueError("Analysis results not available for content generation")
            
            # Create crew for content generation
            crew = self.content_crew.create_crew(
                analysis_results=state["analysis_results"],
                platforms=state["platforms"]
            )
            
            # Execute crew asynchronously
            raw_output = await self.crew_executor.execute_crew(
                crew=crew,
                inputs={
                    "analysis": state["analysis_results"],
                    "platforms": state["platforms"]
                },
                crew_id=f"{state['workflow_id']}-content-generation"
            )
            
            # Parse and validate results
            content_results = self.content_crew.parse_and_validate_results(
                raw_output=raw_output,
                platforms=state["platforms"]
            )
            
            # Check if we got content for all requested platforms
            successful_platforms = content_results["metadata"]["platforms_successful"]
            if len(successful_platforms) < len(state["platforms"]):
                state["generation_status"] = "partial"
                state["warnings"].append(
                    f"Content generated for only {len(successful_platforms)} of "
                    f"{len(state['platforms'])} requested platforms"
                )
            else:
                state["generation_status"] = "completed"
            
            state["content_drafts"] = content_results
            
            logger.info(
                "Content generation completed",
                platforms_successful=successful_platforms
            )
            
            return state
            
        except Exception as e:
            logger.error("Content generation failed", error=str(e))
            
            state["generation_error"] = str(e)
            state["generation_retry_count"] += 1
            
            if state["generation_retry_count"] >= self.settings.workflow.max_retries:
                state["generation_status"] = "failed"
                state["phase"] = WorkflowPhase.FAILED
                state = add_error(state, {
                    "phase": "generation",
                    "error": str(e),
                    "retry_count": state["generation_retry_count"]
                })
            
            return state
    
    async def validate_content_node(self, state: WorkflowState) -> WorkflowState:
        """
        Validate content against platform requirements.
        """
        logger.info("Validating content", workflow_id=state["workflow_id"])
        state = update_phase(state, WorkflowPhase.VALIDATING)
        state["validation_status"] = "pending"
        
        try:
            # Content validation is already done in parse_and_validate_results
            # This node performs additional checks if needed
            
            validation_results = {
                "all_valid": True,
                "platform_results": {}
            }
            
            drafts = state["content_drafts"]["drafts"]
            for platform, content in drafts.items():
                # Additional validation logic here
                validation_results["platform_results"][platform] = {
                    "valid": True,
                    "warnings": []
                }
            
            state["validation_results"] = validation_results
            state["validation_status"] = "completed"
            
            logger.info("Content validation completed")
            return state
            
        except Exception as e:
            logger.error("Content validation failed", error=str(e))
            state["validation_status"] = "failed"
            state = add_error(state, {
                "phase": "validation",
                "error": str(e)
            })
            return state
    
    async def check_rate_limits_node(self, state: WorkflowState) -> WorkflowState:
        """
        Check rate limits for all platforms before publishing.
        """
        logger.info("Checking rate limits", workflow_id=state["workflow_id"])
        
        try:
            rate_limit_status = await self.publisher.check_rate_limits_all()
            state["rate_limit_status"] = rate_limit_status
            
            # Check if any platform would exceed limits
            any_exceeded = any(
                status.get("would_exceed", False)
                for status in rate_limit_status.values()
            )
            
            if any_exceeded:
                state["queued_for_later"] = True
                logger.warning("Rate limits would be exceeded, queuing workflow")
            
            return state
            
        except Exception as e:
            logger.error("Rate limit check failed", error=str(e))
            state = add_error(state, {
                "phase": "rate_limit_check",
                "error": str(e)
            })
            return state
    
    async def publish_content_node(self, state: WorkflowState) -> WorkflowState:
        """
        Publish content to all platforms in parallel.
        """
        logger.info("Publishing content", workflow_id=state["workflow_id"])
        state = update_phase(state, WorkflowPhase.PUBLISHING)
        state["publishing_status"] = "in_progress"
        
        try:
            # Get content drafts
            drafts = state["content_drafts"]["drafts"]
            
            # Publish to all platforms
            results = await self.publisher.publish_all(drafts)
            
            # Update state with results
            state["published_posts"] = results["posts"]
            state["publishing_errors"] = results["errors"]
            
            # Determine overall publishing status
            successful = [p for p in results["posts"] if p["status"] == "success"]
            if len(successful) == 0:
                state["publishing_status"] = "failed"
            elif len(successful) < len(drafts):
                state["publishing_status"] = "partial"
            else:
                state["publishing_status"] = "completed"
            
            logger.info(
                "Publishing completed",
                successful=len(successful),
                total=len(drafts)
            )
            
            return state
            
        except Exception as e:
            logger.error("Publishing failed", error=str(e))
            state["publishing_status"] = "failed"
            state = add_error(state, {
                "phase": "publishing",
                "error": str(e)
            })
            return state
    
    async def calculate_metrics_node(self, state: WorkflowState) -> WorkflowState:
        """
        Calculate final workflow metrics.
        """
        logger.info("Calculating metrics", workflow_id=state["workflow_id"])
        state = update_phase(state, WorkflowPhase.COMPLETED)
        
        try:
            # Calculate success rate
            total_platforms = len(state["platforms"])
            successful_posts = len([
                p for p in state["published_posts"]
                if p["status"] == "success"
            ])
            state["success_rate"] = successful_posts / total_platforms if total_platforms > 0 else 0.0
            
            # Calculate duration
            created_at = datetime.fromisoformat(state["created_at"])
            completed_at = datetime.utcnow()
            duration = (completed_at - created_at).total_seconds()
            state["total_duration"] = duration
            
            # Store metrics
            state["execution_metrics"] = {
                "total_duration_seconds": duration,
                "analysis_retries": state["analysis_retry_count"],
                "generation_retries": state["generation_retry_count"],
                "platforms_requested": total_platforms,
                "platforms_successful": successful_posts,
                "success_rate": state["success_rate"],
                "total_errors": len(state["errors"]),
                "total_warnings": len(state["warnings"])
            }
            
            logger.info(
                "Metrics calculated",
                success_rate=state["success_rate"],
                duration=duration
            )
            
            return state
            
        except Exception as e:
            logger.error("Metrics calculation failed", error=str(e))
            state = add_error(state, {
                "phase": "metrics",
                "error": str(e)
            })
            return state
    
    async def handle_error_node(self, state: WorkflowState) -> WorkflowState:
        """
        Handle workflow errors and cleanup.
        """
        logger.error(
            "Workflow error handler invoked",
            workflow_id=state["workflow_id"],
            errors=state["errors"]
        )
        
        state["phase"] = WorkflowPhase.FAILED
        
        # Cleanup resources
        if self.publisher:
            await self.publisher.cleanup()
        
        return state