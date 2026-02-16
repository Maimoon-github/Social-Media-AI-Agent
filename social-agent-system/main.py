#!/usr/bin/env python3
"""
Autonomous Social Media AI Agent System - Main Entry Point

This script demonstrates how to orchestrate the complete workflow:
1. Analyze GitHub repository and profile
2. Generate platform-optimized content
3. Publish to LinkedIn, X (Twitter), and Instagram
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
import uuid

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import settings, ConfigValidator
from observability.logging_config import setup_logging
from workflows.graph import create_workflow_graph
from persistence.database import DatabaseManager
from integrations.publisher import MultiPlatformPublisher
from integrations.github import GitHubAPIClient, GitHubAnalyzer
from integrations.linkedin import LinkedInClient, LinkedInPublisher
from integrations.x_twitter import XClient, XPublisher
from integrations.instagram import InstagramClient, InstagramPublisher

# Setup logging
logger = setup_logging(settings.observability.log_level)


class SocialAgentOrchestrator:
    """Main orchestrator for the autonomous social media agent system"""
    
    def __init__(self):
        self.workflow_id = str(uuid.uuid4())
        self.db_manager: Optional[DatabaseManager] = None
        self.workflow_graph = None
        self.publisher: Optional[MultiPlatformPublisher] = None
        
    async def initialize(self):
        """Initialize all components"""
        logger.info("Initializing Social Agent System", extra={
            "workflow_id": self.workflow_id,
            "environment": settings.environment
        })
        
        # Validate configuration
        try:
            ConfigValidator.validate_all(settings)
        except ValueError as e:
            logger.error(f"Configuration validation failed: {e}")
            raise
        
        # Initialize database
        self.db_manager = DatabaseManager(
            settings.database.postgres_url.get_secret_value(),
            settings.database.redis_url.get_secret_value()
        )
        await self.db_manager.initialize()
        
        # Initialize publishers
        await self._initialize_publishers()
        
        # Initialize workflow graph
        self.workflow_graph = create_workflow_graph(
            checkpointer=self.db_manager.checkpointer,
            config={
                "max_retries": settings.workflow.max_retries,
                "timeout": settings.workflow.timeout_per_phase
            }
        )
        
        logger.info("System initialization complete")
    
    async def _initialize_publishers(self):
        """Initialize social media platform publishers"""
        # LinkedIn
        linkedin_client = LinkedInClient(
            client_id=settings.linkedin.client_id.get_secret_value(),
            client_secret=settings.linkedin.client_secret.get_secret_value(),
            access_token=settings.linkedin.access_token.get_secret_value(),
            refresh_token=settings.linkedin.refresh_token.get_secret_value()
        )
        linkedin_publisher = LinkedInPublisher(
            client=linkedin_client,
            author_urn="urn:li:person:YOUR_PERSON_ID"  # Get from LinkedIn API
        )
        
        # X (Twitter)
        x_client = XClient(
            api_key=settings.x.api_key.get_secret_value(),
            api_secret=settings.x.api_secret.get_secret_value(),
            access_token=settings.x.access_token.get_secret_value(),
            access_token_secret=settings.x.access_token_secret.get_secret_value()
        )
        x_publisher = XPublisher(client=x_client)
        
        # Instagram
        instagram_client = InstagramClient(
            app_id=settings.instagram.app_id.get_secret_value(),
            app_secret=settings.instagram.app_secret.get_secret_value(),
            access_token=settings.instagram.access_token.get_secret_value(),
            account_id=settings.instagram.account_id
        )
        instagram_publisher = InstagramPublisher(client=instagram_client)
        
        # Multi-platform publisher
        self.publisher = MultiPlatformPublisher(
            linkedin_publisher=linkedin_publisher,
            x_publisher=x_publisher,
            instagram_publisher=instagram_publisher
        )
        
        logger.info("Publishers initialized")
    
    async def run_workflow(
        self,
        github_repo_url: str,
        github_username: str,
        platforms: Optional[list] = None
    ):
        """
        Execute the complete autonomous workflow
        
        Args:
            github_repo_url: URL of GitHub repository to analyze
            github_username: GitHub username to analyze
            platforms: List of platforms to publish to (default: all)
        """
        if platforms is None:
            platforms = ["linkedin", "twitter", "instagram"]
        
        logger.info("Starting workflow execution", extra={
            "workflow_id": self.workflow_id,
            "repo_url": github_repo_url,
            "username": github_username,
            "platforms": platforms
        })
        
        # Prepare initial state
        initial_state = {
            "workflow_id": self.workflow_id,
            "github_repo_url": github_repo_url,
            "github_username": github_username,
            "target_platforms": platforms,
            "started_at": datetime.now(),
            "current_phase": "initialization",
            "retry_count": 0,
            "max_retries": settings.workflow.max_retries,
            "error_messages": [],
            "content_drafts": [],
            "published_posts": [],
            "failed_posts": []
        }
        
        try:
            # Execute workflow graph
            config = {"configurable": {"thread_id": self.workflow_id}}
            
            result = await self.workflow_graph.ainvoke(
                initial_state,
                config=config
            )
            
            # Log results
            self._log_workflow_results(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}", extra={
                "workflow_id": self.workflow_id,
                "error": str(e)
            })
            raise
        
        finally:
            await self.cleanup()
    
    def _log_workflow_results(self, result: dict):
        """Log workflow execution results"""
        successful_posts = len(result.get("published_posts", []))
        failed_posts = len(result.get("failed_posts", []))
        total_time = result.get("total_execution_time", 0)
        
        logger.info("Workflow execution completed", extra={
            "workflow_id": self.workflow_id,
            "successful_posts": successful_posts,
            "failed_posts": failed_posts,
            "total_time_seconds": total_time,
            "status": result.get("current_phase")
        })
        
        # Print summary
        print("\n" + "="*60)
        print("WORKFLOW EXECUTION SUMMARY")
        print("="*60)
        print(f"Workflow ID: {self.workflow_id}")
        print(f"Status: {result.get('current_phase')}")
        print(f"Total Execution Time: {total_time:.2f}s")
        print(f"\nPublishing Results:")
        print(f"  ✓ Successful: {successful_posts}")
        print(f"  ✗ Failed: {failed_posts}")
        
        if result.get("published_posts"):
            print(f"\nPublished Posts:")
            for post in result["published_posts"]:
                print(f"  - {post.get('platform')}: {post.get('post_id')}")
        
        if result.get("failed_posts"):
            print(f"\nFailed Posts:")
            for post in result["failed_posts"]:
                print(f"  - {post.get('platform')}: {post.get('error')}")
        
        print("="*60 + "\n")
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.db_manager:
            await self.db_manager.close()
        logger.info("Cleanup completed")


async def main():
    """Main entry point"""
    
    # Example usage
    orchestrator = SocialAgentOrchestrator()
    
    try:
        await orchestrator.initialize()
        
        # Run workflow for a specific repository
        result = await orchestrator.run_workflow(
            github_repo_url="https://github.com/langchain-ai/langgraph",
            github_username="langchain-ai",
            platforms=["linkedin", "twitter"]  # Can specify specific platforms
        )
        
        logger.info("Workflow completed successfully")
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)


# CLI Entry Point
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Autonomous Social Media AI Agent System"
    )
    parser.add_argument(
        "--repo",
        required=True,
        help="GitHub repository URL to analyze"
    )
    parser.add_argument(
        "--username",
        required=True,
        help="GitHub username to analyze"
    )
    parser.add_argument(
        "--platforms",
        nargs="+",
        choices=["linkedin", "twitter", "instagram"],
        default=["linkedin", "twitter", "instagram"],
        help="Target platforms for publishing"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate content without publishing"
    )
    
    args = parser.parse_args()
    
    # Override settings for dry-run
    if args.dry_run:
        logger.info("Running in DRY-RUN mode - no posts will be published")
        # You would implement dry-run logic in your workflow
    
    # Run async main
    asyncio.run(main())