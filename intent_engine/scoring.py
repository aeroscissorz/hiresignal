"""Scoring logic for intent detection."""
import logging
from typing import List
from .models import Post, ScoredPost, User
from .parse import extract_keywords, prepare_post_text
from .config import config

logger = logging.getLogger(__name__)

# Weights
HIRING_KEYWORD_WEIGHT = 2
SKILL_KEYWORD_WEIGHT = 1


def score_post_for_user(post: Post, user: User) -> ScoredPost:
    """Score a post for a specific user based on their keywords."""
    text = prepare_post_text(post)
    
    # Extract matches using global hiring keywords
    hiring_matches = extract_keywords(text, config.hiring_keywords)
    
    # Extract matches using user's skill keywords
    skill_matches = extract_keywords(text, user.skill_keywords)
    
    # Calculate score
    score = (
        len(hiring_matches) * HIRING_KEYWORD_WEIGHT +
        len(skill_matches) * SKILL_KEYWORD_WEIGHT
    )
    
    return ScoredPost(
        post=post,
        score=score,
        matched_hiring_keywords=hiring_matches,
        matched_skill_keywords=skill_matches
    )


def filter_posts_for_user(posts: List[Post], user: User) -> List[ScoredPost]:
    """Score and filter posts for a specific user."""
    results = []
    
    for post in posts:
        scored = score_post_for_user(post, user)
        if scored.score >= user.score_threshold:
            results.append(scored)
    
    return results
