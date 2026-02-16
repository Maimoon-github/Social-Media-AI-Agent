from langchain.tools import BaseTool
from langchain_ollama import ChatOllama
from typing import Dict, Any, List
from pydantic import Field
from config import get_settings

class TextSummarizationTool(BaseTool):
    """Tool to summarize long text content."""
    
    name: str = "text_summarizer"
    description: str = (
        "Summarizes long text content into concise, key-point format. "
        "Useful for condensing README files, documentation, or long descriptions."
    )
    llm: ChatOllama = Field(default_factory=lambda: ChatOllama(
        model=get_settings().llm.analysis_model,
        temperature=0.3
    ))
    
    def _run(self, text: str, max_points: int = 5) -> str:
        """Summarize text into key points."""
        prompt = f"""
        Summarize the following text into {max_points} key points:
        
        {text}
        
        Return only the key points in a numbered list.
        """
        
        response = self.llm.invoke(prompt)
        return response.content

class SentimentAnalysisTool(BaseTool):
    """Tool to analyze sentiment of text."""
    
    name: str = "sentiment_analyzer"
    description: str = (
        "Analyzes the sentiment of text content and returns "
        "positive, negative, or neutral classification with confidence score."
    )
    llm: ChatOllama = Field(default_factory=lambda: ChatOllama(
        model=get_settings().llm.analysis_model,
        temperature=0.1
    ))
    
    def _run(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text."""
        prompt = f"""
        Analyze the sentiment of the following text.
        Return JSON format:
        {{
            "sentiment": "positive|negative|neutral",
            "confidence": 0.0-1.0,
            "reasoning": "brief explanation"
        }}
        
        Text: {text}
        """
        
        response = self.llm.invoke(prompt)
        # Parse JSON from response
        import json
        try:
            return json.loads(response.content)
        except:
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "reasoning": "Unable to parse sentiment"
            }

class EntityExtractionTool(BaseTool):
    """Tool to extract entities from text."""
    
    name: str = "entity_extractor"
    description: str = (
        "Extracts key entities (technologies, companies, people, concepts) "
        "from text content."
    )
    llm: ChatOllama = Field(default_factory=lambda: ChatOllama(
        model=get_settings().llm.analysis_model,
        temperature=0.2
    ))
    
    def _run(self, text: str) -> List[Dict[str, str]]:
        """Extract entities from text."""
        prompt = f"""
        Extract key entities from the following text.
        Categorize them as: technology, company, person, concept, or other.
        
        Return JSON array format:
        [
            {{"entity": "Python", "type": "technology"}},
            {{"entity": "FastAPI", "type": "technology"}}
        ]
        
        Text: {text}
        """
        
        response = self.llm.invoke(prompt)
        # Parse JSON from response
        import json
        try:
            return json.loads(response.content)
        except:
            return []

class ContentQualityTool(BaseTool):
    """Tool to assess content quality."""
    
    name: str = "content_quality_assessor"
    description: str = (
        "Assesses the quality of generated content based on clarity, "
        "engagement, professionalism, and platform appropriateness."
    )
    llm: ChatOllama = Field(default_factory=lambda: ChatOllama(
        model=get_settings().llm.content_model,
        temperature=0.3
    ))
    
    def _run(self, content: str, platform: str) -> Dict[str, Any]:
        """Assess content quality."""
        prompt = f"""
        Assess the quality of this {platform} content.
        
        Content: {content}
        
        Return JSON format:
        {{
            "overall_score": 0-100,
            "clarity_score": 0-100,
            "engagement_score": 0-100,
            "professionalism_score": 0-100,
            "platform_fit_score": 0-100,
            "suggestions": ["suggestion 1", "suggestion 2"],
            "strengths": ["strength 1", "strength 2"]
        }}
        """
        
        response = self.llm.invoke(prompt)
        # Parse JSON from response
        import json
        try:
            return json.loads(response.content)
        except:
            return {
                "overall_score": 50,
                "suggestions": ["Unable to assess quality"]
            }

def create_llm_tools() -> List[BaseTool]:
    """
    Create all LLM-powered tools.
    
    Returns:
        List of LLM tools
    """
    return [
        TextSummarizationTool(),
        SentimentAnalysisTool(),
        EntityExtractionTool(),
        ContentQualityTool()
    ]