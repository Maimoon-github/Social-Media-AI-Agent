from crewai import Crew, Process
from typing import Dict, Any
from langchain_ollama import ChatOllama
from .agents import create_repository_researcher, create_profile_analyzer
from .tasks import create_repo_analysis_task, create_profile_analysis_task
from .tools import create_github_tools
from config import get_settings

class GitHubAnalysisCrew:
    """
    GitHub analysis crew that combines repository and profile analysis.
    
    Uses DeepSeek-R1 model for analytical reasoning capabilities.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.llm = self._create_llm()
        self.tools = create_github_tools()
        self.agents = self._create_agents()
        self.tasks = None  # Created dynamically per execution
        
    def _create_llm(self) -> ChatOllama:
        """Create LLM instance for analysis."""
        return ChatOllama(
            model=self.settings.llm.analysis_model,
            base_url=self.settings.llm.ollama_base_url,
            temperature=0.3,  # Lower temperature for analytical tasks
            timeout=self.settings.llm.timeout
        )
    
    def _create_agents(self) -> Dict[str, Any]:
        """Create specialized agents for GitHub analysis."""
        return {
            "researcher": create_repository_researcher(self.llm, self.tools),
            "profile_analyzer": create_profile_analyzer(self.llm, self.tools)
        }
    
    def create_crew(
        self,
        github_repo_url: str,
        github_username: str
    ) -> Crew:
        """
        Create a configured crew for GitHub analysis.
        
        Args:
            github_repo_url: Full GitHub repository URL
            github_username: GitHub username to analyze
            
        Returns:
            Configured CrewAI Crew instance
        """
        # Create tasks with specific inputs
        self.tasks = {
            "repo_analysis": create_repo_analysis_task(
                agent=self.agents["researcher"],
                repo_url=github_repo_url
            ),
            "profile_analysis": create_profile_analysis_task(
                agent=self.agents["profile_analyzer"],
                username=github_username
            )
        }
        
        # Create crew with sequential process
        crew = Crew(
            agents=[self.agents["researcher"], self.agents["profile_analyzer"]],
            tasks=[self.tasks["repo_analysis"], self.tasks["profile_analysis"]],
            process=Process.sequential,  # Repository analysis first, then profile
            verbose=True,
            memory=True,  # Enable memory for context retention
            cache=True  # Cache LLM responses
        )
        
        return crew
    
    def parse_results(self, raw_output: str) -> Dict[str, Any]:
        """
        Parse crew output into structured format.
        
        Args:
            raw_output: Raw string output from crew execution
            
        Returns:
            Structured analysis results
        """
        # Parse the output into structured data
        return {
            "repository": {
                "url": None,  # Extract from output
                "name": None,
                "description": None,
                "stars": None,
                "forks": None,
                "health_score": None,
                "tech_stack": [],
                "recent_activity": {},
                "key_insights": []
            },
            "profile": {
                "username": None,
                "name": None,
                "bio": None,
                "expertise_areas": [],
                "contribution_patterns": {},
                "notable_projects": [],
                "professional_positioning": ""
            },
            "analysis_metadata": {
                "timestamp": None,
                "model_used": self.settings.llm.analysis_model,
                "success": True
            }
        }