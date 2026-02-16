from crewai import Crew, Process
from typing import Dict, Any, List
from langchain_ollama import ChatOllama
from .agents import (
    create_linkedin_expert,
    create_x_expert,
    create_instagram_expert
)
from .tasks import (
    create_linkedin_task,
    create_x_task,
    create_instagram_task
)
from .prompts import get_platform_prompt
from config import get_settings
import structlog

logger = structlog.get_logger()

class ContentGenerationCrew:
    """
    Content generation crew that creates platform-optimized social media content.
    
    Uses Qwen 2.5-7B model optimized for creative content generation.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.llm = self._create_llm()
        self.agents = self._create_agents()
        
    def _create_llm(self) -> ChatOllama:
        """Create LLM instance for content generation."""
        return ChatOllama(
            model=self.settings.llm.content_model,
            base_url=self.settings.llm.ollama_base_url,
            temperature=0.8,  # Higher temperature for creative content
            timeout=self.settings.llm.timeout
        )
    
    def _create_agents(self) -> Dict[str, Any]:
        """Create platform-specific content agents."""
        return {
            "linkedin": create_linkedin_expert(self.llm),
            "x": create_x_expert(self.llm),
            "instagram": create_instagram_expert(self.llm)
        }
    
    def create_crew(
        self,
        analysis_results: Dict[str, Any],
        platforms: List[str]
    ) -> Crew:
        """
        Create a configured crew for content generation.
        
        Args:
            analysis_results: GitHub analysis results from GitHubAnalysisCrew
            platforms: List of platforms to generate content for
            
        Returns:
            Configured CrewAI Crew instance
        """
        # Filter agents and create tasks only for requested platforms
        active_agents = []
        active_tasks = []
        
        if "linkedin" in platforms:
            active_agents.append(self.agents["linkedin"])
            active_tasks.append(
                create_linkedin_task(
                    agent=self.agents["linkedin"],
                    analysis=analysis_results
                )
            )
        
        if "twitter" in platforms or "x" in platforms:
            active_agents.append(self.agents["x"])
            active_tasks.append(
                create_x_task(
                    agent=self.agents["x"],
                    analysis=analysis_results
                )
            )
        
        if "instagram" in platforms:
            active_agents.append(self.agents["instagram"])
            active_tasks.append(
                create_instagram_task(
                    agent=self.agents["instagram"],
                    analysis=analysis_results
                )
            )
        
        # Create crew with parallel process for simultaneous content generation
        crew = Crew(
            agents=active_agents,
            tasks=active_tasks,
            process=Process.parallel,  # Generate all content simultaneously
            verbose=True,
            memory=False,  # No memory needed for independent content tasks
            cache=True
        )
        
        logger.info(
            "Content generation crew created",
            platforms=platforms,
            agent_count=len(active_agents)
        )
        
        return crew
    
    def parse_and_validate_results(
        self,
        raw_output: Dict[str, Any],
        platforms: List[str]
    ) -> Dict[str, Any]:
        """
        Parse crew output and validate against platform requirements.
        
        Args:
            raw_output: Raw output from crew execution
            platforms: Requested platforms
            
        Returns:
            Validated content drafts by platform
        """
        validated_content = {}
        
        for platform in platforms:
            try:
                content = self._extract_platform_content(raw_output, platform)
                validation_result = self._validate_content(content, platform)
                
                if validation_result["valid"]:
                    validated_content[platform] = content
                    logger.info(f"{platform} content validated successfully")
                else:
                    logger.warning(
                        f"{platform} content validation failed",
                        errors=validation_result["errors"]
                    )
                    # Optionally trigger regeneration here
                    
            except Exception as e:
                logger.error(f"Failed to process {platform} content", error=str(e))
        
        return {
            "drafts": validated_content,
            "metadata": {
                "model_used": self.settings.llm.content_model,
                "platforms_requested": platforms,
                "platforms_successful": list(validated_content.keys())
            }
        }
    
    def _extract_platform_content(
        self,
        raw_output: Dict[str, Any],
        platform: str
    ) -> Dict[str, Any]:
        """Extract content for specific platform from raw output."""
        # Implementation depends on CrewAI output format
        pass
    
    def _validate_content(
        self,
        content: Dict[str, Any],
        platform: str
    ) -> Dict[str, Any]:
        """
        Validate content against platform requirements.
        
        Returns:
            Dictionary with 'valid' boolean and 'errors' list
        """
        errors = []
        
        if platform == "linkedin":
            # LinkedIn: max 3000 chars, 3-5 hashtags
            text = content.get("text", "")
            hashtags = content.get("hashtags", [])
            
            if len(text) > 3000:
                errors.append("Text exceeds 3000 character limit")
            if len(hashtags) < 3 or len(hashtags) > 5:
                errors.append("Hashtag count must be 3-5")
                
        elif platform in ["twitter", "x"]:
            # X: max 280 chars per tweet, max 10 tweets in thread
            tweets = content.get("tweets", [])
            
            if len(tweets) > 10:
                errors.append("Thread exceeds 10 tweet limit")
            
            for tweet in tweets:
                if len(tweet.get("text", "")) > 280:
                    errors.append(f"Tweet {tweet.get('order')} exceeds 280 characters")
                    
        elif platform == "instagram":
            # Instagram: max 2200 char caption, must have image description
            caption = content.get("caption", "")
            image_description = content.get("image_description", "")
            
            if len(caption) > 2200:
                errors.append("Caption exceeds 2200 character limit")
            if not image_description:
                errors.append("Image description is required")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }