from crewai import Agent
from typing import List
from langchain_ollama import ChatOllama

def create_repository_researcher(
    llm: ChatOllama,
    tools: List
) -> Agent:
    """
    Create the Repository Researcher agent.
    
    This agent specializes in analyzing repository structure, code quality,
    tech stack, and recent activity patterns.
    """
    return Agent(
        role="Senior GitHub Repository Analyst",
        goal=(
            "Analyze repository structure, code quality, technology stack, and "
            "recent activity to provide comprehensive technical insights"
        ),
        backstory=(
            "You are an expert software engineer with deep knowledge of code patterns, "
            "best practices, and project health indicators. You've analyzed thousands "
            "of open-source projects and can quickly identify quality signals, "
            "architectural patterns, and development trends. Your analysis helps "
            "developers and companies understand repository health and technical value."
        ),
        verbose=True,
        allow_delegation=False,
        tools=tools,
        llm=llm,
        max_iter=10,
        max_rpm=10
    )

def create_profile_analyzer(
    llm: ChatOllama,
    tools: List
) -> Agent:
    """
    Create the Profile Analyzer agent.
    
    This agent specializes in extracting developer expertise, contribution
    patterns, and professional identity from GitHub profiles.
    """
    return Agent(
        role="GitHub Profile Intelligence Specialist",
        goal=(
            "Extract developer expertise, contribution patterns, and professional "
            "identity to create a comprehensive profile understanding"
        ),
        backstory=(
            "You are a talent acquisition expert specializing in technical profile "
            "assessment and developer brand analysis. You understand how to read "
            "between the lines of GitHub activity to identify true expertise areas, "
            "commitment patterns, and professional positioning. You've evaluated "
            "thousands of developer profiles and can quickly identify standout talent "
            "and unique value propositions."
        ),
        verbose=True,
        allow_delegation=False,
        tools=tools,
        llm=llm,
        max_iter=10,
        max_rpm=10
    )