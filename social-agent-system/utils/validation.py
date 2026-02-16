from typing import Dict, Any, List
from urllib.parse import urlparse
import re
import structlog

logger = structlog.get_logger()

class ContentValidator:
    """
    Validates social media content against platform requirements.
    """
    
    PLATFORM_LIMITS = {
        "linkedin": {
            "max_text_length": 3000,
            "optimal_text_length": (150, 300),
            "min_hashtags": 3,
            "max_hashtags": 5
        },
        "x": {
            "max_tweet_length": 280,
            "max_thread_length": 10,
            "min_hashtags": 0,
            "max_hashtags": 2
        },
        "twitter": {  # Alias for x
            "max_tweet_length": 280,
            "max_thread_length": 10,
            "min_hashtags": 0,
            "max_hashtags": 2
        },
        "instagram": {
            "max_caption_length": 2200,
            "optimal_caption_length": (150, 500),
            "min_hashtags": 10,
            "max_hashtags": 30,
            "requires_image_description": True
        }
    }
    
    @staticmethod
    def validate_linkedin_content(content: Dict[str, Any]) -> Dict[str, Any]:
        """Validate LinkedIn content."""
        errors = []
        warnings = []
        
        text = content.get("text", "")
        hashtags = content.get("hashtags", [])
        
        limits = ContentValidator.PLATFORM_LIMITS["linkedin"]
        
        # Check text length
        if len(text) > limits["max_text_length"]:
            errors.append(f"Text exceeds maximum length of {limits['max_text_length']} characters")
        
        if len(text) < limits["optimal_text_length"][0]:
            warnings.append(f"Text is shorter than optimal length ({limits['optimal_text_length'][0]} chars)")
        elif len(text) > limits["optimal_text_length"][1]:
            warnings.append(f"Text is longer than optimal length ({limits['optimal_text_length'][1]} chars)")
        
        # Check hashtags
        if len(hashtags) < limits["min_hashtags"]:
            warnings.append(f"Less than {limits['min_hashtags']} hashtags (suboptimal)")
        elif len(hashtags) > limits["max_hashtags"]:
            errors.append(f"More than {limits['max_hashtags']} hashtags")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    @staticmethod
    def validate_x_content(content: Dict[str, Any]) -> Dict[str, Any]:
        """Validate X/Twitter content."""
        errors = []
        warnings = []
        
        tweets = content.get("tweets", [])
        hashtags = content.get("hashtags", [])
        
        limits = ContentValidator.PLATFORM_LIMITS["x"]
        
        # Check thread length
        if len(tweets) > limits["max_thread_length"]:
            errors.append(f"Thread exceeds maximum of {limits['max_thread_length']} tweets")
        
        # Check individual tweet lengths
        for tweet in tweets:
            text = tweet.get("text", "")
            if len(text) > limits["max_tweet_length"]:
                errors.append(
                    f"Tweet {tweet.get('order')} exceeds {limits['max_tweet_length']} characters"
                )
        
        # Check hashtags
        if len(hashtags) > limits["max_hashtags"]:
            warnings.append(f"More than {limits['max_hashtags']} hashtags (may reduce engagement)")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    @staticmethod
    def validate_instagram_content(content: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Instagram content."""
        errors = []
        warnings = []
        
        caption = content.get("caption", "")
        hashtags = content.get("hashtags", [])
        image_description = content.get("image_description", "")
        
        limits = ContentValidator.PLATFORM_LIMITS["instagram"]
        
        # Check caption length
        if len(caption) > limits["max_caption_length"]:
            errors.append(f"Caption exceeds maximum length of {limits['max_caption_length']} characters")
        
        if len(caption) < limits["optimal_caption_length"][0]:
            warnings.append("Caption is shorter than optimal length")
        
        # Check image description
        if limits["requires_image_description"] and not image_description:
            errors.append("Image description is required for Instagram posts")
        
        # Check hashtags
        if len(hashtags) < limits["min_hashtags"]:
            warnings.append(f"Less than {limits['min_hashtags']} hashtags (suboptimal for reach)")
        elif len(hashtags) > limits["max_hashtags"]:
            errors.append(f"More than {limits['max_hashtags']} hashtags")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    @staticmethod
    def validate_content(platform: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate content for any platform.
        
        Args:
            platform: Platform name
            content: Content dictionary
            
        Returns:
            Validation result
        """
        validators = {
            "linkedin": ContentValidator.validate_linkedin_content,
            "x": ContentValidator.validate_x_content,
            "twitter": ContentValidator.validate_x_content,
            "instagram": ContentValidator.validate_instagram_content
        }
        
        validator = validators.get(platform)
        if not validator:
            return {
                "valid": False,
                "errors": [f"Unknown platform: {platform}"],
                "warnings": []
            }
        
        return validator(content)

class URLValidator:
    """
    Validates and parses URLs.
    """
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if URL is valid."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    @staticmethod
    def is_github_url(url: str) -> bool:
        """Check if URL is a GitHub repository URL."""
        if not URLValidator.is_valid_url(url):
            return False
        
        result = urlparse(url)
        return "github.com" in result.netloc
    
    @staticmethod
    def extract_github_repo(url: str) -> tuple:
        """
        Extract owner and repo from GitHub URL.
        
        Returns:
            Tuple of (owner, repo) or (None, None)
        """
        if not URLValidator.is_github_url(url):
            return None, None
        
        parts = url.rstrip("/").split("/")
        if len(parts) >= 2:
            return parts[-2], parts[-1]
        
        return None, None