# Quick Start Implementation Guide
## Building Your First Autonomous Social Media Agent

This guide provides **ready-to-run code** to get your agent system operational in under 30 minutes.

---

## 🚀 Prerequisites

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install core dependencies
pip install crewai crewai-tools langgraph langchain langchain-openai
pip install tweepy aiohttp pydantic python-dotenv redis
pip install fastapi uvicorn
```

### 2. Get API Credentials

#### OpenAI (for LLM):
- Sign up at https://platform.openai.com
- Get API key from https://platform.openai.com/api-keys

#### GitHub:
- Go to https://github.com/settings/tokens
- Generate personal access token with `repo` and `user` scopes

#### LinkedIn:
- Create app at https://developer.linkedin.com
- Request `w_member_social` product access
- Generate OAuth 2.0 credentials

#### X/Twitter (Optional - costs $200/month for Basic tier):
- Apply at https://developer.x.com
- Create app and get OAuth 1.0a credentials

#### Instagram (Optional):
- Create Facebook App at https://developers.facebook.com
- Add Instagram API product
- Link Instagram Business account to Facebook Page

### 3. Create .env File

```bash
# .env
OPENAI_API_KEY=sk-...
GITHUB_TOKEN=ghp_...
LINKEDIN_ACCESS_TOKEN=...
LINKEDIN_USER_URN=...
REDIS_URL=redis://localhost:6379/0
```

---

## 📝 Minimal Working Example (GitHub → LinkedIn Only)

This is the **absolute minimum** to get started:

```python
# minimal_agent.py
import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai_tools import tool
import aiohttp
import asyncio

# Load environment variables
load_dotenv()

# ===================
# 1. DEFINE TOOLS
# ===================

@tool
async def analyze_github_repo(repo_url: str) -> dict:
    """Analyze a GitHub repository and extract key information"""
    # Extract owner/repo from URL
    parts = repo_url.rstrip('/').split('/')
    owner, repo = parts[-2], parts[-1]
    
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"token {os.getenv('GITHUB_TOKEN')}"}
        
        # Get repo data
        async with session.get(
            f"https://api.github.com/repos/{owner}/{repo}",
            headers=headers
        ) as response:
            data = await response.json()
        
        # Get languages
        async with session.get(
            f"https://api.github.com/repos/{owner}/{repo}/languages",
            headers=headers
        ) as response:
            languages = await response.json()
    
    return {
        "name": data.get("name"),
        "description": data.get("description"),
        "stars": data.get("stargazers_count"),
        "forks": data.get("forks_count"),
        "language": data.get("language"),
        "languages": list(languages.keys()),
        "topics": data.get("topics", []),
        "url": data.get("html_url")
    }

@tool
async def publish_to_linkedin(text: str) -> dict:
    """Publish a post to LinkedIn"""
    async with aiohttp.ClientSession() as session:
        headers = {
            "Authorization": f"Bearer {os.getenv('LINKEDIN_ACCESS_TOKEN')}",
            "Content-Type": "application/json",
            "LinkedIn-Version": "202501",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        payload = {
            "author": f"urn:li:person:{os.getenv('LINKEDIN_USER_URN')}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        async with session.post(
            "https://api.linkedin.com/v2/ugcPosts",
            headers=headers,
            json=payload
        ) as response:
            if response.status == 201:
                data = await response.json()
                return {"success": True, "post_id": data.get("id")}
            else:
                error = await response.text()
                return {"success": False, "error": error}

# ===================
# 2. CREATE AGENTS
# ===================

# Agent 1: Analyze GitHub repository
analyzer = Agent(
    role="GitHub Repository Analyst",
    goal="Extract meaningful insights from GitHub repositories",
    backstory="Expert software engineer who identifies key technical highlights",
    tools=[analyze_github_repo],
    verbose=True
)

# Agent 2: Write LinkedIn post
writer = Agent(
    role="LinkedIn Content Writer",
    goal="Create engaging LinkedIn posts about technical projects",
    backstory="Technical writer who makes complex engineering topics accessible",
    verbose=True,
    llm="gpt-4o"  # Specify model
)

# Agent 3: Publish to LinkedIn
publisher = Agent(
    role="LinkedIn Publisher",
    goal="Reliably publish content to LinkedIn",
    backstory="Automation specialist ensuring zero-downtime publishing",
    tools=[publish_to_linkedin],
    verbose=True
)

# ===================
# 3. DEFINE TASKS
# ===================

analyze_task = Task(
    description="""
    Analyze the GitHub repository at {repo_url}.
    Extract: name, description, stars, tech stack, and what makes it interesting.
    """,
    agent=analyzer,
    expected_output="JSON with repository insights"
)

write_task = Task(
    description="""
    Based on the repository analysis, write an engaging LinkedIn post.
    
    Requirements:
    - 1300-1700 characters
    - Start with a compelling hook
    - Highlight the technical innovation
    - Include 3-5 relevant hashtags
    - Professional but conversational tone
    """,
    agent=writer,
    expected_output="LinkedIn post text (1300-1700 chars)",
    context=[analyze_task]  # Depends on analysis
)

publish_task = Task(
    description="""
    Publish the LinkedIn post using the publish_to_linkedin tool.
    Pass the post text exactly as written.
    """,
    agent=publisher,
    expected_output="Publication result with status",
    context=[write_task]
)

# ===================
# 4. CREATE CREW
# ===================

crew = Crew(
    agents=[analyzer, writer, publisher],
    tasks=[analyze_task, write_task, publish_task],
    process=Process.sequential,  # Execute in order
    verbose=True
)

# ===================
# 5. RUN THE CREW
# ===================

async def main():
    result = await crew.kickoff_async(
        inputs={"repo_url": "https://github.com/langchain-ai/langgraph"}
    )
    print("\n" + "="*50)
    print("FINAL RESULT:")
    print("="*50)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

### Run It:

```bash
# Start Redis (required for some tools)
docker run -d -p 6379:6379 redis:7-alpine

# Run the agent
python minimal_agent.py
```

**Expected Output**:
```
> Entering new CrewAgentExecutor chain...
Analyzing repository...
[Tool: analyze_github_repo] Retrieved data for langchain-ai/langgraph
Writing LinkedIn post...
[Agent: writer] Generated 1450 character post
Publishing to LinkedIn...
[Tool: publish_to_linkedin] Post published successfully
Final Answer: Post published with ID: urn:li:share:123456789
```

---

## 🎯 Production-Ready Version with LangGraph

Now let's add proper workflow management with LangGraph:

```python
# production_agent.py
import os
import asyncio
from typing import TypedDict, Literal, Optional, List
from datetime import datetime
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from crewai import Agent, Task, Crew, Process
from crewai_tools import tool

load_dotenv()

# ===================
# 1. STATE DEFINITION
# ===================

class AgentState(TypedDict):
    # Input
    github_repo_url: str
    target_platforms: List[str]
    
    # Analysis results
    repo_analysis: Optional[dict]
    
    # Content
    linkedin_post: Optional[str]
    
    # Publishing results
    publish_results: dict
    
    # Metadata
    workflow_id: str
    status: Literal["pending", "analyzing", "generating", "publishing", "completed", "failed"]
    errors: List[str]
    current_step: str

# ===================
# 2. TOOLS (same as before)
# ===================

@tool
async def analyze_github_repo(repo_url: str) -> dict:
    """Analyze GitHub repository"""
    parts = repo_url.rstrip('/').split('/')
    owner, repo = parts[-2], parts[-1]
    
    import aiohttp
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"token {os.getenv('GITHUB_TOKEN')}"}
        async with session.get(
            f"https://api.github.com/repos/{owner}/{repo}",
            headers=headers
        ) as response:
            data = await response.json()
        
        async with session.get(
            f"https://api.github.com/repos/{owner}/{repo}/languages",
            headers=headers
        ) as response:
            languages = await response.json()
    
    return {
        "name": data.get("name"),
        "description": data.get("description"),
        "stars": data.get("stargazers_count"),
        "forks": data.get("forks_count"),
        "language": data.get("language"),
        "languages": list(languages.keys()),
        "topics": data.get("topics", []),
        "url": data.get("html_url"),
        "created_at": data.get("created_at")
    }

@tool
async def publish_to_linkedin(text: str) -> dict:
    """Publish to LinkedIn"""
    import aiohttp
    async with aiohttp.ClientSession() as session:
        headers = {
            "Authorization": f"Bearer {os.getenv('LINKEDIN_ACCESS_TOKEN')}",
            "Content-Type": "application/json",
            "LinkedIn-Version": "202501",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        payload = {
            "author": f"urn:li:person:{os.getenv('LINKEDIN_USER_URN')}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        async with session.post(
            "https://api.linkedin.com/v2/ugcPosts",
            headers=headers,
            json=payload
        ) as response:
            if response.status == 201:
                data = await response.json()
                return {"success": True, "post_id": data.get("id")}
            else:
                return {"success": False, "error": await response.text()}

# ===================
# 3. WORKFLOW NODES
# ===================

class SocialMediaWorkflow:
    def __init__(self):
        # Initialize agents
        self.analyzer = Agent(
            role="GitHub Repository Analyst",
            goal="Extract meaningful insights from GitHub repositories",
            tools=[analyze_github_repo],
            verbose=True
        )
        
        self.writer = Agent(
            role="LinkedIn Content Writer",
            goal="Create engaging LinkedIn posts",
            verbose=True,
            llm="gpt-4o"
        )
        
        self.publisher = Agent(
            role="LinkedIn Publisher",
            goal="Publish content to LinkedIn",
            tools=[publish_to_linkedin],
            verbose=True
        )
        
        # Create workflow graph
        self.graph = StateGraph(AgentState)
        self._build_graph()
    
    def _build_graph(self):
        """Build the LangGraph workflow"""
        # Add nodes
        self.graph.add_node("analyze", self.analyze_node)
        self.graph.add_node("generate", self.generate_node)
        self.graph.add_node("publish", self.publish_node)
        
        # Define edges
        self.graph.set_entry_point("analyze")
        self.graph.add_edge("analyze", "generate")
        self.graph.add_edge("generate", "publish")
        self.graph.add_edge("publish", END)
        
        # Compile with checkpointing
        checkpointer = SqliteSaver.from_conn_string("checkpoints.db")
        self.app = self.graph.compile(checkpointer=checkpointer)
    
    async def analyze_node(self, state: AgentState) -> AgentState:
        """Node 1: Analyze GitHub repository"""
        print("\n[ANALYZE] Starting GitHub analysis...")
        state["current_step"] = "analyze"
        state["status"] = "analyzing"
        
        try:
            # Create analysis crew
            crew = Crew(
                agents=[self.analyzer],
                tasks=[
                    Task(
                        description=f"Analyze repository: {state['github_repo_url']}",
                        agent=self.analyzer,
                        expected_output="Repository analysis JSON"
                    )
                ],
                process=Process.sequential,
                verbose=True
            )
            
            result = await crew.kickoff_async(
                inputs={"repo_url": state["github_repo_url"]}
            )
            
            state["repo_analysis"] = result
            print(f"[ANALYZE] ✓ Analysis complete: {result}")
        
        except Exception as e:
            state["errors"].append(f"Analysis failed: {str(e)}")
            state["status"] = "failed"
            print(f"[ANALYZE] ✗ Failed: {e}")
        
        return state
    
    async def generate_node(self, state: AgentState) -> AgentState:
        """Node 2: Generate LinkedIn content"""
        print("\n[GENERATE] Creating LinkedIn post...")
        state["current_step"] = "generate"
        state["status"] = "generating"
        
        if not state.get("repo_analysis"):
            state["errors"].append("No analysis data available")
            state["status"] = "failed"
            return state
        
        try:
            crew = Crew(
                agents=[self.writer],
                tasks=[
                    Task(
                        description=f"""
                        Write an engaging LinkedIn post based on this analysis:
                        {state['repo_analysis']}
                        
                        Requirements:
                        - 1300-1700 characters
                        - Compelling hook
                        - Highlight technical innovation
                        - 3-5 hashtags
                        - Professional tone
                        """,
                        agent=self.writer,
                        expected_output="LinkedIn post text"
                    )
                ],
                process=Process.sequential,
                verbose=True
            )
            
            result = await crew.kickoff_async(inputs=state)
            state["linkedin_post"] = result
            print(f"[GENERATE] ✓ Post created ({len(result)} chars)")
        
        except Exception as e:
            state["errors"].append(f"Generation failed: {str(e)}")
            state["status"] = "failed"
            print(f"[GENERATE] ✗ Failed: {e}")
        
        return state
    
    async def publish_node(self, state: AgentState) -> AgentState:
        """Node 3: Publish to LinkedIn"""
        print("\n[PUBLISH] Publishing to LinkedIn...")
        state["current_step"] = "publish"
        state["status"] = "publishing"
        
        if not state.get("linkedin_post"):
            state["errors"].append("No content to publish")
            state["status"] = "failed"
            return state
        
        try:
            crew = Crew(
                agents=[self.publisher],
                tasks=[
                    Task(
                        description=f"Publish this post to LinkedIn: {state['linkedin_post']}",
                        agent=self.publisher,
                        expected_output="Publication result"
                    )
                ],
                process=Process.sequential,
                verbose=True
            )
            
            result = await crew.kickoff_async(inputs=state)
            state["publish_results"]["linkedin"] = result
            state["status"] = "completed"
            print(f"[PUBLISH] ✓ Published successfully")
        
        except Exception as e:
            state["errors"].append(f"Publishing failed: {str(e)}")
            state["status"] = "failed"
            print(f"[PUBLISH] ✗ Failed: {e}")
        
        return state
    
    async def run(self, repo_url: str, workflow_id: str):
        """Execute the workflow"""
        initial_state: AgentState = {
            "github_repo_url": repo_url,
            "target_platforms": ["linkedin"],
            "repo_analysis": None,
            "linkedin_post": None,
            "publish_results": {},
            "workflow_id": workflow_id,
            "status": "pending",
            "errors": [],
            "current_step": "init"
        }
        
        config = {"configurable": {"thread_id": workflow_id}}
        
        print(f"\n{'='*60}")
        print(f"WORKFLOW STARTED: {workflow_id}")
        print(f"Repository: {repo_url}")
        print(f"{'='*60}")
        
        final_state = await self.app.ainvoke(initial_state, config)
        
        print(f"\n{'='*60}")
        print(f"WORKFLOW COMPLETED: {final_state['status']}")
        print(f"{'='*60}")
        
        if final_state["errors"]:
            print(f"\nErrors: {final_state['errors']}")
        
        if final_state.get("publish_results"):
            print(f"\nPublish Results:")
            for platform, result in final_state["publish_results"].items():
                print(f"  {platform}: {result}")
        
        return final_state

# ===================
# 4. MAIN EXECUTION
# ===================

async def main():
    workflow = SocialMediaWorkflow()
    
    # Run workflow
    await workflow.run(
        repo_url="https://github.com/langchain-ai/langgraph",
        workflow_id="demo-001"
    )

if __name__ == "__main__":
    asyncio.run(main())
```

### Run It:

```bash
python production_agent.py
```

**Expected Output**:
```
============================================================
WORKFLOW STARTED: demo-001
Repository: https://github.com/langchain-ai/langgraph
============================================================

[ANALYZE] Starting GitHub analysis...
> Entering new CrewAgentExecutor chain...
[Tool: analyze_github_repo] Retrieved repo data
[ANALYZE] ✓ Analysis complete: {...}

[GENERATE] Creating LinkedIn post...
> Entering new CrewAgentExecutor chain...
[Agent: writer] Generating post...
[GENERATE] ✓ Post created (1456 chars)

[PUBLISH] Publishing to LinkedIn...
> Entering new CrewAgentExecutor chain...
[Tool: publish_to_linkedin] Publishing...
[PUBLISH] ✓ Published successfully

============================================================
WORKFLOW COMPLETED: completed
============================================================

Publish Results:
  linkedin: {'success': True, 'post_id': 'urn:li:share:123456789'}
```

---

## 📊 Add Observability (LangSmith)

```python
# Add to the top of your file
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "social-media-agents"
os.environ["LANGCHAIN_API_KEY"] = "your-langsmith-key"

# That's it! All agent executions are now traced
```

Visit https://smith.langchain.com to see:
- Full execution traces
- LLM calls and costs
- Tool invocations
- Error debugging

---

## 🔄 Add X/Twitter Support

```python
# Add this tool
@tool
async def publish_to_twitter(text: str) -> dict:
    """Publish tweet to X/Twitter"""
    import tweepy
    
    auth = tweepy.OAuth1UserHandler(
        os.getenv("TWITTER_API_KEY"),
        os.getenv("TWITTER_API_SECRET"),
        os.getenv("TWITTER_ACCESS_TOKEN"),
        os.getenv("TWITTER_ACCESS_SECRET")
    )
    client = tweepy.Client(
        consumer_key=os.getenv("TWITTER_API_KEY"),
        consumer_secret=os.getenv("TWITTER_API_SECRET"),
        access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
        access_token_secret=os.getenv("TWITTER_ACCESS_SECRET")
    )
    
    try:
        response = client.create_tweet(text=text)
        return {
            "success": True,
            "tweet_id": response.data['id'],
            "url": f"https://twitter.com/i/web/status/{response.data['id']}"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# Add Twitter writer agent
twitter_writer = Agent(
    role="Twitter Content Specialist",
    goal="Create engaging tweets and threads",
    verbose=True,
    llm="gpt-4o"
)

# Add Twitter publisher
twitter_publisher = Agent(
    role="Twitter Publisher",
    goal="Publish tweets reliably",
    tools=[publish_to_twitter],
    verbose=True
)
```

---

## 📸 Add Instagram Support

```python
@tool
async def publish_to_instagram(image_url: str, caption: str) -> dict:
    """Publish image post to Instagram"""
    import aiohttp
    
    access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    account_id = os.getenv("INSTAGRAM_ACCOUNT_ID")
    
    async with aiohttp.ClientSession() as session:
        # Step 1: Create media container
        async with session.post(
            f"https://graph.facebook.com/v21.0/{account_id}/media",
            params={
                "image_url": image_url,
                "caption": caption,
                "access_token": access_token
            }
        ) as response:
            container_data = await response.json()
            container_id = container_data["id"]
        
        # Step 2: Wait for processing
        await asyncio.sleep(5)
        
        # Step 3: Publish
        async with session.post(
            f"https://graph.facebook.com/v21.0/{account_id}/media_publish",
            params={
                "creation_id": container_id,
                "access_token": access_token
            }
        ) as response:
            result = await response.json()
            return {"success": True, "post_id": result["id"]}
```

---

## 🧪 Testing

```python
# test_workflow.py
import pytest
from production_agent import SocialMediaWorkflow

@pytest.mark.asyncio
async def test_analysis_node():
    workflow = SocialMediaWorkflow()
    
    state = {
        "github_repo_url": "https://github.com/langchain-ai/langgraph",
        "repo_analysis": None,
        "errors": []
    }
    
    result = await workflow.analyze_node(state)
    
    assert result["repo_analysis"] is not None
    assert len(result["errors"]) == 0
    assert "name" in result["repo_analysis"]

# Run tests
# pytest test_workflow.py -v
```

---

## 🚀 Deploy with Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN pip install crewai crewai-tools langgraph langchain \
    langchain-openai tweepy aiohttp redis python-dotenv

COPY . .

CMD ["python", "production_agent.py"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    env_file: .env
    depends_on:
      - redis
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

```bash
docker-compose up
```

---

## 📈 Next Steps

1. **Add More Platforms**: Instagram, TikTok, Medium
2. **Schedule Posts**: Add Celery for background jobs
3. **Add Analytics**: Track engagement metrics
4. **Content Moderation**: Filter profanity/sensitive content
5. **A/B Testing**: Test different post variations
6. **Multi-Repo Analysis**: Process multiple repos in parallel

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'crewai'"
```bash
pip install crewai crewai-tools
```

### "LinkedIn API Error: 401 Unauthorized"
- Token expired (refresh every 60 days)
- Wrong user URN
- Missing permissions

### "Rate limit exceeded"
- Implement exponential backoff
- Use Redis for rate limiting
- Check platform limits (LinkedIn: 100/hour)

### "Workflow stuck at checkpointing"
```bash
rm checkpoints.db  # Delete checkpoint DB
```

---

## 💡 Pro Tips

1. **Start Simple**: Test with just LinkedIn first
2. **Use LangSmith**: Essential for debugging agents
3. **Mock APIs in Dev**: Use fake publishers for testing
4. **Monitor Token Usage**: LLM costs add up quickly
5. **Implement Retries**: Networks fail, plan for it
6. **Cache Results**: Don't re-analyze same repo
7. **Version Your Prompts**: Track what works

---

## 📚 Further Reading

- **CrewAI Docs**: https://docs.crewai.com
- **LangGraph Tutorial**: https://langchain-ai.github.io/langgraph/tutorials/
- **Platform APIs**:
  - LinkedIn: https://learn.microsoft.com/en-us/linkedin/
  - X: https://developer.x.com
  - Instagram: https://developers.facebook.com/docs/instagram-platform

---

**Happy Building! 🎉**

Questions? Check the main architecture doc or reach out to the community.
