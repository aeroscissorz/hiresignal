"""Main engine orchestrating the multi-tenant polling loop."""
import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict
from .config import config
from .ingest import RedditIngester, HackerNewsIngester
from .scoring import filter_posts_for_user
from .notify import get_notifier
from .models import Post, User
from . import database

logger = logging.getLogger(__name__)

MAX_POST_AGE_HOURS = 24


class IntentEngine:
    """Multi-tenant engine that polls once and fans out to all users."""
    
    def __init__(self):
        self.reddit = RedditIngester(config.reddit_subreddits)
        self.hackernews = HackerNewsIngester()
        self.notifier = get_notifier()
        self.running = False
        self.post_cache: Dict[str, Post] = {}
    
    def fetch_all(self) -> List[Post]:
        """Fetch posts from all sources."""
        posts = []
        
        try:
            reddit_posts = self.reddit.fetch()
            posts.extend(reddit_posts)
        except Exception as e:
            logger.error(f"Reddit fetch error: {e}")
        
        try:
            hn_posts = self.hackernews.fetch()
            posts.extend(hn_posts)
        except Exception as e:
            logger.error(f"HN fetch error: {e}")
        
        return posts
    
    def filter_recent_posts(self, posts: List[Post]) -> List[Post]:
        """Filter posts to only include those from the last 24 hours."""
        cutoff = datetime.now() - timedelta(hours=MAX_POST_AGE_HOURS)
        return [p for p in posts if p.timestamp >= cutoff]
    
    def update_cache(self, posts: List[Post]):
        """Update the post cache with new posts."""
        for post in posts:
            if post.id not in self.post_cache:
                self.post_cache[post.id] = post
        
        cutoff = datetime.now() - timedelta(hours=MAX_POST_AGE_HOURS)
        self.post_cache = {
            pid: post for pid, post in self.post_cache.items()
            if post.timestamp >= cutoff
        }
    
    def process_for_user(self, user: User, posts: List[Post]) -> int:
        """Process posts for a single user. Returns alerts sent."""
        notified_ids = database.get_user_notified_posts(user.id)
        new_posts = [p for p in posts if p.id not in notified_ids]
        
        if not new_posts:
            return 0
        
        scored_posts = filter_posts_for_user(new_posts, user)
        
        if not scored_posts:
            return 0
        
        sent = 0
        for scored in scored_posts:
            if self.notifier.send_to_user(user, scored):
                database.update_user_last_notified(user.id, scored.post.id)
                sent += 1
        
        return sent
    
    def process_cycle(self) -> int:
        """Run one polling cycle. Returns total alerts sent."""
        logger.info("Starting poll cycle...")
        
        posts = self.fetch_all()
        recent_posts = self.filter_recent_posts(posts)
        self.update_cache(recent_posts)
        
        all_recent = list(self.post_cache.values())
        logger.info(f"Processing {len(all_recent)} recent posts")
        
        if not all_recent:
            return 0
        
        users_data = database.get_active_users()
        users = [User.from_dict(u) for u in users_data]
        
        logger.info(f"Processing for {len(users)} active users with Telegram linked")
        
        if not users:
            return 0
        
        total_sent = 0
        for user in users:
            try:
                sent = self.process_for_user(user, all_recent)
                if sent > 0:
                    logger.info(f"Sent {sent} alerts to {user.email}")
                total_sent += sent
            except Exception as e:
                logger.error(f"Error processing user {user.id}: {e}")
        
        logger.info(f"Cycle complete. Total alerts: {total_sent}")
        return total_sent
    
    def run(self):
        """Run the engine continuously."""
        config.validate()
        self.running = True
        
        logger.info("Intent Engine started")
        logger.info(f"Monitoring: {config.reddit_subreddits}")
        logger.info(f"Poll interval: {config.poll_interval_seconds}s")
        
        while self.running:
            try:
                self.process_cycle()
            except Exception as e:
                logger.error(f"Cycle error: {e}")
            
            time.sleep(config.poll_interval_seconds)
    
    def stop(self):
        self.running = False
        logger.info("Intent Engine stopped")
