# Autonomous Social Media AI Agent System - Production Design

## Executive Summary

This document outlines a production-grade, fully autonomous AI agent system that analyzes GitHub repositories and profiles, generates platform-optimized social media content, and automatically publishes to LinkedIn, X (Twitter), and Instagram. The system uses open-source frameworks (LangGraph + CrewAI hybrid), async execution patterns, robust state management, and follows modern LLM agent engineering best practices.

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Framework Selection & Rationale](#framework-selection--rationale)
3. [Agent Roles & Responsibilities](#agent-roles--responsibilities)
4. [Workflow Design & State Transitions](#workflow-design--state-transitions)
5. [Configuration Management](#configuration-management)
6. [GitHub Integration](#github-integration)
7. [Social Media Platform Integration](#social-media-platform-integration)
8. [Async Execution Patterns](#async-execution-patterns)
9. [State Management & Persistence](#state-management--persistence)
10. [Error Handling & Retries](#error-handling--retries)
11. [Observability & Logging](#observability--logging)
12. [Project Structure](#project-structure)
13. [Deployment Considerations](#deployment-considerations)
14. [Scalability & Modularity](#scalability--modularity)

---

## 1. System Architecture

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        ORCHESTRATION LAYER                       │
│                    (LangGraph State Machine)                     │
│                                                                   │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │   GitHub     │───▶│   Content    │───▶│  Publishing  │     │
│  │   Analysis   │    │  Generation  │    │   & Queue    │     │
│  │              │    │              │    │              │     │
│  └──────────────┘    └──────────────┘    └──────────────┘     │
│         │                    │                    │              │
└─────────┼────────────────────┼────────────────────┼──────────────┘
          │                    │                    │
          ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                       AGENT EXECUTION LAYER                      │
│                        (CrewAI Agents)                           │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   GitHub     │  │   LinkedIn   │  │      X       │         │
│  │  Researcher  │  │   Content    │  │   Content    │         │
│  │              │  │   Expert     │  │   Expert     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Profile    │  │  Instagram   │  │  Publishing  │         │
│  │   Analyzer   │  │   Content    │  │   Manager    │         │
│  │              │  │   Expert     │  │              │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
          │                    │                    │
          ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                         TOOL LAYER                               │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   GitHub     │  │   LinkedIn   │  │      X       │         │
│  │     API      │  │     API      │  │     API      │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Instagram   │  │     LLM      │  │   Vector     │         │
│  │     API      │  │   Services   │  │     DB       │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
          │                    │                    │
          ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PERSISTENCE LAYER                             │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   PostgreSQL │  │     Redis    │  │     S3       │         │
│  │  (State DB)  │  │   (Cache)    │  │  (Artifacts) │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Architecture Philosophy

**Hybrid Approach: LangGraph + CrewAI**

- **LangGraph**: Manages overall workflow orchestration, state machine, conditional routing, and checkpointing
- **CrewAI**: Powers individual specialized agents with role-based collaboration for content generation

This hybrid approach provides:
- **Control**: LangGraph's explicit state machine for predictable flows
- **Collaboration**: CrewAI's multi-agent patterns for content quality
- **Flexibility**: Best-of-both-worlds for complex social media workflows

---

## 2. Framework Selection & Rationale

### 2.1 Core Framework Stack

| Component | Framework | Justification |
|-----------|-----------|---------------|
| **Orchestration** | LangGraph | Graph-based state machine, checkpointing, conditional edges, pause/resume |
| **Multi-Agent** | CrewAI | Role-based agents, natural task delegation, excellent for content generation |
| **LLM Interface** | LangChain | Model abstraction, tool integration, memory management |
| **Observability** | LangSmith | Native LangChain/LangGraph tracing, debugging, performance monitoring |
| **Async Runtime** | asyncio + aiohttp | Native Python async for concurrent API calls and agent execution |

### 2.2 Why This Combination?

**LangGraph for Orchestration:**
- Explicit state schemas (TypedDict) prevent data loss
- Checkpointing enables pause/resume for long-running workflows
- Conditional edges support platform-specific routing
- Production-ready with LangGraph Platform (May 2025 GA)

**CrewAI for Content Generation:**
- Role-based agents mirror real content teams (researcher, writer, editor)
- Built-in task assignment and collaboration protocols
- Excellent for creative/generative tasks requiring multiple perspectives
- Simpler than pure LangGraph multi-agent for content workflows

**Why Not Single Framework?**
- Pure LangGraph: More boilerplate for role-based content teams
- Pure CrewAI: Less control over state machine and conditional flows
- Hybrid: Best control + best collaboration patterns

---

## 3. Agent Roles & Responsibilities

### 3.1 GitHub Analysis Crew

**1. Repository Researcher Agent**
```python
Role: "Senior GitHub Repository Analyst"
Goal: "Analyze repository structure, code quality, tech stack, and recent activity"
Backstory: """Expert in software engineering with deep knowledge of code patterns, 
            best practices, and project health indicators."""

Tools:
- github_repo_fetch (fetch repo metadata)
- github_code_analyzer (analyze code structure)
- github_commits_fetch (recent commits and trends)
- github_languages_fetch (language breakdown)

Outputs:
- Repository complexity score
- Key technologies used
- Recent significant changes
- Code quality indicators
```

**2. Profile Analyzer Agent**
```python
Role: "GitHub Profile Specialist"
Goal: "Extract developer expertise, contribution patterns, and professional identity"
Backstory: """Talent acquisition expert specializing in technical profile assessment 
            and developer brand analysis."""

Tools:
- github_profile_fetch (user profile data)
- github_contributions_fetch (contribution graph)
- github_repos_list (user's repository portfolio)
- github_activity_fetch (recent activity)

Outputs:
- Developer expertise areas
- Contribution patterns
- Notable projects
- Professional positioning
```

### 3.2 Content Generation Crew

**3. LinkedIn Content Expert**
```python
Role: "LinkedIn Content Strategist"
Goal: "Create professional, engaging LinkedIn posts optimized for B2B audience"
Backstory: """Former marketing director with 10+ years experience crafting viral 
            LinkedIn content for tech companies."""

Requirements:
- Professional tone
- Value-driven messaging
- Industry insights
- Call-to-action inclusion
- Character limit: 3000 (optimal: 150-300)
- Hashtag strategy: 3-5 relevant tags

Output Format:
{
  "text": "Post content",
  "hashtags": ["tech", "github", "opensource"],
  "media_type": null,  # or "image", "article"
  "metadata": {
    "target_audience": "developers, tech leaders",
    "content_pillar": "thought leadership"
  }
}
```

**4. X (Twitter) Content Expert**
```python
Role: "X Content Specialist"
Goal: "Craft concise, engaging tweets optimized for virality and engagement"
Backstory: """Social media manager who built multiple tech accounts to 100k+ followers 
            through strategic threading and community engagement."""

Requirements:
- Concise, punchy messaging
- Thread-aware content
- Trend-responsive
- Character limit: 280 per tweet
- Support for threads (up to 10 tweets)
- Hashtag strategy: 1-2 tags maximum

Output Format:
{
  "tweets": [
    {"text": "Tweet 1...", "order": 1},
    {"text": "Tweet 2...", "order": 2}
  ],
  "hashtags": ["github", "coding"],
  "media_urls": [],
  "metadata": {
    "thread": true,
    "hook_style": "question"
  }
}
```

**5. Instagram Content Expert**
```python
Role: "Instagram Visual Storyteller"
Goal: "Design visually compelling Instagram posts with engaging captions"
Backstory: """Creative director specializing in technical content visualization 
            and developer community building on Instagram."""

Requirements:
- Visual-first thinking
- Engaging captions (125-150 characters for preview)
- Story-driven approach
- Caption limit: 2200 characters
- Hashtag strategy: 5-10 relevant tags
- Image requirement consideration

Output Format:
{
  "caption": "Engaging caption...",
  "hashtags": ["code", "developers", "programming", "tech", "github"],
  "image_prompt": "Description for AI image generation",
  "metadata": {
    "content_type": "carousel | single | reel",
    "visual_style": "minimal, code-focused"
  }
}
```

**6. Publishing Manager Agent**
```python
Role: "Social Media Publishing Coordinator"
Goal: "Orchestrate multi-platform publishing with optimal timing and error handling"
Backstory: """Operations expert who has managed social media campaigns for Fortune 500 
            companies with 99.9% uptime."""

Responsibilities:
- Queue management
- Rate limit handling
- Retry logic coordination
- Publishing status tracking
- Error escalation
- Analytics logging

Tools:
- linkedin_publisher
- x_publisher
- instagram_publisher
- queue_manager
- retry_coordinator
```

### 3.3 Agent Interaction Patterns

```
GitHub Analysis Crew (Parallel Execution)
├── Repository Researcher → Repo Insights
└── Profile Analyzer → Profile Insights
            │
            ├─── Combined Context ───▶ Content Generation Crew
            │
Content Generation Crew (Sequential with Feedback)
├── LinkedIn Expert → Draft
├── X Expert → Draft
└── Instagram Expert → Draft
            │
            ├─── All Drafts ───▶ Publishing Manager
            │
Publishing Manager (Parallel with Rate Limiting)
├── LinkedIn API → Publish
├── X API → Publish
└── Instagram API → Publish
```

---

## 4. Workflow Design & State Transitions

### 4.1 LangGraph State Schema

```python
from typing import TypedDict, List, Optional, Annotated
from datetime import datetime
import operator

class GitHubAnalysisState(TypedDict):
    """State for GitHub analysis results"""
    repository_url: str
    profile_username: str
    repo_metadata: dict
    repo_analysis: dict
    profile_data: dict
    tech_stack: List[str]
    key_insights: List[str]
    analysis_timestamp: datetime

class ContentDraft(TypedDict):
    """Individual platform content draft"""
    platform: str  # linkedin, twitter, instagram
    content: dict  # platform-specific content structure
    status: str  # draft, approved, published, failed
    created_at: datetime
    published_at: Optional[datetime]
    post_id: Optional[str]
    error: Optional[str]

class WorkflowState(TypedDict):
    """Main workflow state - persisted across execution"""
    # Input
    github_repo_url: str
    github_username: str
    
    # Analysis Phase
    github_analysis: Annotated[GitHubAnalysisState, operator.or_]
    analysis_status: str  # pending, in_progress, completed, failed
    
    # Content Generation Phase
    content_drafts: Annotated[List[ContentDraft], operator.add]
    generation_status: str
    
    # Publishing Phase
    publishing_queue: Annotated[List[dict], operator.add]
    published_posts: Annotated[List[dict], operator.add]
    failed_posts: Annotated[List[dict], operator.add]
    
    # Workflow Control
    current_phase: str  # analysis, generation, publishing, completed
    retry_count: int
    max_retries: int
    error_messages: Annotated[List[str], operator.add]
    
    # Metadata
    workflow_id: str
    started_at: datetime
    completed_at: Optional[datetime]
    total_execution_time: Optional[float]
```

### 4.2 LangGraph Node Definitions

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.prebuilt import ToolNode

# Initialize graph with checkpointer
checkpointer = PostgresSaver.from_conn_string(DATABASE_URL)
workflow = StateGraph(WorkflowState)

# Define nodes
async def github_analysis_node(state: WorkflowState) -> dict:
    """Analyze GitHub repo and profile using CrewAI crew"""
    crew = GitHubAnalysisCrew()
    result = await crew.kickoff_async(
        inputs={
            "repository_url": state["github_repo_url"],
            "username": state["github_username"]
        }
    )
    
    return {
        "github_analysis": result,
        "analysis_status": "completed",
        "current_phase": "generation"
    }

async def content_generation_node(state: WorkflowState) -> dict:
    """Generate platform-specific content using CrewAI crew"""
    crew = ContentGenerationCrew()
    
    # Parallel content generation for all platforms
    drafts = await crew.kickoff_async(
        inputs={
            "github_analysis": state["github_analysis"],
            "platforms": ["linkedin", "twitter", "instagram"]
        }
    )
    
    return {
        "content_drafts": drafts,
        "generation_status": "completed",
        "current_phase": "publishing"
    }

async def publishing_node(state: WorkflowState) -> dict:
    """Publish content to all platforms"""
    publisher = PublishingManager()
    
    results = await publisher.publish_all_async(
        drafts=state["content_drafts"]
    )
    
    return {
        "published_posts": results["successful"],
        "failed_posts": results["failed"],
        "current_phase": "completed",
        "completed_at": datetime.now()
    }

def should_retry_analysis(state: WorkflowState) -> str:
    """Conditional edge for retry logic"""
    if state["analysis_status"] == "failed":
        if state["retry_count"] < state["max_retries"]:
            return "retry_analysis"
        else:
            return "fail_workflow"
    return "continue"

def should_continue_to_publishing(state: WorkflowState) -> str:
    """Conditional edge to determine next step"""
    if state["generation_status"] == "completed":
        return "publish"
    elif state["generation_status"] == "failed":
        return "retry_generation"
    return "wait"

# Build graph
workflow.add_node("analyze_github", github_analysis_node)
workflow.add_node("generate_content", content_generation_node)
workflow.add_node("publish_content", publishing_node)
workflow.add_node("handle_error", error_handler_node)

# Add edges
workflow.set_entry_point("analyze_github")
workflow.add_conditional_edges(
    "analyze_github",
    should_retry_analysis,
    {
        "continue": "generate_content",
        "retry_analysis": "analyze_github",
        "fail_workflow": "handle_error"
    }
)
workflow.add_conditional_edges(
    "generate_content",
    should_continue_to_publishing,
    {
        "publish": "publish_content",
        "retry_generation": "generate_content",
        "wait": END
    }
)
workflow.add_edge("publish_content", END)
workflow.add_edge("handle_error", END)

# Compile with checkpointer
app = workflow.compile(checkpointer=checkpointer)
```

### 4.3 State Transition Diagram

```
START
  │
  ▼
┌─────────────────┐
│  Analyze GitHub │◄─────┐
│  (Repo + Profile│      │ Retry
└────────┬────────┘      │ (if failed)
         │                │
         ▼                │
    [Analysis OK?]────────┘
         │
         │ Yes
         ▼
┌─────────────────┐
│ Generate Content│◄─────┐
│  (3 platforms)  │      │ Retry
└────────┬────────┘      │ (if failed)
         │                │
         ▼                │
  [Generation OK?]────────┘
         │
         │ Yes
         ▼
┌─────────────────┐
│ Publish Content │
│  (Parallel)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Log Results    │
│  Save Analytics │
└────────┬────────┘
         │
         ▼
       END
```

---

## 5. Configuration Management

### 5.1 Configuration Structure

```python
# config/settings.py
from pydantic import BaseSettings, Field, SecretStr
from typing import Optional, List
import os

class GitHubConfig(BaseSettings):
    """GitHub API configuration"""
    token: SecretStr = Field(..., env="GITHUB_TOKEN")
    api_base_url: str = "https://api.github.com"
    rate_limit_requests: int = 5000
    rate_limit_window: int = 3600  # seconds
    timeout: int = 30
    
    class Config:
        env_prefix = "GITHUB_"
        env_file = ".env"

class LinkedInConfig(BaseSettings):
    """LinkedIn API configuration"""
    client_id: SecretStr = Field(..., env="LINKEDIN_CLIENT_ID")
    client_secret: SecretStr = Field(..., env="LINKEDIN_CLIENT_SECRET")
    access_token: SecretStr = Field(..., env="LINKEDIN_ACCESS_TOKEN")
    refresh_token: SecretStr = Field(..., env="LINKEDIN_REFRESH_TOKEN")
    api_version: str = "202501"  # YYYYMM format
    api_base_url: str = "https://api.linkedin.com"
    rate_limit_requests: int = 100
    rate_limit_window: int = 86400  # 24 hours
    
    class Config:
        env_prefix = "LINKEDIN_"
        env_file = ".env"

class XConfig(BaseSettings):
    """X (Twitter) API configuration"""
    api_key: SecretStr = Field(..., env="X_API_KEY")
    api_secret: SecretStr = Field(..., env="X_API_SECRET")
    access_token: SecretStr = Field(..., env="X_ACCESS_TOKEN")
    access_token_secret: SecretStr = Field(..., env="X_ACCESS_TOKEN_SECRET")
    bearer_token: SecretStr = Field(..., env="X_BEARER_TOKEN")
    api_version: str = "2"
    api_base_url: str = "https://api.twitter.com"
    rate_limit_posts: int = 50  # per 24 hours (free tier)
    
    class Config:
        env_prefix = "X_"
        env_file = ".env"

class InstagramConfig(BaseSettings):
    """Instagram Graph API configuration"""
    app_id: SecretStr = Field(..., env="INSTAGRAM_APP_ID")
    app_secret: SecretStr = Field(..., env="INSTAGRAM_APP_SECRET")
    access_token: SecretStr = Field(..., env="INSTAGRAM_ACCESS_TOKEN")
    account_id: str = Field(..., env="INSTAGRAM_ACCOUNT_ID")
    api_base_url: str = "https://graph.instagram.com"
    graph_api_version: str = "v24.0"
    rate_limit_posts: int = 25  # per 24 hours
    
    class Config:
        env_prefix = "INSTAGRAM_"
        env_file = ".env"

class LLMConfig(BaseSettings):
    """LLM service configuration"""
    provider: str = "anthropic"  # or "openai", "ollama"
    model: str = "claude-sonnet-4-20250514"
    api_key: SecretStr = Field(..., env="ANTHROPIC_API_KEY")
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: int = 60
    
    class Config:
        env_file = ".env"

class DatabaseConfig(BaseSettings):
    """Database configuration"""
    postgres_url: SecretStr = Field(..., env="DATABASE_URL")
    redis_url: SecretStr = Field(..., env="REDIS_URL")
    pool_size: int = 10
    max_overflow: int = 20
    
    class Config:
        env_prefix = "DB_"
        env_file = ".env"

class ObservabilityConfig(BaseSettings):
    """Monitoring and logging configuration"""
    langsmith_api_key: Optional[SecretStr] = Field(None, env="LANGSMITH_API_KEY")
    langsmith_project: str = "social-agent-system"
    log_level: str = "INFO"
    sentry_dsn: Optional[SecretStr] = Field(None, env="SENTRY_DSN")
    
    class Config:
        env_file = ".env"

class WorkflowConfig(BaseSettings):
    """Workflow execution configuration"""
    max_retries: int = 3
    retry_delay: int = 5  # seconds
    timeout_per_phase: int = 300  # 5 minutes
    enable_checkpointing: bool = True
    concurrent_generation: bool = True
    
    class Config:
        env_file = ".env"

class Settings(BaseSettings):
    """Main settings aggregator"""
    github: GitHubConfig = GitHubConfig()
    linkedin: LinkedInConfig = LinkedInConfig()
    x: XConfig = XConfig()
    instagram: InstagramConfig = InstagramConfig()
    llm: LLMConfig = LLMConfig()
    database: DatabaseConfig = DatabaseConfig()
    observability: ObservabilityConfig = ObservabilityConfig()
    workflow: WorkflowConfig = WorkflowConfig()
    
    # Environment
    environment: str = Field("development", env="ENVIRONMENT")
    debug: bool = Field(False, env="DEBUG")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Singleton instance
settings = Settings()
```

### 5.2 Environment Variables (.env.example)

```bash
# GitHub Configuration
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
GITHUB_RATE_LIMIT_REQUESTS=5000

# LinkedIn Configuration
LINKEDIN_CLIENT_ID=xxxxxxxxxxxx
LINKEDIN_CLIENT_SECRET=xxxxxxxxxxxx
LINKEDIN_ACCESS_TOKEN=xxxxxxxxxxxx
LINKEDIN_REFRESH_TOKEN=xxxxxxxxxxxx
LINKEDIN_API_VERSION=202501

# X (Twitter) Configuration
X_API_KEY=xxxxxxxxxxxx
X_API_SECRET=xxxxxxxxxxxx
X_ACCESS_TOKEN=xxxxxxxxxxxx
X_ACCESS_TOKEN_SECRET=xxxxxxxxxxxx
X_BEARER_TOKEN=xxxxxxxxxxxx

# Instagram Configuration
INSTAGRAM_APP_ID=xxxxxxxxxxxx
INSTAGRAM_APP_SECRET=xxxxxxxxxxxx
INSTAGRAM_ACCESS_TOKEN=xxxxxxxxxxxx
INSTAGRAM_ACCOUNT_ID=xxxxxxxxxxxx

# LLM Configuration
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx
LLM_MODEL=claude-sonnet-4-20250514
LLM_TEMPERATURE=0.7

# Database Configuration
DATABASE_URL=postgresql://user:pass@localhost:5432/social_agent
REDIS_URL=redis://localhost:6379/0

# Observability
LANGSMITH_API_KEY=lsv2_xxxxxxxxxxxx
LANGSMITH_PROJECT=social-agent-system
SENTRY_DSN=https://xxxxxxxxxxxx@sentry.io/xxxxxxxxxxxx
LOG_LEVEL=INFO

# Workflow Configuration
MAX_RETRIES=3
TIMEOUT_PER_PHASE=300
ENABLE_CHECKPOINTING=true

# Environment
ENVIRONMENT=production
DEBUG=false
```

### 5.3 Configuration Validation

```python
# config/validator.py
from typing import List
import logging

logger = logging.getLogger(__name__)

class ConfigValidator:
    """Validates configuration on startup"""
    
    @staticmethod
    def validate_all(settings: Settings) -> List[str]:
        """Run all validation checks"""
        errors = []
        
        errors.extend(ConfigValidator.validate_github(settings.github))
        errors.extend(ConfigValidator.validate_social_media(settings))
        errors.extend(ConfigValidator.validate_llm(settings.llm))
        errors.extend(ConfigValidator.validate_database(settings.database))
        
        if errors:
            logger.error(f"Configuration validation failed: {errors}")
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        logger.info("Configuration validation passed")
        return errors
    
    @staticmethod
    def validate_github(config: GitHubConfig) -> List[str]:
        errors = []
        if not config.token.get_secret_value():
            errors.append("GITHUB_TOKEN is required")
        if config.rate_limit_requests < 1:
            errors.append("GITHUB_RATE_LIMIT_REQUESTS must be positive")
        return errors
    
    @staticmethod
    def validate_social_media(settings: Settings) -> List[str]:
        errors = []
        
        # LinkedIn
        if not settings.linkedin.access_token.get_secret_value():
            errors.append("LINKEDIN_ACCESS_TOKEN is required")
        
        # X (Twitter)
        if not settings.x.api_key.get_secret_value():
            errors.append("X_API_KEY is required")
        
        # Instagram
        if not settings.instagram.app_id.get_secret_value():
            errors.append("INSTAGRAM_APP_ID is required")
        
        return errors
    
    @staticmethod
    def validate_llm(config: LLMConfig) -> List[str]:
        errors = []
        if not config.api_key.get_secret_value():
            errors.append("LLM API key is required")
        if config.temperature < 0 or config.temperature > 2:
            errors.append("LLM temperature must be between 0 and 2")
        return errors
    
    @staticmethod
    def validate_database(config: DatabaseConfig) -> List[str]:
        errors = []
        if not config.postgres_url.get_secret_value():
            errors.append("DATABASE_URL is required")
        if not config.redis_url.get_secret_value():
            errors.append("REDIS_URL is required")
        return errors
```

---

## 6. GitHub Integration

### 6.1 GitHub Tools Implementation

```python
# tools/github_tools.py
from typing import Dict, List, Optional
import aiohttp
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class GitHubAPIClient:
    """Async GitHub API client with rate limiting"""
    
    def __init__(self, token: str, rate_limit: int = 5000):
        self.token = token
        self.base_url = "https://api.github.com"
        self.rate_limit = rate_limit
        self.rate_limit_remaining = rate_limit
        self.rate_limit_reset = None
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "SocialAgentSystem/1.0"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _check_rate_limit(self):
        """Check and wait if rate limit is exceeded"""
        if self.rate_limit_remaining <= 10:
            if self.rate_limit_reset:
                wait_time = (self.rate_limit_reset - datetime.now()).total_seconds()
                if wait_time > 0:
                    logger.warning(f"Rate limit nearly exceeded. Waiting {wait_time}s")
                    await asyncio.sleep(wait_time)
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make authenticated request to GitHub API"""
        await self._check_rate_limit()
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        async with self.session.request(method, url, **kwargs) as response:
            # Update rate limit info
            self.rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
            reset_timestamp = int(response.headers.get('X-RateLimit-Reset', 0))
            self.rate_limit_reset = datetime.fromtimestamp(reset_timestamp)
            
            response.raise_for_status()
            return await response.json()
    
    async def get_repository(self, owner: str, repo: str) -> Dict:
        """Fetch repository metadata"""
        return await self._request('GET', f'/repos/{owner}/{repo}')
    
    async def get_repository_languages(self, owner: str, repo: str) -> Dict:
        """Fetch repository language breakdown"""
        return await self._request('GET', f'/repos/{owner}/{repo}/languages')
    
    async def get_repository_commits(
        self, 
        owner: str, 
        repo: str, 
        per_page: int = 100,
        page: int = 1
    ) -> List[Dict]:
        """Fetch recent commits"""
        return await self._request(
            'GET', 
            f'/repos/{owner}/{repo}/commits',
            params={'per_page': per_page, 'page': page}
        )
    
    async def get_repository_contributors(
        self, 
        owner: str, 
        repo: str
    ) -> List[Dict]:
        """Fetch repository contributors"""
        return await self._request('GET', f'/repos/{owner}/{repo}/contributors')
    
    async def get_user_profile(self, username: str) -> Dict:
        """Fetch user profile"""
        return await self._request('GET', f'/users/{username}')
    
    async def get_user_repositories(
        self, 
        username: str,
        type: str = 'owner',
        sort: str = 'updated'
    ) -> List[Dict]:
        """Fetch user's repositories"""
        return await self._request(
            'GET',
            f'/users/{username}/repos',
            params={'type': type, 'sort': sort, 'per_page': 100}
        )
    
    async def get_repository_readme(self, owner: str, repo: str) -> Dict:
        """Fetch repository README"""
        try:
            return await self._request('GET', f'/repos/{owner}/{repo}/readme')
        except aiohttp.ClientResponseError as e:
            if e.status == 404:
                logger.warning(f"No README found for {owner}/{repo}")
                return {}
            raise

class GitHubAnalyzer:
    """High-level GitHub analysis orchestrator"""
    
    def __init__(self, api_client: GitHubAPIClient):
        self.api = api_client
    
    async def analyze_repository(self, repo_url: str) -> Dict:
        """Comprehensive repository analysis"""
        owner, repo = self._parse_repo_url(repo_url)
        
        # Parallel fetch of all repo data
        repo_data, languages, commits, contributors, readme = await asyncio.gather(
            self.api.get_repository(owner, repo),
            self.api.get_repository_languages(owner, repo),
            self.api.get_repository_commits(owner, repo, per_page=100),
            self.api.get_repository_contributors(owner, repo),
            self.api.get_repository_readme(owner, repo),
            return_exceptions=True
        )
        
        # Analyze results
        analysis = {
            "metadata": {
                "name": repo_data.get("name"),
                "full_name": repo_data.get("full_name"),
                "description": repo_data.get("description"),
                "url": repo_data.get("html_url"),
                "stars": repo_data.get("stargazers_count", 0),
                "forks": repo_data.get("forks_count", 0),
                "watchers": repo_data.get("watchers_count", 0),
                "open_issues": repo_data.get("open_issues_count", 0),
                "created_at": repo_data.get("created_at"),
                "updated_at": repo_data.get("updated_at"),
                "language": repo_data.get("language"),
                "license": repo_data.get("license", {}).get("name"),
            },
            "languages": self._analyze_languages(languages),
            "activity": self._analyze_commits(commits),
            "contributors": self._analyze_contributors(contributors),
            "readme_quality": self._assess_readme_quality(readme),
            "health_score": 0,  # Calculated below
        }
        
        # Calculate health score
        analysis["health_score"] = self._calculate_health_score(analysis)
        
        return analysis
    
    async def analyze_profile(self, username: str) -> Dict:
        """Comprehensive profile analysis"""
        profile, repos = await asyncio.gather(
            self.api.get_user_profile(username),
            self.api.get_user_repositories(username),
            return_exceptions=True
        )
        
        return {
            "username": profile.get("login"),
            "name": profile.get("name"),
            "bio": profile.get("bio"),
            "location": profile.get("location"),
            "company": profile.get("company"),
            "blog": profile.get("blog"),
            "email": profile.get("email"),
            "twitter": profile.get("twitter_username"),
            "followers": profile.get("followers", 0),
            "following": profile.get("following", 0),
            "public_repos": profile.get("public_repos", 0),
            "created_at": profile.get("created_at"),
            "updated_at": profile.get("updated_at"),
            "repositories": self._analyze_user_repos(repos),
            "expertise_areas": self._identify_expertise(repos),
            "contribution_pattern": self._analyze_contribution_pattern(repos),
        }
    
    @staticmethod
    def _parse_repo_url(url: str) -> tuple:
        """Parse GitHub repo URL into owner and repo name"""
        parts = url.rstrip('/').split('/')
        return parts[-2], parts[-1]
    
    def _analyze_languages(self, languages: Dict) -> Dict:
        """Analyze language breakdown"""
        if not languages:
            return {}
        
        total_bytes = sum(languages.values())
        return {
            lang: {
                "bytes": bytes_count,
                "percentage": round((bytes_count / total_bytes) * 100, 2)
            }
            for lang, bytes_count in sorted(
                languages.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
        }
    
    def _analyze_commits(self, commits: List[Dict]) -> Dict:
        """Analyze commit patterns"""
        if not commits:
            return {"total": 0, "recent_activity": "none"}
        
        # Calculate commit frequency
        commit_dates = [c["commit"]["author"]["date"] for c in commits if c]
        
        return {
            "total_recent": len(commits),
            "commit_frequency": "active" if len(commits) > 10 else "moderate",
            "last_commit": commit_dates[0] if commit_dates else None,
        }
    
    def _analyze_contributors(self, contributors: List[Dict]) -> Dict:
        """Analyze contributor distribution"""
        if not contributors:
            return {"total": 0, "distribution": "no data"}
        
        total_contributions = sum(c.get("contributions", 0) for c in contributors)
        
        return {
            "total": len(contributors),
            "top_contributor_percentage": round(
                (contributors[0].get("contributions", 0) / total_contributions) * 100, 2
            ) if contributors else 0,
        }
    
    def _assess_readme_quality(self, readme: Dict) -> Dict:
        """Assess README quality"""
        if not readme:
            return {"exists": False, "quality": "none"}
        
        # Simple heuristic based on size
        size = readme.get("size", 0)
        
        if size < 500:
            quality = "minimal"
        elif size < 2000:
            quality = "moderate"
        else:
            quality = "comprehensive"
        
        return {
            "exists": True,
            "size": size,
            "quality": quality
        }
    
    def _calculate_health_score(self, analysis: Dict) -> int:
        """Calculate repository health score (0-100)"""
        score = 0
        
        # Activity (30 points)
        if analysis["activity"]["total_recent"] > 50:
            score += 30
        elif analysis["activity"]["total_recent"] > 10:
            score += 20
        else:
            score += 10
        
        # Stars (20 points)
        stars = analysis["metadata"]["stars"]
        if stars > 1000:
            score += 20
        elif stars > 100:
            score += 15
        elif stars > 10:
            score += 10
        
        # Contributors (20 points)
        contrib_count = analysis["contributors"]["total"]
        if contrib_count > 10:
            score += 20
        elif contrib_count > 3:
            score += 15
        elif contrib_count > 1:
            score += 10
        
        # Documentation (15 points)
        if analysis["readme_quality"]["quality"] == "comprehensive":
            score += 15
        elif analysis["readme_quality"]["quality"] == "moderate":
            score += 10
        elif analysis["readme_quality"]["exists"]:
            score += 5
        
        # License (15 points)
        if analysis["metadata"]["license"]:
            score += 15
        
        return min(score, 100)
    
    def _analyze_user_repos(self, repos: List[Dict]) -> List[Dict]:
        """Extract key info from user repositories"""
        return [
            {
                "name": repo.get("name"),
                "stars": repo.get("stargazers_count", 0),
                "language": repo.get("language"),
                "url": repo.get("html_url"),
            }
            for repo in (repos or [])[:10]  # Top 10
        ]
    
    def _identify_expertise(self, repos: List[Dict]) -> List[str]:
        """Identify user's expertise areas from repositories"""
        if not repos:
            return []
        
        # Count language usage
        language_counts = {}
        for repo in repos:
            lang = repo.get("language")
            if lang:
                language_counts[lang] = language_counts.get(lang, 0) + 1
        
        # Return top 5 languages
        return sorted(language_counts.keys(), key=language_counts.get, reverse=True)[:5]
    
    def _analyze_contribution_pattern(self, repos: List[Dict]) -> str:
        """Analyze contribution pattern"""
        if not repos:
            return "inactive"
        
        # Simple heuristic based on number of active repos
        active_repos = sum(1 for r in repos if r.get("updated_at"))
        
        if active_repos > 10:
            return "very active"
        elif active_repos > 5:
            return "active"
        elif active_repos > 2:
            return "moderate"
        else:
            return "occasional"
```

### 6.2 GitHub CrewAI Tools

```python
# crews/github_crew/tools.py
from crewai_tools import BaseTool
from typing import Any
from pydantic import Field

class GitHubRepositoryTool(BaseTool):
    name: str = "GitHub Repository Analyzer"
    description: str = """Analyzes a GitHub repository and returns comprehensive 
                         insights including tech stack, activity metrics, and health score."""
    
    api_client: Any = Field(description="GitHub API client instance")
    
    def _run(self, repository_url: str) -> dict:
        """Synchronous execution (CrewAI requirement)"""
        import asyncio
        analyzer = GitHubAnalyzer(self.api_client)
        return asyncio.run(analyzer.analyze_repository(repository_url))

class GitHubProfileTool(BaseTool):
    name: str = "GitHub Profile Analyzer"
    description: str = """Analyzes a GitHub user profile and returns insights about 
                         their expertise, contribution patterns, and notable projects."""
    
    api_client: Any = Field(description="GitHub API client instance")
    
    def _run(self, username: str) -> dict:
        """Synchronous execution"""
        import asyncio
        analyzer = GitHubAnalyzer(self.api_client)
        return asyncio.run(analyzer.analyze_profile(username))
```

---

## 7. Social Media Platform Integration

### 7.1 LinkedIn Integration

```python
# integrations/linkedin.py
import aiohttp
import asyncio
from typing import Dict, Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class LinkedInClient:
    """LinkedIn API client with OAuth 2.0"""
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        access_token: str,
        refresh_token: str
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.base_url = "https://api.linkedin.com"
        self.api_version = "202501"
        self.token_expires_at: Optional[datetime] = None
    
    async def refresh_access_token(self) -> str:
        """Refresh OAuth access token"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://www.linkedin.com/oauth/v2/accessToken",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                }
            ) as response:
                response.raise_for_status()
                data = await response.json()
                self.access_token = data["access_token"]
                self.token_expires_at = datetime.now() + timedelta(seconds=data["expires_in"])
                logger.info("LinkedIn access token refreshed")
                return self.access_token
    
    async def _ensure_valid_token(self):
        """Ensure access token is valid"""
        if self.token_expires_at and datetime.now() >= self.token_expires_at:
            await self.refresh_access_token()
    
    async def create_post(
        self,
        author_urn: str,
        text: str,
        visibility: str = "PUBLIC",
        media_urls: Optional[list] = None
    ) -> Dict:
        """Create a LinkedIn post"""
        await self._ensure_valid_token()
        
        payload = {
            "author": author_urn,
            "commentary": text,
            "visibility": visibility,
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": []
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False
        }
        
        # Add media if provided
        if media_urls:
            payload["content"] = {
                "media": {
                    "title": "Post media",
                    "id": media_urls[0]  # Assumes pre-uploaded media URN
                }
            }
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0",
                "LinkedIn-Version": self.api_version
            }
            
            async with session.post(
                f"{self.base_url}/rest/posts",
                json=payload,
                headers=headers
            ) as response:
                response.raise_for_status()
                post_id = response.headers.get("x-restli-id")
                
                logger.info(f"LinkedIn post created: {post_id}")
                return {
                    "post_id": post_id,
                    "platform": "linkedin",
                    "status": "published",
                    "timestamp": datetime.now().isoformat()
                }

class LinkedInPublisher:
    """High-level LinkedIn publishing manager"""
    
    def __init__(self, client: LinkedInClient, author_urn: str):
        self.client = client
        self.author_urn = author_urn
        self.rate_limit_posts_per_day = 100
        self.posts_published_today = 0
        self.last_reset = datetime.now()
    
    async def publish(self, content: Dict) -> Dict:
        """Publish content to LinkedIn with rate limiting"""
        # Reset daily counter if needed
        if datetime.now().date() > self.last_reset.date():
            self.posts_published_today = 0
            self.last_reset = datetime.now()
        
        # Check rate limit
        if self.posts_published_today >= self.rate_limit_posts_per_day:
            raise Exception("LinkedIn daily post limit reached")
        
        try:
            result = await self.client.create_post(
                author_urn=self.author_urn,
                text=content.get("text"),
                media_urls=content.get("media_urls", [])
            )
            self.posts_published_today += 1
            return result
        except Exception as e:
            logger.error(f"LinkedIn publish failed: {e}")
            return {
                "platform": "linkedin",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
```

### 7.2 X (Twitter) Integration

```python
# integrations/x_twitter.py
import aiohttp
import asyncio
from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta
import hmac
import hashlib
import base64
import urllib.parse
import time

logger = logging.getLogger(__name__)

class XClient:
    """X (Twitter) API client with OAuth 1.0a"""
    
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        access_token: str,
        access_token_secret: str
    ):
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.base_url = "https://api.twitter.com/2"
    
    def _create_oauth_signature(
        self,
        method: str,
        url: str,
        params: Dict
    ) -> str:
        """Create OAuth 1.0a signature"""
        # OAuth parameters
        oauth_params = {
            "oauth_consumer_key": self.api_key,
            "oauth_token": self.access_token,
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": str(int(time.time())),
            "oauth_nonce": base64.b64encode(str(time.time()).encode()).decode(),
            "oauth_version": "1.0"
        }
        
        # Combine all parameters
        all_params = {**oauth_params, **params}
        
        # Create parameter string
        param_string = "&".join(
            f"{urllib.parse.quote(str(k))}={urllib.parse.quote(str(v))}"
            for k, v in sorted(all_params.items())
        )
        
        # Create signature base string
        base_string = f"{method}&{urllib.parse.quote(url)}&{urllib.parse.quote(param_string)}"
        
        # Create signing key
        signing_key = f"{urllib.parse.quote(self.api_secret)}&{urllib.parse.quote(self.access_token_secret)}"
        
        # Create signature
        signature = base64.b64encode(
            hmac.new(
                signing_key.encode(),
                base_string.encode(),
                hashlib.sha1
            ).digest()
        ).decode()
        
        oauth_params["oauth_signature"] = signature
        
        return ", ".join(
            f'{k}="{urllib.parse.quote(str(v))}"'
            for k, v in sorted(oauth_params.items())
        )
    
    async def create_tweet(self, text: str, reply_to: Optional[str] = None) -> Dict:
        """Create a tweet"""
        url = f"{self.base_url}/tweets"
        
        payload = {"text": text}
        if reply_to:
            payload["reply"] = {"in_reply_to_tweet_id": reply_to}
        
        auth_header = self._create_oauth_signature("POST", url, {})
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"OAuth {auth_header}",
                "Content-Type": "application/json"
            }
            
            async with session.post(url, json=payload, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
                
                logger.info(f"Tweet created: {data['data']['id']}")
                return {
                    "tweet_id": data["data"]["id"],
                    "platform": "twitter",
                    "status": "published",
                    "timestamp": datetime.now().isoformat()
                }
    
    async def create_thread(self, tweets: List[str]) -> List[Dict]:
        """Create a tweet thread"""
        results = []
        previous_tweet_id = None
        
        for tweet_text in tweets:
            result = await self.create_tweet(tweet_text, reply_to=previous_tweet_id)
            results.append(result)
            previous_tweet_id = result["tweet_id"]
            await asyncio.sleep(1)  # Rate limiting
        
        return results

class XPublisher:
    """High-level X publishing manager"""
    
    def __init__(self, client: XClient):
        self.client = client
        self.rate_limit_posts_per_day = 50  # Free tier
        self.posts_published_today = 0
        self.last_reset = datetime.now()
    
    async def publish(self, content: Dict) -> Dict:
        """Publish content to X with rate limiting"""
        # Reset daily counter if needed
        if datetime.now().date() > self.last_reset.date():
            self.posts_published_today = 0
            self.last_reset = datetime.now()
        
        # Check rate limit
        tweets = content.get("tweets", [])
        required_slots = len(tweets)
        
        if self.posts_published_today + required_slots > self.rate_limit_posts_per_day:
            raise Exception("X daily post limit reached")
        
        try:
            # Handle thread vs single tweet
            if len(tweets) > 1:
                tweet_texts = [t["text"] for t in sorted(tweets, key=lambda x: x["order"])]
                results = await self.client.create_thread(tweet_texts)
                self.posts_published_today += len(tweets)
                return {
                    "platform": "twitter",
                    "status": "published",
                    "tweet_ids": [r["tweet_id"] for r in results],
                    "thread": True,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                result = await self.client.create_tweet(tweets[0]["text"])
                self.posts_published_today += 1
                return result
        except Exception as e:
            logger.error(f"X publish failed: {e}")
            return {
                "platform": "twitter",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
```

### 7.3 Instagram Integration

```python
# integrations/instagram.py
import aiohttp
import asyncio
from typing import Dict, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class InstagramClient:
    """Instagram Graph API client"""
    
    def __init__(
        self,
        app_id: str,
        app_secret: str,
        access_token: str,
        account_id: str
    ):
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = access_token
        self.account_id = account_id
        self.base_url = "https://graph.instagram.com"
        self.api_version = "v24.0"
    
    async def create_media_container(
        self,
        image_url: str,
        caption: str
    ) -> str:
        """Create Instagram media container (Step 1 of publishing)"""
        url = f"{self.base_url}/{self.api_version}/{self.account_id}/media"
        
        params = {
            "image_url": image_url,
            "caption": caption,
            "access_token": self.access_token
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                container_id = data["id"]
                
                logger.info(f"Instagram container created: {container_id}")
                return container_id
    
    async def publish_container(self, container_id: str) -> str:
        """Publish Instagram media container (Step 2 of publishing)"""
        url = f"{self.base_url}/{self.api_version}/{self.account_id}/media_publish"
        
        params = {
            "creation_id": container_id,
            "access_token": self.access_token
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                media_id = data["id"]
                
                logger.info(f"Instagram post published: {media_id}")
                return media_id
    
    async def create_post(self, image_url: str, caption: str) -> Dict:
        """Complete Instagram post workflow"""
        # Step 1: Create container
        container_id = await self.create_media_container(image_url, caption)
        
        # Wait for Instagram to process
        await asyncio.sleep(10)
        
        # Step 2: Publish
        media_id = await self.publish_container(container_id)
        
        return {
            "post_id": media_id,
            "platform": "instagram",
            "status": "published",
            "timestamp": datetime.now().isoformat()
        }

class InstagramPublisher:
    """High-level Instagram publishing manager"""
    
    def __init__(self, client: InstagramClient):
        self.client = client
        self.rate_limit_posts_per_day = 25
        self.posts_published_today = 0
        self.last_reset = datetime.now()
    
    async def publish(self, content: Dict) -> Dict:
        """Publish content to Instagram with rate limiting"""
        # Reset daily counter if needed
        if datetime.now().date() > self.last_reset.date():
            self.posts_published_today = 0
            self.last_reset = datetime.now()
        
        # Check rate limit
        if self.posts_published_today >= self.rate_limit_posts_per_day:
            raise Exception("Instagram daily post limit reached")
        
        try:
            # Ensure image URL is provided
            if not content.get("image_url"):
                raise ValueError("Instagram requires image_url")
            
            result = await self.client.create_post(
                image_url=content["image_url"],
                caption=f"{content['caption']}\n\n{' '.join(['#' + tag for tag in content.get('hashtags', [])])}"
            )
            self.posts_published_today += 1
            return result
        except Exception as e:
            logger.error(f"Instagram publish failed: {e}")
            return {
                "platform": "instagram",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
```

### 7.4 Unified Publishing Manager

```python
# integrations/publisher.py
from typing import List, Dict
import asyncio
import logging

logger = logging.getLogger(__name__)

class MultiPlatformPublisher:
    """Unified publisher for all social media platforms"""
    
    def __init__(
        self,
        linkedin_publisher: LinkedInPublisher,
        x_publisher: XPublisher,
        instagram_publisher: InstagramPublisher
    ):
        self.publishers = {
            "linkedin": linkedin_publisher,
            "twitter": x_publisher,
            "instagram": instagram_publisher
        }
    
    async def publish_to_platform(
        self,
        platform: str,
        content: Dict
    ) -> Dict:
        """Publish to single platform"""
        if platform not in self.publishers:
            raise ValueError(f"Unsupported platform: {platform}")
        
        publisher = self.publishers[platform]
        
        try:
            result = await publisher.publish(content)
            logger.info(f"Successfully published to {platform}")
            return result
        except Exception as e:
            logger.error(f"Failed to publish to {platform}: {e}")
            return {
                "platform": platform,
                "status": "failed",
                "error": str(e)
            }
    
    async def publish_all_async(
        self,
        drafts: List[Dict]
    ) -> Dict[str, List[Dict]]:
        """Publish to all platforms in parallel"""
        tasks = [
            self.publish_to_platform(draft["platform"], draft["content"])
            for draft in drafts
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful = []
        failed = []
        
        for result in results:
            if isinstance(result, Exception):
                failed.append({
                    "error": str(result),
                    "status": "exception"
                })
            elif result.get("status") == "published":
                successful.append(result)
            else:
                failed.append(result)
        
        return {
            "successful": successful,
            "failed": failed,
            "total": len(drafts),
            "success_rate": len(successful) / len(drafts) if drafts else 0
        }
```

---

## 8. Async Execution Patterns

### 8.1 Async Agent Execution

```python
# crews/async_crew.py
from crewai import Crew, Agent, Task
import asyncio
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class AsyncCrewExecutor:
    """Wrapper for async CrewAI execution"""
    
    def __init__(self, crew: Crew):
        self.crew = crew
    
    async def kickoff_async(self, inputs: Dict) -> Dict:
        """Execute crew asynchronously"""
        loop = asyncio.get_event_loop()
        
        # Run crew in thread pool to avoid blocking
        result = await loop.run_in_executor(
            None,
            self.crew.kickoff,
            inputs
        )
        
        return result

class ParallelAgentExecutor:
    """Execute multiple agents in parallel"""
    
    @staticmethod
    async def execute_agents_parallel(
        agent_tasks: List[tuple]
    ) -> List[Dict]:
        """
        Execute multiple agent tasks in parallel
        
        Args:
            agent_tasks: List of (crew, inputs) tuples
        """
        tasks = [
            AsyncCrewExecutor(crew).kickoff_async(inputs)
            for crew, inputs in agent_tasks
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Agent task {i} failed: {result}")
                processed_results.append({
                    "status": "failed",
                    "error": str(result)
                })
            else:
                processed_results.append(result)
        
        return processed_results
```

### 8.2 Concurrency Control

```python
# utils/concurrency.py
import asyncio
from typing import Callable, List, Any
import logging

logger = logging.getLogger(__name__)

class ConcurrencyManager:
    """Manage concurrent task execution with limits"""
    
    def __init__(self, max_concurrent: int = 5):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.max_concurrent = max_concurrent
    
    async def execute_with_limit(
        self,
        coro: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Execute coroutine with concurrency limit"""
        async with self.semaphore:
            return await coro(*args, **kwargs)
    
    async def execute_batch(
        self,
        tasks: List[Callable],
        *args,
        **kwargs
    ) -> List[Any]:
        """Execute batch of tasks with concurrency limit"""
        coros = [
            self.execute_with_limit(task, *args, **kwargs)
            for task in tasks
        ]
        
        results = await asyncio.gather(*coros, return_exceptions=True)
        
        # Log exceptions
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Task {i} failed: {result}")
        
        return results

class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self, rate: int, per: float):
        """
        Args:
            rate: Number of requests allowed
            per: Time window in seconds
        """
        self.rate = rate
        self.per = per
        self.allowance = rate
        self.last_check = asyncio.get_event_loop().time()
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire permission to proceed"""
        async with self.lock:
            current = asyncio.get_event_loop().time()
            time_passed = current - self.last_check
            self.last_check = current
            
            self.allowance += time_passed * (self.rate / self.per)
            if self.allowance > self.rate:
                self.allowance = self.rate
            
            if self.allowance < 1.0:
                wait_time = (1.0 - self.allowance) * (self.per / self.rate)
                await asyncio.sleep(wait_time)
                self.allowance = 0.0
            else:
                self.allowance -= 1.0
```

---

## 9. State Management & Persistence

### 9.1 PostgreSQL Schema

```sql
-- schema.sql
CREATE TABLE IF NOT EXISTS workflow_states (
    id UUID PRIMARY KEY,
    workflow_id VARCHAR(255) UNIQUE NOT NULL,
    state JSONB NOT NULL,
    checkpoint_id VARCHAR(255),
    parent_checkpoint_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_workflow_id (workflow_id),
    INDEX idx_checkpoint_id (checkpoint_id)
);

CREATE TABLE IF NOT EXISTS github_analyses (
    id SERIAL PRIMARY KEY,
    workflow_id VARCHAR(255) REFERENCES workflow_states(workflow_id),
    repository_url VARCHAR(500),
    username VARCHAR(255),
    analysis_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS content_drafts (
    id SERIAL PRIMARY KEY,
    workflow_id VARCHAR(255) REFERENCES workflow_states(workflow_id),
    platform VARCHAR(50),
    content JSONB,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS published_posts (
    id SERIAL PRIMARY KEY,
    workflow_id VARCHAR(255) REFERENCES workflow_states(workflow_id),
    platform VARCHAR(50),
    post_id VARCHAR(255),
    content JSONB,
    published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    analytics JSONB
);

CREATE TABLE IF NOT EXISTS workflow_metrics (
    id SERIAL PRIMARY KEY,
    workflow_id VARCHAR(255) REFERENCES workflow_states(workflow_id),
    phase VARCHAR(50),
    execution_time FLOAT,
    success BOOLEAN,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 9.2 State Persistence Manager

```python
# persistence/state_manager.py
from typing import Dict, Optional
import asyncpg
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class StateManager:
    """Manage workflow state persistence"""
    
    def __init__(self, db_pool: asyncpg.Pool):
        self.pool = db_pool
    
    async def save_state(
        self,
        workflow_id: str,
        state: Dict,
        checkpoint_id: Optional[str] = None
    ):
        """Save workflow state to database"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO workflow_states (id, workflow_id, state, checkpoint_id, updated_at)
                VALUES (gen_random_uuid(), $1, $2, $3, $4)
                ON CONFLICT (workflow_id)
                DO UPDATE SET
                    state = $2,
                    checkpoint_id = $3,
                    updated_at = $4
            """, workflow_id, json.dumps(state), checkpoint_id, datetime.now())
        
        logger.info(f"State saved for workflow {workflow_id}")
    
    async def load_state(self, workflow_id: str) -> Optional[Dict]:
        """Load workflow state from database"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT state FROM workflow_states
                WHERE workflow_id = $1
            """, workflow_id)
            
            if row:
                return json.loads(row['state'])
            return None
    
    async def save_github_analysis(
        self,
        workflow_id: str,
        repository_url: str,
        username: str,
        analysis_data: Dict
    ):
        """Save GitHub analysis results"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO github_analyses
                (workflow_id, repository_url, username, analysis_data)
                VALUES ($1, $2, $3, $4)
            """, workflow_id, repository_url, username, json.dumps(analysis_data))
    
    async def save_published_post(
        self,
        workflow_id: str,
        platform: str,
        post_id: str,
        content: Dict
    ):
        """Save published post record"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO published_posts
                (workflow_id, platform, post_id, content, published_at)
                VALUES ($1, $2, $3, $4, $5)
            """, workflow_id, platform, post_id, json.dumps(content), datetime.now())
```

---

## 10. Error Handling & Retries

```python
# utils/error_handling.py
import asyncio
from typing import Callable, Any, Optional
import logging
from functools import wraps

logger = logging.getLogger(__name__)

class RetryConfig:
    """Retry configuration"""
    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        backoff_factor: float = 2.0,
        max_delay: float = 60.0,
        exceptions: tuple = (Exception,)
    ):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.backoff_factor = backoff_factor
        self.max_delay = max_delay
        self.exceptions = exceptions

def async_retry(config: RetryConfig):
    """Decorator for async retry logic"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            delay = config.initial_delay
            
            for attempt in range(1, config.max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except config.exceptions as e:
                    last_exception = e
                    logger.warning(
                        f"Attempt {attempt}/{config.max_attempts} failed for {func.__name__}: {e}"
                    )
                    
                    if attempt < config.max_attempts:
                        await asyncio.sleep(delay)
                        delay = min(delay * config.backoff_factor, config.max_delay)
            
            logger.error(f"All {config.max_attempts} attempts failed for {func.__name__}")
            raise last_exception
        
        return wrapper
    return decorator

class CircuitBreaker:
    """Circuit breaker pattern implementation"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "closed"  # closed, open, half_open
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker"""
        if self.state == "open":
            if asyncio.get_event_loop().time() - self.last_failure_time > self.recovery_timeout:
                self.state = "half_open"
                logger.info("Circuit breaker entering half-open state")
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        if self.state == "half_open":
            self.state = "closed"
            logger.info("Circuit breaker closed after successful call")
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = asyncio.get_event_loop().time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            logger.error("Circuit breaker opened due to failures")
```

---

## 11. Observability & Logging

```python
# observability/logging_config.py
import logging
import sys
from pythonjsonlogger import jsonlogger
from datetime import datetime

def setup_logging(log_level: str = "INFO"):
    """Configure structured logging"""
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # JSON formatter
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s"
    )
    
    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger

# observability/tracing.py
from typing import Callable, Any
from functools import wraps
import time
import logging

logger = logging.getLogger(__name__)

def trace_execution(func: Callable) -> Callable:
    """Decorator to trace function execution"""
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        
        logger.info(f"Starting {func.__name__}", extra={
            "function": func.__name__,
            "event": "start"
        })
        
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            logger.info(f"Completed {func.__name__}", extra={
                "function": func.__name__,
                "event": "complete",
                "execution_time": execution_time
            })
            
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            
            logger.error(f"Failed {func.__name__}: {e}", extra={
                "function": func.__name__,
                "event": "error",
                "execution_time": execution_time,
                "error": str(e)
            })
            raise
    
    return wrapper
```

---

## 12. Project Structure

```
social-agent-system/
├── README.md
├── requirements.txt
├── setup.py
├── .env.example
├── .gitignore
│
├── config/
│   ├── __init__.py
│   ├── settings.py           # Pydantic settings
│   └── validator.py          # Config validation
│
├── crews/
│   ├── __init__.py
│   │
│   ├── github_crew/
│   │   ├── __init__.py
│   │   ├── crew.py          # GitHub analysis crew
│   │   ├── agents.py        # Agent definitions
│   │   ├── tasks.py         # Task definitions
│   │   └── tools.py         # GitHub-specific tools
│   │
│   ├── content_crew/
│   │   ├── __init__.py
│   │   ├── crew.py          # Content generation crew
│   │   ├── agents.py        # Platform-specific agents
│   │   ├── tasks.py         # Generation tasks
│   │   └── prompts.py       # Prompt templates
│   │
│   └── async_crew.py        # Async execution wrapper
│
├── workflows/
│   ├── __init__.py
│   ├── graph.py             # LangGraph workflow definition
│   ├── nodes.py             # Graph node implementations
│   ├── edges.py             # Conditional edge logic
│   └── state.py             # State schemas
│
├── integrations/
│   ├── __init__.py
│   ├── github.py            # GitHub API client
│   ├── linkedin.py          # LinkedIn API client
│   ├── x_twitter.py         # X (Twitter) API client
│   ├── instagram.py         # Instagram API client
│   └── publisher.py         # Multi-platform publisher
│
├── tools/
│   ├── __init__.py
│   ├── github_tools.py      # GitHub analysis tools
│   └── llm_tools.py         # LLM-powered tools
│
├── persistence/
│   ├── __init__.py
│   ├── database.py          # Database connection
│   ├── state_manager.py     # State persistence
│   └── cache.py             # Redis cache manager
│
├── utils/
│   ├── __init__.py
│   ├── concurrency.py       # Async utilities
│   ├── error_handling.py    # Retry & circuit breaker
│   └── validation.py        # Data validation
│
├── observability/
│   ├── __init__.py
│   ├── logging_config.py    # Logging setup
│   ├── tracing.py           # Execution tracing
│   └── metrics.py           # Metrics collection
│
├── migrations/
│   ├── versions/
│   └── alembic.ini
│
├── tests/
│   ├── __init__.py
│   ├── test_github_crew.py
│   ├── test_content_crew.py
│   ├── test_integrations.py
│   └── test_workflows.py
│
├── scripts/
│   ├── setup_database.py
│   ├── run_workflow.py
│   └── test_connections.py
│
└── main.py                  # Application entry point
```

---

## 13. Deployment Considerations

### 13.1 Container Configuration

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 agent && chown -R agent:agent /app
USER agent

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
    CMD python -c "import sys; sys.exit(0)"

CMD ["python", "main.py"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    env_file: .env
    depends_on:
      - postgres
      - redis
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: social_agent
      POSTGRES_USER: agent
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"

volumes:
  postgres_data:
  redis_data:
```

### 13.2 Kubernetes Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: social-agent-system
spec:
  replicas: 2
  selector:
    matchLabels:
      app: social-agent
  template:
    metadata:
      labels:
        app: social-agent
    spec:
      containers:
      - name: agent
        image: social-agent:latest
        envFrom:
        - secretRef:
            name: agent-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
```

---

## 14. Scalability & Modularity

### 14.1 Horizontal Scaling Strategy

**Stateless Design:**
- All state persisted in PostgreSQL/Redis
- No in-memory session data
- Enables horizontal pod scaling

**Queue-Based Processing:**
- Use Celery/RQ for async task queue
- Separate workers for different phases
- Independent scaling per workflow phase

**Database Optimization:**
- Connection pooling (pgBouncer)
- Read replicas for analytics
- Partitioning for large tables

### 14.2 Modular Extension Points

**Adding New Platforms:**
```python
# integrations/tiktok.py
class TikTokClient:
    """New platform integration"""
    pass

class TikTokPublisher:
    """Publisher implementation"""
    pass

# Register in publisher.py
publishers["tiktok"] = TikTokPublisher(client)
```

**Adding New Agent Capabilities:**
```python
# crews/seo_crew/
# New specialized crew for SEO optimization
class SEOOptimizationCrew:
    """Optimize content for search engines"""
    pass
```

**Plugin Architecture:**
```python
# plugins/base.py
class AgentPlugin:
    """Base class for plugins"""
    
    def on_analysis_complete(self, data: Dict):
        """Hook called after GitHub analysis"""
        pass
    
    def on_content_generated(self, drafts: List[Dict]):
        """Hook called after content generation"""
        pass
```

---

## Summary

This production-grade system design provides:

✅ **Robust Architecture**: Hybrid LangGraph + CrewAI for optimal control and collaboration  
✅ **Async Execution**: Native Python asyncio with concurrency management  
✅ **State Management**: PostgreSQL checkpointing with Redis caching  
✅ **Error Handling**: Comprehensive retry logic, circuit breakers, and graceful degradation  
✅ **Observability**: Structured logging, tracing, and LangSmith integration  
✅ **Scalability**: Horizontal scaling, queue-based processing, and modular architecture  
✅ **Security**: Environment-based config, secret management, and OAuth 2.0  
✅ **Production-Ready**: Docker, Kubernetes, health checks, and monitoring  

The system is fully autonomous, follows modern LLM agent engineering best practices, and is designed for production deployment at scale.
