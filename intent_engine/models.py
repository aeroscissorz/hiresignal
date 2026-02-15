"""Data models for the intent engine."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Post:
    """Normalized post from any source."""
    id: str
    platform: str
    title: str
    content: str
    url: str
    timestamp: datetime
    raw_text: str = ""
    
    def __post_init__(self):
        self.raw_text = f"{self.title} {self.content}"


@dataclass
class ScoredPost:
    """Post with scoring information."""
    post: Post
    score: int
    matched_hiring_keywords: List[str] = field(default_factory=list)
    matched_skill_keywords: List[str] = field(default_factory=list)
    
    @property
    def all_matched_keywords(self) -> List[str]:
        return self.matched_hiring_keywords + self.matched_skill_keywords


@dataclass
class User:
    """User configuration from database."""
    id: str
    email: str
    telegram_chat_id: Optional[str]
    telegram_linked: bool
    skill_keywords: List[str]
    is_active: bool = True
    score_threshold: int = 3
    
    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Create User from database row."""
        keywords = data.get("skill_keywords") or []
        if isinstance(keywords, str):
            keywords = [k.strip().lower() for k in keywords.split(",") if k.strip()]
        
        return cls(
            id=data["id"],
            email=data.get("email", ""),
            telegram_chat_id=data.get("telegram_chat_id"),
            telegram_linked=bool(data.get("telegram_chat_id")),
            skill_keywords=keywords,
            is_active=data.get("is_active", True),
            score_threshold=data.get("score_threshold", 3)
        )
