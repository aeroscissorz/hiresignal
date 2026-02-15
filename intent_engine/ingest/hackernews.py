"""Hacker News API ingester."""
import logging
import requests
from datetime import datetime
from typing import List, Set, Optional
from ..models import Post

logger = logging.getLogger(__name__)

HN_API_BASE = "https://hacker-news.firebaseio.com/v0"
REQUEST_TIMEOUT = 10


class HackerNewsIngester:
    """Ingests posts from Hacker News API."""
    
    def __init__(self, max_items_per_poll: int = 30):
        self.max_items_per_poll = max_items_per_poll
        self.seen_ids: Set[int] = set()
        self.last_max_id: Optional[int] = None
    
    def _fetch_new_story_ids(self) -> List[int]:
        """Fetch latest story IDs."""
        try:
            resp = requests.get(
                f"{HN_API_BASE}/newstories.json",
                timeout=REQUEST_TIMEOUT
            )
            resp.raise_for_status()
            return resp.json()[:self.max_items_per_poll]
        except Exception as e:
            logger.error(f"Error fetching HN story IDs: {e}")
            return []
    
    def _fetch_item(self, item_id: int) -> Optional[dict]:
        """Fetch a single item by ID."""
        try:
            resp = requests.get(
                f"{HN_API_BASE}/item/{item_id}.json",
                timeout=REQUEST_TIMEOUT
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"Error fetching HN item {item_id}: {e}")
            return None
    
    def _parse_item(self, item: dict) -> Optional[Post]:
        """Parse an HN item into a Post."""
        if not item or item.get("deleted") or item.get("dead"):
            return None
        
        item_id = item.get("id")
        title = item.get("title", "")
        text = item.get("text", "")
        url = item.get("url", f"https://news.ycombinator.com/item?id={item_id}")
        
        timestamp = datetime.fromtimestamp(item.get("time", 0))
        
        return Post(
            id=str(item_id),
            platform="hackernews",
            title=title,
            content=text,
            url=url,
            timestamp=timestamp
        )
    
    def fetch(self) -> List[Post]:
        """Fetch new posts from Hacker News."""
        new_posts = []
        story_ids = self._fetch_new_story_ids()
        
        for story_id in story_ids:
            if story_id in self.seen_ids:
                continue
            
            self.seen_ids.add(story_id)
            item = self._fetch_item(story_id)
            
            if item:
                post = self._parse_item(item)
                if post:
                    new_posts.append(post)
                    logger.debug(f"New HN post: {post.title[:50]}...")
        
        logger.info(f"Fetched {len(story_ids)} HN stories, {len(new_posts)} new")
        return new_posts
