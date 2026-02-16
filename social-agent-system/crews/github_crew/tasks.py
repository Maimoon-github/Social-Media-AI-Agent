from crewai import Task, Agent
from typing import Dict, Any

def create_repo_analysis_task(
    agent: Agent,
    repo_url: str
) -> Task:
    """
    Create repository analysis task.
    
    Args:
        agent: Repository researcher agent
        repo_url: GitHub repository URL
        
    Returns:
        Configured Task instance
    """
    return Task(
        description=f"""
        Analyze the GitHub repository: {repo_url}
        
        Your analysis should include:
        1. Repository metadata (name, description, stars, forks, creation date)
        2. Technology stack identification (languages, frameworks, tools)
        3. Code quality assessment (structure, patterns, documentation)
        4. Recent activity analysis (commit frequency, contributor patterns)
        5. Repository health score (0-100) based on:
           - Code quality indicators
           - Documentation completeness
           - Issue management
           - Community engagement
           - Update frequency
        6. Key technical insights and notable features
        
        Use the provided GitHub tools to fetch:
        - Repository metadata
        - Language breakdown
        - Recent commits
        - Issue/PR statistics
        - README content
        
        Provide a comprehensive technical profile of the repository that would
        be valuable for content creation about this project.
        """,
        agent=agent,
        expected_output="""
        A detailed technical analysis in JSON format:
        {
            "name": "repository name",
            "description": "description",
            "metrics": {
                "stars": int,
                "forks": int,
                "open_issues": int,
                "watchers": int
            },
            "health_score": float (0-100),
            "tech_stack": ["Python", "FastAPI", "PostgreSQL"],
            "code_quality": {
                "structure": "well-organized/needs-improvement",
                "documentation": "excellent/good/lacking",
                "test_coverage": "high/medium/low/unknown"
            },
            "recent_activity": {
                "commit_frequency": "daily/weekly/monthly",
                "last_commit": "timestamp",
                "active_contributors": int
            },
            "key_insights": [
                "Unique features",
                "Technical highlights",
                "Noteworthy patterns"
            ]
        }
        """
    )

def create_profile_analysis_task(
    agent: Agent,
    username: str
) -> Task:
    """
    Create profile analysis task.
    
    Args:
        agent: Profile analyzer agent
        username: GitHub username
        
    Returns:
        Configured Task instance
    """
    return Task(
        description=f"""
        Analyze the GitHub profile: {username}
        
        Your analysis should include:
        1. Profile metadata (name, bio, location, company)
        2. Expertise areas (based on repository topics and languages)
        3. Contribution patterns:
           - Commit frequency and timing
           - Type of contributions (code, documentation, issues)
           - Collaboration patterns
        4. Notable projects and their impact
        5. Professional positioning and personal brand
        6. Community engagement (stars received, followers)
        
        Use the provided GitHub tools to fetch:
        - User profile data
        - Repository list and details
        - Contribution activity
        - Language statistics
        
        Synthesize this data into a professional narrative that captures
        the developer's expertise and value proposition.
        """,
        agent=agent,
        expected_output="""
        A comprehensive profile analysis in JSON format:
        {
            "username": "username",
            "name": "Full Name",
            "bio": "Bio text",
            "metadata": {
                "location": "Location",
                "company": "Company",
                "followers": int,
                "total_stars_received": int
            },
            "expertise_areas": [
                {"area": "Machine Learning", "confidence": "high/medium/low"},
                {"area": "Backend Development", "confidence": "high/medium/low"}
            ],
            "contribution_patterns": {
                "frequency": "daily/weekly/sporadic",
                "primary_languages": ["Python", "JavaScript"],
                "contribution_types": {
                    "code": percentage,
                    "documentation": percentage,
                    "issues": percentage
                }
            },
            "notable_projects": [
                {
                    "name": "project-name",
                    "description": "description",
                    "stars": int,
                    "impact": "high/medium/low"
                }
            ],
            "professional_positioning": "A concise narrative of how this developer positions themselves professionally"
        }
        """
    )