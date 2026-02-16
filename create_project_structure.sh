#!/bin/bash

# Script to create the project structure for social-agent-system
# Run this script in the parent directory where you want the project folder created.

set -e  # Exit on error

PROJECT_ROOT="social-agent-system"

echo "Creating project structure in ./$PROJECT_ROOT ..."

# Create root directory
mkdir -p "$PROJECT_ROOT"

# Create root files
touch "$PROJECT_ROOT/README.md"
touch "$PROJECT_ROOT/requirements.txt"
touch "$PROJECT_ROOT/setup.py"
touch "$PROJECT_ROOT/.env.example"
touch "$PROJECT_ROOT/.gitignore"
touch "$PROJECT_ROOT/main.py"

# Config directory
mkdir -p "$PROJECT_ROOT/config"
touch "$PROJECT_ROOT/config/__init__.py"
touch "$PROJECT_ROOT/config/settings.py"
touch "$PROJECT_ROOT/config/validator.py"

# Crews directory
mkdir -p "$PROJECT_ROOT/crews"
touch "$PROJECT_ROOT/crews/__init__.py"
touch "$PROJECT_ROOT/crews/async_crew.py"

# GitHub crew subdirectory
mkdir -p "$PROJECT_ROOT/crews/github_crew"
touch "$PROJECT_ROOT/crews/github_crew/__init__.py"
touch "$PROJECT_ROOT/crews/github_crew/crew.py"
touch "$PROJECT_ROOT/crews/github_crew/agents.py"
touch "$PROJECT_ROOT/crews/github_crew/tasks.py"
touch "$PROJECT_ROOT/crews/github_crew/tools.py"

# Content crew subdirectory
mkdir -p "$PROJECT_ROOT/crews/content_crew"
touch "$PROJECT_ROOT/crews/content_crew/__init__.py"
touch "$PROJECT_ROOT/crews/content_crew/crew.py"
touch "$PROJECT_ROOT/crews/content_crew/agents.py"
touch "$PROJECT_ROOT/crews/content_crew/tasks.py"
touch "$PROJECT_ROOT/crews/content_crew/prompts.py"

# Workflows directory
mkdir -p "$PROJECT_ROOT/workflows"
touch "$PROJECT_ROOT/workflows/__init__.py"
touch "$PROJECT_ROOT/workflows/graph.py"
touch "$PROJECT_ROOT/workflows/nodes.py"
touch "$PROJECT_ROOT/workflows/edges.py"
touch "$PROJECT_ROOT/workflows/state.py"

# Integrations directory
mkdir -p "$PROJECT_ROOT/integrations"
touch "$PROJECT_ROOT/integrations/__init__.py"
touch "$PROJECT_ROOT/integrations/github.py"
touch "$PROJECT_ROOT/integrations/linkedin.py"
touch "$PROJECT_ROOT/integrations/x_twitter.py"
touch "$PROJECT_ROOT/integrations/instagram.py"
touch "$PROJECT_ROOT/integrations/publisher.py"

# Tools directory
mkdir -p "$PROJECT_ROOT/tools"
touch "$PROJECT_ROOT/tools/__init__.py"
touch "$PROJECT_ROOT/tools/github_tools.py"
touch "$PROJECT_ROOT/tools/llm_tools.py"

# Persistence directory
mkdir -p "$PROJECT_ROOT/persistence"
touch "$PROJECT_ROOT/persistence/__init__.py"
touch "$PROJECT_ROOT/persistence/database.py"
touch "$PROJECT_ROOT/persistence/state_manager.py"
touch "$PROJECT_ROOT/persistence/cache.py"

# Utils directory
mkdir -p "$PROJECT_ROOT/utils"
touch "$PROJECT_ROOT/utils/__init__.py"
touch "$PROJECT_ROOT/utils/concurrency.py"
touch "$PROJECT_ROOT/utils/error_handling.py"
touch "$PROJECT_ROOT/utils/validation.py"

# Observability directory
mkdir -p "$PROJECT_ROOT/observability"
touch "$PROJECT_ROOT/observability/__init__.py"
touch "$PROJECT_ROOT/observability/logging_config.py"
touch "$PROJECT_ROOT/observability/tracing.py"
touch "$PROJECT_ROOT/observability/metrics.py"

# Migrations directory
mkdir -p "$PROJECT_ROOT/migrations/versions"
touch "$PROJECT_ROOT/migrations/alembic.ini"

# Tests directory
mkdir -p "$PROJECT_ROOT/tests"
touch "$PROJECT_ROOT/tests/__init__.py"
touch "$PROJECT_ROOT/tests/test_github_crew.py"
touch "$PROJECT_ROOT/tests/test_content_crew.py"
touch "$PROJECT_ROOT/tests/test_integrations.py"
touch "$PROJECT_ROOT/tests/test_workflows.py"

# Scripts directory
mkdir -p "$PROJECT_ROOT/scripts"
touch "$PROJECT_ROOT/scripts/setup_database.py"
touch "$PROJECT_ROOT/scripts/run_workflow.py"
touch "$PROJECT_ROOT/scripts/test_connections.py"

echo "✅ Project structure created successfully in ./$PROJECT_ROOT"