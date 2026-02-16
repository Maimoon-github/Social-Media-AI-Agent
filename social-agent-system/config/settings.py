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