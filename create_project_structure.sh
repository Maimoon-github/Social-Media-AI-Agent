#!/bin/bash

# create_project_structure.sh
# This script creates the full project structure for the Social Media Agent System.

set -e  # Exit on error

echo "Creating project structure for social-media-agent-system..."

# Create root directories
mkdir -p src/agents/tools
mkdir -p src/workflows
mkdir -p src/publishers
mkdir -p src/services
mkdir -p src/models
mkdir -p src/utils

mkdir -p tests/unit
mkdir -p tests/integration
mkdir -p tests/e2e

mkdir -p scripts
mkdir -p monitoring
mkdir -p docs

# Create root files
touch README.md
touch pyproject.toml
touch docker-compose.yml
touch Dockerfile
touch .env.example
touch .gitignore

# Create src/__init__.py
touch src/__init__.py

# Create src/main.py
touch src/main.py

# Create src/config.py
touch src/config.py

# Create agents files
touch src/agents/__init__.py
touch src/agents/github_agents.py
touch src/agents/content_agents.py
touch src/agents/publishing_agents.py

# Create agents/tools files
touch src/agents/tools/__init__.py
touch src/agents/tools/github_tools.py
touch src/agents/tools/llm_tools.py
touch src/agents/tools/validation_tools.py

# Create workflows files
touch src/workflows/__init__.py
touch src/workflows/main_workflow.py
touch src/workflows/state.py
touch src/workflows/nodes.py

# Create publishers files
touch src/publishers/__init__.py
touch src/publishers/linkedin.py
touch src/publishers/twitter.py
touch src/publishers/instagram.py

# Create services files
touch src/services/__init__.py
touch src/services/state_manager.py
touch src/services/rate_limiter.py
touch src/services/retry_handler.py
touch src/services/content_moderator.py

# Create models files
touch src/models/__init__.py
touch src/models/agent_state.py
touch src/models/content_models.py
touch src/models/platform_models.py

# Create utils files
touch src/utils/__init__.py
touch src/utils/logger.py
touch src/utils/metrics.py
touch src/utils/validators.py

# Create tests files
touch tests/__init__.py
touch tests/conftest.py
touch tests/unit/__init__.py
touch tests/unit/test_agents.py
touch tests/unit/test_publishers.py
touch tests/unit/test_state_manager.py
touch tests/integration/__init__.py
touch tests/integration/test_workflow.py
touch tests/integration/test_api_integration.py
touch tests/e2e/__init__.py
touch tests/e2e/test_full_pipeline.py

# Create scripts files
touch scripts/setup_db.py
touch scripts/refresh_tokens.py
touch scripts/seed_test_data.py

# Create monitoring files
touch monitoring/prometheus.yml
touch monitoring/grafana_dashboard.json

# Create docs files
touch docs/architecture.md
touch docs/api_reference.md
touch docs/deployment.md

echo "Project structure created successfully!"