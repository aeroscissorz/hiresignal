"""Supabase database client and operations."""
import logging
import secrets
from typing import List, Optional, Dict, Any
from supabase import create_client, Client
from .config import config

logger = logging.getLogger(__name__)

_client: Optional[Client] = None


def get_client() -> Client:
    """Get or create Supabase client."""
    global _client
    if _client is None:
        _client = create_client(config.supabase_url, config.supabase_service_key)
    return _client


def get_active_users() -> List[Dict[str, Any]]:
    """Fetch all active users with Telegram linked."""
    try:
        client = get_client()
        response = client.table("users").select("*").eq("is_active", True).not_.is_("telegram_chat_id", "null").execute()
        return response.data or []
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        return []


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Fetch a single user by ID."""
    try:
        client = get_client()
        response = client.table("users").select("*").eq("id", user_id).single().execute()
        return response.data
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {e}")
        return None


def get_user_by_link_code(code: str) -> Optional[Dict[str, Any]]:
    """Fetch user by their Telegram link code."""
    try:
        client = get_client()
        response = client.table("users").select("*").eq("telegram_link_code", code).single().execute()
        return response.data
    except Exception as e:
        logger.error(f"Error fetching user by link code: {e}")
        return None


def get_user_by_chat_id(chat_id: str) -> Optional[Dict[str, Any]]:
    """Fetch user by their Telegram chat ID."""
    try:
        client = get_client()
        response = client.table("users").select("*").eq("telegram_chat_id", chat_id).single().execute()
        return response.data
    except Exception as e:
        logger.error(f"Error fetching user by chat_id: {e}")
        return None


def link_telegram(user_id: str, chat_id: str) -> bool:
    """Link a Telegram chat ID to a user."""
    try:
        client = get_client()
        client.table("users").update({
            "telegram_chat_id": chat_id,
            "telegram_link_code": None  # Clear the code after linking
        }).eq("id", user_id).execute()
        return True
    except Exception as e:
        logger.error(f"Error linking Telegram: {e}")
        return False


def generate_link_code(user_id: str) -> Optional[str]:
    """Generate a unique link code for Telegram connection."""
    try:
        code = secrets.token_urlsafe(16)
        client = get_client()
        client.table("users").update({
            "telegram_link_code": code
        }).eq("id", user_id).execute()
        return code
    except Exception as e:
        logger.error(f"Error generating link code: {e}")
        return None


def unlink_telegram(user_id: str) -> bool:
    """Unlink Telegram from a user."""
    try:
        client = get_client()
        client.table("users").update({
            "telegram_chat_id": None
        }).eq("id", user_id).execute()
        return True
    except Exception as e:
        logger.error(f"Error unlinking Telegram: {e}")
        return False


def update_user_last_notified(user_id: str, post_id: str) -> bool:
    """Track that a user was notified about a post."""
    try:
        client = get_client()
        client.table("notifications").insert({
            "user_id": user_id,
            "post_id": post_id
        }).execute()
        return True
    except Exception as e:
        logger.error(f"Error tracking notification: {e}")
        return False


def get_user_notified_posts(user_id: str) -> set:
    """Get all post IDs a user has been notified about."""
    try:
        client = get_client()
        response = client.table("notifications").select("post_id").eq("user_id", user_id).execute()
        return {row["post_id"] for row in (response.data or [])}
    except Exception as e:
        logger.error(f"Error fetching user notifications: {e}")
        return set()
