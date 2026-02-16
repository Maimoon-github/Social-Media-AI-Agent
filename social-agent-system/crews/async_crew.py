import asyncio
from typing import Any, Dict, Optional
from concurrent.futures import ThreadPoolExecutor
from crewai import Crew
import structlog

logger = structlog.get_logger()

class AsyncCrewExecutor:
    """
    Async wrapper for CrewAI crew execution.
    
    CrewAI is synchronous by design, so we use a thread pool executor
    to run crews without blocking the event loop.
    """
    
    def __init__(self, max_workers: int = 5):
        """
        Initialize async executor.
        
        Args:
            max_workers: Maximum number of concurrent crew executions
        """
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.active_crews: Dict[str, Crew] = {}
        
    async def execute_crew(
        self,
        crew: Crew,
        inputs: Dict[str, Any],
        crew_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a CrewAI crew asynchronously.
        
        Args:
            crew: CrewAI Crew instance
            inputs: Input data for the crew
            crew_id: Optional identifier for tracking
            
        Returns:
            Crew execution results
        """
        if crew_id:
            self.active_crews[crew_id] = crew
            logger.info("Starting crew execution", crew_id=crew_id)
        
        try:
            # Run crew in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor,
                crew.kickoff,
                inputs
            )
            
            logger.info("Crew execution completed", crew_id=crew_id)
            return result
            
        except Exception as e:
            logger.error("Crew execution failed", crew_id=crew_id, error=str(e))
            raise
            
        finally:
            if crew_id and crew_id in self.active_crews:
                del self.active_crews[crew_id]
    
    async def execute_multiple_crews(
        self,
        crews: Dict[str, Tuple[Crew, Dict[str, Any]]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Execute multiple crews concurrently.
        
        Args:
            crews: Dictionary mapping crew_id to (crew, inputs) tuples
            
        Returns:
            Dictionary mapping crew_id to results
        """
        tasks = {
            crew_id: self.execute_crew(crew, inputs, crew_id)
            for crew_id, (crew, inputs) in crews.items()
        }
        
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        return {
            crew_id: result
            for crew_id, result in zip(tasks.keys(), results)
        }
    
    async def shutdown(self):
        """Shutdown the executor and cleanup resources."""
        logger.info("Shutting down crew executor")
        self.executor.shutdown(wait=True)
        self.active_crews.clear()