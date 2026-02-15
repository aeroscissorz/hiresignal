"""Text parsing and normalization."""
import re
import html
from typing import List
from .models import Post


def normalize_text(text: str) -> str:
    """Normalize text for processing."""
    if not text:
        return ""
    
    # Decode HTML entities
    text = html.unescape(text)
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    
    # Remove URLs
    text = re.sub(r'https?://\S+', ' ', text)
    text = re.sub(r'www\.\S+', ' ', text)
    
    # Lowercase
    text = text.lower()
    
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Strip
    text = text.strip()
    
    return text


def extract_keywords(text: str, keywords: List[str]) -> List[str]:
    """Extract matching keywords from text."""
    normalized = normalize_text(text)
    matched = []
    
    for keyword in keywords:
        keyword_lower = keyword.lower().strip()
        if keyword_lower and keyword_lower in normalized:
            matched.append(keyword_lower)
    
    return matched


def prepare_post_text(post: Post) -> str:
    """Prepare combined text from post for analysis."""
    return normalize_text(post.raw_text)
