from langchain.tools import BaseTool
from typing import List, Dict, Any
from pydantic import Field
from integrations.github import GitHubClient
from config import get_settings

class GitHubRepoFetchTool(BaseTool):
    """Tool to fetch repository metadata."""
    
    name: str = "github_repo_fetch"
    description: str = (
        "Fetches GitHub repository metadata including name, description, "
        "stars, forks, and other basic information. Input should be the "
        "full repository URL or 'owner/repo' format."
    )
    github_client: GitHubClient = Field(default_factory=lambda: GitHubClient())
    
    def _run(self, repo_identifier: str) -> Dict[str, Any]:
        """Fetch repository data."""
        return self.github_client.get_repository(repo_identifier)

class GitHubLanguagesTool(BaseTool):
    """Tool to fetch repository language breakdown."""
    
    name: str = "github_languages_fetch"
    description: str = (
        "Fetches the programming language breakdown for a repository, "
        "showing which languages are used and their proportions."
    )
    github_client: GitHubClient = Field(default_factory=lambda: GitHubClient())
    
    def _run(self, repo_identifier: str) -> Dict[str, int]:
        """Fetch language statistics."""
        return self.github_client.get_languages(repo_identifier)

class GitHubCommitsTool(BaseTool):
    """Tool to fetch recent commits."""
    
    name: str = "github_commits_fetch"
    description: str = (
        "Fetches recent commits from a repository, including commit messages, "
        "authors, and timestamps. Useful for understanding recent activity."
    )
    github_client: GitHubClient = Field(default_factory=lambda: GitHubClient())
    
    def _run(self, repo_identifier: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch recent commits."""
        return self.github_client.get_commits(repo_identifier, limit=limit)

class GitHubProfileTool(BaseTool):
    """Tool to fetch user profile data."""
    
    name: str = "github_profile_fetch"
    description: str = (
        "Fetches GitHub user profile information including name, bio, "
        "location, company, followers, and other public profile data."
    )
    github_client: GitHubClient = Field(default_factory=lambda: GitHubClient())
    
    def _run(self, username: str) -> Dict[str, Any]:
        """Fetch user profile."""
        return self.github_client.get_user(username)

class GitHubUserReposTool(BaseTool):
    """Tool to fetch user's repositories."""
    
    name: str = "github_repos_list"
    description: str = (
        "Fetches a list of repositories owned by a user, including "
        "repository names, descriptions, stars, and language information."
    )
    github_client: GitHubClient = Field(default_factory=lambda: GitHubClient())
    
    def _run(self, username: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch user repositories."""
        return self.github_client.get_user_repos(username, limit=limit)

def create_github_tools() -> List[BaseTool]:
    """
    Create all GitHub analysis tools.
    
    Returns:
        List of configured tool instances
    """
    return [
        GitHubRepoFetchTool(),
        GitHubLanguagesTool(),
        GitHubCommitsTool(),
        GitHubProfileTool(),
        GitHubUserReposTool()
    ]