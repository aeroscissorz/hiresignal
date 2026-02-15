"""Data ingestion modules."""
from .reddit import RedditIngester
from .hackernews import HackerNewsIngester

__all__ = ["RedditIngester", "HackerNewsIngester"]
