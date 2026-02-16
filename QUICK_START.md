# Quick Start Guide - Autonomous Social Media AI Agent System

## Overview

This guide will help you set up and run the autonomous social media agent system in under 30 minutes.

---

## Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (recommended)
- GitHub Account
- LinkedIn Developer Account
- X (Twitter) Developer Account
- Instagram Business Account

---

## 1. Installation

### Option A: Docker Compose (Recommended)

```bash
# Clone or create project
mkdir social-agent-system
cd social-agent-system

# Copy the design files
# (Copy the main.py, requirements.txt, and design document)

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env

# Start services
docker-compose up -d

# View logs
docker-compose logs -f app
```

### Option B: Manual Installation

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up database
./scripts/setup_database.py

# Configure environment
cp .env.example .env
nano .env
```

---

## 2. API Setup

### GitHub API

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo`, `user`
4. Copy token to `.env` as `GITHUB_TOKEN`

### LinkedIn API

1. Go to: https://www.linkedin.com/developers/apps
2. Create new app
3. Add Products: "Sign In with LinkedIn using OpenID Connect"
4. Get credentials:
   - Client ID → `LINKEDIN_CLIENT_ID`
   - Client Secret → `LINKEDIN_CLIENT_SECRET`
5. OAuth redirect: `http://localhost:8000/callback`
6. Generate access token:
   ```bash
   python scripts/linkedin_oauth.py
   ```

### X (Twitter) API

1. Go to: https://developer.x.com
2. Create project and app
3. Get credentials from "Keys and tokens":
   - API Key → `X_API_KEY`
   - API Secret → `X_API_SECRET`
   - Access Token → `X_ACCESS_TOKEN`
   - Access Token Secret → `X_ACCESS_TOKEN_SECRET`
   - Bearer Token → `X_BEARER_TOKEN`

### Instagram API

1. Go to: https://developers.facebook.com
2. Create new app
3. Add "Instagram Graph API" product
4. Connect Instagram Business Account
5. Generate access token:
   - App ID → `INSTAGRAM_APP_ID`
   - App Secret → `INSTAGRAM_APP_SECRET`
   - Access Token → `INSTAGRAM_ACCESS_TOKEN`
   - Account ID → `INSTAGRAM_ACCOUNT_ID`

### LLM Provider (Anthropic)

1. Go to: https://console.anthropic.com
2. Create API key
3. Copy to `.env` as `ANTHROPIC_API_KEY`

---

## 3. Environment Configuration

### Complete .env File

```bash
# GitHub
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx

# LinkedIn
LINKEDIN_CLIENT_ID=xxxxxxxxxxxx
LINKEDIN_CLIENT_SECRET=xxxxxxxxxxxx
LINKEDIN_ACCESS_TOKEN=xxxxxxxxxxxx
LINKEDIN_REFRESH_TOKEN=xxxxxxxxxxxx

# X (Twitter)
X_API_KEY=xxxxxxxxxxxx
X_API_SECRET=xxxxxxxxxxxx
X_ACCESS_TOKEN=xxxxxxxxxxxx
X_ACCESS_TOKEN_SECRET=xxxxxxxxxxxx
X_BEARER_TOKEN=xxxxxxxxxxxx

# Instagram
INSTAGRAM_APP_ID=xxxxxxxxxxxx
INSTAGRAM_APP_SECRET=xxxxxxxxxxxx
INSTAGRAM_ACCESS_TOKEN=xxxxxxxxxxxx
INSTAGRAM_ACCOUNT_ID=xxxxxxxxxxxx

# LLM
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx
LLM_MODEL=claude-sonnet-4-20250514

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/social_agent
REDIS_URL=redis://localhost:6379/0

# Observability (Optional)
LANGSMITH_API_KEY=lsv2_xxxxxxxxxxxx
SENTRY_DSN=https://xxxxxxxxxxxx@sentry.io/xxxxxxxxxxxx

# Environment
ENVIRONMENT=development
DEBUG=false
LOG_LEVEL=INFO
```

---

## 4. Database Setup

### Create Database

```bash
# Using Docker
docker-compose up -d postgres redis

# Or manually
createdb social_agent
redis-server
```

### Run Migrations

```bash
# Initialize database
python scripts/setup_database.py

# Or use alembic
alembic upgrade head
```

---

## 5. Running the System

### Basic Usage

```bash
python main.py \
  --repo https://github.com/langchain-ai/langgraph \
  --username langchain-ai \
  --platforms linkedin twitter instagram
```

### Dry Run (No Publishing)

```bash
python main.py \
  --repo https://github.com/facebook/react \
  --username facebook \
  --dry-run
```

### Single Platform

```bash
python main.py \
  --repo https://github.com/openai/gpt-4 \
  --username openai \
  --platforms linkedin
```

---

## 6. Programmatic Usage

### Python Script Example

```python
import asyncio
from main import SocialAgentOrchestrator

async def run_analysis():
    orchestrator = SocialAgentOrchestrator()
    
    await orchestrator.initialize()
    
    result = await orchestrator.run_workflow(
        github_repo_url="https://github.com/anthropics/anthropic-sdk-python",
        github_username="anthropics",
        platforms=["linkedin", "twitter"]
    )
    
    print(f"Published {len(result['published_posts'])} posts")
    return result

if __name__ == "__main__":
    asyncio.run(run_analysis())
```

---

## 7. Testing

### Run Tests

```bash
# All tests
pytest

# Specific test suite
pytest tests/test_integrations.py

# With coverage
pytest --cov=. --cov-report=html
```

### Test Individual Components

```bash
# Test GitHub connection
python scripts/test_github.py

# Test social media connections
python scripts/test_social_apis.py

# Test LLM connection
python scripts/test_llm.py
```

---

## 8. Monitoring

### View Logs

```bash
# Docker
docker-compose logs -f app

# Local
tail -f logs/app.log
```

### LangSmith Dashboard

1. Go to: https://smith.langchain.com
2. View traces in your project
3. Monitor agent performance

### Metrics

```bash
# View workflow metrics
python scripts/view_metrics.py --workflow-id <id>

# Export analytics
python scripts/export_analytics.py --days 7
```

---

## 9. Common Issues

### Rate Limiting

**Problem**: "Rate limit exceeded" errors

**Solution**:
```python
# Adjust rate limits in config/settings.py
LINKEDIN_RATE_LIMIT_REQUESTS = 50  # Reduce from 100
X_RATE_LIMIT_POSTS = 25  # Reduce from 50
```

### Token Expiration

**Problem**: "Invalid access token" errors

**Solution**:
```bash
# Refresh tokens
python scripts/refresh_tokens.py
```

### Database Connection

**Problem**: "Connection refused" errors

**Solution**:
```bash
# Check database is running
docker-compose ps

# Restart services
docker-compose restart postgres redis
```

---

## 10. Production Deployment

### Kubernetes

```bash
# Create secrets
kubectl create secret generic agent-secrets --from-env-file=.env

# Deploy
kubectl apply -f k8s/

# Check status
kubectl get pods -l app=social-agent
```

### AWS ECS

```bash
# Build and push image
docker build -t social-agent:latest .
docker tag social-agent:latest <ecr-url>/social-agent:latest
docker push <ecr-url>/social-agent:latest

# Deploy using CloudFormation or Terraform
terraform apply
```

---

## 11. Customization

### Adding New Platforms

1. Create client in `integrations/new_platform.py`
2. Implement publisher interface
3. Register in `MultiPlatformPublisher`
4. Update workflow graph

### Custom Content Strategies

```python
# crews/content_crew/agents.py
custom_agent = Agent(
    role="Custom Content Strategist",
    goal="Create content for specific audience",
    backstory="...",
    tools=[...],
    llm=llm
)
```

### Custom Analysis

```python
# crews/github_crew/agents.py
security_analyst = Agent(
    role="Security Analyst",
    goal="Analyze repository security",
    tools=[security_scanner_tool],
    llm=llm
)
```

---

## 12. Best Practices

### Rate Limiting

- Monitor API usage daily
- Implement exponential backoff
- Use queue for high-volume scenarios

### Error Handling

- Always use try-except blocks
- Log errors with context
- Implement circuit breakers

### Content Quality

- Review generated content before publishing
- A/B test different styles
- Monitor engagement metrics

### Security

- Never commit .env files
- Rotate API keys regularly
- Use environment-specific configs

---

## 13. Resources

### Documentation

- [Full System Design](./autonomous_social_agent_system_design.md)
- [API Reference](./docs/api-reference.md)
- [Architecture Guide](./docs/architecture.md)

### Community

- GitHub Issues: Report bugs or request features
- Discord: Join our community
- Blog: Latest updates and tutorials

### Support

- Email: support@example.com
- Slack: #social-agent-support
- Office Hours: Tuesdays 2-3 PM EST

---

## 14. Next Steps

1. **Week 1**: Set up basic workflow
2. **Week 2**: Customize content strategies
3. **Week 3**: Add analytics and monitoring
4. **Week 4**: Optimize and scale

---

## Troubleshooting Checklist

- [ ] All API credentials configured in .env
- [ ] Database and Redis running
- [ ] Dependencies installed (`pip list`)
- [ ] Firewall allows outbound HTTPS
- [ ] API rate limits not exceeded
- [ ] Tokens not expired
- [ ] Python version 3.11+
- [ ] Sufficient disk space
- [ ] Network connectivity

---

## Success Metrics

After setup, you should see:

✓ GitHub analysis completing in <30s  
✓ Content generation in <60s  
✓ Publishing to all platforms <90s  
✓ 90%+ success rate  
✓ Zero manual intervention required  

---

For detailed technical information, see the [Full System Design Document](./autonomous_social_agent_system_design.md).

Happy automating! 🚀
