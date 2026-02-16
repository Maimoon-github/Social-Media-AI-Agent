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