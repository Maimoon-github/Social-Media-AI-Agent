# Autonomous Social Agent System - Prompt Engineering Framework

## Document Overview

This framework provides detailed, implementation-ready prompts for every file in the autonomous social media AI agent system. Each prompt specifies purpose, responsibilities, inputs, outputs, dependencies, synchronization requirements, state interactions, and implementation constraints.

**System Context:**
- **Architecture**: LangGraph (orchestration) + CrewAI (multi-agent content generation) hybrid
- **LLM Provider**: Ollama (DeepSeek-R1 for analysis, Qwen 2.5-7B for social content)
- **State Management**: PostgreSQL (persistence) + Redis (caching/rate limiting)
- **Execution Model**: Async-first with asyncio and aiohttp
- **Deployment**: Docker/Kubernetes with horizontal scaling support

---

## Table of Contents

1. [Root Level Files](#1-root-level-files)
2. [Configuration Module](#2-configuration-module-config)
3. [Crews Module](#3-crews-module-crews)
4. [Workflows Module](#4-workflows-module-workflows)
5. [Integrations Module](#5-integrations-module-integrations)
6. [Tools Module](#6-tools-module-tools)
7. [Persistence Module](#7-persistence-module-persistence)
8. [Utilities Module](#8-utilities-module-utils)
9. [Observability Module](#9-observability-module-observability)
10. [Tests Module](#10-tests-module-tests)
11. [Scripts Module](#11-scripts-module-scripts)
12. [Migrations](#12-migrations-migrations)

---

## 1. ROOT LEVEL FILES

### 1.1 main.py

**Purpose**: Application entry point and orchestration controller

**Responsibilities**:
- Parse command-line arguments (repo URL, username, platforms, dry-run mode)
- Initialize the SocialAgentOrchestrator
- Coordinate workflow execution from start to completion
- Handle top-level error handling and graceful shutdown
- Provide CLI interface for manual invocations

**Inputs**:
- Command-line arguments:
  - `--repo`: GitHub repository URL (required)
  - `--username`: GitHub username (required)
  - `--platforms`: List of platforms (linkedin, twitter, instagram)
  - `--dry-run`: Boolean flag to skip actual publishing
  - `--config`: Optional path to custom config file
  - `--workflow-id`: Optional ID to resume existing workflow

**Outputs**:
- Exit code (0 for success, non-zero for failures)
- Console output with workflow progress
- Workflow summary (analysis results, content drafts, publishing status)
- Workflow ID for tracking/resuming

**Dependencies**:
- `config.settings`: Load system configuration
- `config.validator`: Validate configuration before execution
- `workflows.graph`: LangGraph workflow definition
- `persistence.database`: Database connection initialization
- `observability.logging_config`: Setup logging infrastructure
- `asyncio`: Async runtime management

**State Interactions**:
- Creates initial workflow state with unique workflow_id
- Triggers state persistence through checkpointing
- Polls workflow state for progress monitoring

**Synchronization Requirements**:
- Must initialize database connections before workflow execution
- Must setup logging before any operations
- Must validate all API credentials before proceeding
- Must release all resources on shutdown (database, Redis, file handles)

**Implementation Details**:
```python
# Structure:
class SocialAgentOrchestrator:
    def __init__(self, config_path: Optional[str] = None):
        # Load configuration
        # Initialize database connections
        # Setup logging and tracing
        
    async def initialize(self):
        # Validate configuration
        # Test database connectivity
        # Authenticate with all platform APIs
        # Initialize LangGraph workflow
        
    async def run_workflow(
        self,
        github_repo_url: str,
        github_username: str,
        platforms: List[str],
        dry_run: bool = False,
        workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        # Execute full workflow
        # Handle checkpointing
        # Return results
        
    async def cleanup(self):
        # Close database connections
        # Release Redis connections
        # Flush logs

async def main():
    parser = argparse.ArgumentParser()
    # Define CLI arguments
    args = parser.parse_args()
    
    orchestrator = SocialAgentOrchestrator()
    await orchestrator.initialize()
    
    result = await orchestrator.run_workflow(
        github_repo_url=args.repo,
        github_username=args.username,
        platforms=args.platforms,
        dry_run=args.dry_run
    )
    
    await orchestrator.cleanup()
    
if __name__ == "__main__":
    asyncio.run(main())
```

**Error Handling**:
- Catch and log all exceptions at top level
- Provide user-friendly error messages
- Exit with appropriate status codes
- Save partial state on crashes

**Success Criteria**:
- Workflow completes end-to-end in <5 minutes
- At least one platform publishes successfully
- All state is persisted at checkpoints
- Resources are properly cleaned up

---

### 1.2 requirements.txt

**Purpose**: Python dependency specification

**Content**:
```
# Core frameworks
langgraph==0.2.50
langchain==0.3.10
langchain-core==0.3.25
crewai==0.80.0
langsmith==0.2.10

# LLM Providers
langchain-ollama==0.2.0

# Async & HTTP
aiohttp==3.11.0
httpx==0.28.1

# Database
sqlalchemy==2.0.36
asyncpg==0.30.0
psycopg2-binary==2.9.10
alembic==1.14.0

# Caching
redis==5.2.1
hiredis==3.0.0

# API Clients
PyGithub==2.5.0
python-linkedin-v2==0.2.0
tweepy==4.14.0
instagrapi==2.1.2

# Data Processing
pydantic==2.10.4
pydantic-settings==2.6.1

# Utilities
python-dotenv==1.0.1
tenacity==9.0.0
backoff==2.2.1

# Observability
structlog==24.4.0
sentry-sdk==2.19.2

# Testing
pytest==8.3.4
pytest-asyncio==0.24.0
pytest-cov==6.0.0
pytest-mock==3.14.0
```

**Notes**:
- Pin exact versions for reproducibility
- Separate sections by functionality
- Include both sync and async HTTP clients
- Add testing frameworks

---

### 1.3 setup.py

**Purpose**: Package installation configuration

**Responsibilities**:
- Define package metadata
- Specify dependencies
- Configure entry points for CLI

**Content Structure**:
```python
from setuptools import setup, find_packages

setup(
    name="social-agent-system",
    version="1.0.0",
    description="Autonomous social media AI agent system",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        # Read from requirements.txt
    ],
    entry_points={
        "console_scripts": [
            "social-agent=main:main",
        ],
    },
    python_requires=">=3.11",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.11",
    ],
)
```

---

### 1.4 .env.example

**Purpose**: Environment configuration template

**Content**:
```bash
# GitHub API
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx

# LinkedIn API
LINKEDIN_CLIENT_ID=xxxxxxxxxxxx
LINKEDIN_CLIENT_SECRET=xxxxxxxxxxxx
LINKEDIN_ACCESS_TOKEN=xxxxxxxxxxxx
LINKEDIN_REFRESH_TOKEN=xxxxxxxxxxxx

# X (Twitter) API
X_API_KEY=xxxxxxxxxxxx
X_API_SECRET=xxxxxxxxxxxx
X_ACCESS_TOKEN=xxxxxxxxxxxx
X_ACCESS_TOKEN_SECRET=xxxxxxxxxxxx
X_BEARER_TOKEN=xxxxxxxxxxxx

# Instagram API
INSTAGRAM_APP_ID=xxxxxxxxxxxx
INSTAGRAM_APP_SECRET=xxxxxxxxxxxx
INSTAGRAM_ACCESS_TOKEN=xxxxxxxxxxxx
INSTAGRAM_ACCOUNT_ID=xxxxxxxxxxxx

# LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_ANALYSIS_MODEL=deepseek-r1:latest
OLLAMA_CONTENT_MODEL=qwen2.5:7b

# Database
DATABASE_URL=postgresql://agent:password@localhost:5432/social_agent
REDIS_URL=redis://localhost:6379/0

# Observability (Optional)
LANGSMITH_API_KEY=lsv2_xxxxxxxxxxxx
LANGSMITH_PROJECT=social-agent-system
SENTRY_DSN=https://xxxxxxxxxxxx@sentry.io/xxxxxxxxxxxx

# System Configuration
ENVIRONMENT=development
DEBUG=false
LOG_LEVEL=INFO
MAX_RETRIES=3
WORKFLOW_TIMEOUT=300
```

---

### 1.5 .gitignore

**Purpose**: Specify files to exclude from version control

**Content**:
```
# Environment
.env
.env.local
*.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Database
*.db
*.sqlite3

# Logs
logs/
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# Testing
.pytest_cache/
.coverage
htmlcov/

# Build artifacts
build/
dist/
*.egg-info/

# Docker
docker-compose.override.yml

# OS
.DS_Store
Thumbs.db
```

---

### 1.6 README.md

**Purpose**: Project documentation and quick start guide

**Structure**:
```markdown
# Autonomous Social Media AI Agent System

## Overview
Fully autonomous system that analyzes GitHub repositories and generates 
platform-optimized social media content using LangGraph + CrewAI.

## Features
- GitHub repository analysis with health scoring
- Multi-platform content generation (LinkedIn, X, Instagram)
- Async execution with state persistence
- Robust error handling and retry logic
- Horizontal scaling support

## Quick Start
[Link to detailed quick start guide]

## Architecture
[High-level architecture diagram]

## Documentation
- [Full System Design](./autonomous_social_agent_system_design.md)
- [Workflow Diagrams](./social_agent_system_diagrams.md)
- [API Reference](./docs/api-reference.md)

## License
MIT
```

---

## 2. CONFIGURATION MODULE (config/)

### 2.1 config/__init__.py

**Purpose**: Configuration module initialization

**Content**:
```python
"""Configuration management for the social agent system."""

from .settings import Settings, get_settings
from .validator import ConfigValidator

__all__ = ["Settings", "get_settings", "ConfigValidator"]
```

---

### 2.2 config/settings.py

**Purpose**: Centralized configuration management using Pydantic

**Responsibilities**:
- Load environment variables
- Define configuration schemas with validation
- Provide type-safe configuration access
- Support multiple environments (dev, staging, prod)

**Configuration Schemas**:

```python
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings
from typing import Optional, List
from enum import Enum

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class GitHubConfig(BaseModel):
    token: str = Field(..., description="GitHub personal access token")
    api_base_url: str = Field(default="https://api.github.com", description="GitHub API base URL")
    rate_limit_requests: int = Field(default=5000, description="Hourly rate limit")
    timeout: int = Field(default=30, description="API timeout in seconds")

class LinkedInConfig(BaseModel):
    client_id: str
    client_secret: str
    access_token: str
    refresh_token: Optional[str] = None
    rate_limit_requests: int = Field(default=100, description="Daily rate limit")

class XConfig(BaseModel):
    api_key: str
    api_secret: str
    access_token: str
    access_token_secret: str
    bearer_token: str
    rate_limit_posts: int = Field(default=50, description="Daily post limit")

class InstagramConfig(BaseModel):
    app_id: str
    app_secret: str
    access_token: str
    account_id: str
    rate_limit_posts: int = Field(default=25, description="Daily post limit")

class LLMConfig(BaseModel):
    provider: str = Field(default="ollama", description="LLM provider (ollama)")
    ollama_base_url: str = Field(default="http://localhost:11434")
    analysis_model: str = Field(default="deepseek-r1:latest", description="Model for GitHub analysis")
    content_model: str = Field(default="qwen2.5:7b", description="Model for content generation")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, ge=1)
    timeout: int = Field(default=120, description="LLM request timeout")

class DatabaseConfig(BaseModel):
    url: str = Field(..., description="PostgreSQL connection URL")
    pool_size: int = Field(default=10)
    max_overflow: int = Field(default=20)
    pool_timeout: int = Field(default=30)
    echo: bool = Field(default=False, description="SQL echo for debugging")

class RedisConfig(BaseModel):
    url: str = Field(..., description="Redis connection URL")
    max_connections: int = Field(default=50)
    decode_responses: bool = Field(default=True)

class ObservabilityConfig(BaseModel):
    langsmith_api_key: Optional[str] = None
    langsmith_project: str = Field(default="social-agent-system")
    sentry_dsn: Optional[str] = None
    log_level: str = Field(default="INFO")

class WorkflowConfig(BaseModel):
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_delay: int = Field(default=2, description="Base delay in seconds")
    workflow_timeout: int = Field(default=300, description="Max workflow duration in seconds")
    checkpoint_interval: int = Field(default=60, description="Checkpoint save interval")

class Settings(BaseSettings):
    environment: Environment = Field(default=Environment.DEVELOPMENT)
    debug: bool = Field(default=False)
    
    github: GitHubConfig
    linkedin: LinkedInConfig
    x: XConfig
    instagram: InstagramConfig
    llm: LLMConfig
    database: DatabaseConfig
    redis: RedisConfig
    observability: ObservabilityConfig
    workflow: WorkflowConfig
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"
        case_sensitive = False
    
    @field_validator("environment", mode="before")
    @classmethod
    def validate_environment(cls, v):
        if isinstance(v, str):
            return Environment(v.lower())
        return v

# Singleton pattern for settings
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """Get application settings singleton."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
```

**Dependencies**:
- `pydantic`: Data validation
- `pydantic-settings`: Environment variable loading
- `python-dotenv`: .env file support

**Usage Pattern**:
```python
from config import get_settings

settings = get_settings()
github_token = settings.github.token
```

---

### 2.3 config/validator.py

**Purpose**: Pre-flight validation of configuration and API connectivity

**Responsibilities**:
- Validate all API credentials before workflow execution
- Test database connectivity
- Verify Redis availability
- Check LLM service reachability
- Validate rate limits are within bounds

**Implementation**:

```python
from typing import Dict, List, Tuple
import asyncio
import aiohttp
from .settings import Settings
from integrations.github import GitHubClient
from integrations.linkedin import LinkedInClient
from integrations.x_twitter import XClient
from integrations.instagram import InstagramClient
from persistence.database import DatabaseManager
from persistence.cache import CacheManager

class ValidationError(Exception):
    """Configuration validation error."""
    pass

class ConfigValidator:
    """Validates system configuration and external dependencies."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.validation_results: Dict[str, bool] = {}
        
    async def validate_all(self) -> Tuple[bool, List[str]]:
        """
        Run all validation checks.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Run validations concurrently
        results = await asyncio.gather(
            self._validate_github(),
            self._validate_linkedin(),
            self._validate_x(),
            self._validate_instagram(),
            self._validate_llm(),
            self._validate_database(),
            self._validate_redis(),
            return_exceptions=True
        )
        
        # Collect errors
        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                errors.append(str(result))
                
        is_valid = len(errors) == 0
        return is_valid, errors
    
    async def _validate_github(self) -> bool:
        """Validate GitHub API credentials."""
        try:
            client = GitHubClient(token=self.settings.github.token)
            # Test API call
            await client.get_rate_limit()
            self.validation_results["github"] = True
            return True
        except Exception as e:
            raise ValidationError(f"GitHub validation failed: {e}")
    
    async def _validate_linkedin(self) -> bool:
        """Validate LinkedIn API credentials."""
        try:
            client = LinkedInClient(
                client_id=self.settings.linkedin.client_id,
                client_secret=self.settings.linkedin.client_secret,
                access_token=self.settings.linkedin.access_token
            )
            # Test API call
            await client.verify_token()
            self.validation_results["linkedin"] = True
            return True
        except Exception as e:
            raise ValidationError(f"LinkedIn validation failed: {e}")
    
    async def _validate_x(self) -> bool:
        """Validate X (Twitter) API credentials."""
        try:
            client = XClient(
                api_key=self.settings.x.api_key,
                api_secret=self.settings.x.api_secret,
                access_token=self.settings.x.access_token,
                access_token_secret=self.settings.x.access_token_secret
            )
            # Test API call
            await client.verify_credentials()
            self.validation_results["x"] = True
            return True
        except Exception as e:
            raise ValidationError(f"X validation failed: {e}")
    
    async def _validate_instagram(self) -> bool:
        """Validate Instagram API credentials."""
        try:
            client = InstagramClient(
                app_id=self.settings.instagram.app_id,
                app_secret=self.settings.instagram.app_secret,
                access_token=self.settings.instagram.access_token
            )
            # Test API call
            await client.verify_token()
            self.validation_results["instagram"] = True
            return True
        except Exception as e:
            raise ValidationError(f"Instagram validation failed: {e}")
    
    async def _validate_llm(self) -> bool:
        """Validate LLM service availability."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.settings.llm.ollama_base_url}/api/tags"
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Check if required models are available
                        available_models = [m["name"] for m in data.get("models", [])]
                        if self.settings.llm.analysis_model not in available_models:
                            raise ValidationError(f"Analysis model {self.settings.llm.analysis_model} not found")
                        if self.settings.llm.content_model not in available_models:
                            raise ValidationError(f"Content model {self.settings.llm.content_model} not found")
                        
                        self.validation_results["llm"] = True
                        return True
                    else:
                        raise ValidationError(f"Ollama service returned status {response.status}")
        except Exception as e:
            raise ValidationError(f"LLM validation failed: {e}")
    
    async def _validate_database(self) -> bool:
        """Validate database connectivity."""
        try:
            db_manager = DatabaseManager(self.settings.database.url)
            await db_manager.connect()
            await db_manager.disconnect()
            self.validation_results["database"] = True
            return True
        except Exception as e:
            raise ValidationError(f"Database validation failed: {e}")
    
    async def _validate_redis(self) -> bool:
        """Validate Redis connectivity."""
        try:
            cache_manager = CacheManager(self.settings.redis.url)
            await cache_manager.connect()
            await cache_manager.ping()
            await cache_manager.disconnect()
            self.validation_results["redis"] = True
            return True
        except Exception as e:
            raise ValidationError(f"Redis validation failed: {e}")
```

**Dependencies**:
- `config.settings`: Configuration access
- `integrations.*`: All platform clients
- `persistence.database`: Database manager
- `persistence.cache`: Cache manager

**Usage Pattern**:
```python
from config import get_settings, ConfigValidator

settings = get_settings()
validator = ConfigValidator(settings)
is_valid, errors = await validator.validate_all()

if not is_valid:
    for error in errors:
        logger.error(error)
    sys.exit(1)
```

---

## 3. CREWS MODULE (crews/)

### 3.1 crews/__init__.py

**Purpose**: Crews module initialization

**Content**:
```python
"""Multi-agent crews for GitHub analysis and content generation."""

from .github_crew import GitHubAnalysisCrew
from .content_crew import ContentGenerationCrew
from .async_crew import AsyncCrewExecutor

__all__ = ["GitHubAnalysisCrew", "ContentGenerationCrew", "AsyncCrewExecutor"]
```

---

### 3.2 crews/async_crew.py

**Purpose**: Async wrapper for CrewAI execution

**Responsibilities**:
- Wrap CrewAI's sync execution in async context
- Prevent blocking of the main event loop
- Handle concurrent crew executions
- Manage resource cleanup

**Implementation**:

```python
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
```

**Dependencies**:
- `crewai`: CrewAI framework
- `asyncio`: Async execution
- `concurrent.futures`: Thread pool for sync-to-async bridging

**Synchronization Requirements**:
- Must not block the main event loop
- Must properly cleanup thread pool on shutdown
- Must handle exceptions without crashing the workflow

---

### 3.3 crews/github_crew/__init__.py

**Content**:
```python
"""GitHub analysis crew components."""

from .crew import GitHubAnalysisCrew

__all__ = ["GitHubAnalysisCrew"]
```

---

### 3.4 crews/github_crew/crew.py

**Purpose**: Orchestrate GitHub analysis using specialized agents

**Responsibilities**:
- Initialize GitHub analysis agents
- Define analysis tasks
- Coordinate agent collaboration
- Return structured analysis results

**Implementation**:

```python
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
```

**Dependencies**:
- `crewai`: Crew orchestration
- `langchain_ollama`: Ollama LLM integration
- `.agents`: Agent definitions
- `.tasks`: Task definitions
- `.tools`: GitHub analysis tools

**Input Schema**:
```python
{
    "github_repo_url": "https://github.com/owner/repo",
    "github_username": "owner"
}
```

**Output Schema**:
```python
{
    "repository": {
        "url": str,
        "name": str,
        "description": str,
        "stars": int,
        "forks": int,
        "health_score": float,  # 0-100
        "tech_stack": List[str],
        "recent_activity": Dict,
        "key_insights": List[str]
    },
    "profile": {
        "username": str,
        "name": str,
        "bio": str,
        "expertise_areas": List[str],
        "contribution_patterns": Dict,
        "notable_projects": List[Dict],
        "professional_positioning": str
    },
    "analysis_metadata": {
        "timestamp": str,
        "model_used": str,
        "success": bool
    }
}
```

---

### 3.5 crews/github_crew/agents.py

**Purpose**: Define specialized GitHub analysis agents

**Implementation**:

```python
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
```

**Agent Configuration**:
- `max_iter`: Maximum iterations per agent (prevent infinite loops)
- `max_rpm`: Rate limit requests per minute
- `allow_delegation`: Disabled for focused analysis
- `verbose`: Enable for debugging and observability

---

### 3.6 crews/github_crew/tasks.py

**Purpose**: Define specific analysis tasks for agents

**Implementation**:

```python
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
```

**Task Dependencies**:
- Repository analysis must complete before profile analysis
- Results are used as context for subsequent content generation

---

### 3.7 crews/github_crew/tools.py

**Purpose**: GitHub-specific tools for agent use

**Implementation**:

```python
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
```

**Dependencies**:
- `langchain.tools`: Tool base classes
- `integrations.github`: GitHub API client

**Tool Usage Pattern**:
Agents automatically select and invoke tools based on task requirements.

---

### 3.8 crews/content_crew/__init__.py

**Content**:
```python
"""Content generation crew components."""

from .crew import ContentGenerationCrew

__all__ = ["ContentGenerationCrew"]
```

---

### 3.9 crews/content_crew/crew.py

**Purpose**: Orchestrate platform-specific content generation

**Responsibilities**:
- Initialize content generation agents for each platform
- Define content creation tasks
- Coordinate parallel content generation
- Validate generated content against platform requirements
- Return structured content drafts

**Implementation**:

```python
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
```

**Dependencies**:
- `crewai`: Crew orchestration
- `langchain_ollama`: Ollama LLM integration
- `.agents`, `.tasks`, `.prompts`: Content generation components

**Input Schema**:
```python
{
    "analysis_results": {
        "repository": {...},  # From GitHubAnalysisCrew
        "profile": {...}
    },
    "platforms": ["linkedin", "twitter", "instagram"]
}
```

**Output Schema**:
```python
{
    "drafts": {
        "linkedin": {
            "text": str,
            "hashtags": List[str],
            "media_type": Optional[str],
            "metadata": Dict
        },
        "twitter": {
            "tweets": List[Dict],
            "hashtags": List[str],
            "metadata": Dict
        },
        "instagram": {
            "caption": str,
            "hashtags": List[str],
            "image_description": str,
            "metadata": Dict
        }
    },
    "metadata": {
        "model_used": str,
        "platforms_requested": List[str],
        "platforms_successful": List[str]
    }
}
```

---

### 3.10 crews/content_crew/agents.py

**Purpose**: Define platform-specific content generation agents

**Implementation**:

```python
from crewai import Agent
from langchain_ollama import ChatOllama

def create_linkedin_expert(llm: ChatOllama) -> Agent:
    """
    Create LinkedIn content expert agent.
    
    Specializes in professional, B2B-focused content that drives engagement
    and positions technical work as thought leadership.
    """
    return Agent(
        role="LinkedIn Content Strategist & Thought Leadership Expert",
        goal=(
            "Create professional, engaging LinkedIn posts that position technical "
            "work as industry thought leadership and drive B2B engagement"
        ),
        backstory=(
            "You are a former marketing director with 10+ years of experience crafting "
            "viral LinkedIn content for tech companies. You've helped dozens of CTOs "
            "and engineering leaders build their personal brands through strategic "
            "content that balances technical depth with business value. You understand "
            "LinkedIn's algorithm and know exactly how to structure posts for maximum "
            "reach: compelling hooks, value-driven insights, strategic hashtags, and "
            "clear calls-to-action. Your content consistently generates hundreds of "
            "comments and shares."
        ),
        verbose=True,
        allow_delegation=False,
        llm=llm,
        max_iter=5
    )

def create_x_expert(llm: ChatOllama) -> Agent:
    """
    Create X (Twitter) content expert agent.
    
    Specializes in concise, punchy content optimized for virality and
    thread-based storytelling.
    """
    return Agent(
        role="X (Twitter) Viral Content Specialist & Thread Architect",
        goal=(
            "Craft concise, engaging tweets and threads optimized for virality, "
            "engagement, and community building in the tech space"
        ),
        backstory=(
            "You are a social media manager who built multiple tech accounts to 100k+ "
            "followers through strategic threading and community engagement. You've "
            "mastered the art of the hook tweet, know when to thread vs. single tweet, "
            "and understand X's unique culture and algorithm. You can distill complex "
            "technical concepts into punchy, quotable insights that developers love to "
            "retweet. Your threads consistently go viral because you balance education "
            "with entertainment and always leave value in every tweet."
        ),
        verbose=True,
        allow_delegation=False,
        llm=llm,
        max_iter=5
    )

def create_instagram_expert(llm: ChatOllama) -> Agent:
    """
    Create Instagram content expert agent.
    
    Specializes in visual storytelling with compelling captions that work
    alongside technical imagery.
    """
    return Agent(
        role="Instagram Visual Storyteller & Developer Community Builder",
        goal=(
            "Design visually compelling Instagram content with engaging captions "
            "that build community around technical projects"
        ),
        backstory=(
            "You are a creative director specializing in technical content visualization "
            "and developer community building on Instagram. You've grown multiple dev-focused "
            "Instagram accounts to 50k+ followers by combining stunning visuals with "
            "authentic storytelling. You understand that Instagram is visual-first but "
            "caption-driven for engagement. You know how to describe visual concepts for "
            "images that haven't been created yet, write captions that hook within the "
            "first line, use hashtags strategically, and build genuine community through "
            "relatable tech narratives."
        ),
        verbose=True,
        allow_delegation=False,
        llm=llm,
        max_iter=5
    )
```

**Agent Characteristics**:
- Lower `max_iter` for faster content generation
- Platform-specific expertise encoded in backstories
- No delegation needed (independent content creation)

---

### 3.11 crews/content_crew/tasks.py

**Purpose**: Define platform-specific content generation tasks

**Implementation**:

```python
from crewai import Task, Agent
from typing import Dict, Any

def create_linkedin_task(
    agent: Agent,
    analysis: Dict[str, Any]
) -> Task:
    """
    Create LinkedIn content generation task.
    
    Args:
        agent: LinkedIn expert agent
        analysis: GitHub analysis results
        
    Returns:
        Configured Task instance
    """
    repo = analysis.get("repository", {})
    profile = analysis.get("profile", {})
    
    return Task(
        description=f"""
        Create a professional LinkedIn post about the GitHub repository and developer profile.
        
        Repository Context:
        - Name: {repo.get('name')}
        - Description: {repo.get('description')}
        - Tech Stack: {', '.join(repo.get('tech_stack', []))}
        - Health Score: {repo.get('health_score')}
        - Key Insights: {repo.get('key_insights')}
        
        Developer Context:
        - Username: {profile.get('username')}
        - Expertise: {', '.join([e.get('area') for e in profile.get('expertise_areas', [])])}
        - Professional Positioning: {profile.get('professional_positioning')}
        
        Content Requirements:
        1. **Hook**: Start with a compelling opening that grabs attention
        2. **Value**: Focus on the business or technical value of the project
        3. **Insights**: Share 2-3 key technical insights or learnings
        4. **Credibility**: Reference the developer's expertise naturally
        5. **Call-to-Action**: End with a clear CTA (check it out, share thoughts, etc.)
        6. **Length**: 150-300 characters optimal (max 3000)
        7. **Hashtags**: 3-5 relevant hashtags (#opensource #github #[tech])
        8. **Tone**: Professional but approachable, thought-leadership style
        
        Structure:
        - Line 1-2: Hook (question, surprising fact, bold statement)
        - Line 3-6: Context and value proposition
        - Line 7-12: Technical insights and highlights
        - Line 13-15: Developer positioning
        - Line 16-17: Call-to-action
        - Line 18: Hashtags
        
        Avoid:
        - Generic praise ("amazing project", "check this out")
        - Over-technical jargon without explanation
        - Salesy language
        - More than 5 hashtags
        """,
        agent=agent,
        expected_output="""
        JSON format:
        {
            "text": "Complete LinkedIn post text with line breaks",
            "hashtags": ["opensource", "github", "python", "ai", "machinelearning"],
            "media_type": null,
            "metadata": {
                "target_audience": "developers, tech leaders, CTOs",
                "content_pillar": "thought leadership",
                "expected_engagement": "high/medium/low",
                "hook_type": "question/fact/statement"
            }
        }
        """
    )

def create_x_task(
    agent: Agent,
    analysis: Dict[str, Any]
) -> Task:
    """
    Create X (Twitter) content generation task.
    
    Args:
        agent: X expert agent
        analysis: GitHub analysis results
        
    Returns:
        Configured Task instance
    """
    repo = analysis.get("repository", {})
    profile = analysis.get("profile", {})
    
    return Task(
        description=f"""
        Create an engaging X (Twitter) thread about the GitHub repository and developer.
        
        Repository Context:
        - Name: {repo.get('name')}
        - Description: {repo.get('description')}
        - Tech Stack: {', '.join(repo.get('tech_stack', []))}
        - Key Insights: {repo.get('key_insights')}
        
        Developer Context:
        - Username: @{profile.get('username')}
        - Expertise: {', '.join([e.get('area') for e in profile.get('expertise_areas', [])])}
        
        Content Requirements:
        1. **Format**: Thread (3-7 tweets optimal, max 10)
        2. **Hook Tweet**: Start with a punchy, quotable first tweet
        3. **Value**: Each tweet should provide standalone value
        4. **Length**: Max 280 characters per tweet
        5. **Hashtags**: 1-2 max (usually only in first tweet)
        6. **Tone**: Casual, engaging, developer-friendly
        7. **Engagement**: Include questions or calls for community input
        
        Thread Structure:
        Tweet 1: Hook - surprising insight or question
        Tweet 2-3: Context and problem being solved
        Tweet 4-6: Technical highlights (one per tweet)
        Tweet 7: Developer credit and call-to-action
        Optional Tweet 8+: Additional insights or community question
        
        Best Practices:
        - Use emojis sparingly (1-2 max, usually 🧵 for thread indicator)
        - Number tweets if it helps clarity (1/7, 2/7, etc.)
        - Make each tweet quotable/retweetable on its own
        - Tag the developer's X handle if you have it
        - Use simple language - avoid jargon
        """,
        agent=agent,
        expected_output="""
        JSON format:
        {
            "tweets": [
                {
                    "text": "Tweet 1 text (max 280 chars)",
                    "order": 1
                },
                {
                    "text": "Tweet 2 text (max 280 chars)",
                    "order": 2
                }
            ],
            "hashtags": ["github", "opensource"],
            "media_urls": [],
            "metadata": {
                "thread": true,
                "tweet_count": 5,
                "hook_style": "question/fact/insight",
                "expected_engagement": "high/medium/low"
            }
        }
        """
    )

def create_instagram_task(
    agent: Agent,
    analysis: Dict[str, Any]
) -> Task:
    """
    Create Instagram content generation task.
    
    Args:
        agent: Instagram expert agent
        analysis: GitHub analysis results
        
    Returns:
        Configured Task instance
    """
    repo = analysis.get("repository", {})
    profile = analysis.get("profile", {})
    
    return Task(
        description=f"""
        Create an Instagram post about the GitHub repository with visual description and caption.
        
        Repository Context:
        - Name: {repo.get('name')}
        - Description: {repo.get('description')}
        - Tech Stack: {', '.join(repo.get('tech_stack', []))}
        - Key Insights: {repo.get('key_insights')}
        
        Developer Context:
        - Username: {profile.get('username')}
        - Expertise: {', '.join([e.get('area') for e in profile.get('expertise_areas', [])])}
        
        Content Requirements:
        
        A. Image Description:
        Describe a compelling visual for this repository that could be:
        - Screenshot of code with syntax highlighting
        - Architecture diagram concept
        - UI/UX mockup if applicable
        - Data visualization
        - Before/after comparison
        - Infographic summarizing key points
        
        Be specific: colors, layout, text overlays, visual hierarchy
        
        B. Caption Requirements:
        1. **Hook**: First line must grab attention (shows in feed)
        2. **Story**: Tell the story of the project or developer journey
        3. **Value**: What can followers learn or gain?
        4. **Length**: 150-500 characters optimal (max 2200)
        5. **Hashtags**: 10-15 relevant hashtags (at the end or in comments)
        6. **Emojis**: 3-5 relevant emojis to break up text
        7. **Call-to-Action**: Clear CTA (link in bio, save this post, etc.)
        8. **Tone**: Authentic, inspiring, community-focused
        
        Caption Structure:
        Line 1-2: Hook with emoji
        
        Line 3-8: Story or context
        Line 9-12: Technical highlights (simplified)
        Line 13-15: Developer positioning or community value
        Line 16-17: Call-to-action
        
        [Hashtags]
        
        Best Practices:
        - Write for mobile (short paragraphs, line breaks)
        - Use plain language - Instagram isn't for deep tech
        - Focus on impact and inspiration over implementation
        - Make it relatable to broader audience
        """,
        agent=agent,
        expected_output="""
        JSON format:
        {
            "caption": "Full Instagram caption with emojis and line breaks",
            "hashtags": [
                "coding", "programming", "github", "opensource",
                "developer", "tech", "software", "python", 
                "machinelearning", "ai", "developers", "code"
            ],
            "image_description": "Detailed description of the visual concept to be created",
            "image_style": "code-screenshot/diagram/infographic/ui-mockup",
            "metadata": {
                "target_audience": "developers, tech enthusiasts, learners",
                "content_pillar": "education/inspiration/community",
                "visual_priority": "high",
                "expected_engagement": "high/medium/low"
            }
        }
        """
    )
```

**Task Design Principles**:
- Provide rich context from analysis results
- Specify platform-specific constraints explicitly
- Include structure templates for consistency
- Define clear expected output formats
- Embed best practices in descriptions

---

### 3.12 crews/content_crew/prompts.py

**Purpose**: Reusable prompt templates and fragments

**Implementation**:

```python
"""
Prompt templates and fragments for content generation.
"""

from typing import Dict, Any

# Platform-specific guidelines
LINKEDIN_GUIDELINES = """
LinkedIn Content Guidelines:
- Professional tone but approachable
- Focus on value and insights
- Character limit: 3000 (optimal: 150-300)
- Hashtags: 3-5 relevant tags
- Structure: Hook → Value → Insights → CTA
- Target: Developers, tech leaders, CTOs
"""

X_GUIDELINES = """
X (Twitter) Content Guidelines:
- Concise and punchy
- Character limit: 280 per tweet
- Thread limit: 10 tweets max
- Hashtags: 1-2 maximum
- Format: Thread-aware storytelling
- Target: Developer community
"""

INSTAGRAM_GUIDELINES = """
Instagram Content Guidelines:
- Visual-first thinking
- Caption limit: 2200 characters
- Hashtags: 10-15 relevant tags
- Tone: Authentic and inspiring
- Must include image description
- Target: Broader tech audience
"""

def get_platform_prompt(platform: str) -> str:
    """Get platform-specific guidelines."""
    prompts = {
        "linkedin": LINKEDIN_GUIDELINES,
        "twitter": X_GUIDELINES,
        "x": X_GUIDELINES,
        "instagram": INSTAGRAM_GUIDELINES
    }
    return prompts.get(platform, "")

# Common prompt fragments
TECH_STACK_CONTEXT = """
Technology Stack Context:
{tech_stack}

Use this to:
- Identify target audience (developers using these technologies)
- Choose relevant hashtags
- Frame technical insights appropriately
"""

DEVELOPER_CONTEXT = """
Developer Profile Context:
- Username: {username}
- Expertise: {expertise}
- Notable Projects: {projects}

Use this to:
- Position the developer's credibility
- Reference their expertise naturally
- Build narrative around their work
"""

def format_tech_stack_context(tech_stack: list) -> str:
    """Format technology stack for prompts."""
    return TECH_STACK_CONTEXT.format(
        tech_stack=", ".join(tech_stack) if tech_stack else "Not specified"
    )

def format_developer_context(profile: Dict[str, Any]) -> str:
    """Format developer profile for prompts."""
    expertise = ", ".join([
        e.get("area") for e in profile.get("expertise_areas", [])
    ])
    projects = ", ".join([
        p.get("name") for p in profile.get("notable_projects", [])[:3]
    ])
    
    return DEVELOPER_CONTEXT.format(
        username=profile.get("username", "Unknown"),
        expertise=expertise or "General development",
        projects=projects or "Various projects"
    )
```

**Usage**:
- Import in task definitions for consistent prompting
- Combine fragments to build complete prompts
- Maintain platform-specific guidelines centrally

---

## 4. WORKFLOWS MODULE (workflows/)

### 4.1 workflows/__init__.py

**Content**:
```python
"""LangGraph workflow orchestration."""

from .graph import SocialAgentWorkflow
from .state import WorkflowState
from .nodes import WorkflowNodes
from .edges import WorkflowEdges

__all__ = [
    "SocialAgentWorkflow",
    "WorkflowState",
    "WorkflowNodes",
    "WorkflowEdges"
]
```

---

### 4.2 workflows/state.py

**Purpose**: Define workflow state schema and state management

**Responsibilities**:
- Define TypedDict schema for workflow state
- Ensure type safety across workflow nodes
- Track workflow progress and phase transitions
- Store analysis results, content drafts, and publishing status

**Implementation**:

```python
from typing import TypedDict, List, Dict, Any, Optional, Literal
from datetime import datetime
from enum import Enum

class WorkflowPhase(str, Enum):
    """Workflow execution phases."""
    IDLE = "idle"
    INITIALIZING = "initializing"
    ANALYZING = "analyzing"
    GENERATING = "generating"
    VALIDATING = "validating"
    PUBLISHING = "publishing"
    COMPLETED = "completed"
    FAILED = "failed"

class PlatformStatus(TypedDict):
    """Status for individual platform publishing."""
    platform: str
    status: Literal["pending", "success", "failed", "skipped"]
    post_id: Optional[str]
    error: Optional[str]
    timestamp: Optional[str]
    retry_count: int

class WorkflowState(TypedDict):
    """
    Complete workflow state schema.
    
    This state is persisted at each checkpoint and enables pause/resume functionality.
    """
    # Workflow metadata
    workflow_id: str
    phase: WorkflowPhase
    created_at: str
    updated_at: str
    
    # Input parameters
    github_repo_url: str
    github_username: str
    platforms: List[str]
    dry_run: bool
    
    # GitHub Analysis Phase
    analysis_status: Literal["pending", "in_progress", "completed", "failed"]
    analysis_results: Optional[Dict[str, Any]]
    analysis_error: Optional[str]
    analysis_retry_count: int
    
    # Content Generation Phase
    generation_status: Literal["pending", "in_progress", "completed", "partial", "failed"]
    content_drafts: Optional[Dict[str, Any]]
    generation_error: Optional[str]
    generation_retry_count: int
    
    # Validation Phase
    validation_status: Literal["pending", "completed", "failed"]
    validation_results: Optional[Dict[str, Any]]
    
    # Publishing Phase
    publishing_status: Literal["pending", "in_progress", "completed", "partial", "failed"]
    published_posts: List[PlatformStatus]
    publishing_errors: List[str]
    
    # Rate Limiting
    rate_limit_status: Dict[str, Any]  # Platform-specific rate limit info
    queued_for_later: bool
    
    # Metrics
    execution_metrics: Dict[str, Any]
    success_rate: float
    total_duration: Optional[float]
    
    # Error tracking
    errors: List[Dict[str, Any]]
    warnings: List[str]
    
    # Checkpointing
    last_checkpoint: str
    checkpoint_count: int

# Initial state factory
def create_initial_state(
    workflow_id: str,
    github_repo_url: str,
    github_username: str,
    platforms: List[str],
    dry_run: bool = False
) -> WorkflowState:
    """
    Create initial workflow state.
    
    Args:
        workflow_id: Unique workflow identifier
        github_repo_url: GitHub repository URL
        github_username: GitHub username
        platforms: List of target platforms
        dry_run: Whether to skip actual publishing
        
    Returns:
        Initial workflow state
    """
    now = datetime.utcnow().isoformat()
    
    return WorkflowState(
        # Metadata
        workflow_id=workflow_id,
        phase=WorkflowPhase.IDLE,
        created_at=now,
        updated_at=now,
        
        # Inputs
        github_repo_url=github_repo_url,
        github_username=github_username,
        platforms=platforms,
        dry_run=dry_run,
        
        # Analysis
        analysis_status="pending",
        analysis_results=None,
        analysis_error=None,
        analysis_retry_count=0,
        
        # Generation
        generation_status="pending",
        content_drafts=None,
        generation_error=None,
        generation_retry_count=0,
        
        # Validation
        validation_status="pending",
        validation_results=None,
        
        # Publishing
        publishing_status="pending",
        published_posts=[],
        publishing_errors=[],
        
        # Rate Limiting
        rate_limit_status={},
        queued_for_later=False,
        
        # Metrics
        execution_metrics={},
        success_rate=0.0,
        total_duration=None,
        
        # Errors
        errors=[],
        warnings=[],
        
        # Checkpointing
        last_checkpoint=now,
        checkpoint_count=0
    )

# State update helpers
def update_phase(state: WorkflowState, new_phase: WorkflowPhase) -> WorkflowState:
    """Update workflow phase and timestamp."""
    state["phase"] = new_phase
    state["updated_at"] = datetime.utcnow().isoformat()
    return state

def add_error(state: WorkflowState, error: Dict[str, Any]) -> WorkflowState:
    """Add error to state tracking."""
    state["errors"].append({
        **error,
        "timestamp": datetime.utcnow().isoformat()
    })
    return state

def increment_checkpoint(state: WorkflowState) -> WorkflowState:
    """Increment checkpoint counter."""
    state["checkpoint_count"] += 1
    state["last_checkpoint"] = datetime.utcnow().isoformat()
    return state
```

**Dependencies**:
- `typing`: Type annotations
- `datetime`: Timestamp management
- `enum`: Phase enumeration

**State Transitions**:
```
IDLE → INITIALIZING → ANALYZING → GENERATING → VALIDATING → PUBLISHING → COMPLETED
                ↓          ↓           ↓           ↓            ↓
              FAILED    FAILED      FAILED      FAILED       FAILED
```

---

### 4.3 workflows/graph.py

**Purpose**: Define LangGraph workflow structure

**Responsibilities**:
- Create graph nodes for each workflow phase
- Define conditional edges for routing
- Configure checkpointing for state persistence
- Handle workflow execution and error propagation

**Implementation**:

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres import PostgresSaver
from typing import Dict, Any
from .state import WorkflowState, WorkflowPhase, create_initial_state
from .nodes import WorkflowNodes
from .edges import WorkflowEdges
from config import get_settings
import structlog

logger = structlog.get_logger()

class SocialAgentWorkflow:
    """
    LangGraph workflow orchestration for the social agent system.
    
    This class defines the complete workflow graph including nodes,
    edges, and checkpointing configuration.
    """
    
    def __init__(self, checkpointer: PostgresSaver):
        """
        Initialize workflow.
        
        Args:
            checkpointer: PostgreSQL checkpointer for state persistence
        """
        self.settings = get_settings()
        self.checkpointer = checkpointer
        self.nodes = WorkflowNodes()
        self.edges = WorkflowEdges()
        self.graph = self._build_graph()
        
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow.
        
        Returns:
            Configured StateGraph instance
        """
        # Create graph with state schema
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("initialize", self.nodes.initialize_node)
        workflow.add_node("analyze_github", self.nodes.analyze_github_node)
        workflow.add_node("generate_content", self.nodes.generate_content_node)
        workflow.add_node("validate_content", self.nodes.validate_content_node)
        workflow.add_node("check_rate_limits", self.nodes.check_rate_limits_node)
        workflow.add_node("publish_content", self.nodes.publish_content_node)
        workflow.add_node("calculate_metrics", self.nodes.calculate_metrics_node)
        workflow.add_node("handle_error", self.nodes.handle_error_node)
        
        # Set entry point
        workflow.set_entry_point("initialize")
        
        # Add edges
        # Initialize → Analyze (or Error if init fails)
        workflow.add_conditional_edges(
            "initialize",
            self.edges.route_after_initialize,
            {
                "analyze": "analyze_github",
                "error": "handle_error"
            }
        )
        
        # Analyze → Generate (or Retry or Error)
        workflow.add_conditional_edges(
            "analyze_github",
            self.edges.route_after_analysis,
            {
                "generate": "generate_content",
                "retry": "analyze_github",
                "error": "handle_error"
            }
        )
        
        # Generate → Validate (or Retry or Error)
        workflow.add_conditional_edges(
            "generate_content",
            self.edges.route_after_generation,
            {
                "validate": "validate_content",
                "retry": "generate_content",
                "error": "handle_error"
            }
        )
        
        # Validate → Check Rate Limits (or Error)
        workflow.add_conditional_edges(
            "validate_content",
            self.edges.route_after_validation,
            {
                "check_limits": "check_rate_limits",
                "error": "handle_error"
            }
        )
        
        # Check Rate Limits → Publish or Queue
        workflow.add_conditional_edges(
            "check_rate_limits",
            self.edges.route_after_rate_check,
            {
                "publish": "publish_content",
                "queue": END  # Queue for later, end workflow
            }
        )
        
        # Publish → Calculate Metrics (or Retry)
        workflow.add_conditional_edges(
            "publish_content",
            self.edges.route_after_publishing,
            {
                "calculate": "calculate_metrics",
                "retry": "publish_content",
                "error": "handle_error"
            }
        )
        
        # Calculate Metrics → END
        workflow.add_edge("calculate_metrics", END)
        
        # Error Handler → END
        workflow.add_edge("handle_error", END)
        
        return workflow.compile(checkpointer=self.checkpointer)
    
    async def execute(
        self,
        github_repo_url: str,
        github_username: str,
        platforms: List[str],
        dry_run: bool = False,
        workflow_id: Optional[str] = None
    ) -> WorkflowState:
        """
        Execute the workflow.
        
        Args:
            github_repo_url: GitHub repository URL
            github_username: GitHub username
            platforms: Target platforms for publishing
            dry_run: Skip actual publishing if True
            workflow_id: Resume existing workflow if provided
            
        Returns:
            Final workflow state
        """
        # Create or resume workflow state
        if workflow_id:
            logger.info("Resuming workflow", workflow_id=workflow_id)
            # Load state from checkpoint
            state = await self._load_checkpoint(workflow_id)
        else:
            # Create new workflow
            import uuid
            workflow_id = str(uuid.uuid4())
            logger.info("Starting new workflow", workflow_id=workflow_id)
            
            state = create_initial_state(
                workflow_id=workflow_id,
                github_repo_url=github_repo_url,
                github_username=github_username,
                platforms=platforms,
                dry_run=dry_run
            )
        
        try:
            # Execute graph
            final_state = await self.graph.ainvoke(
                state,
                config={
                    "configurable": {
                        "thread_id": workflow_id
                    }
                }
            )
            
            logger.info(
                "Workflow completed",
                workflow_id=workflow_id,
                phase=final_state["phase"],
                success_rate=final_state["success_rate"]
            )
            
            return final_state
            
        except Exception as e:
            logger.error(
                "Workflow execution failed",
                workflow_id=workflow_id,
                error=str(e)
            )
            raise
    
    async def _load_checkpoint(self, workflow_id: str) -> WorkflowState:
        """Load workflow state from checkpoint."""
        # Implementation depends on PostgresSaver API
        # This should retrieve the latest checkpoint for the workflow
        pass
```

**Dependencies**:
- `langgraph.graph`: Graph construction
- `langgraph.checkpoint.postgres`: State persistence
- `.state`: State schema
- `.nodes`: Node implementations
- `.edges`: Edge routing logic

**Checkpointing Strategy**:
- Checkpoint after each major phase
- Enable pause/resume for long-running workflows
- Persist state to PostgreSQL for durability

---

### 4.4 workflows/nodes.py

**Purpose**: Implement workflow graph nodes

**Responsibilities**:
- Execute phase-specific logic
- Update workflow state
- Handle errors and retries
- Integrate with crews and integrations

**Implementation** (showing key nodes):

```python
from typing import Dict, Any
from datetime import datetime
import structlog
from .state import WorkflowState, WorkflowPhase, update_phase, add_error
from crews import GitHubAnalysisCrew, ContentGenerationCrew, AsyncCrewExecutor
from integrations.publisher import MultiPlatformPublisher
from config import get_settings

logger = structlog.get_logger()

class WorkflowNodes:
    """Implementations of workflow graph nodes."""
    
    def __init__(self):
        self.settings = get_settings()
        self.crew_executor = AsyncCrewExecutor()
        self.github_crew = GitHubAnalysisCrew()
        self.content_crew = ContentGenerationCrew()
        self.publisher = None  # Initialized in initialize_node
        
    async def initialize_node(self, state: WorkflowState) -> WorkflowState:
        """
        Initialize workflow resources.
        
        - Validate configuration
        - Initialize publishers
        - Setup tracing
        """
        logger.info("Initializing workflow", workflow_id=state["workflow_id"])
        state = update_phase(state, WorkflowPhase.INITIALIZING)
        
        try:
            # Initialize publishers
            self.publisher = MultiPlatformPublisher(
                platforms=state["platforms"],
                dry_run=state["dry_run"]
            )
            await self.publisher.initialize()
            
            logger.info("Workflow initialized successfully")
            return state
            
        except Exception as e:
            logger.error("Initialization failed", error=str(e))
            state = add_error(state, {
                "phase": "initialization",
                "error": str(e)
            })
            state["phase"] = WorkflowPhase.FAILED
            return state
    
    async def analyze_github_node(self, state: WorkflowState) -> WorkflowState:
        """
        Execute GitHub analysis using GitHubAnalysisCrew.
        """
        logger.info("Starting GitHub analysis", workflow_id=state["workflow_id"])
        state = update_phase(state, WorkflowPhase.ANALYZING)
        state["analysis_status"] = "in_progress"
        
        try:
            # Create crew for this specific analysis
            crew = self.github_crew.create_crew(
                github_repo_url=state["github_repo_url"],
                github_username=state["github_username"]
            )
            
            # Execute crew asynchronously
            raw_output = await self.crew_executor.execute_crew(
                crew=crew,
                inputs={
                    "repo_url": state["github_repo_url"],
                    "username": state["github_username"]
                },
                crew_id=f"{state['workflow_id']}-github-analysis"
            )
            
            # Parse and structure results
            analysis_results = self.github_crew.parse_results(raw_output)
            
            state["analysis_results"] = analysis_results
            state["analysis_status"] = "completed"
            
            logger.info(
                "GitHub analysis completed",
                health_score=analysis_results.get("repository", {}).get("health_score")
            )
            
            return state
            
        except Exception as e:
            logger.error("GitHub analysis failed", error=str(e))
            
            state["analysis_error"] = str(e)
            state["analysis_retry_count"] += 1
            
            if state["analysis_retry_count"] >= self.settings.workflow.max_retries:
                state["analysis_status"] = "failed"
                state["phase"] = WorkflowPhase.FAILED
                state = add_error(state, {
                    "phase": "analysis",
                    "error": str(e),
                    "retry_count": state["analysis_retry_count"]
                })
            
            return state
    
    async def generate_content_node(self, state: WorkflowState) -> WorkflowState:
        """
        Generate platform-specific content using ContentGenerationCrew.
        """
        logger.info("Starting content generation", workflow_id=state["workflow_id"])
        state = update_phase(state, WorkflowPhase.GENERATING)
        state["generation_status"] = "in_progress"
        
        try:
            # Ensure analysis results are available
            if not state["analysis_results"]:
                raise ValueError("Analysis results not available for content generation")
            
            # Create crew for content generation
            crew = self.content_crew.create_crew(
                analysis_results=state["analysis_results"],
                platforms=state["platforms"]
            )
            
            # Execute crew asynchronously
            raw_output = await self.crew_executor.execute_crew(
                crew=crew,
                inputs={
                    "analysis": state["analysis_results"],
                    "platforms": state["platforms"]
                },
                crew_id=f"{state['workflow_id']}-content-generation"
            )
            
            # Parse and validate results
            content_results = self.content_crew.parse_and_validate_results(
                raw_output=raw_output,
                platforms=state["platforms"]
            )
            
            # Check if we got content for all requested platforms
            successful_platforms = content_results["metadata"]["platforms_successful"]
            if len(successful_platforms) < len(state["platforms"]):
                state["generation_status"] = "partial"
                state["warnings"].append(
                    f"Content generated for only {len(successful_platforms)} of "
                    f"{len(state['platforms'])} requested platforms"
                )
            else:
                state["generation_status"] = "completed"
            
            state["content_drafts"] = content_results
            
            logger.info(
                "Content generation completed",
                platforms_successful=successful_platforms
            )
            
            return state
            
        except Exception as e:
            logger.error("Content generation failed", error=str(e))
            
            state["generation_error"] = str(e)
            state["generation_retry_count"] += 1
            
            if state["generation_retry_count"] >= self.settings.workflow.max_retries:
                state["generation_status"] = "failed"
                state["phase"] = WorkflowPhase.FAILED
                state = add_error(state, {
                    "phase": "generation",
                    "error": str(e),
                    "retry_count": state["generation_retry_count"]
                })
            
            return state
    
    async def validate_content_node(self, state: WorkflowState) -> WorkflowState:
        """
        Validate content against platform requirements.
        """
        logger.info("Validating content", workflow_id=state["workflow_id"])
        state = update_phase(state, WorkflowPhase.VALIDATING)
        state["validation_status"] = "pending"
        
        try:
            # Content validation is already done in parse_and_validate_results
            # This node performs additional checks if needed
            
            validation_results = {
                "all_valid": True,
                "platform_results": {}
            }
            
            drafts = state["content_drafts"]["drafts"]
            for platform, content in drafts.items():
                # Additional validation logic here
                validation_results["platform_results"][platform] = {
                    "valid": True,
                    "warnings": []
                }
            
            state["validation_results"] = validation_results
            state["validation_status"] = "completed"
            
            logger.info("Content validation completed")
            return state
            
        except Exception as e:
            logger.error("Content validation failed", error=str(e))
            state["validation_status"] = "failed"
            state = add_error(state, {
                "phase": "validation",
                "error": str(e)
            })
            return state
    
    async def check_rate_limits_node(self, state: WorkflowState) -> WorkflowState:
        """
        Check rate limits for all platforms before publishing.
        """
        logger.info("Checking rate limits", workflow_id=state["workflow_id"])
        
        try:
            rate_limit_status = await self.publisher.check_rate_limits_all()
            state["rate_limit_status"] = rate_limit_status
            
            # Check if any platform would exceed limits
            any_exceeded = any(
                status.get("would_exceed", False)
                for status in rate_limit_status.values()
            )
            
            if any_exceeded:
                state["queued_for_later"] = True
                logger.warning("Rate limits would be exceeded, queuing workflow")
            
            return state
            
        except Exception as e:
            logger.error("Rate limit check failed", error=str(e))
            state = add_error(state, {
                "phase": "rate_limit_check",
                "error": str(e)
            })
            return state
    
    async def publish_content_node(self, state: WorkflowState) -> WorkflowState:
        """
        Publish content to all platforms in parallel.
        """
        logger.info("Publishing content", workflow_id=state["workflow_id"])
        state = update_phase(state, WorkflowPhase.PUBLISHING)
        state["publishing_status"] = "in_progress"
        
        try:
            # Get content drafts
            drafts = state["content_drafts"]["drafts"]
            
            # Publish to all platforms
            results = await self.publisher.publish_all(drafts)
            
            # Update state with results
            state["published_posts"] = results["posts"]
            state["publishing_errors"] = results["errors"]
            
            # Determine overall publishing status
            successful = [p for p in results["posts"] if p["status"] == "success"]
            if len(successful) == 0:
                state["publishing_status"] = "failed"
            elif len(successful) < len(drafts):
                state["publishing_status"] = "partial"
            else:
                state["publishing_status"] = "completed"
            
            logger.info(
                "Publishing completed",
                successful=len(successful),
                total=len(drafts)
            )
            
            return state
            
        except Exception as e:
            logger.error("Publishing failed", error=str(e))
            state["publishing_status"] = "failed"
            state = add_error(state, {
                "phase": "publishing",
                "error": str(e)
            })
            return state
    
    async def calculate_metrics_node(self, state: WorkflowState) -> WorkflowState:
        """
        Calculate final workflow metrics.
        """
        logger.info("Calculating metrics", workflow_id=state["workflow_id"])
        state = update_phase(state, WorkflowPhase.COMPLETED)
        
        try:
            # Calculate success rate
            total_platforms = len(state["platforms"])
            successful_posts = len([
                p for p in state["published_posts"]
                if p["status"] == "success"
            ])
            state["success_rate"] = successful_posts / total_platforms if total_platforms > 0 else 0.0
            
            # Calculate duration
            created_at = datetime.fromisoformat(state["created_at"])
            completed_at = datetime.utcnow()
            duration = (completed_at - created_at).total_seconds()
            state["total_duration"] = duration
            
            # Store metrics
            state["execution_metrics"] = {
                "total_duration_seconds": duration,
                "analysis_retries": state["analysis_retry_count"],
                "generation_retries": state["generation_retry_count"],
                "platforms_requested": total_platforms,
                "platforms_successful": successful_posts,
                "success_rate": state["success_rate"],
                "total_errors": len(state["errors"]),
                "total_warnings": len(state["warnings"])
            }
            
            logger.info(
                "Metrics calculated",
                success_rate=state["success_rate"],
                duration=duration
            )
            
            return state
            
        except Exception as e:
            logger.error("Metrics calculation failed", error=str(e))
            state = add_error(state, {
                "phase": "metrics",
                "error": str(e)
            })
            return state
    
    async def handle_error_node(self, state: WorkflowState) -> WorkflowState:
        """
        Handle workflow errors and cleanup.
        """
        logger.error(
            "Workflow error handler invoked",
            workflow_id=state["workflow_id"],
            errors=state["errors"]
        )
        
        state["phase"] = WorkflowPhase.FAILED
        
        # Cleanup resources
        if self.publisher:
            await self.publisher.cleanup()
        
        return state
```

**Node Characteristics**:
- Each node is async for non-blocking execution
- Nodes update state and return modified state
- Errors are logged and added to state
- Retry logic is handled within nodes

---

### 4.5 workflows/edges.py

**Purpose**: Implement conditional routing logic between nodes

**Implementation**:

```python
from typing import Literal
from .state import WorkflowState
from config import get_settings
import structlog

logger = structlog.get_logger()

class WorkflowEdges:
    """Conditional edge routing logic."""
    
    def __init__(self):
        self.settings = get_settings()
    
    def route_after_initialize(
        self,
        state: WorkflowState
    ) -> Literal["analyze", "error"]:
        """Route after initialization."""
        if state["phase"] == "failed":
            return "error"
        return "analyze"
    
    def route_after_analysis(
        self,
        state: WorkflowState
    ) -> Literal["generate", "retry", "error"]:
        """Route after GitHub analysis."""
        if state["analysis_status"] == "completed":
            return "generate"
        
        elif state["analysis_status"] == "failed":
            if state["analysis_retry_count"] < self.settings.workflow.max_retries:
                logger.info(
                    "Retrying GitHub analysis",
                    retry_count=state["analysis_retry_count"]
                )
                return "retry"
            else:
                logger.error("Max retries exceeded for GitHub analysis")
                return "error"
        
        return "error"
    
    def route_after_generation(
        self,
        state: WorkflowState
    ) -> Literal["validate", "retry", "error"]:
        """Route after content generation."""
        if state["generation_status"] in ["completed", "partial"]:
            # Proceed even with partial content
            return "validate"
        
        elif state["generation_status"] == "failed":
            if state["generation_retry_count"] < self.settings.workflow.max_retries:
                logger.info(
                    "Retrying content generation",
                    retry_count=state["generation_retry_count"]
                )
                return "retry"
            else:
                logger.error("Max retries exceeded for content generation")
                return "error"
        
        return "error"
    
    def route_after_validation(
        self,
        state: WorkflowState
    ) -> Literal["check_limits", "error"]:
        """Route after content validation."""
        if state["validation_status"] == "completed":
            return "check_limits"
        return "error"
    
    def route_after_rate_check(
        self,
        state: WorkflowState
    ) -> Literal["publish", "queue"]:
        """Route after rate limit check."""
        if state["queued_for_later"]:
            logger.info("Workflow queued due to rate limits")
            return "queue"
        return "publish"
    
    def route_after_publishing(
        self,
        state: WorkflowState
    ) -> Literal["calculate", "retry", "error"]:
        """Route after publishing attempt."""
        if state["publishing_status"] in ["completed", "partial"]:
            # Proceed to metrics even if some platforms failed
            return "calculate"
        
        elif state["publishing_status"] == "failed":
            # Check if all platforms failed
            all_failed = all(
                p["status"] == "failed"
                for p in state["published_posts"]
            )
            
            if all_failed:
                logger.error("All platform publishing failed")
                return "error"
            else:
                # At least one succeeded
                return "calculate"
        
        return "calculate"
```

**Edge Logic**:
- Routes based on state values
- Implements retry logic within defined limits
- Handles partial successes gracefully
- Logs routing decisions for observability

---

## 5. INTEGRATIONS MODULE (integrations/)

### 5.1 integrations/__init__.py

**Content**:
```python
"""External API integrations."""

from .github import GitHubClient
from .linkedin import LinkedInClient
from .x_twitter import XClient
from .instagram import InstagramClient
from .publisher import MultiPlatformPublisher

__all__ = [
    "GitHubClient",
    "LinkedInClient",
    "XClient",
    "InstagramClient",
    "MultiPlatformPublisher"
]
```

---

### 5.2 integrations/github.py

**Purpose**: GitHub API client with rate limiting and error handling

**Responsibilities**:
- Authenticate with GitHub API
- Fetch repository metadata, commits, languages
- Fetch user profile and repository list
- Handle rate limiting and pagination
- Cache frequent requests

**Implementation**:

```python
import aiohttp
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import structlog
from config import get_settings
from utils.error_handling import with_retry, CircuitBreaker
from persistence.cache import CacheManager

logger = structlog.get_logger()

class GitHubClient:
    """
    Async GitHub API client with rate limiting and caching.
    
    Uses GitHub REST API v3 with personal access token authentication.
    """
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize GitHub client.
        
        Args:
            token: GitHub personal access token (reads from config if not provided)
        """
        self.settings = get_settings()
        self.token = token or self.settings.github.token
        self.base_url = self.settings.github.api_base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60
        )
        self.cache = CacheManager()
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
    
    async def connect(self):
        """Initialize HTTP session."""
        if not self.session:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "SocialAgentSystem/1.0"
            }
            timeout = aiohttp.ClientTimeout(total=self.settings.github.timeout)
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=timeout
            )
            await self.cache.connect()
            logger.info("GitHub client connected")
    
    async def disconnect(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
            await self.cache.disconnect()
            logger.info("GitHub client disconnected")
    
    @with_retry(max_attempts=3, backoff_factor=2)
    async def get_repository(self, repo_identifier: str) -> Dict[str, Any]:
        """
        Fetch repository metadata.
        
        Args:
            repo_identifier: "owner/repo" or full URL
            
        Returns:
            Repository metadata dictionary
        """
        # Parse identifier
        if "/" in repo_identifier and not repo_identifier.startswith("http"):
            owner, repo = repo_identifier.split("/", 1)
        else:
            # Extract from URL
            parts = repo_identifier.rstrip("/").split("/")
            owner, repo = parts[-2], parts[-1]
        
        cache_key = f"github:repo:{owner}/{repo}"
        
        # Check cache
        cached = await self.cache.get(cache_key)
        if cached:
            logger.debug("Cache hit for repository", repo=f"{owner}/{repo}")
            return cached
        
        # Fetch from API
        url = f"{self.base_url}/repos/{owner}/{repo}"
        
        async with self.circuit_breaker:
            async with self.session.get(url) as response:
                await self._check_rate_limit(response)
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Structure the response
                    result = {
                        "name": data["name"],
                        "full_name": data["full_name"],
                        "description": data.get("description"),
                        "url": data["html_url"],
                        "stars": data["stargazers_count"],
                        "forks": data["forks_count"],
                        "watchers": data["watchers_count"],
                        "open_issues": data["open_issues_count"],
                        "language": data.get("language"),
                        "created_at": data["created_at"],
                        "updated_at": data["updated_at"],
                        "pushed_at": data["pushed_at"],
                        "size": data["size"],
                        "default_branch": data["default_branch"],
                        "license": data.get("license", {}).get("name") if data.get("license") else None,
                        "topics": data.get("topics", []),
                        "has_wiki": data["has_wiki"],
                        "has_pages": data["has_pages"],
                        "archived": data["archived"]
                    }
                    
                    # Cache for 1 hour
                    await self.cache.set(cache_key, result, ttl=3600)
                    
                    logger.info("Repository fetched", repo=f"{owner}/{repo}")
                    return result
                    
                elif response.status == 404:
                    raise ValueError(f"Repository not found: {owner}/{repo}")
                else:
                    error = await response.text()
                    raise Exception(f"GitHub API error: {response.status} - {error}")
    
    @with_retry(max_attempts=3, backoff_factor=2)
    async def get_languages(self, repo_identifier: str) -> Dict[str, int]:
        """
        Fetch repository language breakdown.
        
        Args:
            repo_identifier: "owner/repo" format
            
        Returns:
            Dictionary mapping language names to byte counts
        """
        owner, repo = self._parse_repo_identifier(repo_identifier)
        cache_key = f"github:languages:{owner}/{repo}"
        
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        
        url = f"{self.base_url}/repos/{owner}/{repo}/languages"
        
        async with self.circuit_breaker:
            async with self.session.get(url) as response:
                await self._check_rate_limit(response)
                
                if response.status == 200:
                    data = await response.json()
                    await self.cache.set(cache_key, data, ttl=3600)
                    return data
                else:
                    raise Exception(f"Failed to fetch languages: {response.status}")
    
    @with_retry(max_attempts=3, backoff_factor=2)
    async def get_commits(
        self,
        repo_identifier: str,
        limit: int = 10,
        since: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch recent commits.
        
        Args:
            repo_identifier: "owner/repo" format
            limit: Maximum number of commits to fetch
            since: Only commits after this date
            
        Returns:
            List of commit dictionaries
        """
        owner, repo = self._parse_repo_identifier(repo_identifier)
        
        params = {"per_page": limit}
        if since:
            params["since"] = since.isoformat()
        
        url = f"{self.base_url}/repos/{owner}/{repo}/commits"
        
        async with self.circuit_breaker:
            async with self.session.get(url, params=params) as response:
                await self._check_rate_limit(response)
                
                if response.status == 200:
                    data = await response.json()
                    
                    commits = []
                    for commit in data:
                        commits.append({
                            "sha": commit["sha"],
                            "message": commit["commit"]["message"],
                            "author": commit["commit"]["author"]["name"],
                            "date": commit["commit"]["author"]["date"],
                            "url": commit["html_url"]
                        })
                    
                    return commits
                else:
                    raise Exception(f"Failed to fetch commits: {response.status}")
    
    @with_retry(max_attempts=3, backoff_factor=2)
    async def get_user(self, username: str) -> Dict[str, Any]:
        """
        Fetch user profile.
        
        Args:
            username: GitHub username
            
        Returns:
            User profile dictionary
        """
        cache_key = f"github:user:{username}"
        
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        
        url = f"{self.base_url}/users/{username}"
        
        async with self.circuit_breaker:
            async with self.session.get(url) as response:
                await self._check_rate_limit(response)
                
                if response.status == 200:
                    data = await response.json()
                    
                    result = {
                        "username": data["login"],
                        "name": data.get("name"),
                        "bio": data.get("bio"),
                        "location": data.get("location"),
                        "company": data.get("company"),
                        "blog": data.get("blog"),
                        "email": data.get("email"),
                        "avatar_url": data["avatar_url"],
                        "followers": data["followers"],
                        "following": data["following"],
                        "public_repos": data["public_repos"],
                        "public_gists": data["public_gists"],
                        "created_at": data["created_at"],
                        "updated_at": data["updated_at"]
                    }
                    
                    await self.cache.set(cache_key, result, ttl=3600)
                    return result
                    
                elif response.status == 404:
                    raise ValueError(f"User not found: {username}")
                else:
                    error = await response.text()
                    raise Exception(f"GitHub API error: {response.status} - {error}")
    
    @with_retry(max_attempts=3, backoff_factor=2)
    async def get_user_repos(
        self,
        username: str,
        limit: int = 20,
        sort: str = "updated"
    ) -> List[Dict[str, Any]]:
        """
        Fetch user's repositories.
        
        Args:
            username: GitHub username
            limit: Maximum number of repos to fetch
            sort: Sort order (created, updated, pushed, full_name)
            
        Returns:
            List of repository dictionaries
        """
        params = {
            "per_page": limit,
            "sort": sort,
            "direction": "desc"
        }
        
        url = f"{self.base_url}/users/{username}/repos"
        
        async with self.circuit_breaker:
            async with self.session.get(url, params=params) as response:
                await self._check_rate_limit(response)
                
                if response.status == 200:
                    data = await response.json()
                    
                    repos = []
                    for repo in data:
                        repos.append({
                            "name": repo["name"],
                            "full_name": repo["full_name"],
                            "description": repo.get("description"),
                            "url": repo["html_url"],
                            "stars": repo["stargazers_count"],
                            "forks": repo["forks_count"],
                            "language": repo.get("language"),
                            "updated_at": repo["updated_at"]
                        })
                    
                    return repos
                else:
                    raise Exception(f"Failed to fetch user repos: {response.status}")
    
    async def get_rate_limit(self) -> Dict[str, Any]:
        """
        Check current rate limit status.
        
        Returns:
            Rate limit information
        """
        url = f"{self.base_url}/rate_limit"
        
        async with self.session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data["rate"]
            else:
                raise Exception(f"Failed to check rate limit: {response.status}")
    
    async def _check_rate_limit(self, response: aiohttp.ClientResponse):
        """Check rate limit from response headers."""
        remaining = response.headers.get("X-RateLimit-Remaining")
        reset_time = response.headers.get("X-RateLimit-Reset")
        
        if remaining and int(remaining) < 100:
            logger.warning(
                "GitHub rate limit low",
                remaining=remaining,
                reset_time=reset_time
            )
        
        if remaining and int(remaining) == 0:
            # Calculate wait time
            reset_timestamp = int(reset_time)
            wait_time = reset_timestamp - int(datetime.now().timestamp())
            logger.error(
                "GitHub rate limit exceeded",
                wait_seconds=wait_time
            )
            raise Exception(f"Rate limit exceeded. Reset in {wait_time} seconds.")
    
    def _parse_repo_identifier(self, identifier: str) -> tuple:
        """Parse repository identifier into owner and repo."""
        if "/" in identifier and not identifier.startswith("http"):
            return identifier.split("/", 1)
        else:
            parts = identifier.rstrip("/").split("/")
            return parts[-2], parts[-1]
```

**Dependencies**:
- `aiohttp`: Async HTTP client
- `config`: Configuration access
- `utils.error_handling`: Retry decorator and circuit breaker
- `persistence.cache`: Redis caching

**Rate Limiting**:
- Monitor `X-RateLimit-Remaining` header
- Warn when below 100 requests remaining
- Raise exception when limit reached
- Cache responses to reduce API calls

---

### 5.3 integrations/linkedin.py

**Purpose**: LinkedIn API client for content publishing

**Implementation** (key methods):

```python
import aiohttp
from typing import Dict, Any, Optional
import structlog
from config import get_settings
from utils.error_handling import with_retry

logger = structlog.get_logger()

class LinkedInClient:
    """
    LinkedIn API client for publishing posts.
    
    Uses LinkedIn API v202501 with OAuth 2.0 authentication.
    """
    
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None
    ):
        self.settings = get_settings()
        self.client_id = client_id or self.settings.linkedin.client_id
        self.client_secret = client_secret or self.settings.linkedin.client_secret
        self.access_token = access_token or self.settings.linkedin.access_token
        self.refresh_token = refresh_token or self.settings.linkedin.refresh_token
        self.base_url = "https://api.linkedin.com/v2"
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def connect(self):
        """Initialize HTTP session."""
        if not self.session:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            self.session = aiohttp.ClientSession(headers=headers)
            logger.info("LinkedIn client connected")
    
    async def disconnect(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def verify_token(self) -> bool:
        """Verify access token is valid."""
        url = f"{self.base_url}/me"
        
        try:
            async with self.session.get(url) as response:
                return response.status == 200
        except Exception as e:
            logger.error("Token verification failed", error=str(e))
            return False
    
    @with_retry(max_attempts=3, backoff_factor=2)
    async def create_post(
        self,
        text: str,
        visibility: str = "PUBLIC"
    ) -> Dict[str, Any]:
        """
        Create a LinkedIn post.
        
        Args:
            text: Post content
            visibility: Post visibility (PUBLIC, CONNECTIONS)
            
        Returns:
            Post creation response with post ID
        """
        # Get user URN
        user_urn = await self._get_user_urn()
        
        # Construct post payload
        payload = {
            "author": user_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility
            }
        }
        
        url = f"{self.base_url}/ugcPosts"
        
        async with self.session.post(url, json=payload) as response:
            if response.status in [200, 201]:
                data = await response.json()
                post_id = data.get("id")
                
                logger.info("LinkedIn post created", post_id=post_id)
                
                return {
                    "post_id": post_id,
                    "status": "success",
                    "url": f"https://www.linkedin.com/feed/update/{post_id}"
                }
            else:
                error = await response.text()
                logger.error("LinkedIn post failed", status=response.status, error=error)
                raise Exception(f"LinkedIn API error: {response.status} - {error}")
    
    async def _get_user_urn(self) -> str:
        """Get user URN for API calls."""
        url = f"{self.base_url}/me"
        
        async with self.session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return f"urn:li:person:{data['id']}"
            else:
                raise Exception("Failed to get user URN")
    
    async def refresh_access_token(self) -> str:
        """
        Refresh the access token using refresh token.
        
        Returns:
            New access token
        """
        url = "https://www.linkedin.com/oauth/v2/accessToken"
        
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    new_token = data["access_token"]
                    self.access_token = new_token
                    
                    # Update session headers
                    if self.session:
                        self.session.headers["Authorization"] = f"Bearer {new_token}"
                    
                    logger.info("LinkedIn access token refreshed")
                    return new_token
                else:
                    error = await response.text()
                    raise Exception(f"Token refresh failed: {error}")
```

**Key Features**:
- OAuth 2.0 token management
- Automatic token refresh
- Post creation with visibility control
- Error handling and retry logic

---

### 5.4 integrations/x_twitter.py

**Purpose**: X (Twitter) API client for thread publishing

**Implementation** (key methods):

```python
import aiohttp
from typing import Dict, Any, List, Optional
import structlog
from config import get_settings
from utils.error_handling import with_retry

logger = structlog.get_logger()

class XClient:
    """
    X (Twitter) API v2 client for publishing tweets and threads.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        access_token_secret: Optional[str] = None,
        bearer_token: Optional[str] = None
    ):
        self.settings = get_settings()
        self.api_key = api_key or self.settings.x.api_key
        self.api_secret = api_secret or self.settings.x.api_secret
        self.access_token = access_token or self.settings.x.access_token
        self.access_token_secret = access_token_secret or self.settings.x.access_token_secret
        self.bearer_token = bearer_token or self.settings.x.bearer_token
        self.base_url = "https://api.twitter.com/2"
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def connect(self):
        """Initialize HTTP session."""
        if not self.session:
            headers = {
                "Authorization": f"Bearer {self.bearer_token}",
                "Content-Type": "application/json"
            }
            self.session = aiohttp.ClientSession(headers=headers)
            logger.info("X client connected")
    
    async def disconnect(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def verify_credentials(self) -> bool:
        """Verify API credentials are valid."""
        url = f"{self.base_url}/users/me"
        
        try:
            async with self.session.get(url) as response:
                return response.status == 200
        except Exception as e:
            logger.error("Credentials verification failed", error=str(e))
            return False
    
    @with_retry(max_attempts=3, backoff_factor=2)
    async def create_tweet(
        self,
        text: str,
        reply_to_tweet_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a single tweet.
        
        Args:
            text: Tweet content (max 280 characters)
            reply_to_tweet_id: ID of tweet to reply to (for threading)
            
        Returns:
            Tweet creation response
        """
        if len(text) > 280:
            raise ValueError(f"Tweet text exceeds 280 characters: {len(text)}")
        
        payload = {"text": text}
        
        if reply_to_tweet_id:
            payload["reply"] = {"in_reply_to_tweet_id": reply_to_tweet_id}
        
        url = f"{self.base_url}/tweets"
        
        async with self.session.post(url, json=payload) as response:
            if response.status in [200, 201]:
                data = await response.json()
                tweet_id = data["data"]["id"]
                
                logger.info("Tweet created", tweet_id=tweet_id)
                
                return {
                    "tweet_id": tweet_id,
                    "status": "success",
                    "url": f"https://twitter.com/i/web/status/{tweet_id}"
                }
            else:
                error = await response.text()
                logger.error("Tweet creation failed", status=response.status, error=error)
                raise Exception(f"X API error: {response.status} - {error}")
    
    async def create_thread(
        self,
        tweets: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create a thread of tweets.
        
        Args:
            tweets: List of tweet dictionaries with 'text' and 'order'
            
        Returns:
            Thread creation results
        """
        if len(tweets) > 10:
            raise ValueError(f"Thread exceeds maximum of 10 tweets: {len(tweets)}")
        
        # Sort by order
        sorted_tweets = sorted(tweets, key=lambda t: t["order"])
        
        tweet_ids = []
        previous_tweet_id = None
        
        for tweet in sorted_tweets:
            try:
                result = await self.create_tweet(
                    text=tweet["text"],
                    reply_to_tweet_id=previous_tweet_id
                )
                
                tweet_ids.append(result["tweet_id"])
                previous_tweet_id = result["tweet_id"]
                
            except Exception as e:
                logger.error(
                    "Failed to create tweet in thread",
                    order=tweet["order"],
                    error=str(e)
                )
                # Stop thread creation on error
                break
        
        logger.info("Thread created", tweet_count=len(tweet_ids))
        
        return {
            "tweet_ids": tweet_ids,
            "thread_url": f"https://twitter.com/i/web/status/{tweet_ids[0]}" if tweet_ids else None,
            "status": "success" if len(tweet_ids) == len(sorted_tweets) else "partial"
        }
```

**Thread Creation**:
- Posts tweets sequentially in thread
- Uses reply_to mechanism for threading
- Validates character limits
- Handles partial thread failures

---

### 5.5 integrations/instagram.py

**Purpose**: Instagram Graph API client for media publishing

**Implementation** (key methods):

```python
import aiohttp
from typing import Dict, Any, Optional
import structlog
from config import get_settings
from utils.error_handling import with_retry

logger = structlog.get_logger()

class InstagramClient:
    """
    Instagram Graph API client for media publishing.
    
    Requires Instagram Business Account linked to Facebook Page.
    """
    
    def __init__(
        self,
        app_id: Optional[str] = None,
        app_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        account_id: Optional[str] = None
    ):
        self.settings = get_settings()
        self.app_id = app_id or self.settings.instagram.app_id
        self.app_secret = app_secret or self.settings.instagram.app_secret
        self.access_token = access_token or self.settings.instagram.access_token
        self.account_id = account_id or self.settings.instagram.account_id
        self.base_url = "https://graph.facebook.com/v24.0"
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def connect(self):
        """Initialize HTTP session."""
        if not self.session:
            self.session = aiohttp.ClientSession()
            logger.info("Instagram client connected")
    
    async def disconnect(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def verify_token(self) -> bool:
        """Verify access token is valid."""
        url = f"{self.base_url}/me"
        params = {"access_token": self.access_token}
        
        try:
            async with self.session.get(url, params=params) as response:
                return response.status == 200
        except Exception as e:
            logger.error("Token verification failed", error=str(e))
            return False
    
    @with_retry(max_attempts=3, backoff_factor=2)
    async def create_media_container(
        self,
        image_url: str,
        caption: str
    ) -> str:
        """
        Create Instagram media container.
        
        Args:
            image_url: Publicly accessible image URL
            caption: Post caption (max 2200 characters)
            
        Returns:
            Container ID
        """
        if len(caption) > 2200:
            raise ValueError(f"Caption exceeds 2200 characters: {len(caption)}")
        
        url = f"{self.base_url}/{self.account_id}/media"
        
        payload = {
            "image_url": image_url,
            "caption": caption,
            "access_token": self.access_token
        }
        
        async with self.session.post(url, data=payload) as response:
            if response.status in [200, 201]:
                data = await response.json()
                container_id = data["id"]
                
                logger.info("Media container created", container_id=container_id)
                return container_id
            else:
                error = await response.text()
                raise Exception(f"Container creation failed: {response.status} - {error}")
    
    @with_retry(max_attempts=3, backoff_factor=2)
    async def publish_media_container(
        self,
        container_id: str
    ) -> Dict[str, Any]:
        """
        Publish Instagram media container.
        
        Args:
            container_id: Container ID from create_media_container
            
        Returns:
            Publication response with media ID
        """
        url = f"{self.base_url}/{self.account_id}/media_publish"
        
        payload = {
            "creation_id": container_id,
            "access_token": self.access_token
        }
        
        async with self.session.post(url, data=payload) as response:
            if response.status in [200, 201]:
                data = await response.json()
                media_id = data["id"]
                
                logger.info("Media published", media_id=media_id)
                
                return {
                    "media_id": media_id,
                    "status": "success",
                    "url": f"https://www.instagram.com/p/{media_id}"
                }
            else:
                error = await response.text()
                raise Exception(f"Media publication failed: {response.status} - {error}")
    
    async def create_post(
        self,
        image_url: str,
        caption: str
    ) -> Dict[str, Any]:
        """
        Create and publish Instagram post (convenience method).
        
        Args:
            image_url: Publicly accessible image URL
            caption: Post caption
            
        Returns:
            Publication response
        """
        # Create container
        container_id = await self.create_media_container(image_url, caption)
        
        # Wait a moment for processing
        await asyncio.sleep(2)
        
        # Publish container
        result = await self.publish_media_container(container_id)
        
        return result
```

**Two-Step Process**:
1. Create media container with image URL and caption
2. Publish the container to Instagram

**Image Requirements**:
- Image must be publicly accessible via HTTPS
- Supported formats: JPG, PNG
- Aspect ratio constraints apply

---

### 5.6 integrations/publisher.py

**Purpose**: Multi-platform publishing coordinator

**Responsibilities**:
- Coordinate publishing across all platforms
- Handle parallel publishing with error isolation
- Manage rate limiting checks
- Aggregate publishing results

**Implementation**:

```python
import asyncio
from typing import Dict, Any, List, Optional
import structlog
from .linkedin import LinkedInClient
from .x_twitter import XClient
from .instagram import InstagramClient
from config import get_settings
from persistence.cache import CacheManager

logger = structlog.get_logger()

class MultiPlatformPublisher:
    """
    Coordinates content publishing across multiple social media platforms.
    
    Publishes to LinkedIn, X (Twitter), and Instagram in parallel while
    handling errors and rate limits per platform.
    """
    
    def __init__(self, platforms: List[str], dry_run: bool = False):
        """
        Initialize multi-platform publisher.
        
        Args:
            platforms: List of platforms to publish to
            dry_run: If True, skip actual API calls
        """
        self.settings = get_settings()
        self.platforms = platforms
        self.dry_run = dry_run
        self.clients: Dict[str, Any] = {}
        self.cache = CacheManager()
        
    async def initialize(self):
        """Initialize platform clients."""
        await self.cache.connect()
        
        if "linkedin" in self.platforms:
            self.clients["linkedin"] = LinkedInClient()
            await self.clients["linkedin"].connect()
        
        if "twitter" in self.platforms or "x" in self.platforms:
            self.clients["x"] = XClient()
            await self.clients["x"].connect()
        
        if "instagram" in self.platforms:
            self.clients["instagram"] = InstagramClient()
            await self.clients["instagram"].connect()
        
        logger.info("Multi-platform publisher initialized", platforms=self.platforms)
    
    async def cleanup(self):
        """Cleanup platform clients."""
        for client in self.clients.values():
            await client.disconnect()
        
        await self.cache.disconnect()
        logger.info("Multi-platform publisher cleaned up")
    
    async def check_rate_limits_all(self) -> Dict[str, Any]:
        """
        Check rate limits for all platforms.
        
        Returns:
            Dictionary of rate limit status per platform
        """
        rate_limits = {}
        
        for platform in self.platforms:
            try:
                usage = await self._get_rate_limit_usage(platform)
                remaining = await self._get_remaining_quota(platform)
                
                rate_limits[platform] = {
                    "usage_today": usage,
                    "remaining_today": remaining,
                    "would_exceed": remaining <= 0
                }
                
            except Exception as e:
                logger.error(f"Failed to check {platform} rate limit", error=str(e))
                rate_limits[platform] = {
                    "error": str(e),
                    "would_exceed": False  # Assume OK if check fails
                }
        
        return rate_limits
    
    async def publish_all(
        self,
        content_drafts: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Publish content to all platforms in parallel.
        
        Args:
            content_drafts: Dictionary of platform-specific content
            
        Returns:
            Publishing results for all platforms
        """
        if self.dry_run:
            logger.info("DRY RUN: Skipping actual publishing")
            return self._mock_publish_results(content_drafts)
        
        # Create publishing tasks
        tasks = {}
        
        if "linkedin" in content_drafts:
            tasks["linkedin"] = self._publish_linkedin(content_drafts["linkedin"])
        
        if "twitter" in content_drafts or "x" in content_drafts:
            content = content_drafts.get("twitter") or content_drafts.get("x")
            tasks["x"] = self._publish_x(content)
        
        if "instagram" in content_drafts:
            tasks["instagram"] = self._publish_instagram(content_drafts["instagram"])
        
        # Execute all publishing tasks in parallel
        results = await asyncio.gather(
            *tasks.values(),
            return_exceptions=True
        )
        
        # Aggregate results
        posts = []
        errors = []
        
        for platform, result in zip(tasks.keys(), results):
            if isinstance(result, Exception):
                logger.error(f"{platform} publishing failed", error=str(result))
                errors.append(f"{platform}: {str(result)}")
                posts.append({
                    "platform": platform,
                    "status": "failed",
                    "error": str(result),
                    "post_id": None,
                    "timestamp": None,
                    "retry_count": 0
                })
            else:
                posts.append({
                    "platform": platform,
                    "status": result["status"],
                    "post_id": result.get("post_id") or result.get("tweet_ids", [None])[0],
                    "url": result.get("url") or result.get("thread_url"),
                    "timestamp": datetime.utcnow().isoformat(),
                    "retry_count": 0,
                    "error": None
                })
        
        logger.info(
            "Publishing completed",
            successful=len([p for p in posts if p["status"] == "success"]),
            failed=len(errors)
        )
        
        return {
            "posts": posts,
            "errors": errors
        }
    
    async def _publish_linkedin(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Publish to LinkedIn."""
        logger.info("Publishing to LinkedIn")
        
        client = self.clients["linkedin"]
        
        # Construct post text with hashtags
        text = content["text"]
        hashtags = " ".join(f"#{tag}" for tag in content.get("hashtags", []))
        full_text = f"{text}\n\n{hashtags}"
        
        result = await client.create_post(text=full_text)
        
        # Update rate limit tracking
        await self._increment_rate_limit_usage("linkedin")
        
        return result
    
    async def _publish_x(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Publish to X (Twitter)."""
        logger.info("Publishing to X")
        
        client = self.clients["x"]
        
        tweets = content["tweets"]
        
        if len(tweets) == 1:
            # Single tweet
            result = await client.create_tweet(text=tweets[0]["text"])
        else:
            # Thread
            result = await client.create_thread(tweets=tweets)
        
        # Update rate limit tracking
        await self._increment_rate_limit_usage("x")
        
        return result
    
    async def _publish_instagram(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Publish to Instagram."""
        logger.info("Publishing to Instagram")
        
        client = self.clients["instagram"]
        
        # Instagram requires an image URL
        # In production, this would be generated from image_description
        # For now, we'll need to handle image generation separately
        
        # Placeholder: This should be replaced with actual image generation/upload
        image_url = "https://placeholder.com/instagram-post.jpg"
        
        caption = content["caption"]
        hashtags = " ".join(f"#{tag}" for tag in content.get("hashtags", []))
        full_caption = f"{caption}\n\n{hashtags}"
        
        result = await client.create_post(
            image_url=image_url,
            caption=full_caption
        )
        
        # Update rate limit tracking
        await self._increment_rate_limit_usage("instagram")
        
        return result
    
    async def _get_rate_limit_usage(self, platform: str) -> int:
        """Get today's API usage count for platform."""
        date_key = datetime.utcnow().strftime("%Y-%m-%d")
        cache_key = f"rate_limit:{platform}:{date_key}"
        
        usage = await self.cache.get(cache_key)
        return int(usage) if usage else 0
    
    async def _get_remaining_quota(self, platform: str) -> int:
        """Get remaining quota for platform today."""
        limits = {
            "linkedin": self.settings.linkedin.rate_limit_requests,
            "x": self.settings.x.rate_limit_posts,
            "instagram": self.settings.instagram.rate_limit_posts
        }
        
        limit = limits.get(platform, 100)
        usage = await self._get_rate_limit_usage(platform)
        
        return max(0, limit - usage)
    
    async def _increment_rate_limit_usage(self, platform: str):
        """Increment rate limit usage counter."""
        date_key = datetime.utcnow().strftime("%Y-%m-%d")
        cache_key = f"rate_limit:{platform}:{date_key}"
        
        # Increment with expiry of 24 hours
        await self.cache.incr(cache_key, ttl=86400)
    
    def _mock_publish_results(self, content_drafts: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock results for dry run mode."""
        posts = []
        
        for platform in content_drafts.keys():
            posts.append({
                "platform": platform,
                "status": "success",
                "post_id": f"mock-{platform}-{datetime.utcnow().timestamp()}",
                "url": f"https://mock-url.com/{platform}",
                "timestamp": datetime.utcnow().isoformat(),
                "retry_count": 0,
                "error": None
            })
        
        return {
            "posts": posts,
            "errors": []
        }
```

**Parallel Publishing**:
- Uses `asyncio.gather` for concurrent execution
- Isolates errors per platform
- Continues even if one platform fails
- Tracks rate limits using Redis cache

---

---

## 6. TOOLS MODULE (tools/)

### 6.1 tools/__init__.py

**Content**:
```python
"""Tool implementations for agents."""

from .github_tools import create_github_tools
from .llm_tools import create_llm_tools

__all__ = ["create_github_tools", "create_llm_tools"]
```

---

### 6.2 tools/github_tools.py

**Purpose**: LangChain-compatible GitHub analysis tools

**Note**: This file exports tools for use by CrewAI agents. Implementation details are already covered in `crews/github_crew/tools.py`. This module provides any additional GitHub-specific tools not used by agents.

**Implementation**:

```python
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
```

---

### 6.3 tools/llm_tools.py

**Purpose**: LLM-powered analysis and processing tools

**Responsibilities**:
- Text summarization
- Sentiment analysis
- Entity extraction
- Content quality assessment

**Implementation**:

```python
from langchain.tools import BaseTool
from langchain_ollama import ChatOllama
from typing import Dict, Any, List
from pydantic import Field
from config import get_settings

class TextSummarizationTool(BaseTool):
    """Tool to summarize long text content."""
    
    name: str = "text_summarizer"
    description: str = (
        "Summarizes long text content into concise, key-point format. "
        "Useful for condensing README files, documentation, or long descriptions."
    )
    llm: ChatOllama = Field(default_factory=lambda: ChatOllama(
        model=get_settings().llm.analysis_model,
        temperature=0.3
    ))
    
    def _run(self, text: str, max_points: int = 5) -> str:
        """Summarize text into key points."""
        prompt = f"""
        Summarize the following text into {max_points} key points:
        
        {text}
        
        Return only the key points in a numbered list.
        """
        
        response = self.llm.invoke(prompt)
        return response.content

class SentimentAnalysisTool(BaseTool):
    """Tool to analyze sentiment of text."""
    
    name: str = "sentiment_analyzer"
    description: str = (
        "Analyzes the sentiment of text content and returns "
        "positive, negative, or neutral classification with confidence score."
    )
    llm: ChatOllama = Field(default_factory=lambda: ChatOllama(
        model=get_settings().llm.analysis_model,
        temperature=0.1
    ))
    
    def _run(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text."""
        prompt = f"""
        Analyze the sentiment of the following text.
        Return JSON format:
        {{
            "sentiment": "positive|negative|neutral",
            "confidence": 0.0-1.0,
            "reasoning": "brief explanation"
        }}
        
        Text: {text}
        """
        
        response = self.llm.invoke(prompt)
        # Parse JSON from response
        import json
        try:
            return json.loads(response.content)
        except:
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "reasoning": "Unable to parse sentiment"
            }

class EntityExtractionTool(BaseTool):
    """Tool to extract entities from text."""
    
    name: str = "entity_extractor"
    description: str = (
        "Extracts key entities (technologies, companies, people, concepts) "
        "from text content."
    )
    llm: ChatOllama = Field(default_factory=lambda: ChatOllama(
        model=get_settings().llm.analysis_model,
        temperature=0.2
    ))
    
    def _run(self, text: str) -> List[Dict[str, str]]:
        """Extract entities from text."""
        prompt = f"""
        Extract key entities from the following text.
        Categorize them as: technology, company, person, concept, or other.
        
        Return JSON array format:
        [
            {{"entity": "Python", "type": "technology"}},
            {{"entity": "FastAPI", "type": "technology"}}
        ]
        
        Text: {text}
        """
        
        response = self.llm.invoke(prompt)
        # Parse JSON from response
        import json
        try:
            return json.loads(response.content)
        except:
            return []

class ContentQualityTool(BaseTool):
    """Tool to assess content quality."""
    
    name: str = "content_quality_assessor"
    description: str = (
        "Assesses the quality of generated content based on clarity, "
        "engagement, professionalism, and platform appropriateness."
    )
    llm: ChatOllama = Field(default_factory=lambda: ChatOllama(
        model=get_settings().llm.content_model,
        temperature=0.3
    ))
    
    def _run(self, content: str, platform: str) -> Dict[str, Any]:
        """Assess content quality."""
        prompt = f"""
        Assess the quality of this {platform} content.
        
        Content: {content}
        
        Return JSON format:
        {{
            "overall_score": 0-100,
            "clarity_score": 0-100,
            "engagement_score": 0-100,
            "professionalism_score": 0-100,
            "platform_fit_score": 0-100,
            "suggestions": ["suggestion 1", "suggestion 2"],
            "strengths": ["strength 1", "strength 2"]
        }}
        """
        
        response = self.llm.invoke(prompt)
        # Parse JSON from response
        import json
        try:
            return json.loads(response.content)
        except:
            return {
                "overall_score": 50,
                "suggestions": ["Unable to assess quality"]
            }

def create_llm_tools() -> List[BaseTool]:
    """
    Create all LLM-powered tools.
    
    Returns:
        List of LLM tools
    """
    return [
        TextSummarizationTool(),
        SentimentAnalysisTool(),
        EntityExtractionTool(),
        ContentQualityTool()
    ]
```

**Usage Context**:
- These tools can be added to agents for enhanced capabilities
- Useful for content validation and quality checks
- Can be used in post-generation refinement

---

## 7. PERSISTENCE MODULE (persistence/)

### 7.1 persistence/__init__.py

**Content**:
```python
"""Data persistence and caching."""

from .database import DatabaseManager, get_db_manager
from .state_manager import StateManager
from .cache import CacheManager

__all__ = [
    "DatabaseManager",
    "get_db_manager",
    "StateManager",
    "CacheManager"
]
```

---

### 7.2 persistence/database.py

**Purpose**: PostgreSQL database connection and management

**Responsibilities**:
- Manage database connections with connection pooling
- Provide async database operations
- Handle database migrations
- Support checkpoint storage for LangGraph

**Implementation**:

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Integer, DateTime, JSON, Float, Boolean, Text
from typing import Optional, Dict, Any
from datetime import datetime
import structlog
from config import get_settings

logger = structlog.get_logger()

Base = declarative_base()

# Database Models

class WorkflowRun(Base):
    """Workflow execution record."""
    
    __tablename__ = "workflow_runs"
    
    id = Column(String, primary_key=True)
    status = Column(String, nullable=False)
    phase = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)
    
    github_repo_url = Column(String, nullable=False)
    github_username = Column(String, nullable=False)
    platforms = Column(JSON, nullable=False)
    dry_run = Column(Boolean, default=False)
    
    analysis_results = Column(JSON)
    content_drafts = Column(JSON)
    published_posts = Column(JSON)
    
    success_rate = Column(Float, default=0.0)
    total_duration = Column(Float)
    execution_metrics = Column(JSON)
    
    errors = Column(JSON)
    warnings = Column(JSON)

class PublishedPost(Base):
    """Published social media post record."""
    
    __tablename__ = "published_posts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    workflow_id = Column(String, nullable=False, index=True)
    platform = Column(String, nullable=False)
    post_id = Column(String)
    status = Column(String, nullable=False)
    content = Column(Text)
    url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    error_message = Column(Text)

class RateLimitLog(Base):
    """Rate limit usage tracking."""
    
    __tablename__ = "rate_limit_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    platform = Column(String, nullable=False, index=True)
    date = Column(String, nullable=False, index=True)  # YYYY-MM-DD format
    requests_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Database Manager

class DatabaseManager:
    """
    Manages PostgreSQL database connections and operations.
    
    Provides async database access with connection pooling and
    supports LangGraph checkpoint storage.
    """
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize database manager.
        
        Args:
            database_url: Database connection URL (uses config if not provided)
        """
        self.settings = get_settings()
        self.database_url = database_url or self.settings.database.url
        
        # Create async engine
        self.engine = create_async_engine(
            self.database_url,
            pool_size=self.settings.database.pool_size,
            max_overflow=self.settings.database.max_overflow,
            pool_timeout=self.settings.database.pool_timeout,
            echo=self.settings.database.echo
        )
        
        # Create session factory
        self.SessionLocal = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        self._connected = False
    
    async def connect(self):
        """Initialize database connection and create tables."""
        if not self._connected:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            self._connected = True
            logger.info("Database connected", url=self.database_url)
    
    async def disconnect(self):
        """Close database connection."""
        if self._connected:
            await self.engine.dispose()
            self._connected = False
            logger.info("Database disconnected")
    
    async def get_session(self) -> AsyncSession:
        """Get database session."""
        return self.SessionLocal()
    
    async def save_workflow_run(self, workflow_data: Dict[str, Any]):
        """Save workflow run to database."""
        async with self.SessionLocal() as session:
            workflow = WorkflowRun(**workflow_data)
            session.add(workflow)
            await session.commit()
            logger.info("Workflow run saved", workflow_id=workflow_data["id"])
    
    async def update_workflow_run(self, workflow_id: str, updates: Dict[str, Any]):
        """Update workflow run."""
        async with self.SessionLocal() as session:
            result = await session.execute(
                f"SELECT * FROM workflow_runs WHERE id = :id",
                {"id": workflow_id}
            )
            workflow = result.scalar_one_or_none()
            
            if workflow:
                for key, value in updates.items():
                    setattr(workflow, key, value)
                
                workflow.updated_at = datetime.utcnow()
                await session.commit()
                logger.info("Workflow run updated", workflow_id=workflow_id)
    
    async def get_workflow_run(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow run by ID."""
        async with self.SessionLocal() as session:
            result = await session.execute(
                f"SELECT * FROM workflow_runs WHERE id = :id",
                {"id": workflow_id}
            )
            workflow = result.scalar_one_or_none()
            
            if workflow:
                return {
                    "id": workflow.id,
                    "status": workflow.status,
                    "phase": workflow.phase,
                    "created_at": workflow.created_at.isoformat(),
                    "analysis_results": workflow.analysis_results,
                    "content_drafts": workflow.content_drafts,
                    "published_posts": workflow.published_posts
                }
            return None
    
    async def save_published_post(self, post_data: Dict[str, Any]):
        """Save published post record."""
        async with self.SessionLocal() as session:
            post = PublishedPost(**post_data)
            session.add(post)
            await session.commit()
            logger.info("Published post saved", platform=post_data["platform"])
    
    async def log_rate_limit(self, platform: str, date: str):
        """Log rate limit usage."""
        async with self.SessionLocal() as session:
            result = await session.execute(
                f"SELECT * FROM rate_limit_logs WHERE platform = :platform AND date = :date",
                {"platform": platform, "date": date}
            )
            log = result.scalar_one_or_none()
            
            if log:
                log.requests_count += 1
                log.updated_at = datetime.utcnow()
            else:
                log = RateLimitLog(
                    platform=platform,
                    date=date,
                    requests_count=1
                )
                session.add(log)
            
            await session.commit()

# Singleton instance
_db_manager: Optional[DatabaseManager] = None

def get_db_manager() -> DatabaseManager:
    """Get database manager singleton."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager
```

**Database Schema**:
- `workflow_runs`: Complete workflow execution records
- `published_posts`: Individual post publication records
- `rate_limit_logs`: Rate limit usage tracking per platform/day

**Connection Pooling**:
- Configurable pool size and max overflow
- Async connections for non-blocking operations
- Automatic connection management

---

### 7.3 persistence/state_manager.py

**Purpose**: LangGraph state persistence and checkpointing

**Responsibilities**:
- Save workflow state at checkpoints
- Load state for workflow resumption
- Support LangGraph's PostgresSaver interface
- Handle state serialization/deserialization

**Implementation**:

```python
from langgraph.checkpoint.postgres import PostgresSaver
from typing import Dict, Any, Optional
import structlog
from .database import DatabaseManager

logger = structlog.get_logger()

class StateManager:
    """
    Manages workflow state persistence for LangGraph.
    
    Integrates with LangGraph's PostgresSaver for checkpoint storage
    and provides additional state management capabilities.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize state manager.
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
        self.checkpointer: Optional[PostgresSaver] = None
    
    async def initialize(self):
        """Initialize checkpointer."""
        # Create PostgresSaver instance for LangGraph
        self.checkpointer = PostgresSaver.from_conn_string(
            self.db_manager.database_url
        )
        await self.checkpointer.setup()
        logger.info("State manager initialized with PostgreSQL checkpointer")
    
    def get_checkpointer(self) -> PostgresSaver:
        """
        Get LangGraph checkpointer instance.
        
        Returns:
            PostgresSaver for use with LangGraph workflows
        """
        if not self.checkpointer:
            raise RuntimeError("State manager not initialized. Call initialize() first.")
        return self.checkpointer
    
    async def save_checkpoint(
        self,
        workflow_id: str,
        state: Dict[str, Any],
        checkpoint_name: str
    ):
        """
        Save a named checkpoint (in addition to automatic LangGraph checkpoints).
        
        Args:
            workflow_id: Workflow identifier
            state: Current workflow state
            checkpoint_name: Human-readable checkpoint name
        """
        # Save to workflow_runs table
        await self.db_manager.update_workflow_run(
            workflow_id=workflow_id,
            updates={
                "phase": state.get("phase"),
                "analysis_results": state.get("analysis_results"),
                "content_drafts": state.get("content_drafts"),
                "published_posts": state.get("published_posts"),
                "execution_metrics": state.get("execution_metrics")
            }
        )
        
        logger.info(
            "Checkpoint saved",
            workflow_id=workflow_id,
            checkpoint=checkpoint_name
        )
    
    async def load_checkpoint(
        self,
        workflow_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Load the latest checkpoint for a workflow.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            Workflow state if found, None otherwise
        """
        workflow_data = await self.db_manager.get_workflow_run(workflow_id)
        
        if workflow_data:
            logger.info("Checkpoint loaded", workflow_id=workflow_id)
            return workflow_data
        
        logger.warning("No checkpoint found", workflow_id=workflow_id)
        return None
    
    async def list_checkpoints(self, workflow_id: str) -> list:
        """
        List all checkpoints for a workflow.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            List of checkpoint metadata
        """
        # Query checkpointer for all checkpoints
        # Implementation depends on PostgresSaver API
        pass
    
    async def cleanup_old_checkpoints(self, days: int = 30):
        """
        Clean up checkpoints older than specified days.
        
        Args:
            days: Number of days to retain checkpoints
        """
        # Implementation for cleanup
        logger.info(f"Cleaning up checkpoints older than {days} days")
```

**Checkpointing Strategy**:
- Automatic checkpoints via LangGraph at node boundaries
- Manual checkpoints at phase transitions
- Supports workflow pause/resume
- Enables debugging and recovery

---

### 7.4 persistence/cache.py

**Purpose**: Redis cache manager for rate limiting and data caching

**Implementation**:

```python
import redis.asyncio as aioredis
from typing import Optional, Any
import json
import structlog
from config import get_settings

logger = structlog.get_logger()

class CacheManager:
    """
    Redis cache manager for rate limiting and data caching.
    
    Provides async Redis operations with automatic serialization.
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize cache manager.
        
        Args:
            redis_url: Redis connection URL (uses config if not provided)
        """
        self.settings = get_settings()
        self.redis_url = redis_url or self.settings.redis.url
        self.client: Optional[aioredis.Redis] = None
    
    async def connect(self):
        """Connect to Redis."""
        if not self.client:
            self.client = await aioredis.from_url(
                self.redis_url,
                max_connections=self.settings.redis.max_connections,
                decode_responses=self.settings.redis.decode_responses
            )
            logger.info("Redis cache connected")
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.client:
            await self.client.close()
            self.client = None
            logger.info("Redis cache disconnected")
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        value = await self.client.get(key)
        
        if value:
            try:
                # Try to deserialize JSON
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                # Return as string if not JSON
                return value
        
        return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ):
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None for no expiry)
        """
        # Serialize value
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        elif not isinstance(value, (str, bytes)):
            value = str(value)
        
        if ttl:
            await self.client.setex(key, ttl, value)
        else:
            await self.client.set(key, value)
    
    async def delete(self, key: str):
        """Delete key from cache."""
        await self.client.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        return bool(await self.client.exists(key))
    
    async def incr(self, key: str, ttl: Optional[int] = None) -> int:
        """
        Increment counter.
        
        Args:
            key: Counter key
            ttl: Set expiry if this is the first increment
            
        Returns:
            New counter value
        """
        value = await self.client.incr(key)
        
        # Set TTL on first increment
        if value == 1 and ttl:
            await self.client.expire(key, ttl)
        
        return value
    
    async def ping(self) -> bool:
        """Ping Redis to check connectivity."""
        try:
            return await self.client.ping()
        except Exception as e:
            logger.error("Redis ping failed", error=str(e))
            return False
    
    async def flush_pattern(self, pattern: str):
        """
        Delete all keys matching pattern.
        
        Args:
            pattern: Key pattern (e.g., "rate_limit:*")
        """
        keys = []
        async for key in self.client.scan_iter(match=pattern):
            keys.append(key)
        
        if keys:
            await self.client.delete(*keys)
            logger.info(f"Flushed {len(keys)} keys matching pattern", pattern=pattern)
```

**Cache Usage Patterns**:
- Rate limit tracking: `rate_limit:{platform}:{date}`
- API response caching: `github:repo:{owner}/{repo}`
- Temporary data: `temp:{workflow_id}:{key}`

---

## 8. UTILITIES MODULE (utils/)

### 8.1 utils/__init__.py

**Content**:
```python
"""Utility functions and helpers."""

from .concurrency import RateLimiter, Semaphore
from .error_handling import with_retry, CircuitBreaker, exponential_backoff
from .validation import ContentValidator, URLValidator

__all__ = [
    "RateLimiter",
    "Semaphore",
    "with_retry",
    "CircuitBreaker",
    "exponential_backoff",
    "ContentValidator",
    "URLValidator"
]
```

---

### 8.2 utils/concurrency.py

**Purpose**: Async concurrency management utilities

**Implementation**:

```python
import asyncio
from typing import Optional
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger()

class RateLimiter:
    """
    Token bucket rate limiter for API calls.
    
    Ensures requests don't exceed specified rate limits.
    """
    
    def __init__(self, requests_per_second: float = 1.0):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_second: Maximum requests per second
        """
        self.requests_per_second = requests_per_second
        self.min_interval = 1.0 / requests_per_second
        self.last_request = None
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire permission to make a request (blocks if needed)."""
        async with self._lock:
            now = datetime.utcnow()
            
            if self.last_request:
                elapsed = (now - self.last_request).total_seconds()
                if elapsed < self.min_interval:
                    wait_time = self.min_interval - elapsed
                    logger.debug(f"Rate limiting: waiting {wait_time:.2f}s")
                    await asyncio.sleep(wait_time)
            
            self.last_request = datetime.utcnow()

class Semaphore:
    """
    Async semaphore for limiting concurrent operations.
    """
    
    def __init__(self, value: int = 5):
        """
        Initialize semaphore.
        
        Args:
            value: Maximum concurrent operations
        """
        self._semaphore = asyncio.Semaphore(value)
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._semaphore.acquire()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        self._semaphore.release()

async def gather_with_concurrency(n: int, *tasks):
    """
    Execute tasks with limited concurrency.
    
    Args:
        n: Maximum concurrent tasks
        *tasks: Coroutines to execute
        
    Returns:
        List of results
    """
    semaphore = asyncio.Semaphore(n)
    
    async def sem_task(task):
        async with semaphore:
            return await task
    
    return await asyncio.gather(*(sem_task(task) for task in tasks))
```

---

### 8.3 utils/error_handling.py

**Purpose**: Error handling utilities (retry, circuit breaker, backoff)

**Implementation**:

```python
import asyncio
from typing import Callable, Any
from functools import wraps
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger()

def exponential_backoff(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
    """
    Calculate exponential backoff delay.
    
    Args:
        attempt: Attempt number (0-indexed)
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        
    Returns:
        Delay in seconds
    """
    delay = base_delay * (2 ** attempt)
    return min(delay, max_delay)

def with_retry(
    max_attempts: int = 3,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator for automatic retry with exponential backoff.
    
    Args:
        max_attempts: Maximum number of attempts
        backoff_factor: Backoff multiplication factor
        exceptions: Exception types to catch and retry
        
    Usage:
        @with_retry(max_attempts=3, backoff_factor=2)
        async def fetch_data():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                    
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_attempts - 1:
                        delay = exponential_backoff(attempt, base_delay=backoff_factor)
                        logger.warning(
                            f"Attempt {attempt + 1} failed, retrying in {delay}s",
                            function=func.__name__,
                            error=str(e)
                        )
                        await asyncio.sleep(delay)
                    else:
                        logger.error(
                            f"All {max_attempts} attempts failed",
                            function=func.__name__,
                            error=str(e)
                        )
            
            raise last_exception
        
        return wrapper
    return decorator

class CircuitBreaker:
    """
    Circuit breaker pattern for API resilience.
    
    Prevents cascading failures by stopping requests to failing services.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds before attempting recovery
            expected_exception: Exception type to track
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open
    
    async def __aenter__(self):
        """Check circuit state before operation."""
        if self.state == "open":
            # Check if recovery timeout has passed
            if self.last_failure_time:
                elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
                if elapsed >= self.recovery_timeout:
                    logger.info("Circuit breaker: attempting recovery (half-open)")
                    self.state = "half_open"
                else:
                    raise Exception("Circuit breaker is OPEN - service unavailable")
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Record success/failure after operation."""
        if exc_type is None:
            # Success
            if self.state == "half_open":
                logger.info("Circuit breaker: recovery successful (closing)")
                self.state = "closed"
                self.failure_count = 0
        
        elif issubclass(exc_type, self.expected_exception):
            # Failure
            self.failure_count += 1
            self.last_failure_time = datetime.utcnow()
            
            if self.failure_count >= self.failure_threshold:
                logger.error(
                    "Circuit breaker: threshold exceeded (opening)",
                    failures=self.failure_count
                )
                self.state = "open"
            
            if self.state == "half_open":
                # Failed during recovery
                self.state = "open"
        
        return False  # Don't suppress exception
```

---

### 8.4 utils/validation.py

**Purpose**: Data validation utilities

**Implementation**:

```python
from typing import Dict, Any, List
from urllib.parse import urlparse
import re
import structlog

logger = structlog.get_logger()

class ContentValidator:
    """
    Validates social media content against platform requirements.
    """
    
    PLATFORM_LIMITS = {
        "linkedin": {
            "max_text_length": 3000,
            "optimal_text_length": (150, 300),
            "min_hashtags": 3,
            "max_hashtags": 5
        },
        "x": {
            "max_tweet_length": 280,
            "max_thread_length": 10,
            "min_hashtags": 0,
            "max_hashtags": 2
        },
        "twitter": {  # Alias for x
            "max_tweet_length": 280,
            "max_thread_length": 10,
            "min_hashtags": 0,
            "max_hashtags": 2
        },
        "instagram": {
            "max_caption_length": 2200,
            "optimal_caption_length": (150, 500),
            "min_hashtags": 10,
            "max_hashtags": 30,
            "requires_image_description": True
        }
    }
    
    @staticmethod
    def validate_linkedin_content(content: Dict[str, Any]) -> Dict[str, Any]:
        """Validate LinkedIn content."""
        errors = []
        warnings = []
        
        text = content.get("text", "")
        hashtags = content.get("hashtags", [])
        
        limits = ContentValidator.PLATFORM_LIMITS["linkedin"]
        
        # Check text length
        if len(text) > limits["max_text_length"]:
            errors.append(f"Text exceeds maximum length of {limits['max_text_length']} characters")
        
        if len(text) < limits["optimal_text_length"][0]:
            warnings.append(f"Text is shorter than optimal length ({limits['optimal_text_length'][0]} chars)")
        elif len(text) > limits["optimal_text_length"][1]:
            warnings.append(f"Text is longer than optimal length ({limits['optimal_text_length'][1]} chars)")
        
        # Check hashtags
        if len(hashtags) < limits["min_hashtags"]:
            warnings.append(f"Less than {limits['min_hashtags']} hashtags (suboptimal)")
        elif len(hashtags) > limits["max_hashtags"]:
            errors.append(f"More than {limits['max_hashtags']} hashtags")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    @staticmethod
    def validate_x_content(content: Dict[str, Any]) -> Dict[str, Any]:
        """Validate X/Twitter content."""
        errors = []
        warnings = []
        
        tweets = content.get("tweets", [])
        hashtags = content.get("hashtags", [])
        
        limits = ContentValidator.PLATFORM_LIMITS["x"]
        
        # Check thread length
        if len(tweets) > limits["max_thread_length"]:
            errors.append(f"Thread exceeds maximum of {limits['max_thread_length']} tweets")
        
        # Check individual tweet lengths
        for tweet in tweets:
            text = tweet.get("text", "")
            if len(text) > limits["max_tweet_length"]:
                errors.append(
                    f"Tweet {tweet.get('order')} exceeds {limits['max_tweet_length']} characters"
                )
        
        # Check hashtags
        if len(hashtags) > limits["max_hashtags"]:
            warnings.append(f"More than {limits['max_hashtags']} hashtags (may reduce engagement)")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    @staticmethod
    def validate_instagram_content(content: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Instagram content."""
        errors = []
        warnings = []
        
        caption = content.get("caption", "")
        hashtags = content.get("hashtags", [])
        image_description = content.get("image_description", "")
        
        limits = ContentValidator.PLATFORM_LIMITS["instagram"]
        
        # Check caption length
        if len(caption) > limits["max_caption_length"]:
            errors.append(f"Caption exceeds maximum length of {limits['max_caption_length']} characters")
        
        if len(caption) < limits["optimal_caption_length"][0]:
            warnings.append("Caption is shorter than optimal length")
        
        # Check image description
        if limits["requires_image_description"] and not image_description:
            errors.append("Image description is required for Instagram posts")
        
        # Check hashtags
        if len(hashtags) < limits["min_hashtags"]:
            warnings.append(f"Less than {limits['min_hashtags']} hashtags (suboptimal for reach)")
        elif len(hashtags) > limits["max_hashtags"]:
            errors.append(f"More than {limits['max_hashtags']} hashtags")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    @staticmethod
    def validate_content(platform: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate content for any platform.
        
        Args:
            platform: Platform name
            content: Content dictionary
            
        Returns:
            Validation result
        """
        validators = {
            "linkedin": ContentValidator.validate_linkedin_content,
            "x": ContentValidator.validate_x_content,
            "twitter": ContentValidator.validate_x_content,
            "instagram": ContentValidator.validate_instagram_content
        }
        
        validator = validators.get(platform)
        if not validator:
            return {
                "valid": False,
                "errors": [f"Unknown platform: {platform}"],
                "warnings": []
            }
        
        return validator(content)

class URLValidator:
    """
    Validates and parses URLs.
    """
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if URL is valid."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    @staticmethod
    def is_github_url(url: str) -> bool:
        """Check if URL is a GitHub repository URL."""
        if not URLValidator.is_valid_url(url):
            return False
        
        result = urlparse(url)
        return "github.com" in result.netloc
    
    @staticmethod
    def extract_github_repo(url: str) -> tuple:
        """
        Extract owner and repo from GitHub URL.
        
        Returns:
            Tuple of (owner, repo) or (None, None)
        """
        if not URLValidator.is_github_url(url):
            return None, None
        
        parts = url.rstrip("/").split("/")
        if len(parts) >= 2:
            return parts[-2], parts[-1]
        
        return None, None
```

---

## 9. OBSERVABILITY MODULE (observability/)

### 9.1 observability/__init__.py

**Content**:
```python
"""Observability: logging, tracing, and metrics."""

from .logging_config import setup_logging, get_logger
from .tracing import setup_tracing, trace_workflow
from .metrics import MetricsCollector

__all__ = [
    "setup_logging",
    "get_logger",
    "setup_tracing",
    "trace_workflow",
    "MetricsCollector"
]
```

---

### 9.2 observability/logging_config.py

**Purpose**: Structured logging configuration

**Responsibilities**:
- Setup structured logging with structlog
- Configure log levels per environment
- Format logs for different outputs (console, file, JSON)
- Integrate with external logging services (Sentry)

**Implementation**:

```python
import logging
import sys
from pathlib import Path
import structlog
from typing import Optional
from config import get_settings

def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None
) -> None:
    """
    Setup structured logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
    """
    settings = get_settings()
    log_level = log_level or settings.observability.log_level
    
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper())
    )
    
    # Setup structlog processors
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    
    # Add different renderers based on environment
    if settings.environment == "development":
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        processors.append(structlog.processors.JSONRenderer())
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Setup file logging if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, log_level.upper()))
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        logging.getLogger().addHandler(file_handler)
    
    # Setup Sentry if configured
    if settings.observability.sentry_dsn:
        import sentry_sdk
        sentry_sdk.init(
            dsn=settings.observability.sentry_dsn,
            environment=settings.environment.value,
            traces_sample_rate=1.0 if settings.environment == "development" else 0.1
        )
    
    logger = structlog.get_logger()
    logger.info(
        "Logging configured",
        level=log_level,
        environment=settings.environment.value,
        file=log_file
    )

def get_logger(name: Optional[str] = None) -> structlog.BoundLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Structured logger instance
    """
    return structlog.get_logger(name)
```

**Logging Best Practices**:
- Use structured logging with context
- Log at appropriate levels
- Include workflow_id in all logs
- Avoid logging sensitive data (tokens, passwords)

---

### 9.3 observability/tracing.py

**Purpose**: Distributed tracing with LangSmith

**Implementation**:

```python
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
```

**Tracing Integration**:
- Automatic tracing for LangChain/LangGraph operations
- Custom trace decorators for workflows
- Context managers for trace metadata
- Integration with LangSmith dashboard

---

### 9.4 observability/metrics.py

**Purpose**: Collect and track system metrics

**Implementation**:

```python
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
```

---

## 10. TESTS MODULE (tests/)

### 10.1 tests/__init__.py

**Content**:
```python
"""Test suite for the social agent system."""

# Test configuration and fixtures can be defined here
```

---

### 10.2 tests/test_github_crew.py

**Purpose**: Test GitHub analysis crew functionality

**Implementation**:

```python
import pytest
import asyncio
from crews.github_crew import GitHubAnalysisCrew
from crews.async_crew import AsyncCrewExecutor
from unittest.mock import Mock, patch, AsyncMock

@pytest.fixture
def github_crew():
    """Create GitHub analysis crew instance."""
    return GitHubAnalysisCrew()

@pytest.fixture
def async_executor():
    """Create async crew executor."""
    return AsyncCrewExecutor(max_workers=2)

@pytest.mark.asyncio
async def test_crew_initialization(github_crew):
    """Test that crew initializes correctly."""
    assert github_crew.llm is not None
    assert github_crew.tools is not None
    assert "researcher" in github_crew.agents
    assert "profile_analyzer" in github_crew.agents

@pytest.mark.asyncio
async def test_create_crew(github_crew):
    """Test crew creation with specific inputs."""
    crew = github_crew.create_crew(
        github_repo_url="https://github.com/test/repo",
        github_username="testuser"
    )
    
    assert crew is not None
    assert len(crew.agents) == 2
    assert len(crew.tasks) == 2

@pytest.mark.asyncio
@patch('crews.github_crew.crew.Crew.kickoff')
async def test_crew_execution(mock_kickoff, github_crew, async_executor):
    """Test crew execution through async executor."""
    # Mock crew output
    mock_output = """
    Repository Analysis:
    - Name: test-repo
    - Stars: 100
    - Health Score: 85
    
    Profile Analysis:
    - Username: testuser
    - Expertise: Python, Machine Learning
    """
    mock_kickoff.return_value = mock_output
    
    crew = github_crew.create_crew(
        github_repo_url="https://github.com/test/repo",
        github_username="testuser"
    )
    
    result = await async_executor.execute_crew(
        crew=crew,
        inputs={
            "repo_url": "https://github.com/test/repo",
            "username": "testuser"
        }
    )
    
    assert result is not None
    mock_kickoff.assert_called_once()

@pytest.mark.asyncio
async def test_parse_results(github_crew):
    """Test parsing of crew output."""
    raw_output = """
    {
        "repository": {
            "name": "test-repo",
            "health_score": 85,
            "tech_stack": ["Python", "FastAPI"]
        },
        "profile": {
            "username": "testuser",
            "expertise_areas": [{"area": "Python", "confidence": "high"}]
        }
    }
    """
    
    results = github_crew.parse_results(raw_output)
    
    assert results is not None
    assert "repository" in results
    assert "profile" in results

@pytest.mark.asyncio
async def test_crew_error_handling(github_crew, async_executor):
    """Test error handling in crew execution."""
    crew = github_crew.create_crew(
        github_repo_url="https://github.com/invalid/repo",
        github_username="invaliduser"
    )
    
    # This should handle the error gracefully
    with pytest.raises(Exception):
        await async_executor.execute_crew(
            crew=crew,
            inputs={
                "repo_url": "https://github.com/invalid/repo",
                "username": "invaliduser"
            }
        )

def test_agent_configuration(github_crew):
    """Test that agents are properly configured."""
    researcher = github_crew.agents["researcher"]
    profile_analyzer = github_crew.agents["profile_analyzer"]
    
    assert researcher.role == "Senior GitHub Repository Analyst"
    assert profile_analyzer.role == "GitHub Profile Intelligence Specialist"
    assert researcher.llm is not None
    assert len(researcher.tools) > 0
```

---

### 10.3 tests/test_content_crew.py

**Purpose**: Test content generation crew

**Implementation**:

```python
import pytest
from crews.content_crew import ContentGenerationCrew
from unittest.mock import Mock, patch

@pytest.fixture
def content_crew():
    """Create content generation crew instance."""
    return ContentGenerationCrew()

@pytest.fixture
def sample_analysis():
    """Sample GitHub analysis results for testing."""
    return {
        "repository": {
            "name": "test-repo",
            "description": "A test repository",
            "tech_stack": ["Python", "FastAPI"],
            "health_score": 85,
            "key_insights": ["Well structured", "Good documentation"]
        },
        "profile": {
            "username": "testuser",
            "expertise_areas": [
                {"area": "Python", "confidence": "high"},
                {"area": "Backend", "confidence": "medium"}
            ],
            "professional_positioning": "Backend developer"
        }
    }

def test_crew_initialization(content_crew):
    """Test content crew initialization."""
    assert content_crew.llm is not None
    assert "linkedin" in content_crew.agents
    assert "x" in content_crew.agents
    assert "instagram" in content_crew.agents

def test_create_crew_all_platforms(content_crew, sample_analysis):
    """Test crew creation for all platforms."""
    platforms = ["linkedin", "twitter", "instagram"]
    crew = content_crew.create_crew(
        analysis_results=sample_analysis,
        platforms=platforms
    )
    
    assert crew is not None
    assert len(crew.agents) == 3
    assert len(crew.tasks) == 3

def test_create_crew_single_platform(content_crew, sample_analysis):
    """Test crew creation for single platform."""
    platforms = ["linkedin"]
    crew = content_crew.create_crew(
        analysis_results=sample_analysis,
        platforms=platforms
    )
    
    assert len(crew.agents) == 1
    assert len(crew.tasks) == 1

def test_content_validation_linkedin(content_crew):
    """Test LinkedIn content validation."""
    content = {
        "text": "Test post content",
        "hashtags": ["python", "github", "opensource"]
    }
    
    result = content_crew._validate_content(content, "linkedin")
    
    assert result["valid"] is True
    assert len(result["errors"]) == 0

def test_content_validation_linkedin_too_long(content_crew):
    """Test LinkedIn content validation with too long text."""
    content = {
        "text": "x" * 3001,  # Exceeds 3000 char limit
        "hashtags": ["python", "github", "opensource"]
    }
    
    result = content_crew._validate_content(content, "linkedin")
    
    assert result["valid"] is False
    assert len(result["errors"]) > 0

def test_content_validation_x_thread(content_crew):
    """Test X/Twitter thread validation."""
    content = {
        "tweets": [
            {"text": "Tweet 1", "order": 1},
            {"text": "Tweet 2", "order": 2}
        ],
        "hashtags": ["github"]
    }
    
    result = content_crew._validate_content(content, "x")
    
    assert result["valid"] is True

def test_content_validation_x_too_many_tweets(content_crew):
    """Test X validation with too many tweets."""
    content = {
        "tweets": [
            {"text": f"Tweet {i}", "order": i}
            for i in range(1, 12)  # 11 tweets, exceeds limit of 10
        ],
        "hashtags": ["github"]
    }
    
    result = content_crew._validate_content(content, "x")
    
    assert result["valid"] is False

def test_content_validation_instagram(content_crew):
    """Test Instagram content validation."""
    content = {
        "caption": "Test caption",
        "hashtags": ["coding"] * 15,  # 15 hashtags
        "image_description": "Test image"
    }
    
    result = content_crew._validate_content(content, "instagram")
    
    assert result["valid"] is True

def test_content_validation_instagram_missing_image(content_crew):
    """Test Instagram validation without image description."""
    content = {
        "caption": "Test caption",
        "hashtags": ["coding"] * 15,
        "image_description": ""  # Missing
    }
    
    result = content_crew._validate_content(content, "instagram")
    
    assert result["valid"] is False
```

---

### 10.4 tests/test_integrations.py

**Purpose**: Test external API integrations

**Implementation**:

```python
import pytest
from integrations.github import GitHubClient
from integrations.linkedin import LinkedInClient
from integrations.x_twitter import XClient
from integrations.instagram import InstagramClient
from unittest.mock import Mock, patch, AsyncMock
import aiohttp

@pytest.fixture
async def github_client():
    """Create GitHub client."""
    client = GitHubClient(token="test_token")
    await client.connect()
    yield client
    await client.disconnect()

@pytest.mark.asyncio
@patch('aiohttp.ClientSession.get')
async def test_github_get_repository(mock_get, github_client):
    """Test GitHub repository fetching."""
    # Mock response
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={
        "name": "test-repo",
        "full_name": "owner/test-repo",
        "stargazers_count": 100,
        "forks_count": 20
    })
    mock_response.headers = {"X-RateLimit-Remaining": "5000"}
    mock_get.return_value.__aenter__.return_value = mock_response
    
    result = await github_client.get_repository("owner/test-repo")
    
    assert result["name"] == "test-repo"
    assert result["stars"] == 100
    assert result["forks"] == 20

@pytest.mark.asyncio
@patch('aiohttp.ClientSession.get')
async def test_github_rate_limit_warning(mock_get, github_client):
    """Test GitHub rate limit warning."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={})
    mock_response.headers = {"X-RateLimit-Remaining": "50"}  # Low
    mock_get.return_value.__aenter__.return_value = mock_response
    
    # Should log warning but not raise exception
    result = await github_client.get_repository("owner/test-repo")

@pytest.mark.asyncio
async def test_linkedin_client_initialization():
    """Test LinkedIn client initialization."""
    client = LinkedInClient(
        client_id="test_id",
        client_secret="test_secret",
        access_token="test_token"
    )
    
    await client.connect()
    assert client.session is not None
    await client.disconnect()

@pytest.mark.asyncio
@patch('aiohttp.ClientSession.post')
async def test_linkedin_create_post(mock_post):
    """Test LinkedIn post creation."""
    client = LinkedInClient(
        client_id="test_id",
        client_secret="test_secret",
        access_token="test_token"
    )
    await client.connect()
    
    # Mock response
    mock_response = AsyncMock()
    mock_response.status = 201
    mock_response.json = AsyncMock(return_value={"id": "post123"})
    mock_post.return_value.__aenter__.return_value = mock_response
    
    result = await client.create_post(text="Test post")
    
    assert result["post_id"] == "post123"
    assert result["status"] == "success"
    
    await client.disconnect()

@pytest.mark.asyncio
async def test_x_client_initialization():
    """Test X/Twitter client initialization."""
    client = XClient(
        api_key="test_key",
        api_secret="test_secret",
        access_token="test_token",
        access_token_secret="test_token_secret",
        bearer_token="test_bearer"
    )
    
    await client.connect()
    assert client.session is not None
    await client.disconnect()

@pytest.mark.asyncio
@patch('aiohttp.ClientSession.post')
async def test_x_create_thread(mock_post):
    """Test X thread creation."""
    client = XClient(
        api_key="test_key",
        api_secret="test_secret",
        access_token="test_token",
        access_token_secret="test_token_secret",
        bearer_token="test_bearer"
    )
    await client.connect()
    
    # Mock response for each tweet
    mock_response = AsyncMock()
    mock_response.status = 201
    call_count = [0]
    
    async def mock_json():
        call_count[0] += 1
        return {"data": {"id": f"tweet{call_count[0]}"}}
    
    mock_response.json = mock_json
    mock_post.return_value.__aenter__.return_value = mock_response
    
    tweets = [
        {"text": "Tweet 1", "order": 1},
        {"text": "Tweet 2", "order": 2}
    ]
    
    result = await client.create_thread(tweets=tweets)
    
    assert len(result["tweet_ids"]) == 2
    assert result["status"] == "success"
    
    await client.disconnect()
```

---

### 10.5 tests/test_workflows.py

**Purpose**: Test LangGraph workflow orchestration

**Implementation**:

```python
import pytest
from workflows.graph import SocialAgentWorkflow
from workflows.state import create_initial_state, WorkflowPhase
from workflows.nodes import WorkflowNodes
from workflows.edges import WorkflowEdges
from unittest.mock import Mock, AsyncMock, patch

@pytest.fixture
def workflow_state():
    """Create initial workflow state for testing."""
    return create_initial_state(
        workflow_id="test-workflow-123",
        github_repo_url="https://github.com/test/repo",
        github_username="testuser",
        platforms=["linkedin", "twitter"],
        dry_run=True
    )

def test_initial_state_creation(workflow_state):
    """Test initial state is created correctly."""
    assert workflow_state["workflow_id"] == "test-workflow-123"
    assert workflow_state["phase"] == WorkflowPhase.IDLE
    assert workflow_state["platforms"] == ["linkedin", "twitter"]
    assert workflow_state["dry_run"] is True
    assert workflow_state["analysis_status"] == "pending"

def test_workflow_nodes_initialization():
    """Test workflow nodes are initialized."""
    nodes = WorkflowNodes()
    
    assert nodes.github_crew is not None
    assert nodes.content_crew is not None
    assert nodes.crew_executor is not None

@pytest.mark.asyncio
async def test_initialize_node(workflow_state):
    """Test initialization node."""
    nodes = WorkflowNodes()
    
    result_state = await nodes.initialize_node(workflow_state)
    
    assert result_state["phase"] == WorkflowPhase.INITIALIZING

def test_workflow_edges_routing():
    """Test conditional edge routing logic."""
    edges = WorkflowEdges()
    
    # Test successful initialization routing
    state = {"phase": WorkflowPhase.INITIALIZING, "analysis_status": "pending"}
    route = edges.route_after_initialize(state)
    assert route == "analyze"
    
    # Test failed initialization routing
    state = {"phase": "failed"}
    route = edges.route_after_initialize(state)
    assert route == "error"

def test_workflow_edges_retry_logic():
    """Test retry logic in edges."""
    edges = WorkflowEdges()
    
    # Test retry when under max retries
    state = {
        "analysis_status": "failed",
        "analysis_retry_count": 1
    }
    route = edges.route_after_analysis(state)
    assert route == "retry"
    
    # Test error when max retries exceeded
    state = {
        "analysis_status": "failed",
        "analysis_retry_count": 3
    }
    route = edges.route_after_analysis(state)
    assert route == "error"

@pytest.mark.asyncio
@patch('workflows.nodes.WorkflowNodes._publish_linkedin')
@patch('workflows.nodes.WorkflowNodes._publish_x')
async def test_publish_content_node(mock_x, mock_linkedin, workflow_state):
    """Test publishing node."""
    nodes = WorkflowNodes()
    
    # Setup state with content
    workflow_state["content_drafts"] = {
        "drafts": {
            "linkedin": {"text": "Test post", "hashtags": ["test"]},
            "twitter": {"tweets": [{"text": "Test tweet", "order": 1}]}
        }
    }
    workflow_state["phase"] = WorkflowPhase.PUBLISHING
    
    # Mock successful publishing
    mock_linkedin.return_value = {
        "status": "success",
        "post_id": "linkedin123"
    }
    mock_x.return_value = {
        "status": "success",
        "tweet_ids": ["tweet123"]
    }
    
    result_state = await nodes.publish_content_node(workflow_state)
    
    assert result_state["publishing_status"] in ["completed", "partial"]
    assert len(result_state["published_posts"]) > 0
```

---

## 11. SCRIPTS MODULE (scripts/)

### 11.1 scripts/setup_database.py

**Purpose**: Initialize database schema and tables

**Implementation**:

```python
#!/usr/bin/env python3
"""
Database setup script.

Creates all necessary tables and initializes the database schema.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from persistence.database import DatabaseManager, Base
from config import get_settings
import structlog

logger = structlog.get_logger()

async def setup_database():
    """Setup database tables and schema."""
    settings = get_settings()
    
    logger.info("Setting up database", url=settings.database.url)
    
    db_manager = DatabaseManager()
    
    try:
        await db_manager.connect()
        
        # Create all tables
        async with db_manager.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database setup completed successfully")
        
        # Verify tables were created
        async with db_manager.engine.connect() as conn:
            result = await conn.execute(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public'"
            )
            tables = [row[0] for row in result]
            logger.info("Created tables", tables=tables)
        
    except Exception as e:
        logger.error("Database setup failed", error=str(e))
        sys.exit(1)
    
    finally:
        await db_manager.disconnect()

def main():
    """Main entry point."""
    logger.info("Starting database setup")
    asyncio.run(setup_database())
    logger.info("Database setup script completed")

if __name__ == "__main__":
    main()
```

---

### 11.2 scripts/run_workflow.py

**Purpose**: Command-line script to run workflows

**Implementation**:

```python
#!/usr/bin/env python3
"""
Workflow execution script.

Runs the social agent workflow from the command line.
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import SocialAgentOrchestrator
from observability.logging_config import setup_logging
import structlog

logger = structlog.get_logger()

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Run the autonomous social media agent workflow"
    )
    
    parser.add_argument(
        "--repo",
        required=True,
        help="GitHub repository URL"
    )
    
    parser.add_argument(
        "--username",
        required=True,
        help="GitHub username"
    )
    
    parser.add_argument(
        "--platforms",
        nargs="+",
        default=["linkedin", "twitter", "instagram"],
        choices=["linkedin", "twitter", "x", "instagram"],
        help="Target platforms for publishing"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without actually publishing"
    )
    
    parser.add_argument(
        "--workflow-id",
        help="Resume existing workflow by ID"
    )
    
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level"
    )
    
    return parser.parse_args()

async def main():
    """Main execution function."""
    args = parse_arguments()
    
    # Setup logging
    setup_logging(log_level=args.log_level)
    
    logger.info(
        "Starting workflow execution",
        repo=args.repo,
        username=args.username,
        platforms=args.platforms,
        dry_run=args.dry_run
    )
    
    # Create orchestrator
    orchestrator = SocialAgentOrchestrator()
    
    try:
        # Initialize
        await orchestrator.initialize()
        
        # Run workflow
        result = await orchestrator.run_workflow(
            github_repo_url=args.repo,
            github_username=args.username,
            platforms=args.platforms,
            dry_run=args.dry_run,
            workflow_id=args.workflow_id
        )
        
        # Print results
        logger.info(
            "Workflow completed",
            workflow_id=result["workflow_id"],
            phase=result["phase"],
            success_rate=result["success_rate"],
            duration=result.get("total_duration")
        )
        
        print("\n=== Workflow Results ===")
        print(f"Workflow ID: {result['workflow_id']}")
        print(f"Status: {result['phase']}")
        print(f"Success Rate: {result['success_rate']:.1%}")
        print(f"\nPublished Posts:")
        for post in result["published_posts"]:
            print(f"  - {post['platform']}: {post['status']}")
            if post['status'] == 'success':
                print(f"    URL: {post.get('url')}")
        
        sys.exit(0)
        
    except Exception as e:
        logger.error("Workflow execution failed", error=str(e))
        sys.exit(1)
    
    finally:
        await orchestrator.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

---

### 11.3 scripts/test_connections.py

**Purpose**: Test all external API connections

**Implementation**:

```python
#!/usr/bin/env python3
"""
Connection testing script.

Tests connectivity to all external services (GitHub, LinkedIn, X, Instagram, LLM, Database, Redis).
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import get_settings, ConfigValidator
from observability.logging_config import setup_logging
import structlog

logger = structlog.get_logger()

async def test_all_connections():
    """Test all external connections."""
    setup_logging(log_level="INFO")
    settings = get_settings()
    
    logger.info("Testing all connections...")
    
    validator = ConfigValidator(settings)
    is_valid, errors = await validator.validate_all()
    
    print("\n=== Connection Test Results ===\n")
    
    for service, status in validator.validation_results.items():
        symbol = "✓" if status else "✗"
        print(f"{symbol} {service.upper()}: {'Connected' if status else 'Failed'}")
    
    if errors:
        print("\n=== Errors ===\n")
        for error in errors:
            print(f"  - {error}")
    
    print("\n" + "=" * 32)
    
    if is_valid:
        print("\n✓ All connections successful!")
        sys.exit(0)
    else:
        print("\n✗ Some connections failed. Check errors above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_all_connections())
```

---

## 12. MIGRATIONS (migrations/)

### 12.1 migrations/alembic.ini

**Purpose**: Alembic configuration for database migrations

**Content**:
```ini
[alembic]
script_location = migrations
prepend_sys_path = .
sqlalchemy.url = driver://user:pass@localhost/dbname

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

---

### 12.2 Migration Usage

**Creating Migrations**:
```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add new column to workflow_runs"

# Create empty migration
alembic revision -m "Custom migration"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

---

## 13. COMPREHENSIVE INTEGRATION & EXECUTION FLOW

### 13.1 System Startup Sequence

```
1. main.py invoked
   ↓
2. Load configuration (config/settings.py)
   ↓
3. Setup logging (observability/logging_config.py)
   ↓
4. Setup tracing (observability/tracing.py)
   ↓
5. Validate configuration (config/validator.py)
   ↓
6. Initialize database (persistence/database.py)
   ↓
7. Initialize Redis cache (persistence/cache.py)
   ↓
8. Initialize state manager (persistence/state_manager.py)
   ↓
9. Create workflow graph (workflows/graph.py)
   ↓
10. Ready for workflow execution
```

### 13.2 Workflow Execution Flow

```
Workflow Start
   ↓
Initialize Node (workflows/nodes.py)
   - Initialize publishers (integrations/publisher.py)
   - Setup metrics collection (observability/metrics.py)
   ↓
Analyze GitHub Node
   - Execute GitHubAnalysisCrew (crews/github_crew/)
   - Use GitHub tools (tools/github_tools.py)
   - Call GitHub API (integrations/github.py)
   - Cache results (persistence/cache.py)
   - Save checkpoint (persistence/state_manager.py)
   ↓
Generate Content Node
   - Execute ContentGenerationCrew (crews/content_crew/)
   - Generate platform-specific content
   - Validate content (utils/validation.py)
   - Save checkpoint
   ↓
Validate Content Node
   - Validate against platform requirements
   - Check formatting and constraints
   ↓
Check Rate Limits Node
   - Query Redis for usage (persistence/cache.py)
   - Determine if publishing is allowed
   ↓
Publish Content Node
   - Publish to LinkedIn (integrations/linkedin.py)
   - Publish to X (integrations/x_twitter.py)
   - Publish to Instagram (integrations/instagram.py)
   - Execute in parallel with error isolation
   - Update rate limit counters
   - Save published posts (persistence/database.py)
   - Save checkpoint
   ↓
Calculate Metrics Node
   - Calculate success rates
   - Record duration
   - Save execution metrics (observability/metrics.py)
   ↓
Workflow End
   - Save final state
   - Cleanup resources
   - Return results
```

### 13.3 Error Handling Flow

```
Error Occurs in Any Node
   ↓
Capture Exception
   ↓
Check Retry Count
   ↓
If < Max Retries:
   - Increment retry counter
   - Apply exponential backoff (utils/error_handling.py)
   - Return to failed node
   ↓
If >= Max Retries:
   - Log error (observability/logging_config.py)
   - Add to errors list
   - Route to error handler node
   ↓
Error Handler Node
   - Save error state
   - Cleanup resources
   - Mark workflow as failed
   - End workflow
```

### 13.4 State Checkpointing Flow

```
After Each Major Node
   ↓
Update Workflow State (workflows/state.py)
   ↓
Save to PostgreSQL (persistence/state_manager.py)
   - LangGraph automatic checkpoint
   - Custom named checkpoint
   ↓
Update Database Record (persistence/database.py)
   - Update workflow_runs table
   - Save intermediate results
   ↓
Checkpoint Complete
   - State can be resumed from this point
   - Continue to next node
```

---

## 14. DEPLOYMENT CHECKLIST

### 14.1 Pre-Deployment

- [ ] All tests passing (`pytest`)
- [ ] Configuration validated (`scripts/test_connections.py`)
- [ ] Database migrations applied (`alembic upgrade head`)
- [ ] Environment variables set (`.env` file)
- [ ] API credentials configured
- [ ] Rate limits configured appropriately
- [ ] Logging level set for environment
- [ ] Monitoring/observability configured

### 14.2 Deployment Steps

```bash
# 1. Build Docker image
docker build -t social-agent:latest .

# 2. Run database setup
docker-compose run app python scripts/setup_database.py

# 3. Test connections
docker-compose run app python scripts/test_connections.py

# 4. Start services
docker-compose up -d

# 5. Verify health
docker-compose ps
docker-compose logs -f app
```

### 14.3 Post-Deployment

- [ ] Verify all containers running
- [ ] Test workflow execution
- [ ] Monitor logs for errors
- [ ] Verify metrics collection
- [ ] Check LangSmith traces
- [ ] Verify rate limit tracking

---

## 15. TROUBLESHOOTING GUIDE

### 15.1 Common Issues

**Issue: Database connection fails**
- Check DATABASE_URL in .env
- Verify PostgreSQL is running
- Test connection: `docker-compose ps postgres`

**Issue: Redis connection fails**
- Check REDIS_URL in .env
- Verify Redis is running
- Test connection: `redis-cli ping`

**Issue: API authentication fails**
- Verify API credentials in .env
- Check token expiration
- Run `scripts/test_connections.py`

**Issue: LLM service unavailable**
- Verify Ollama is running: `ollama list`
- Check OLLAMA_BASE_URL
- Verify models are pulled: `ollama pull deepseek-r1:latest`

**Issue: Rate limit exceeded**
- Check Redis rate limit counters
- Review rate limit settings in config
- Wait for rate limit reset
- Consider queuing workflow for later

**Issue: Workflow hangs**
- Check for blocking operations in logs
- Verify async/await patterns
- Check for circuit breaker activation
- Review timeout settings

---

## 16. SUMMARY

This comprehensive prompt engineering framework provides:

✅ **Complete File-Level Specifications**: Every file with purpose, inputs, outputs, dependencies
✅ **Clear Integration Patterns**: How components connect and synchronize
✅ **State Management Details**: LangGraph checkpointing and state persistence
✅ **Error Handling Strategy**: Retries, circuit breakers, graceful degradation
✅ **Async Execution Patterns**: Non-blocking operations throughout
✅ **Testing Strategy**: Comprehensive test coverage for all modules
✅ **Deployment Guidance**: Docker, Kubernetes, environment configuration
✅ **Observability Integration**: Logging, tracing, metrics collection

### Key Implementation Principles

1. **Async-First**: All I/O operations use async/await
2. **State Persistence**: Checkpoints at every phase boundary
3. **Error Resilience**: Retry logic, circuit breakers, partial success handling
4. **Rate Limiting**: Redis-backed tracking with per-platform limits
5. **Modularity**: Clear separation of concerns, easy to extend
6. **Observability**: Structured logging, distributed tracing, metrics
7. **Type Safety**: Pydantic models and TypedDict for state
8. **Testing**: Comprehensive pytest suite with mocks

### Next Steps for Implementation

1. **Phase 1**: Core infrastructure (config, database, state management)
2. **Phase 2**: Integrations (GitHub, social platforms)
3. **Phase 3**: Crews (GitHub analysis, content generation)
4. **Phase 4**: Workflow orchestration (LangGraph nodes and edges)
5. **Phase 5**: Observability and testing
6. **Phase 6**: Deployment and production readiness

This framework is ready for direct implementation. Each file specification provides everything needed to build a production-grade, autonomous social media AI agent system.