import os
from typing import Optional, Dict, Any
from functools import wraps
import structlog
from config import get_settings

logger = structlog.get_logger()

def setup_tracing() -> None:
    """
    Setup LangSmith tracing for LangChain/LangGraph.
    
    Configures environment variables for automatic tracing.
    """
    settings = get_settings()
    
    if settings.observability.langsmith_api_key:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = settings.observability.langsmith_api_key
        os.environ["LANGCHAIN_PROJECT"] = settings.observability.langsmith_project
        
        logger.info(
            "LangSmith tracing enabled",
            project=settings.observability.langsmith_project
        )
    else:
        logger.warning("LangSmith API key not configured - tracing disabled")

def trace_workflow(workflow_name: str):
    """
    Decorator to trace workflow execution in LangSmith.
    
    Args:
        workflow_name: Name of the workflow for tracing
        
    Usage:
        @trace_workflow("github_analysis")
        async def analyze_github(repo_url: str):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # LangChain automatically traces when LANGCHAIN_TRACING_V2 is enabled
            # This wrapper adds additional context
            
            from langchain.callbacks import tracing_v2_enabled
            
            with tracing_v2_enabled(
                project_name=get_settings().observability.langsmith_project,
                tags=[workflow_name]
            ):
                result = await func(*args, **kwargs)
                return result
        
        return wrapper
    return decorator

class TracingContext:
    """
    Context manager for adding tracing metadata.
    
    Usage:
        async with TracingContext(workflow_id="123", phase="analysis"):
            # Code here will be traced with added metadata
            ...
    """
    
    def __init__(self, **metadata: Any):
        """
        Initialize tracing context.
        
        Args:
            **metadata: Metadata to add to traces
        """
        self.metadata = metadata
        self.previous_metadata = {}
    
    async def __aenter__(self):
        """Enter context and set metadata."""
        # Store metadata in structlog context
        for key, value in self.metadata.items():
            structlog.contextvars.bind_contextvars(**{key: value})
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit context and restore metadata."""
        # Clear context vars
        for key in self.metadata.keys():
            structlog.contextvars.unbind_contextvars(key)
        
        return False