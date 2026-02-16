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