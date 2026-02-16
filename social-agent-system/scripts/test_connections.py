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