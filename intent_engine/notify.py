"""Telegram notification module - single bot for all users."""
import html
import logging
import requests
from .models import ScoredPost, User
from .config import config

logger = logging.getLogger(__name__)

TELEGRAM_API = "https://api.telegram.org"
REQUEST_TIMEOUT = 10


class TelegramNotifier:
    """Sends alerts via your single Telegram bot to all users."""
    
    def __init__(self):
        self.bot_token = config.telegram_bot_token
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        return html.escape(text)
    
    def _format_message(self, scored: ScoredPost) -> str:
        """Format a scored post into a Telegram message using HTML."""
        post = scored.post
        
        hiring_kw = ", ".join(scored.matched_hiring_keywords) or "none"
        skill_kw = ", ".join(scored.matched_skill_keywords) or "none"
        title = self._escape_html(post.title)
        
        message = (
            f"🎯 <b>New Opportunity Detected!</b>\n\n"
            f"<b>Platform:</b> {post.platform}\n"
            f"<b>Score:</b> {scored.score}\n"
            f"<b>Hiring Keywords:</b> {hiring_kw}\n"
            f"<b>Your Skills Matched:</b> {skill_kw}\n\n"
            f"<b>Title:</b> {title}\n\n"
            f"🔗 {post.url}\n\n"
            f"<i>{post.timestamp.strftime('%Y-%m-%d %H:%M')}</i>"
        )
        
        return message
    
    def send_to_user(self, user: User, scored: ScoredPost) -> bool:
        """Send a notification to a specific user."""
        if not user.telegram_chat_id:
            return False
        
        message = self._format_message(scored)
        
        try:
            url = f"{TELEGRAM_API}/bot{self.bot_token}/sendMessage"
            payload = {
                "chat_id": user.telegram_chat_id,
                "text": message,
                "parse_mode": "HTML",
                "disable_web_page_preview": False
            }
            
            resp = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            
            logger.info(f"Sent alert to {user.email}: {scored.post.title[:40]}...")
            return True
            
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                error_text = e.response.text
                logger.error(f"Telegram error for {user.email}: {error_text}")
                # If user blocked the bot, we could mark them inactive
                if "bot was blocked" in error_text.lower():
                    logger.warning(f"User {user.email} blocked the bot")
            else:
                logger.error(f"Failed to send to {user.email}: {e}")
            return self._send_plain(user, scored)
    
    def _send_plain(self, user: User, scored: ScoredPost) -> bool:
        """Fallback: send as plain text."""
        post = scored.post
        hiring_kw = ", ".join(scored.matched_hiring_keywords) or "none"
        skill_kw = ", ".join(scored.matched_skill_keywords) or "none"
        
        message = (
            f"New Opportunity Detected!\n\n"
            f"Platform: {post.platform}\n"
            f"Score: {scored.score}\n"
            f"Hiring Keywords: {hiring_kw}\n"
            f"Your Skills Matched: {skill_kw}\n\n"
            f"Title: {post.title}\n\n"
            f"{post.url}"
        )
        
        try:
            url = f"{TELEGRAM_API}/bot{self.bot_token}/sendMessage"
            payload = {
                "chat_id": user.telegram_chat_id,
                "text": message
            }
            
            resp = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            return True
        except:
            return False
    
    def send_welcome(self, chat_id: str, email: str) -> bool:
        """Send welcome message after linking."""
        message = (
            f"✅ <b>Successfully Connected!</b>\n\n"
            f"Your account <b>{email}</b> is now linked.\n\n"
            f"You'll receive alerts when we detect opportunities matching your skills.\n\n"
            f"💡 <i>Tip: Configure your skills in the dashboard to get relevant alerts.</i>"
        )
        
        try:
            url = f"{TELEGRAM_API}/bot{self.bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            resp = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            return True
        except:
            return False


# Singleton instance
_notifier = None

def get_notifier() -> TelegramNotifier:
    global _notifier
    if _notifier is None:
        _notifier = TelegramNotifier()
    return _notifier
