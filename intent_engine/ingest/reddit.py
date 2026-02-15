"""Reddit RSS feed ingester."""
import logging
import feedparser
from datetime import datetime
from typing import List, Set
from ..models import Post

logger = logging.getLogger(__name__)


class RedditIngester:
    """Ingests posts from Reddit RSS feeds."""
    
    def __init__(self, subreddits: List[str]):
        self.subreddits = subreddits
        self.seen_ids: Set[str] = set()
    
    def _get_feed_url(self, subreddit: str) -> str:
        """Generate RSS feed URL for a subreddit."""
        return f"https://www.reddit.com/r/{subreddit}/new/.rss"
    
    def _parse_entry(self, entry, subreddit: str) -> Post:
        """Parse a feed entry into a Post."""
        post_id = entry.get("id", entry.get("link", ""))
        title = entry.get("title", "")
        content = entry.get("summary", "")
        url = entry.get("link", "")
        
        # Parse timestamp
        published = entry.get("published_parsed") or entry.get("updated_parsed")
        if published:
            timestamp = datetime(*published[:6])
        else:
            timestamp = datetime.now()
        
        return Post(
            id=post_id,
            platform=f"reddit/r/{subreddit}",
            title=title,
            content=content,
            url=url,
            timestamp=timestamp
        )
    
    def fetch(self) -> List[Post]:
        """Fetch new posts from all configured subreddits."""
        new_posts = []
        
        for subreddit in self.subreddits:
            try:
                feed_url = self._get_feed_url(subreddit)
                feed = feedparser.parse(feed_url)
                
                if feed.bozo and feed.bozo_exception:
                    logger.warning(f"Feed parse warning for r/{subreddit}: {feed.bozo_exception}")
                
                for entry in feed.entries:
                    post = self._parse_entry(entry, subreddit)
                    
                    if post.id not in self.seen_ids:
                        self.seen_ids.add(post.id)
                        new_posts.append(post)
                        logger.debug(f"New Reddit post: {post.title[:50]}...")
                
                logger.info(f"Fetched {len(feed.entries)} entries from r/{subreddit}, {len([p for p in new_posts if subreddit in p.platform])} new")
                
            except Exception as e:
                logger.error(f"Error fetching r/{subreddit}: {e}")
                continue
        
        return new_posts
