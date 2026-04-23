#!/usr/bin/env bash
set -euo pipefail

# ------------------------------------------------------------
# Social Media AI Posting System - Project Bootstrapper
# Creates the full directory structure and stub files.
# Run from the directory where you want the project root.
# ------------------------------------------------------------

PROJECT_ROOT="${PWD}/social_media_ai"

# Color output for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Bootstrapping Social Media AI project at ${PROJECT_ROOT}${NC}"

# Create top-level directories
mkdir -p "${PROJECT_ROOT}"/{config,core/crews,core/graph,core/tools,platforms,scheduler,ui/templates,utils}

# Create root files (if not exist)
touch_if_missing() {
    if [[ ! -f "$1" ]]; then
        echo "# Auto-generated file" > "$1"
        echo -e "${YELLOW}   Created: $1${NC}"
    else
        echo -e "${YELLOW}   Already exists: $1${NC}"
    fi
}

# Use a function that adds minimal content for Python stubs
create_py_stub() {
    local file="$1"
    local classname="${2:-}"
    if [[ ! -f "$file" ]]; then
        mkdir -p "$(dirname "$file")"
        echo '"""Auto-generated stub."""' > "$file"
        if [[ -n "$classname" ]]; then
            echo -e "\n\nclass ${classname}:\n    pass" >> "$file"
        fi
        echo -e "${YELLOW}   Created: $file${NC}"
    else
        echo -e "${YELLOW}   Already exists: $file${NC}"
    fi
}

# Root files
touch_if_missing "${PROJECT_ROOT}/.env"
touch_if_missing "${PROJECT_ROOT}/requirements.txt"
touch_if_missing "${PROJECT_ROOT}/docker-compose.yml"
touch_if_missing "${PROJECT_ROOT}/README.md"

# config/
create_py_stub "${PROJECT_ROOT}/config/__init__.py"
create_py_stub "${PROJECT_ROOT}/config/settings.py" "Settings"
create_py_stub "${PROJECT_ROOT}/config/platforms.py" "PlatformConfig"

# core/
create_py_stub "${PROJECT_ROOT}/core/__init__.py"
create_py_stub "${PROJECT_ROOT}/core/llm_factory.py" "LLMFactory"

# core/crews/
create_py_stub "${PROJECT_ROOT}/core/crews/__init__.py"
create_py_stub "${PROJECT_ROOT}/core/crews/content_crew.py" "ContentCrew"
create_py_stub "${PROJECT_ROOT}/core/crews/agents.py" "Agents"
create_py_stub "${PROJECT_ROOT}/core/crews/tasks.py" "Tasks"

# core/graph/
create_py_stub "${PROJECT_ROOT}/core/graph/__init__.py"
create_py_stub "${PROJECT_ROOT}/core/graph/workflow.py" "Workflow"

# core/tools/
create_py_stub "${PROJECT_ROOT}/core/tools/__init__.py"
create_py_stub "${PROJECT_ROOT}/core/tools/search_tool.py" "SearchTool"
create_py_stub "${PROJECT_ROOT}/core/tools/image_gen_tool.py" "ImageGenTool"

# platforms/
create_py_stub "${PROJECT_ROOT}/platforms/__init__.py"
create_py_stub "${PROJECT_ROOT}/platforms/base.py" "BasePoster"
for plat in twitter linkedin instagram facebook threads youtube tiktok; do
    create_py_stub "${PROJECT_ROOT}/platforms/${plat}.py" "${plat^}Poster"
done

# scheduler/
create_py_stub "${PROJECT_ROOT}/scheduler/__init__.py"
create_py_stub "${PROJECT_ROOT}/scheduler/scheduler.py" "Scheduler"
create_py_stub "${PROJECT_ROOT}/scheduler/queue.py" "Queue"

# ui/
create_py_stub "${PROJECT_ROOT}/ui/__init__.py"
create_py_stub "${PROJECT_ROOT}/ui/app.py" "UIApp"
touch_if_missing "${PROJECT_ROOT}/ui/templates/.gitkeep"

# utils/
create_py_stub "${PROJECT_ROOT}/utils/__init__.py"
create_py_stub "${PROJECT_ROOT}/utils/logger.py" "Logger"
create_py_stub "${PROJECT_ROOT}/utils/media_handler.py" "MediaHandler"

# Optional: write a minimal requirements.txt with common packages
if [[ ! -s "${PROJECT_ROOT}/requirements.txt" ]]; then
    cat > "${PROJECT_ROOT}/requirements.txt" << 'EOF'
# Core AI / Orchestration
crewai>=0.28.0
langchain>=0.1.0
langgraph>=0.0.20
langsmith>=0.0.77

# LLM backends
ollama>=0.1.0
openai>=1.0.0
groq>=0.4.0

# Platform SDKs
tweepy>=4.14.0
google-api-python-client>=2.111.0
python-instagram>=1.2.0   # may need alternatives; placeholder
facebook-sdk>=3.1.0
tiktok-business-api>=0.0.1   # placeholder

# Scheduling & utilities
apscheduler>=3.10.0
redis>=5.0.0

# Web search & tools
tavily-python>=0.3.0
beautifulsoup4>=4.12.0

# UI
streamlit>=1.28.0
gradio>=4.0.0

# Helpers
python-dotenv>=1.0.0
pillow>=10.0.0
requests>=2.31.0
EOF
    echo -e "${YELLOW}   Created default requirements.txt${NC}"
fi

# Minimal docker-compose.yml
if [[ ! -s "${PROJECT_ROOT}/docker-compose.yml" ]]; then
    cat > "${PROJECT_ROOT}/docker-compose.yml" << 'EOF'
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
  app:
    build: .
    depends_on:
      - redis
    environment:
      - REDIS_URL=redis://redis:6379
    volumes:
      - .:/app
volumes:
  redis_data:
EOF
    echo -e "${YELLOW}   Created docker-compose.yml${NC}"
fi

# Simple README
if [[ ! -s "${PROJECT_ROOT}/README.md" ]]; then
    cat > "${PROJECT_ROOT}/README.md" << 'EOF'
# Social Media AI Posting System

Automated content generation and posting to Twitter, LinkedIn, Instagram, Facebook, Threads, YouTube, TikTok using CrewAI, LangGraph, and Ollama/local LLMs.

## Setup
1. Copy `.env.example` to `.env` and fill in your API keys.
2. Install dependencies: `pip install -r requirements.txt`
3. Run using `streamlit run ui/app.py` or `python scheduler/scheduler.py`

## Structure
- `core/` – LLM factory, CrewAI agents/tasks, LangGraph workflow, tools.
- `platforms/` – Platform-specific posters (abstract base class).
- `scheduler/` – APScheduler + Redis queue.
- `ui/` – Streamlit or Gradio dashboard.
- `utils/` – Logging and media helpers.

See `config/` for settings and platform configuration.
EOF
    echo -e "${YELLOW}   Created README.md${NC}"
fi

# Create a helpful .env.example (not mandatory but professional)
if [[ ! -f "${PROJECT_ROOT}/.env.example" ]]; then
    cat > "${PROJECT_ROOT}/.env.example" << 'EOF'
# LLM Providers
OLLAMA_BASE_URL=http://localhost:11434
OPENAI_API_KEY=
GROQ_API_KEY=

# Social Media API Keys
TWITTER_BEARER_TOKEN=
LINKEDIN_ACCESS_TOKEN=
INSTAGRAM_ACCESS_TOKEN=
FACEBOOK_ACCESS_TOKEN=
THREADS_ACCESS_TOKEN=
YOUTUBE_API_KEY=
TIKTOK_ACCESS_TOKEN=

# Redis (optional)
REDIS_URL=redis://localhost:6379

# Web Search (e.g., Tavily)
TAVILY_API_KEY=
EOF
    echo -e "${YELLOW}   Created .env.example (copy to .env and fill)${NC}"
fi

echo -e "${GREEN}✅ Bootstrapping complete! Project ready at ${PROJECT_ROOT}${NC}"
echo "Next steps:"
echo "  cd ${PROJECT_ROOT}"
echo "  python -m venv venv && source venv/bin/activate"
echo "  pip install -r requirements.txt"
echo "  cp .env.example .env  # then edit .env"
echo "  # Start developing with ui/app.py or scheduler/scheduler.py"