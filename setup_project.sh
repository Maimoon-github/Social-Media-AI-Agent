#!/usr/bin/env bash

# -----------------------------------------------------------------------------
# Social Media AI Posting System - Project Setup Script
# Creates the full directory structure, virtual environment, and base files.
# Usage: ./setup_project.sh
# -----------------------------------------------------------------------------

set -euo pipefail  # Exit on error, undefined variable, or pipe failure

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Project root (current directory)
PROJECT_ROOT="$(pwd)/social_media_ai"

# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------
log_info()    { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $1"; }
confirm() {
    read -r -p "$1 [y/N] " response
    case "$response" in
        [yY][eE][sS]|[yY]) return 0 ;;
        *) return 1 ;;
    esac
}

# -----------------------------------------------------------------------------
# Prerequisites check
# -----------------------------------------------------------------------------
log_info "Checking prerequisites..."

command -v python3 >/dev/null 2>&1 || { log_error "Python3 is required but not installed. Aborting."; exit 1; }
command -v pip3 >/dev/null 2>&1 || { log_error "pip3 is required but not installed. Aborting."; exit 1; }

PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if [[ "$(echo "$PY_VERSION < 3.10" | bc)" -eq 1 ]]; then
    log_error "Python 3.10+ is required (found $PY_VERSION). Aborting."
    exit 1
fi

# Optional: check Docker if docker-compose will be used
if command -v docker >/dev/null 2>&1 && command -v docker-compose >/dev/null 2>&1; then
    log_info "Docker and docker-compose found."
else
    log_warn "Docker or docker-compose not found. The docker-compose.yml file will still be created, but you may need to install Docker manually."
fi

# -----------------------------------------------------------------------------
# Create directory structure
# -----------------------------------------------------------------------------
log_info "Creating project directory: $PROJECT_ROOT"
mkdir -p "$PROJECT_ROOT"

cd "$PROJECT_ROOT"

log_info "Creating directory tree..."
mkdir -p config core/crews core/graph core/tools platforms scheduler/ui/templates utils

# -----------------------------------------------------------------------------
# Create Python package files (__init__.py)
# -----------------------------------------------------------------------------
touch config/__init__.py
touch core/__init__.py
touch core/crews/__init__.py
touch core/graph/__init__.py
touch core/tools/__init__.py
touch platforms/__init__.py
touch scheduler/__init__.py
touch scheduler/ui/__init__.py
touch utils/__init__.py

# -----------------------------------------------------------------------------
# Create base configuration files with minimal content
# -----------------------------------------------------------------------------
log_info "Creating configuration files..."

# .env template
cat > .env << 'EOF'
# API Keys (add your own)
OPENAI_API_KEY=
GROQ_API_KEY=
# Social Media API Credentials
TWITTER_API_KEY=
TWITTER_API_SECRET=
TWITTER_ACCESS_TOKEN=
TWITTER_ACCESS_SECRET=
LINKEDIN_CLIENT_ID=
LINKEDIN_CLIENT_SECRET=
LINKEDIN_ACCESS_TOKEN=
META_APP_ID=
META_APP_SECRET=
META_ACCESS_TOKEN=
YOUTUBE_API_KEY=
TIKTOK_ACCESS_TOKEN=
# Optional: Ollama endpoint (default local)
OLLAMA_BASE_URL=http://localhost:11434
# Redis (if used)
REDIS_URL=redis://localhost:6379/0
EOF

# requirements.txt - core dependencies
cat > requirements.txt << 'EOF'
# Core AI frameworks
langchain>=0.3.0
langgraph>=0.2.0
langsmith>=0.1.0
crewai>=0.70.0
# LLM providers
openai>=1.0.0
groq>=0.9.0
ollama>=0.3.0
# Social media APIs
tweepy>=4.14.0
python-linkedin>=1.5.0
requests>=2.31.0
google-api-python-client>=2.108.0
# Scheduler & queue
apscheduler>=3.10.0
redis>=5.0.0
rq>=1.15.0
# Web search & utilities
duckduckgo-search>=5.0.0
beautifulsoup4>=4.12.0
Pillow>=10.0.0
# UI
streamlit>=1.32.0
gradio>=4.0.0
# Misc
python-dotenv>=1.0.0
pydantic>=2.0.0
loguru>=0.7.0
EOF

# docker-compose.yml (Redis + optional Ollama)
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    container_name: social_redis
    ports:
      - "6379:6379"
    restart: unless-stopped

  ollama:
    image: ollama/ollama:latest
    container_name: social_ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    restart: unless-stopped
    # Uncomment to pull a model on startup (e.g., llama3.2)
    # command: sh -c "ollama pull llama3.2 && ollama serve"

volumes:
  ollama_data:
EOF

# README.md
cat > README.md << 'EOF'
# Social Media AI Posting System

Automated social media posting using CrewAI, LangGraph, and local/cloud LLMs.

## Quick Start
1. Copy `.env` and fill in your API keys.
2. Run `python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`
3. Start services: `docker-compose up -d` (Redis and optional Ollama)
4. Launch UI: `streamlit run ui/app.py` or `python ui/app.py`

## Project Structure
See the original hierarchy – fully generated by `setup_project.sh`.

## Supported Platforms
Twitter, LinkedIn, Instagram, Facebook, Threads, YouTube, TikTok.
EOF

# config/settings.py
cat > config/settings.py << 'EOF'
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # LLM choices
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")  # ollama, openai, groq
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-70b-8192")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    # Social Media (partial example)
    TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
    # ... add all others as needed

    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

settings = Settings()
EOF

# config/platforms.py
cat > config/platforms.py << 'EOF'
PLATFORM_CONFIG = {
    "twitter": {"enabled": True, "max_length": 280},
    "linkedin": {"enabled": True, "max_length": 3000},
    "instagram": {"enabled": True, "supports_images": True},
    "facebook": {"enabled": True},
    "threads": {"enabled": True},
    "youtube": {"enabled": False, "requires_video": True},
    "tiktok": {"enabled": False, "requires_video": True},
}
EOF

# core/llm_factory.py
cat > core/llm_factory.py << 'EOF'
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from config.settings import settings

def get_llm(temperature=0.7):
    provider = settings.LLM_PROVIDER
    if provider == "openai":
        return ChatOpenAI(model=settings.OPENAI_MODEL, temperature=temperature, api_key=settings.OPENAI_API_KEY)
    elif provider == "groq":
        return ChatGroq(model=settings.GROQ_MODEL, temperature=temperature, api_key=settings.GROQ_API_KEY)
    else:  # default ollama
        return ChatOllama(model=settings.OLLAMA_MODEL, base_url=settings.OLLAMA_BASE_URL, temperature=temperature)
EOF

# platforms/base.py (abstract poster)
cat > platforms/base.py << 'EOF'
from abc import ABC, abstractmethod

class BasePoster(ABC):
    @abstractmethod
    def post(self, content: str, media_path: str = None) -> dict:
        """Post content to platform, return response."""
        pass
EOF

# scheduler/scheduler.py
cat > scheduler/scheduler.py << 'EOF'
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = BackgroundScheduler()

def schedule_job(func, cron_expression: str, job_id: str):
    trigger = CronTrigger.from_crontab(cron_expression)
    scheduler.add_job(func, trigger, id=job_id, replace_existing=True)
    return job_id

def start_scheduler():
    scheduler.start()
EOF

# utils/logger.py
cat > utils/logger.py << 'EOF'
from loguru import logger
import sys

logger.add(sys.stdout, level="INFO")
logger.add("logs/app.log", rotation="1 day", retention="7 days")

def get_logger(name=None):
    return logger.bind(name=name)
EOF

# ui/app.py (Streamlit example)
cat > ui/app.py << 'EOF'
import streamlit as st
from core.llm_factory import get_llm

st.title("Social Media AI Posting System")
st.write("Generate and schedule posts using CrewAI + LangGraph")

if st.button("Generate Post"):
    llm = get_llm()
    st.write("LLM ready. (Full CrewAI integration coming soon)")
EOF

# Make scripts executable (if any)
chmod +x ui/app.py 2>/dev/null || true

# -----------------------------------------------------------------------------
# Virtual environment and dependencies
# -----------------------------------------------------------------------------
log_info "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

log_info "Upgrading pip and installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

# -----------------------------------------------------------------------------
# Git initialization (optional)
# -----------------------------------------------------------------------------
if confirm "Initialize a Git repository in this project?"; then
    git init
    echo "venv/" > .gitignore
    echo "__pycache__/" >> .gitignore
    echo "*.pyc" >> .gitignore
    echo ".env" >> .gitignore
    echo "logs/" >> .gitignore
    git add .
    git commit -m "Initial project structure from setup script"
    log_info "Git initialized and first commit created."
fi

# -----------------------------------------------------------------------------
# Final instructions
# -----------------------------------------------------------------------------
cat << EOF

${GREEN}✅ Project setup complete!${NC}

Next steps:
1. cd $PROJECT_ROOT
2. Edit the .env file with your API keys.
3. Activate the virtual environment: source venv/bin/activate
4. (Optional) Start Docker services: docker-compose up -d
5. Run the UI: streamlit run ui/app.py

Project location: $PROJECT_ROOT

Happy posting!
EOF

exit 0