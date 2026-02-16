# Autonomous Social Media AI Agent System Architecture
## Production-Grade Multi-Agent System for GitHub Analysis & Social Media Publishing

---

## 📋 Executive Summary

This document presents a production-ready, fully autonomous AI agent system that:
1. Analyzes GitHub repositories and profiles
2. Generates high-quality, platform-optimized content
3. Automatically publishes to LinkedIn, X (Twitter), and Instagram

**Tech Stack**: CrewAI + LangGraph + LangChain (all free/open-source)  
**Execution Model**: Asynchronous, event-driven  
**Deployment**: Containerized, scalable, observable

---

## 🏗️ System Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Orchestration Layer                      │
│  ┌──────────────────────┐  ┌──────────────────────────┐    │
│  │   LangGraph Flow     │  │   CrewAI Coordinator    │    │
│  │  (State Machine)     │  │   (Agent Manager)       │    │
│  └──────────────────────┘  └──────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
┌───────────────▼────┐ ┌─────▼──────┐ ┌───▼────────────┐
│  GitHub Analysis   │ │  Content   │ │  Publishing    │
│     Agents         │ │ Generation │ │    Agents      │
│  ┌──────────────┐  │ │  Agents    │ │ ┌────────────┐ │
│  │ Repo Analyzer│  │ │            │ │ │ LinkedIn   │ │
│  │ Profile      │  │ │            │ │ │ X/Twitter  │ │
│  │ Reader       │  │ │            │ │ │ Instagram  │ │
│  └──────────────┘  │ │            │ │ └────────────┘ │
└────────────────────┘ └────────────┘ └────────────────┘
         │                   │                │
         └───────────────────┼────────────────┘
                             │
                    ┌────────▼─────────┐
                    │  Shared State    │
                    │  Management      │
                    │  (Redis/SQLite)  │
                    └──────────────────┘
                             │
                    ┌────────▼─────────┐
                    │  Observability   │
                    │  (LangSmith)     │
                    └──────────────────┘
```

### Design Principles (2025 Best Practices)

1. **Deterministic Backbone with Intelligence at Edges**: LangGraph provides structured workflow control while agents handle intelligent decision-making
2. **Agentic Systems Pattern**: Combines flow-based orchestration with multi-agent collaboration (as recommended by CrewAI in Dec 2025)
3. **Async-First**: All I/O operations are asynchronous for maximum throughput
4. **State Persistence**: Checkpointing at each major step for fault tolerance
5. **Observable by Default**: LangSmith integration for full execution tracing

---

## 🤖 Agent Roles and Responsibilities

### 1. GitHub Analysis Crew (CrewAI)

#### **Repository Analyzer Agent**
```yaml
role: "Senior Code Repository Analyst"
goal: "Extract meaningful insights from GitHub repositories including tech stack, architecture patterns, code quality, and recent activity"
backstory: "Expert software engineer with 15+ years analyzing codebases. Specializes in identifying architectural decisions and technical highlights."
tools:
  - github_api_tool
  - code_analysis_tool
  - metrics_calculator_tool
reasoning: true  # Enable ReAct pattern for complex analysis
inject_date: true  # Context-aware analysis
```

**Responsibilities**:
- Fetch repository metadata (stars, forks, contributors, languages)
- Analyze code structure and patterns using GitHub API
- Extract README, key files, and documentation
- Identify unique technical innovations
- Calculate repository health metrics

#### **Profile Insights Agent**
```yaml
role: "Developer Relations Specialist"
goal: "Understand developer profiles, contributions, and expertise areas from GitHub activity"
backstory: "Community expert who reads between the lines of commits, issues, and PRs to understand developer impact."
tools:
  - github_graphql_tool
  - contribution_analyzer_tool
reasoning: true
```

**Responsibilities**:
- Analyze commit history and patterns
- Extract contributor expertise areas
- Identify key projects and achievements
- Assess community engagement

### 2. Content Generation Crew (CrewAI)

#### **Content Strategist Agent**
```yaml
role: "Multi-Platform Social Media Strategist"
goal: "Create platform-specific content strategies that maximize engagement while maintaining authentic technical voice"
backstory: "Former developer who became a tech influencer. Knows what resonates on each platform."
reasoning: true
max_reasoning_attempts: 3
```

**Responsibilities**:
- Decide content angles for each platform
- Determine optimal posting times
- Create content calendar
- Define hashtag strategies per platform

#### **LinkedIn Writer Agent**
```yaml
role: "Professional Technical Writer"
goal: "Craft engaging LinkedIn posts that showcase technical depth while remaining accessible"
backstory: "Technical writer who specializes in making complex engineering topics compelling for professional audiences."
tools:
  - llm_tool (GPT-4/Claude for generation)
  - linkedin_character_validator
```

**Output Format**: 
- 1300-1900 characters (optimal for LinkedIn)
- Professional tone with technical credibility
- Story-driven narrative structure
- Industry-relevant hashtags (3-5)

#### **X/Twitter Writer Agent**
```yaml
role: "Tech Twitter Specialist"
goal: "Create punchy, engaging tweets and threads that drive developer engagement"
backstory: "Developer advocate who understands Twitter's fast-paced culture and viral mechanics."
tools:
  - llm_tool
  - twitter_thread_validator
```

**Output Format**:
- Single tweets: 200-280 characters
- Threads: 3-5 tweets with narrative flow
- Developer-friendly tone
- Strategic hashtags (2-3 max)
- Emoji use (1-2 per tweet)

#### **Instagram Caption Writer Agent**
```yaml
role: "Visual Content Creator"
goal: "Write captions that complement technical visuals and drive engagement"
backstory: "Designer who bridges the gap between code and visual storytelling."
tools:
  - llm_tool
  - hashtag_optimizer
```

**Output Format**:
- First line: hook (125 chars)
- Body: 500-1000 characters
- Call-to-action
- Hashtags: 10-20 relevant tags
- Emoji-friendly tone

### 3. Publishing Crew (CrewAI)

#### **LinkedIn Publisher Agent**
```yaml
role: "LinkedIn Automation Specialist"
goal: "Reliably publish content to LinkedIn with proper error handling and retry logic"
backstory: "DevOps engineer who ensures zero-downtime deployments."
tools:
  - linkedin_api_tool
  - media_uploader_tool
```

#### **X Publisher Agent**
```yaml
role: "Twitter API Specialist"
goal: "Navigate X API rate limits and publish content reliably"
tools:
  - x_api_tool
  - thread_publisher_tool
```

#### **Instagram Publisher Agent**
```yaml
role: "Instagram API Specialist"
goal: "Handle Instagram Graph API's media container workflow"
tools:
  - instagram_graph_api_tool
  - media_container_manager
```

---

## 🔄 Workflow Design (LangGraph State Machine)

### State Schema

```python
from typing import TypedDict, List, Optional, Literal
from datetime import datetime

class AgentState(TypedDict):
    # Input
    github_repo_url: str
    github_profile_url: Optional[str]
    target_platforms: List[Literal["linkedin", "twitter", "instagram"]]
    
    # GitHub Analysis Results
    repo_analysis: Optional[dict]
    profile_insights: Optional[dict]
    
    # Content Generation Results
    content_strategy: Optional[dict]
    linkedin_post: Optional[dict]
    twitter_content: Optional[dict]
    instagram_content: Optional[dict]
    
    # Publishing Results
    publish_results: dict
    
    # Metadata
    workflow_id: str
    status: Literal["pending", "analyzing", "generating", "publishing", "completed", "failed"]
    errors: List[str]
    created_at: datetime
    completed_at: Optional[datetime]
    
    # Checkpointing
    last_checkpoint: str
    retry_count: int
```

### LangGraph Workflow Definition

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

class SocialMediaAgentWorkflow:
    def __init__(self):
        # Initialize state graph with checkpointing
        self.checkpointer = SqliteSaver.from_conn_string("workflow_checkpoints.db")
        self.graph = StateGraph(AgentState)
        
        # Define nodes (each maps to agent crew execution)
        self.graph.add_node("analyze_github", self.analyze_github_node)
        self.graph.add_node("generate_content", self.generate_content_node)
        self.graph.add_node("publish_content", self.publish_content_node)
        self.graph.add_node("handle_error", self.error_handler_node)
        
        # Define edges (workflow transitions)
        self.graph.set_entry_point("analyze_github")
        
        self.graph.add_conditional_edges(
            "analyze_github",
            self.should_continue_after_analysis,
            {
                "continue": "generate_content",
                "error": "handle_error"
            }
        )
        
        self.graph.add_conditional_edges(
            "generate_content",
            self.should_continue_after_generation,
            {
                "continue": "publish_content",
                "error": "handle_error"
            }
        )
        
        self.graph.add_conditional_edges(
            "publish_content",
            self.should_complete,
            {
                "complete": END,
                "retry": "publish_content",
                "error": "handle_error"
            }
        )
        
        self.graph.add_edge("handle_error", END)
        
        # Compile with checkpointing
        self.app = self.graph.compile(checkpointer=self.checkpointer)
    
    async def analyze_github_node(self, state: AgentState) -> AgentState:
        """Execute GitHub analysis crew"""
        from crewai import Crew, Process
        
        crew = Crew(
            agents=[self.repo_analyzer, self.profile_insights_agent],
            tasks=[
                Task(
                    description=f"Analyze repository: {state['github_repo_url']}",
                    agent=self.repo_analyzer,
                    expected_output="JSON with repo metrics, tech stack, and insights"
                ),
                Task(
                    description=f"Analyze profile: {state['github_profile_url']}",
                    agent=self.profile_insights_agent,
                    expected_output="JSON with developer expertise and contributions",
                    async_execution=True  # Run in parallel
                )
            ],
            process=Process.parallel,  # Parallel execution
            verbose=True
        )
        
        try:
            result = await crew.kickoff_async(inputs=state)
            state["repo_analysis"] = result["repo_analysis"]
            state["profile_insights"] = result["profile_insights"]
            state["status"] = "analyzing"
            state["last_checkpoint"] = "analyze_complete"
        except Exception as e:
            state["errors"].append(str(e))
            state["status"] = "failed"
        
        return state
    
    async def generate_content_node(self, state: AgentState) -> AgentState:
        """Execute content generation crew"""
        # Use CrewAI with planning enabled for structured content creation
        crew = Crew(
            agents=[
                self.content_strategist,
                self.linkedin_writer,
                self.twitter_writer,
                self.instagram_writer
            ],
            tasks=[...],
            process=Process.sequential,
            planning=True,  # Enable planning for coordinated content
            verbose=True
        )
        
        result = await crew.kickoff_async(inputs=state)
        # Update state with generated content
        return state
    
    async def publish_content_node(self, state: AgentState) -> AgentState:
        """Execute publishing crew with retry logic"""
        # Publisher crew with async execution
        return state
    
    def should_continue_after_analysis(self, state: AgentState) -> str:
        """Conditional routing after analysis"""
        if state.get("errors"):
            return "error"
        if state.get("repo_analysis") and state.get("profile_insights"):
            return "continue"
        return "error"
    
    # ... other conditional functions
```

### Execution Flow Diagram

```
START
  │
  ▼
┌────────────────────┐
│ Analyze GitHub     │
│ (Parallel)         │
│ • Repo Analysis    │
│ • Profile Analysis │
└─────────┬──────────┘
          │
     [Checkpoint]
          │
          ▼
┌────────────────────┐
│ Generate Content   │
│ (Sequential+Plan)  │
│ • Strategy         │
│ • LinkedIn Post    │
│ • Twitter Thread   │
│ • Instagram Caption│
└─────────┬──────────┘
          │
     [Checkpoint]
          │
          ▼
┌────────────────────┐
│ Publish Content    │
│ (Parallel)         │
│ • LinkedIn         │
│ • X/Twitter        │
│ • Instagram        │
└─────────┬──────────┘
          │
     [Checkpoint]
          │
          ▼
        END
```

---

## 🔌 Social Media API Integration

### 1. LinkedIn API Integration

**Authentication**: OAuth 2.0  
**API Version**: LinkedIn Marketing API v2 (202501+)  
**Permissions Required**: `w_member_social`, `r_basicprofile`

```python
import asyncio
import aiohttp
from typing import Dict

class LinkedInPublisher:
    def __init__(self, access_token: str, user_urn: str):
        self.access_token = access_token
        self.user_urn = user_urn
        self.api_base = "https://api.linkedin.com/v2"
    
    async def publish_post(
        self,
        text: str,
        media_url: Optional[str] = None
    ) -> Dict:
        """
        Publish a post to LinkedIn using Posts API
        Rate limit: ~100 posts/day per user
        """
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "LinkedIn-Version": "202501",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        payload = {
            "author": f"urn:li:person:{self.user_urn}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "NONE" if not media_url else "IMAGE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        if media_url:
            # Upload media first, then reference in post
            media_id = await self._upload_media(media_url)
            payload["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                {
                    "status": "READY",
                    "media": media_id
                }
            ]
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_base}/ugcPosts",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 201:
                    data = await response.json()
                    return {
                        "success": True,
                        "post_id": data.get("id"),
                        "url": f"https://www.linkedin.com/feed/update/{data.get('id')}"
                    }
                else:
                    error_data = await response.text()
                    raise Exception(f"LinkedIn API Error: {response.status} - {error_data}")
    
    async def _upload_media(self, media_url: str) -> str:
        """Upload image to LinkedIn"""
        # Implementation for media upload
        pass
```

**Credentials Setup**:
1. Create app at https://developer.linkedin.com
2. Request `w_member_social` product access
3. Generate OAuth 2.0 tokens (expires every 60 days)
4. Use token refresh flow for long-running systems

**Rate Limits**: 
- 100 API calls per hour per user
- ~100 posts per day recommended

---

### 2. X (Twitter) API Integration

**Authentication**: OAuth 1.0a (recommended for posting)  
**API Version**: X API v2  
**Tier**: Basic ($200/month) or Free (500 posts/month, write-only)  
**Permissions**: `tweet.read`, `tweet.write`, `users.read`

```python
import tweepy
from typing import List, Optional

class XPublisher:
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        access_token: str,
        access_secret: str
    ):
        # OAuth 1.0a authentication (best for posting)
        auth = tweepy.OAuth1UserHandler(
            api_key, api_secret,
            access_token, access_secret
        )
        self.client = tweepy.Client(
            bearer_token=None,
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_secret,
            wait_on_rate_limit=True
        )
        self.api = tweepy.API(auth)
    
    async def post_tweet(self, text: str, media_paths: Optional[List[str]] = None) -> Dict:
        """
        Post a single tweet
        Free tier: 500 posts/month, ~17 per day
        Basic tier: 10k posts/month
        """
        try:
            media_ids = []
            if media_paths:
                for path in media_paths[:4]:  # Max 4 images
                    media = self.api.media_upload(path)
                    media_ids.append(media.media_id)
            
            response = self.client.create_tweet(
                text=text,
                media_ids=media_ids if media_ids else None
            )
            
            tweet_id = response.data['id']
            return {
                "success": True,
                "tweet_id": tweet_id,
                "url": f"https://twitter.com/i/web/status/{tweet_id}"
            }
        except tweepy.TweepyException as e:
            raise Exception(f"X API Error: {str(e)}")
    
    async def post_thread(self, tweets: List[str], media_paths: Optional[List[str]] = None) -> Dict:
        """
        Post a thread of tweets
        Automatically chains replies
        """
        thread_ids = []
        previous_tweet_id = None
        
        for i, tweet_text in enumerate(tweets):
            media = [media_paths[i]] if media_paths and i < len(media_paths) else None
            
            response = self.client.create_tweet(
                text=tweet_text,
                in_reply_to_tweet_id=previous_tweet_id,
                media_ids=media if media else None
            )
            
            tweet_id = response.data['id']
            thread_ids.append(tweet_id)
            previous_tweet_id = tweet_id
        
        return {
            "success": True,
            "thread_ids": thread_ids,
            "url": f"https://twitter.com/i/web/status/{thread_ids[0]}"
        }
```

**Cost Considerations** (2025 Pricing):
- **Free Tier**: 500 posts/month (write-only, no read access)
- **Basic**: $200/month (10,000 posts, read access)
- **Alternative**: Consider third-party APIs like Late.dev ($100/month savings)

**Setup**:
1. Apply for X Developer account at developer.x.com
2. Create project and app
3. Set permissions to "Read and Write"
4. Generate OAuth 1.0a credentials
5. Store securely in environment variables

---

### 3. Instagram API Integration

**Authentication**: Facebook Graph API OAuth 2.0  
**API Version**: Graph API v21.0+  
**Account Type**: Instagram Business or Creator Account  
**Permissions**: `instagram_basic`, `instagram_content_publish`, `pages_read_engagement`

```python
import aiohttp
from typing import Dict, Optional
import asyncio

class InstagramPublisher:
    def __init__(self, access_token: str, instagram_account_id: str):
        self.access_token = access_token
        self.account_id = instagram_account_id
        self.graph_api = "https://graph.facebook.com/v21.0"
    
    async def publish_image_post(
        self,
        image_url: str,
        caption: str,
        location_id: Optional[str] = None
    ) -> Dict:
        """
        Publish single image post to Instagram
        Two-step process: Create container -> Publish container
        Rate limit: 50 published posts per 24 hours
        """
        # Step 1: Create media container
        container_id = await self._create_media_container(
            image_url=image_url,
            caption=caption,
            location_id=location_id
        )
        
        # Step 2: Poll until container is ready
        await self._wait_for_container_ready(container_id)
        
        # Step 3: Publish the container
        result = await self._publish_container(container_id)
        
        return {
            "success": True,
            "post_id": result["id"],
            "url": f"https://www.instagram.com/p/{result['id']}"
        }
    
    async def publish_carousel(
        self,
        media_urls: List[str],
        caption: str
    ) -> Dict:
        """
        Publish carousel post (2-10 images/videos)
        """
        # Create containers for each media item
        container_ids = []
        for url in media_urls[:10]:  # Max 10 items
            container = await self._create_media_container(
                image_url=url,
                is_carousel_item=True
            )
            container_ids.append(container)
        
        # Create carousel container
        carousel_container = await self._create_carousel_container(
            children=container_ids,
            caption=caption
        )
        
        await self._wait_for_container_ready(carousel_container)
        result = await self._publish_container(carousel_container)
        
        return {"success": True, "post_id": result["id"]}
    
    async def _create_media_container(
        self,
        image_url: str,
        caption: Optional[str] = None,
        is_carousel_item: bool = False,
        location_id: Optional[str] = None
    ) -> str:
        """Create media container for image"""
        async with aiohttp.ClientSession() as session:
            params = {
                "image_url": image_url,
                "access_token": self.access_token
            }
            
            if caption and not is_carousel_item:
                params["caption"] = caption
            if is_carousel_item:
                params["is_carousel_item"] = "true"
            if location_id:
                params["location_id"] = location_id
            
            async with session.post(
                f"{self.graph_api}/{self.account_id}/media",
                params=params
            ) as response:
                data = await response.json()
                if "id" in data:
                    return data["id"]
                raise Exception(f"Instagram API Error: {data}")
    
    async def _wait_for_container_ready(self, container_id: str, max_wait: int = 60):
        """Poll container status until ready"""
        start_time = asyncio.get_event_loop().time()
        
        while True:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.graph_api}/{container_id}",
                    params={
                        "fields": "status_code",
                        "access_token": self.access_token
                    }
                ) as response:
                    data = await response.json()
                    status = data.get("status_code")
                    
                    if status == "FINISHED":
                        return True
                    elif status == "ERROR":
                        raise Exception("Media processing failed")
                    
                    if asyncio.get_event_loop().time() - start_time > max_wait:
                        raise Exception("Media processing timeout")
                    
                    await asyncio.sleep(2)
    
    async def _publish_container(self, container_id: str) -> Dict:
        """Publish the media container"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.graph_api}/{self.account_id}/media_publish",
                params={
                    "creation_id": container_id,
                    "access_token": self.access_token
                }
            ) as response:
                return await response.json()
    
    async def _create_carousel_container(
        self,
        children: List[str],
        caption: str
    ) -> str:
        """Create carousel container"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.graph_api}/{self.account_id}/media",
                params={
                    "media_type": "CAROUSEL",
                    "children": ",".join(children),
                    "caption": caption,
                    "access_token": self.access_token
                }
            ) as response:
                data = await response.json()
                return data["id"]
```

**Setup Process**:
1. Convert personal Instagram to Business/Creator account
2. Link to Facebook Page
3. Create Facebook App at developers.facebook.com
4. Add Instagram Basic Display and Instagram API products
5. Configure OAuth redirect URLs
6. Request permissions: `instagram_basic`, `instagram_content_publish`, `pages_read_engagement`
7. Generate long-lived access tokens (60 days, auto-refresh)
8. Retrieve Instagram Business Account ID

**Rate Limits**:
- 200 API calls per hour per user
- 50 published posts per 24-hour rolling window
- Carousels count as 1 post

---

## 🗄️ State Management & Schema Design

### Database Schema (SQLite + Redis)

```sql
-- SQLite for persistent workflow state
CREATE TABLE workflow_runs (
    id TEXT PRIMARY KEY,
    github_repo_url TEXT NOT NULL,
    github_profile_url TEXT,
    target_platforms TEXT, -- JSON array
    status TEXT CHECK(status IN ('pending', 'analyzing', 'generating', 'publishing', 'completed', 'failed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    error_log TEXT, -- JSON array of errors
    retry_count INTEGER DEFAULT 0
);

CREATE TABLE checkpoints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_id TEXT REFERENCES workflow_runs(id),
    checkpoint_name TEXT NOT NULL,
    state_snapshot TEXT NOT NULL, -- JSON blob
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE analysis_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_id TEXT REFERENCES workflow_runs(id),
    repo_analysis TEXT, -- JSON
    profile_insights TEXT, -- JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE generated_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_id TEXT REFERENCES workflow_runs(id),
    platform TEXT CHECK(platform IN ('linkedin', 'twitter', 'instagram')),
    content TEXT NOT NULL, -- JSON with text, media_urls, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE published_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_id TEXT REFERENCES workflow_runs(id),
    platform TEXT NOT NULL,
    post_id TEXT, -- Platform-specific ID
    post_url TEXT,
    published_at TIMESTAMP,
    status TEXT CHECK(status IN ('success', 'failed', 'retrying')),
    error_message TEXT
);

-- Redis for fast state access and caching
-- Key patterns:
-- workflow:{workflow_id}:state -> Current workflow state (AgentState)
-- workflow:{workflow_id}:lock -> Distributed lock for concurrent access
-- rate_limit:linkedin:{user_id} -> Rate limiting counters
-- rate_limit:twitter:{user_id} -> Rate limiting counters
-- rate_limit:instagram:{account_id} -> Rate limiting counters
-- cache:github:repo:{owner}/{repo} -> Cached repo data (TTL: 1 hour)
```

### State Management Implementation

```python
import asyncio
import json
from typing import Optional
import aiosqlite
import redis.asyncio as redis
from contextlib import asynccontextmanager

class StateManager:
    def __init__(self, sqlite_path: str, redis_url: str):
        self.sqlite_path = sqlite_path
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
    
    async def initialize(self):
        """Initialize database schema"""
        async with aiosqlite.connect(self.sqlite_path) as db:
            # Create tables (schema above)
            await db.executescript(SCHEMA_SQL)
            await db.commit()
    
    async def save_workflow_state(
        self,
        workflow_id: str,
        state: AgentState
    ):
        """
        Save workflow state to both Redis (fast access) and SQLite (persistence)
        """
        # Save to Redis for fast access
        await self.redis_client.setex(
            f"workflow:{workflow_id}:state",
            3600,  # 1 hour TTL
            json.dumps(state, default=str)
        )
        
        # Save to SQLite for persistence
        async with aiosqlite.connect(self.sqlite_path) as db:
            await db.execute(
                """
                UPDATE workflow_runs 
                SET status = ?, completed_at = ?, error_log = ?
                WHERE id = ?
                """,
                (state["status"], state.get("completed_at"), json.dumps(state["errors"]), workflow_id)
            )
            await db.commit()
    
    async def create_checkpoint(
        self,
        workflow_id: str,
        checkpoint_name: str,
        state: AgentState
    ):
        """Create checkpoint for fault tolerance"""
        async with aiosqlite.connect(self.sqlite_path) as db:
            await db.execute(
                """
                INSERT INTO checkpoints (workflow_id, checkpoint_name, state_snapshot)
                VALUES (?, ?, ?)
                """,
                (workflow_id, checkpoint_name, json.dumps(state, default=str))
            )
            await db.commit()
    
    async def restore_from_checkpoint(
        self,
        workflow_id: str,
        checkpoint_name: Optional[str] = None
    ) -> AgentState:
        """Restore workflow from latest or specified checkpoint"""
        async with aiosqlite.connect(self.sqlite_path) as db:
            if checkpoint_name:
                query = """
                    SELECT state_snapshot FROM checkpoints 
                    WHERE workflow_id = ? AND checkpoint_name = ?
                    ORDER BY created_at DESC LIMIT 1
                """
                params = (workflow_id, checkpoint_name)
            else:
                query = """
                    SELECT state_snapshot FROM checkpoints 
                    WHERE workflow_id = ?
                    ORDER BY created_at DESC LIMIT 1
                """
                params = (workflow_id,)
            
            async with db.execute(query, params) as cursor:
                row = await cursor.fetchone()
                if row:
                    return json.loads(row[0])
                raise ValueError(f"No checkpoint found for workflow {workflow_id}")
    
    @asynccontextmanager
    async def distributed_lock(self, workflow_id: str, timeout: int = 60):
        """Distributed lock for concurrent workflow access"""
        lock_key = f"workflow:{workflow_id}:lock"
        lock_id = f"{workflow_id}:{asyncio.current_task().get_name()}"
        
        # Acquire lock with timeout
        acquired = await self.redis_client.set(
            lock_key, lock_id, nx=True, ex=timeout
        )
        
        if not acquired:
            raise Exception(f"Could not acquire lock for workflow {workflow_id}")
        
        try:
            yield
        finally:
            # Release lock only if we still own it
            lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
            """
            await self.redis_client.eval(lua_script, 1, lock_key, lock_id)
    
    async def check_rate_limit(
        self,
        platform: str,
        user_id: str,
        limit: int,
        window: int = 3600
    ) -> bool:
        """
        Check if within rate limit
        Returns True if can proceed, False if rate limited
        """
        key = f"rate_limit:{platform}:{user_id}"
        
        # Increment counter
        count = await self.redis_client.incr(key)
        
        # Set expiry on first increment
        if count == 1:
            await self.redis_client.expire(key, window)
        
        return count <= limit
```

---

## ⚙️ Configuration Management

### Environment Variables (.env)

```bash
# Application
APP_NAME=social-media-agent-system
ENVIRONMENT=production
LOG_LEVEL=INFO
WORKER_CONCURRENCY=4

# Database
SQLITE_DB_PATH=/data/workflows.db
REDIS_URL=redis://localhost:6379/0

# LLM Configuration
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DEFAULT_LLM_MODEL=gpt-4o
FALLBACK_LLM_MODEL=claude-3-5-sonnet-20241022

# GitHub API
GITHUB_TOKEN=ghp_...
GITHUB_API_BASE=https://api.github.com

# LinkedIn API
LINKEDIN_CLIENT_ID=...
LINKEDIN_CLIENT_SECRET=...
LINKEDIN_ACCESS_TOKEN=...
LINKEDIN_USER_URN=...
LINKEDIN_TOKEN_EXPIRES=2025-04-01T00:00:00Z

# X/Twitter API
TWITTER_API_KEY=...
TWITTER_API_SECRET=...
TWITTER_ACCESS_TOKEN=...
TWITTER_ACCESS_SECRET=...
TWITTER_BEARER_TOKEN=...

# Instagram API
INSTAGRAM_ACCESS_TOKEN=...
INSTAGRAM_ACCOUNT_ID=...
FACEBOOK_PAGE_ID=...

# Observability
LANGSMITH_API_KEY=lsv2_...
LANGSMITH_PROJECT_NAME=social-media-agents
LANGSMITH_TRACING=true

# Rate Limiting
LINKEDIN_HOURLY_LIMIT=100
TWITTER_DAILY_LIMIT=500
INSTAGRAM_DAILY_LIMIT=50

# Retry Configuration
MAX_RETRIES=3
RETRY_BACKOFF_FACTOR=2
RETRY_MAX_DELAY=60

# Feature Flags
ENABLE_CONTENT_MODERATION=true
ENABLE_AUTO_PUBLISH=true
ENABLE_DRY_RUN=false
```

### Configuration Loader

```python
from pydantic import BaseSettings, SecretStr, validator
from typing import Optional, Literal
from datetime import datetime

class Settings(BaseSettings):
    # Application
    app_name: str = "social-media-agent-system"
    environment: Literal["development", "staging", "production"] = "development"
    log_level: str = "INFO"
    worker_concurrency: int = 4
    
    # Database
    sqlite_db_path: str = "./workflows.db"
    redis_url: str = "redis://localhost:6379/0"
    
    # LLM
    openai_api_key: Optional[SecretStr] = None
    anthropic_api_key: Optional[SecretStr] = None
    default_llm_model: str = "gpt-4o"
    fallback_llm_model: str = "claude-3-5-sonnet-20241022"
    
    # GitHub
    github_token: SecretStr
    github_api_base: str = "https://api.github.com"
    
    # LinkedIn
    linkedin_client_id: str
    linkedin_client_secret: SecretStr
    linkedin_access_token: SecretStr
    linkedin_user_urn: str
    linkedin_token_expires: datetime
    
    # X/Twitter
    twitter_api_key: str
    twitter_api_secret: SecretStr
    twitter_access_token: SecretStr
    twitter_access_secret: SecretStr
    twitter_bearer_token: Optional[SecretStr] = None
    
    # Instagram
    instagram_access_token: SecretStr
    instagram_account_id: str
    facebook_page_id: str
    
    # Observability
    langsmith_api_key: Optional[SecretStr] = None
    langsmith_project_name: str = "social-media-agents"
    langsmith_tracing: bool = True
    
    # Rate Limiting
    linkedin_hourly_limit: int = 100
    twitter_daily_limit: int = 500
    instagram_daily_limit: int = 50
    
    # Retry
    max_retries: int = 3
    retry_backoff_factor: int = 2
    retry_max_delay: int = 60
    
    # Feature Flags
    enable_content_moderation: bool = True
    enable_auto_publish: bool = True
    enable_dry_run: bool = False
    
    @validator("linkedin_token_expires", pre=True)
    def parse_datetime(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v)
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Singleton settings instance
settings = Settings()
```

---

## 📁 Recommended Project Structure

```
social-media-agent-system/
│
├── README.md
├── pyproject.toml          # Poetry/pip dependencies
├── docker-compose.yml      # Full stack deployment
├── Dockerfile
├── .env.example
├── .gitignore
│
├── src/
│   ├── __init__.py
│   │
│   ├── main.py             # Application entry point
│   ├── config.py           # Configuration management
│   │
│   ├── agents/             # CrewAI agent definitions
│   │   ├── __init__.py
│   │   ├── github_agents.py      # Repo & profile analyzers
│   │   ├── content_agents.py     # Writers for each platform
│   │   ├── publishing_agents.py  # Platform publishers
│   │   └── tools/                # Agent tools
│   │       ├── github_tools.py
│   │       ├── llm_tools.py
│   │       └── validation_tools.py
│   │
│   ├── workflows/          # LangGraph workflows
│   │   ├── __init__.py
│   │   ├── main_workflow.py      # Primary state machine
│   │   ├── state.py              # State schema
│   │   └── nodes.py              # Node implementations
│   │
│   ├── publishers/         # Platform-specific publishers
│   │   ├── __init__.py
│   │   ├── linkedin.py
│   │   ├── twitter.py
│   │   └── instagram.py
│   │
│   ├── services/           # Core services
│   │   ├── __init__.py
│   │   ├── state_manager.py
│   │   ├── rate_limiter.py
│   │   ├── retry_handler.py
│   │   └── content_moderator.py
│   │
│   ├── models/             # Data models
│   │   ├── __init__.py
│   │   ├── agent_state.py
│   │   ├── content_models.py
│   │   └── platform_models.py
│   │
│   └── utils/              # Utilities
│       ├── __init__.py
│       ├── logger.py
│       ├── metrics.py
│       └── validators.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py         # Pytest fixtures
│   ├── unit/
│   │   ├── test_agents.py
│   │   ├── test_publishers.py
│   │   └── test_state_manager.py
│   ├── integration/
│   │   ├── test_workflow.py
│   │   └── test_api_integration.py
│   └── e2e/
│       └── test_full_pipeline.py
│
├── scripts/
│   ├── setup_db.py         # Initialize databases
│   ├── refresh_tokens.py   # Refresh OAuth tokens
│   └── seed_test_data.py
│
├── monitoring/
│   ├── prometheus.yml      # Metrics config
│   └── grafana_dashboard.json
│
└── docs/
    ├── architecture.md
    ├── api_reference.md
    └── deployment.md
```

---

## 🔧 Best Practices Implementation

### 1. Agent Architecture & Orchestration

**Pattern**: Agentic Systems (Flow + Crews)
- Use LangGraph for deterministic workflow control
- Use CrewAI for intelligent agent coordination
- Each crew handles a specific domain (analysis, generation, publishing)
- Planning enabled for content generation crews

```python
# Example: Combining LangGraph + CrewAI
from langgraph.graph import StateGraph
from crewai import Crew, Agent, Task, Process

class AgenticWorkflow:
    def __init__(self):
        # LangGraph provides the deterministic backbone
        self.graph = StateGraph(AgentState)
        
        # CrewAI provides intelligent agents at each node
        self.analysis_crew = self._create_analysis_crew()
        self.content_crew = self._create_content_crew()
        self.publishing_crew = self._create_publishing_crew()
    
    def _create_content_crew(self) -> Crew:
        return Crew(
            agents=[...],
            tasks=[...],
            process=Process.sequential,
            planning=True,  # Enable coordinated planning
            memory=True,    # Enable long-term memory
            verbose=True
        )
```

### 2. Memory Handling

**Short-term Memory**: In-memory state during workflow execution  
**Long-term Memory**: Redis for fast access, SQLite for persistence  
**Context Window Management**: Summarization for long conversations

```python
from crewai import Crew
from langchain.memory import ConversationBufferMemory

# Enable memory in CrewAI
crew = Crew(
    agents=[...],
    tasks=[...],
    memory=True,  # Enables memory across tasks
    verbose=True
)

# Custom memory for context retention
class ContextualMemory:
    def __init__(self):
        self.short_term = {}  # Current workflow context
        self.long_term_store = None  # Redis/SQLite connection
    
    async def add_to_context(self, key: str, value: any):
        """Add to short-term memory"""
        self.short_term[key] = value
    
    async def persist(self, workflow_id: str):
        """Move short-term to long-term storage"""
        await self.long_term_store.save(workflow_id, self.short_term)
```

### 3. Tool Integration

```python
from crewai_tools import tool
from langchain.tools import BaseTool
import aiohttp

@tool
async def github_repository_analyzer(repo_url: str) -> dict:
    """
    Analyze a GitHub repository comprehensively
    
    Args:
        repo_url: GitHub repository URL (e.g., https://github.com/owner/repo)
    
    Returns:
        dict: Repository analysis including metrics, tech stack, and insights
    """
    # Extract owner and repo from URL
    parts = repo_url.rstrip('/').split('/')
    owner, repo = parts[-2], parts[-1]
    
    async with aiohttp.ClientSession() as session:
        # Fetch repository data
        async with session.get(
            f"https://api.github.com/repos/{owner}/{repo}",
            headers={"Authorization": f"token {settings.github_token.get_secret_value()}"}
        ) as response:
            repo_data = await response.json()
        
        # Fetch languages
        async with session.get(
            f"https://api.github.com/repos/{owner}/{repo}/languages",
            headers={"Authorization": f"token {settings.github_token.get_secret_value()}"}
        ) as response:
            languages = await response.json()
        
        # Fetch recent commits
        async with session.get(
            f"https://api.github.com/repos/{owner}/{repo}/commits?per_page=10",
            headers={"Authorization": f"token {settings.github_token.get_secret_value()}"}
        ) as response:
            commits = await response.json()
    
    return {
        "name": repo_data.get("name"),
        "description": repo_data.get("description"),
        "stars": repo_data.get("stargazers_count"),
        "forks": repo_data.get("forks_count"),
        "watchers": repo_data.get("watchers_count"),
        "open_issues": repo_data.get("open_issues_count"),
        "language": repo_data.get("language"),
        "languages": languages,
        "created_at": repo_data.get("created_at"),
        "updated_at": repo_data.get("updated_at"),
        "topics": repo_data.get("topics", []),
        "license": repo_data.get("license", {}).get("name"),
        "recent_commit_count": len(commits),
        "is_active": len(commits) > 0,
        "health_score": calculate_health_score(repo_data, commits)
    }

def calculate_health_score(repo_data: dict, commits: list) -> float:
    """Calculate repository health score (0-100)"""
    score = 0.0
    
    # Activity score (40 points)
    if len(commits) > 5:
        score += 40
    elif len(commits) > 0:
        score += 20
    
    # Community score (30 points)
    stars = repo_data.get("stargazers_count", 0)
    if stars > 100:
        score += 30
    elif stars > 10:
        score += 15
    
    # Documentation score (30 points)
    has_readme = repo_data.get("has_readme", False)
    has_wiki = repo_data.get("has_wiki", False)
    has_description = bool(repo_data.get("description"))
    
    if has_readme:
        score += 15
    if has_wiki:
        score += 10
    if has_description:
        score += 5
    
    return min(score, 100.0)
```

### 4. Error Handling & Retries

```python
import asyncio
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from typing import Callable, Any

class RetryHandler:
    @staticmethod
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        retry=retry_if_exception_type((aiohttp.ClientError, TimeoutError)),
        reraise=True
    )
    async def with_retry(func: Callable, *args, **kwargs) -> Any:
        """Execute function with exponential backoff retry"""
        return await func(*args, **kwargs)
    
    @staticmethod
    async def safe_execute(
        func: Callable,
        *args,
        fallback: Any = None,
        **kwargs
    ) -> Any:
        """Execute with fallback on failure"""
        try:
            return await RetryHandler.with_retry(func, *args, **kwargs)
        except Exception as e:
            logger.error(f"Failed after retries: {e}")
            return fallback

# Usage in workflow nodes
async def publish_content_node(state: AgentState) -> AgentState:
    """Publish with retry logic"""
    for platform in state["target_platforms"]:
        try:
            publisher = get_publisher(platform)
            result = await RetryHandler.with_retry(
                publisher.publish,
                state[f"{platform}_content"]
            )
            state["publish_results"][platform] = result
        except Exception as e:
            state["errors"].append(f"{platform}: {str(e)}")
            state["publish_results"][platform] = {"success": False, "error": str(e)}
    
    return state
```

### 5. Observability & Logging

**LangSmith Integration** (Recommended):
```python
import os
os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key.get_secret_value()
os.environ["LANGSMITH_TRACING"] = str(settings.langsmith_tracing)
os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project_name

from langsmith import trace

@trace(name="github_analysis")
async def analyze_github_node(state: AgentState) -> AgentState:
    """Traced execution for observability"""
    # LangSmith automatically captures:
    # - Inputs/outputs
    # - LLM calls
    # - Tool invocations
    # - Execution time
    # - Errors
    
    result = await analysis_crew.kickoff_async(inputs=state)
    return result
```

**Structured Logging**:
```python
import structlog
from datetime import datetime

logger = structlog.get_logger()

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
)

# Usage
logger.info(
    "workflow_started",
    workflow_id=workflow_id,
    repo_url=repo_url,
    platforms=target_platforms
)

logger.error(
    "publishing_failed",
    workflow_id=workflow_id,
    platform="linkedin",
    error=str(e),
    retry_count=retry_count
)
```

**Metrics Collection** (Prometheus):
```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Define metrics
workflow_executions = Counter(
    'workflow_executions_total',
    'Total workflow executions',
    ['status']
)

workflow_duration = Histogram(
    'workflow_duration_seconds',
    'Workflow execution duration',
    ['stage']
)

agent_llm_tokens = Counter(
    'agent_llm_tokens_total',
    'Total LLM tokens used',
    ['agent', 'model']
)

active_workflows = Gauge(
    'active_workflows',
    'Currently executing workflows'
)

# Usage in workflow
@workflow_duration.labels(stage='github_analysis').time()
async def analyze_github_node(state: AgentState) -> AgentState:
    active_workflows.inc()
    try:
        result = await analysis_crew.kickoff_async(inputs=state)
        workflow_executions.labels(status='success').inc()
        return result
    except Exception as e:
        workflow_executions.labels(status='failed').inc()
        raise
    finally:
        active_workflows.dec()

# Start metrics server
start_http_server(9090)
```

### 6. Scalability & Modularity

**Horizontal Scaling with Celery**:
```python
from celery import Celery
from kombu import Queue

app = Celery('social_media_agents', broker=settings.redis_url)

app.conf.task_queues = (
    Queue('github_analysis', routing_key='analysis'),
    Queue('content_generation', routing_key='generation'),
    Queue('publishing', routing_key='publishing'),
)

@app.task(queue='github_analysis', bind=True, max_retries=3)
async def analyze_github_task(self, workflow_id: str, repo_url: str):
    """Async Celery task for GitHub analysis"""
    try:
        workflow = SocialMediaAgentWorkflow()
        state = await workflow.execute_analysis(workflow_id, repo_url)
        return state
    except Exception as e:
        self.retry(exc=e, countdown=60)

@app.task(queue='publishing', rate_limit='10/h')  # Platform rate limits
async def publish_to_platform_task(workflow_id: str, platform: str, content: dict):
    """Rate-limited publishing task"""
    publisher = get_publisher(platform)
    return await publisher.publish(content)
```

**Message Queue Architecture**:
```
┌─────────────┐       ┌──────────────┐       ┌─────────────┐
│   FastAPI   │──────▶│    Redis     │──────▶│   Celery    │
│  API Server │       │  Message     │       │  Workers    │
└─────────────┘       │   Queue      │       └─────────────┘
                      └──────────────┘              │
                                                    ▼
                                          ┌─────────────────┐
                                          │ Worker Pool (1) │
                                          │ GitHub Analysis │
                                          └─────────────────┘
                                          ┌─────────────────┐
                                          │ Worker Pool (2) │
                                          │ Content Gen     │
                                          └─────────────────┘
                                          ┌─────────────────┐
                                          │ Worker Pool (3) │
                                          │ Publishing      │
                                          └─────────────────┘
```

---

## 🚀 Deployment

### Docker Compose Stack

```yaml
version: '3.8'

services:
  # Main application
  app:
    build: .
    container_name: social-media-agent
    env_file: .env
    depends_on:
      - redis
      - postgres
    volumes:
      - ./data:/data
      - ./logs:/logs
    ports:
      - "8000:8000"
    restart: unless-stopped
    command: uvicorn src.main:app --host 0.0.0.0 --port 8000
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
  
  # Celery workers
  celery-worker:
    build: .
    container_name: celery-worker
    env_file: .env
    depends_on:
      - redis
      - postgres
    volumes:
      - ./data:/data
      - ./logs:/logs
    restart: unless-stopped
    command: celery -A src.tasks worker --loglevel=info --concurrency=4 -Q github_analysis,content_generation,publishing
  
  # Redis for state management and message queue
  redis:
    image: redis:7-alpine
    container_name: redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    command: redis-server --appendonly yes
  
  # PostgreSQL for persistent storage (alternative to SQLite)
  postgres:
    image: postgres:15-alpine
    container_name: postgres
    environment:
      POSTGRES_DB: social_media_agents
      POSTGRES_USER: agent_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
  
  # Prometheus for metrics
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    restart: unless-stopped
  
  # Grafana for dashboards
  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD}
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana_dashboard.json:/etc/grafana/provisioning/dashboards/dashboard.json
    restart: unless-stopped

volumes:
  redis_data:
  postgres_data:
  prometheus_data:
  grafana_data:
```

### Dockerfile

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml poetry.lock ./

# Install Python dependencies
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p /data /logs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 📊 Complete Example: Main Application

```python
# src/main.py
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import List, Literal, Optional
import uuid
from datetime import datetime

from src.workflows.main_workflow import SocialMediaAgentWorkflow
from src.services.state_manager import StateManager
from src.config import settings
from src.utils.logger import logger

# Initialize FastAPI
app = FastAPI(
    title="Social Media Agent System",
    description="Autonomous AI agents for GitHub analysis and social media publishing",
    version="1.0.0"
)

# Initialize services
state_manager = StateManager(
    sqlite_path=settings.sqlite_db_path,
    redis_url=settings.redis_url
)
workflow_engine = SocialMediaAgentWorkflow(state_manager=state_manager)

# Request/Response models
class WorkflowRequest(BaseModel):
    github_repo_url: HttpUrl
    github_profile_url: Optional[HttpUrl] = None
    target_platforms: List[Literal["linkedin", "twitter", "instagram"]]
    auto_publish: bool = False

class WorkflowResponse(BaseModel):
    workflow_id: str
    status: str
    created_at: datetime
    message: str

class WorkflowStatus(BaseModel):
    workflow_id: str
    status: str
    current_stage: Optional[str]
    progress: float  # 0.0 to 1.0
    errors: List[str]
    results: Optional[dict]

# API Endpoints
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    await state_manager.initialize()
    logger.info("Application started successfully")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }

@app.post("/workflows", response_model=WorkflowResponse)
async def create_workflow(
    request: WorkflowRequest,
    background_tasks: BackgroundTasks
):
    """
    Create a new workflow to analyze GitHub repo and publish to social media
    """
    workflow_id = str(uuid.uuid4())
    
    # Create initial state
    initial_state = {
        "workflow_id": workflow_id,
        "github_repo_url": str(request.github_repo_url),
        "github_profile_url": str(request.github_profile_url) if request.github_profile_url else None,
        "target_platforms": request.target_platforms,
        "status": "pending",
        "errors": [],
        "publish_results": {},
        "created_at": datetime.utcnow(),
        "completed_at": None,
        "last_checkpoint": "initialized",
        "retry_count": 0
    }
    
    # Save initial state
    await state_manager.save_workflow_state(workflow_id, initial_state)
    
    # Execute workflow in background
    background_tasks.add_task(
        execute_workflow,
        workflow_id=workflow_id,
        initial_state=initial_state
    )
    
    logger.info(
        "workflow_created",
        workflow_id=workflow_id,
        repo_url=str(request.github_repo_url),
        platforms=request.target_platforms
    )
    
    return WorkflowResponse(
        workflow_id=workflow_id,
        status="pending",
        created_at=initial_state["created_at"],
        message="Workflow created successfully. Processing in background."
    )

@app.get("/workflows/{workflow_id}", response_model=WorkflowStatus)
async def get_workflow_status(workflow_id: str):
    """Get status of a specific workflow"""
    try:
        # Retrieve state from Redis or SQLite
        state = await state_manager.get_workflow_state(workflow_id)
        
        if not state:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Calculate progress based on completed stages
        progress = calculate_progress(state)
        
        return WorkflowStatus(
            workflow_id=workflow_id,
            status=state["status"],
            current_stage=state.get("last_checkpoint"),
            progress=progress,
            errors=state.get("errors", []),
            results=state.get("publish_results") if state["status"] == "completed" else None
        )
    except Exception as e:
        logger.error("failed_to_get_workflow_status", workflow_id=workflow_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/workflows/{workflow_id}/retry")
async def retry_workflow(
    workflow_id: str,
    background_tasks: BackgroundTasks
):
    """Retry a failed workflow from last checkpoint"""
    try:
        # Restore from checkpoint
        state = await state_manager.restore_from_checkpoint(workflow_id)
        
        # Reset status
        state["status"] = "pending"
        state["retry_count"] += 1
        
        if state["retry_count"] > settings.max_retries:
            raise HTTPException(
                status_code=400,
                detail=f"Maximum retries ({settings.max_retries}) exceeded"
            )
        
        # Execute workflow from checkpoint
        background_tasks.add_task(
            execute_workflow,
            workflow_id=workflow_id,
            initial_state=state
        )
        
        return {"message": "Workflow retry initiated", "workflow_id": workflow_id}
    except Exception as e:
        logger.error("failed_to_retry_workflow", workflow_id=workflow_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

async def execute_workflow(workflow_id: str, initial_state: dict):
    """Background task to execute the workflow"""
    try:
        # Execute LangGraph workflow
        result = await workflow_engine.run(
            inputs=initial_state,
            config={"configurable": {"thread_id": workflow_id}}
        )
        
        logger.info(
            "workflow_completed",
            workflow_id=workflow_id,
            status=result["status"],
            platforms=result.get("publish_results", {}).keys()
        )
    except Exception as e:
        logger.error(
            "workflow_failed",
            workflow_id=workflow_id,
            error=str(e)
        )
        # Update state with error
        await state_manager.save_workflow_state(
            workflow_id,
            {**initial_state, "status": "failed", "errors": [str(e)]}
        )

def calculate_progress(state: dict) -> float:
    """Calculate workflow progress percentage"""
    stages = ["initialized", "analyze_complete", "generate_complete", "publish_complete"]
    current_stage = state.get("last_checkpoint", "initialized")
    
    if current_stage in stages:
        return (stages.index(current_stage) + 1) / len(stages)
    return 0.0

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## 🎯 Key Takeaways

### ✅ This Architecture Provides:

1. **Production-Ready**: Fault-tolerant, scalable, observable
2. **Free & Open-Source**: All frameworks (CrewAI, LangGraph, LangChain) are MIT-licensed
3. **Async-First**: Maximum throughput with async/await patterns
4. **Observable**: Full tracing via LangSmith + Prometheus metrics
5. **Modular**: Easy to extend with new platforms or agents
6. **Robust**: Checkpointing, retries, rate limiting, error handling
7. **Modern**: Follows 2025 best practices (Agentic Systems pattern)

### 🔑 Critical Success Factors:

1. **Use LangGraph for Workflow Control**: Don't rely solely on agent orchestration
2. **Enable Planning in CrewAI**: For multi-step content generation
3. **Implement Checkpointing**: Essential for fault tolerance
4. **Monitor Everything**: LangSmith + Prometheus + structured logging
5. **Respect Rate Limits**: Implement proper throttling for each platform
6. **Test Token Refresh**: OAuth tokens expire (LinkedIn: 60 days, Instagram: 60 days)
7. **Use Distributed Locks**: Prevent concurrent access to same workflow

### 📈 Scalability Path:

**Phase 1** (Single Server): FastAPI + Celery + Redis  
**Phase 2** (Horizontal Scale): Load balancer + Multiple workers  
**Phase 3** (High Availability): Kubernetes + Redis Cluster + PostgreSQL HA

---

## 📚 Additional Resources

### Documentation:
- LangGraph: https://langchain-ai.github.io/langgraph/
- CrewAI: https://docs.crewai.com/
- LangChain: https://python.langchain.com/docs/
- LangSmith: https://docs.smith.langchain.com/

### API Documentation:
- LinkedIn API: https://learn.microsoft.com/en-us/linkedin/
- X API: https://developer.x.com/en/docs
- Instagram Graph API: https://developers.facebook.com/docs/instagram-platform

### Community:
- LangGraph Discord: https://discord.gg/langchain
- CrewAI GitHub: https://github.com/joaomdmoura/crewAI

---

**Author**: Claude (Anthropic)  
**Last Updated**: February 16, 2025  
**License**: MIT
