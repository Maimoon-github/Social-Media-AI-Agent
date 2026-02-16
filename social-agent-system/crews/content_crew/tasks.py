from crewai import Task, Agent
from typing import Dict, Any

def create_linkedin_task(
    agent: Agent,
    analysis: Dict[str, Any]
) -> Task:
    """
    Create LinkedIn content generation task.
    
    Args:
        agent: LinkedIn expert agent
        analysis: GitHub analysis results
        
    Returns:
        Configured Task instance
    """
    repo = analysis.get("repository", {})
    profile = analysis.get("profile", {})
    
    return Task(
        description=f"""
        Create a professional LinkedIn post about the GitHub repository and developer profile.
        
        Repository Context:
        - Name: {repo.get('name')}
        - Description: {repo.get('description')}
        - Tech Stack: {', '.join(repo.get('tech_stack', []))}
        - Health Score: {repo.get('health_score')}
        - Key Insights: {repo.get('key_insights')}
        
        Developer Context:
        - Username: {profile.get('username')}
        - Expertise: {', '.join([e.get('area') for e in profile.get('expertise_areas', [])])}
        - Professional Positioning: {profile.get('professional_positioning')}
        
        Content Requirements:
        1. **Hook**: Start with a compelling opening that grabs attention
        2. **Value**: Focus on the business or technical value of the project
        3. **Insights**: Share 2-3 key technical insights or learnings
        4. **Credibility**: Reference the developer's expertise naturally
        5. **Call-to-Action**: End with a clear CTA (check it out, share thoughts, etc.)
        6. **Length**: 150-300 characters optimal (max 3000)
        7. **Hashtags**: 3-5 relevant hashtags (#opensource #github #[tech])
        8. **Tone**: Professional but approachable, thought-leadership style
        
        Structure:
        - Line 1-2: Hook (question, surprising fact, bold statement)
        - Line 3-6: Context and value proposition
        - Line 7-12: Technical insights and highlights
        - Line 13-15: Developer positioning
        - Line 16-17: Call-to-action
        - Line 18: Hashtags
        
        Avoid:
        - Generic praise ("amazing project", "check this out")
        - Over-technical jargon without explanation
        - Salesy language
        - More than 5 hashtags
        """,
        agent=agent,
        expected_output="""
        JSON format:
        {
            "text": "Complete LinkedIn post text with line breaks",
            "hashtags": ["opensource", "github", "python", "ai", "machinelearning"],
            "media_type": null,
            "metadata": {
                "target_audience": "developers, tech leaders, CTOs",
                "content_pillar": "thought leadership",
                "expected_engagement": "high/medium/low",
                "hook_type": "question/fact/statement"
            }
        }
        """
    )

def create_x_task(
    agent: Agent,
    analysis: Dict[str, Any]
) -> Task:
    """
    Create X (Twitter) content generation task.
    
    Args:
        agent: X expert agent
        analysis: GitHub analysis results
        
    Returns:
        Configured Task instance
    """
    repo = analysis.get("repository", {})
    profile = analysis.get("profile", {})
    
    return Task(
        description=f"""
        Create an engaging X (Twitter) thread about the GitHub repository and developer.
        
        Repository Context:
        - Name: {repo.get('name')}
        - Description: {repo.get('description')}
        - Tech Stack: {', '.join(repo.get('tech_stack', []))}
        - Key Insights: {repo.get('key_insights')}
        
        Developer Context:
        - Username: @{profile.get('username')}
        - Expertise: {', '.join([e.get('area') for e in profile.get('expertise_areas', [])])}
        
        Content Requirements:
        1. **Format**: Thread (3-7 tweets optimal, max 10)
        2. **Hook Tweet**: Start with a punchy, quotable first tweet
        3. **Value**: Each tweet should provide standalone value
        4. **Length**: Max 280 characters per tweet
        5. **Hashtags**: 1-2 max (usually only in first tweet)
        6. **Tone**: Casual, engaging, developer-friendly
        7. **Engagement**: Include questions or calls for community input
        
        Thread Structure:
        Tweet 1: Hook - surprising insight or question
        Tweet 2-3: Context and problem being solved
        Tweet 4-6: Technical highlights (one per tweet)
        Tweet 7: Developer credit and call-to-action
        Optional Tweet 8+: Additional insights or community question
        
        Best Practices:
        - Use emojis sparingly (1-2 max, usually 🧵 for thread indicator)
        - Number tweets if it helps clarity (1/7, 2/7, etc.)
        - Make each tweet quotable/retweetable on its own
        - Tag the developer's X handle if you have it
        - Use simple language - avoid jargon
        """,
        agent=agent,
        expected_output="""
        JSON format:
        {
            "tweets": [
                {
                    "text": "Tweet 1 text (max 280 chars)",
                    "order": 1
                },
                {
                    "text": "Tweet 2 text (max 280 chars)",
                    "order": 2
                }
            ],
            "hashtags": ["github", "opensource"],
            "media_urls": [],
            "metadata": {
                "thread": true,
                "tweet_count": 5,
                "hook_style": "question/fact/insight",
                "expected_engagement": "high/medium/low"
            }
        }
        """
    )

def create_instagram_task(
    agent: Agent,
    analysis: Dict[str, Any]
) -> Task:
    """
    Create Instagram content generation task.
    
    Args:
        agent: Instagram expert agent
        analysis: GitHub analysis results
        
    Returns:
        Configured Task instance
    """
    repo = analysis.get("repository", {})
    profile = analysis.get("profile", {})
    
    return Task(
        description=f"""
        Create an Instagram post about the GitHub repository with visual description and caption.
        
        Repository Context:
        - Name: {repo.get('name')}
        - Description: {repo.get('description')}
        - Tech Stack: {', '.join(repo.get('tech_stack', []))}
        - Key Insights: {repo.get('key_insights')}
        
        Developer Context:
        - Username: {profile.get('username')}
        - Expertise: {', '.join([e.get('area') for e in profile.get('expertise_areas', [])])}
        
        Content Requirements:
        
        A. Image Description:
        Describe a compelling visual for this repository that could be:
        - Screenshot of code with syntax highlighting
        - Architecture diagram concept
        - UI/UX mockup if applicable
        - Data visualization
        - Before/after comparison
        - Infographic summarizing key points
        
        Be specific: colors, layout, text overlays, visual hierarchy
        
        B. Caption Requirements:
        1. **Hook**: First line must grab attention (shows in feed)
        2. **Story**: Tell the story of the project or developer journey
        3. **Value**: What can followers learn or gain?
        4. **Length**: 150-500 characters optimal (max 2200)
        5. **Hashtags**: 10-15 relevant hashtags (at the end or in comments)
        6. **Emojis**: 3-5 relevant emojis to break up text
        7. **Call-to-Action**: Clear CTA (link in bio, save this post, etc.)
        8. **Tone**: Authentic, inspiring, community-focused
        
        Caption Structure:
        Line 1-2: Hook with emoji
        
        Line 3-8: Story or context
        Line 9-12: Technical highlights (simplified)
        Line 13-15: Developer positioning or community value
        Line 16-17: Call-to-action
        
        [Hashtags]
        
        Best Practices:
        - Write for mobile (short paragraphs, line breaks)
        - Use plain language - Instagram isn't for deep tech
        - Focus on impact and inspiration over implementation
        - Make it relatable to broader audience
        """,
        agent=agent,
        expected_output="""
        JSON format:
        {
            "caption": "Full Instagram caption with emojis and line breaks",
            "hashtags": [
                "coding", "programming", "github", "opensource",
                "developer", "tech", "software", "python", 
                "machinelearning", "ai", "developers", "code"
            ],
            "image_description": "Detailed description of the visual concept to be created",
            "image_style": "code-screenshot/diagram/infographic/ui-mockup",
            "metadata": {
                "target_audience": "developers, tech enthusiasts, learners",
                "content_pillar": "education/inspiration/community",
                "visual_priority": "high",
                "expected_engagement": "high/medium/low"
            }
        }
        """
    )