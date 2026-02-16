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