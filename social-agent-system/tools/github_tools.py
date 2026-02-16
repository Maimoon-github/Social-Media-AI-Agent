from langchain.tools import BaseTool
from typing import List
from integrations.github import GitHubClient
from crews.github_crew.tools import create_github_tools as create_crew_tools

def create_github_tools() -> List[BaseTool]:
    """
    Create all GitHub tools for agent use.
    
    Returns:
        List of GitHub analysis tools
    """
    # Reuse crew tools
    return create_crew_tools()

# Additional GitHub tools can be defined here if needed