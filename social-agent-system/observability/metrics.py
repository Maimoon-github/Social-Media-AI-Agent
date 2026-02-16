from typing import Dict, Any, List
from datetime import datetime
import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()

@dataclass
class WorkflowMetrics:
    """Metrics for a single workflow execution."""
    
    workflow_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    
    # Phase durations (in seconds)
    initialization_duration: float = 0.0
    analysis_duration: float = 0.0
    generation_duration: float = 0.0
    publishing_duration: float = 0.0
    total_duration: float = 0.0
    
    # Counts
    api_calls_github: int = 0
    api_calls_linkedin: int = 0
    api_calls_x: int = 0
    api_calls_instagram: int = 0
    llm_calls_analysis: int = 0
    llm_calls_content: int = 0
    
    # Retries
    retry_count_analysis: int = 0
    retry_count_generation: int = 0
    retry_count_publishing: int = 0
    
    # Results
    platforms_requested: int = 0
    platforms_successful: int = 0
    success_rate: float = 0.0
    
    # Errors
    error_count: int = 0
    errors: List[str] = field(default_factory=list)

class MetricsCollector:
    """
    Collects and aggregates metrics across workflow executions.
    
    Provides insights into system performance, API usage, and success rates.
    """
    
    def __init__(self):
        self.workflows: Dict[str, WorkflowMetrics] = {}
        self.aggregate_metrics = {
            "total_workflows": 0,
            "successful_workflows": 0,
            "failed_workflows": 0,
            "average_duration": 0.0,
            "total_api_calls": 0,
            "total_llm_calls": 0
        }
    
    def start_workflow(self, workflow_id: str) -> WorkflowMetrics:
        """
        Start tracking a new workflow.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            WorkflowMetrics instance
        """
        metrics = WorkflowMetrics(
            workflow_id=workflow_id,
            start_time=datetime.utcnow()
        )
        self.workflows[workflow_id] = metrics
        
        logger.info("Metrics tracking started", workflow_id=workflow_id)
        return metrics
    
    def end_workflow(self, workflow_id: str):
        """Mark workflow as completed and calculate metrics."""
        if workflow_id not in self.workflows:
            logger.warning("Workflow not found in metrics", workflow_id=workflow_id)
            return
        
        metrics = self.workflows[workflow_id]
        metrics.end_time = datetime.utcnow()
        metrics.total_duration = (
            metrics.end_time - metrics.start_time
        ).total_seconds()
        
        # Update aggregate metrics
        self.aggregate_metrics["total_workflows"] += 1
        if metrics.success_rate > 0:
            self.aggregate_metrics["successful_workflows"] += 1
        else:
            self.aggregate_metrics["failed_workflows"] += 1
        
        # Update average duration
        total = self.aggregate_metrics["total_workflows"]
        current_avg = self.aggregate_metrics["average_duration"]
        self.aggregate_metrics["average_duration"] = (
            (current_avg * (total - 1) + metrics.total_duration) / total
        )
        
        logger.info(
            "Workflow metrics completed",
            workflow_id=workflow_id,
            duration=metrics.total_duration,
            success_rate=metrics.success_rate
        )
    
    def record_phase_duration(
        self,
        workflow_id: str,
        phase: str,
        duration: float
    ):
        """Record duration for a specific phase."""
        if workflow_id not in self.workflows:
            return
        
        metrics = self.workflows[workflow_id]
        
        phase_mapping = {
            "initialization": "initialization_duration",
            "analysis": "analysis_duration",
            "generation": "generation_duration",
            "publishing": "publishing_duration"
        }
        
        if phase in phase_mapping:
            setattr(metrics, phase_mapping[phase], duration)
    
    def record_api_call(self, workflow_id: str, platform: str):
        """Record an API call."""
        if workflow_id not in self.workflows:
            return
        
        metrics = self.workflows[workflow_id]
        
        platform_mapping = {
            "github": "api_calls_github",
            "linkedin": "api_calls_linkedin",
            "x": "api_calls_x",
            "twitter": "api_calls_x",
            "instagram": "api_calls_instagram"
        }
        
        if platform in platform_mapping:
            current = getattr(metrics, platform_mapping[platform])
            setattr(metrics, platform_mapping[platform], current + 1)
        
        self.aggregate_metrics["total_api_calls"] += 1
    
    def record_llm_call(self, workflow_id: str, purpose: str):
        """Record an LLM call."""
        if workflow_id not in self.workflows:
            return
        
        metrics = self.workflows[workflow_id]
        
        if purpose == "analysis":
            metrics.llm_calls_analysis += 1
        elif purpose == "content":
            metrics.llm_calls_content += 1
        
        self.aggregate_metrics["total_llm_calls"] += 1
    
    def record_retry(self, workflow_id: str, phase: str):
        """Record a retry attempt."""
        if workflow_id not in self.workflows:
            return
        
        metrics = self.workflows[workflow_id]
        
        if phase == "analysis":
            metrics.retry_count_analysis += 1
        elif phase == "generation":
            metrics.retry_count_generation += 1
        elif phase == "publishing":
            metrics.retry_count_publishing += 1
    
    def record_error(self, workflow_id: str, error: str):
        """Record an error."""
        if workflow_id not in self.workflows:
            return
        
        metrics = self.workflows[workflow_id]
        metrics.error_count += 1
        metrics.errors.append(error)
    
    def get_workflow_metrics(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get metrics for a specific workflow."""
        if workflow_id not in self.workflows:
            return None
        
        metrics = self.workflows[workflow_id]
        
        return {
            "workflow_id": metrics.workflow_id,
            "total_duration": metrics.total_duration,
            "phase_durations": {
                "initialization": metrics.initialization_duration,
                "analysis": metrics.analysis_duration,
                "generation": metrics.generation_duration,
                "publishing": metrics.publishing_duration
            },
            "api_calls": {
                "github": metrics.api_calls_github,
                "linkedin": metrics.api_calls_linkedin,
                "x": metrics.api_calls_x,
                "instagram": metrics.api_calls_instagram,
                "total": (
                    metrics.api_calls_github +
                    metrics.api_calls_linkedin +
                    metrics.api_calls_x +
                    metrics.api_calls_instagram
                )
            },
            "llm_calls": {
                "analysis": metrics.llm_calls_analysis,
                "content": metrics.llm_calls_content,
                "total": metrics.llm_calls_analysis + metrics.llm_calls_content
            },
            "retries": {
                "analysis": metrics.retry_count_analysis,
                "generation": metrics.retry_count_generation,
                "publishing": metrics.retry_count_publishing,
                "total": (
                    metrics.retry_count_analysis +
                    metrics.retry_count_generation +
                    metrics.retry_count_publishing
                )
            },
            "results": {
                "platforms_requested": metrics.platforms_requested,
                "platforms_successful": metrics.platforms_successful,
                "success_rate": metrics.success_rate
            },
            "errors": {
                "count": metrics.error_count,
                "messages": metrics.errors
            }
        }
    
    def get_aggregate_metrics(self) -> Dict[str, Any]:
        """Get aggregate metrics across all workflows."""
        return self.aggregate_metrics.copy()
    
    def export_metrics(self, format: str = "json") -> str:
        """
        Export metrics in specified format.
        
        Args:
            format: Output format (json, csv)
            
        Returns:
            Formatted metrics string
        """
        if format == "json":
            import json
            return json.dumps({
                "aggregate": self.aggregate_metrics,
                "workflows": {
                    wf_id: self.get_workflow_metrics(wf_id)
                    for wf_id in self.workflows.keys()
                }
            }, indent=2)
        
        # CSV export could be implemented here
        return ""

# Singleton instance
_metrics_collector: Optional[MetricsCollector] = None

def get_metrics_collector() -> MetricsCollector:
    """Get metrics collector singleton."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector