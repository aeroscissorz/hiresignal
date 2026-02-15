"""Configuration management via environment variables."""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """Application configuration."""
    
    # Supabase
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_anon_key: str = os.getenv("SUPABASE_ANON_KEY", "")
    supabase_service_key: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    
    # Single Telegram Bot (your bot)
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_bot_username: str = os.getenv("TELEGRAM_BOT_USERNAME", "")
    
    # Polling
    poll_interval_seconds: int = int(os.getenv("POLL_INTERVAL_SECONDS", "60"))
    
    # Scoring
    score_threshold: int = int(os.getenv("SCORE_THRESHOLD", "3"))
    
    # Reddit subreddits to monitor
    reddit_subreddits: list = None
    
    # Default hiring keywords
    hiring_keywords: list = None
    
    def __post_init__(self):
        self.reddit_subreddits = os.getenv(
            "REDDIT_SUBREDDITS", 
            "forhire,freelance,startups"
        ).split(",")
        
        self.hiring_keywords = os.getenv(
            "HIRING_KEYWORDS",
            "hiring,looking for,need,seeking,want to hire,freelancer needed,contractor,remote position,job,opportunity"
        ).lower().split(",")
    
    def validate(self) -> bool:
        """Validate required configuration."""
        if not self.supabase_url:
            raise ValueError("SUPABASE_URL is required")
        if not self.supabase_service_key:
            raise ValueError("SUPABASE_SERVICE_KEY is required")
        if not self.telegram_bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        return True


config = Config()
