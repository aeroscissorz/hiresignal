"""Telegram bot handler for user linking via /start command."""
import logging
import requests
import time
from threading import Thread
from .config import config
from . import database
from .notify import get_notifier
from .models import User

logger = logging.getLogger(__name__)

# Reference to the engine for sending welcome posts
_engine_ref = None

def set_engine_ref(engine):
    """Set reference to the engine for welcome post sending."""
    global _engine_ref
    _engine_ref = engine

TELEGRAM_API = "https://api.telegram.org"


class TelegramBotHandler:
    """Handles incoming Telegram messages for user linking."""
    
    def __init__(self):
        self.bot_token = config.telegram_bot_token
        self.last_update_id = 0
        self.running = False
    
    def _get_updates(self):
        """Poll for new messages."""
        try:
            url = f"{TELEGRAM_API}/bot{self.bot_token}/getUpdates"
            params = {
                "offset": self.last_update_id + 1,
                "timeout": 30
            }
            resp = requests.get(url, params=params, timeout=35)
            resp.raise_for_status()
            return resp.json().get("result", [])
        except Exception as e:
            logger.error(f"Error getting updates: {e}")
            return []
    
    def _handle_message(self, message: dict):
        """Handle an incoming message."""
        chat_id = str(message.get("chat", {}).get("id"))
        text = message.get("text", "")
        
        if not chat_id or not text:
            return
        
        # Handle /start with link code
        if text.startswith("/start"):
            parts = text.split()
            if len(parts) > 1:
                link_code = parts[1]
                self._handle_link(chat_id, link_code)
            else:
                self._send_message(chat_id, 
                    "👋 Welcome to HireSignal!\n\n"
                    "To connect your account, please use the link from your dashboard.\n\n"
                    "Commands:\n"
                    "/gift - Get past 24h opportunities\n"
                    "/help - Show help\n"
                    "/status - Check connection status"
                )
        
        elif text.startswith("/gift"):
            self._handle_gift(chat_id)
        
        elif text.startswith("/help"):
            self._send_message(chat_id,
                "🚀 HireSignal Bot\n\n"
                "I'll send you job opportunities matching your skills!\n\n"
                "Commands:\n"
                "/gift - Get past 24h opportunities\n"
                "/status - Check your connection\n"
                "/help - Show this message"
            )
        
        elif text.startswith("/status"):
            self._handle_status(chat_id)
    
    def _handle_status(self, chat_id: str):
        """Check user's connection status."""
        user_data = database.get_user_by_chat_id(chat_id)
        if user_data:
            skills = user_data.get("skill_keywords") or []
            skill_text = ", ".join(skills) if skills else "None set"
            self._send_message(chat_id,
                f"✅ Connected!\n\n"
                f"Email: {user_data.get('email')}\n"
                f"Skills: {skill_text}\n\n"
                f"💡 Update your skills in the dashboard to get better matches."
            )
        else:
            self._send_message(chat_id,
                "❌ Not connected.\n\n"
                "Please link your account from the HireSignal dashboard."
            )
    
    def _handle_gift(self, chat_id: str):
        """Send past 24h posts to an existing user."""
        user_data = database.get_user_by_chat_id(chat_id)
        if not user_data:
            self._send_message(chat_id,
                "❌ Your account is not linked.\n\n"
                "Please connect from the HireSignal dashboard first."
            )
            return
        
        self._send_message(chat_id, "🔍 Searching for opportunities...")
        self._send_welcome_posts(user_data, chat_id)
    
    def _handle_link(self, chat_id: str, link_code: str):
        """Link a user's Telegram account."""
        user_data = database.get_user_by_link_code(link_code)
        
        if not user_data:
            self._send_message(chat_id, 
                "❌ Invalid or expired link code.\n\n"
                "Please generate a new link from your dashboard."
            )
            return
        
        # Link the account
        if database.link_telegram(user_data["id"], chat_id):
            notifier = get_notifier()
            notifier.send_welcome(chat_id, user_data.get("email", ""))
            logger.info(f"Linked Telegram for user {user_data.get('email')}")
            
            # Send past 24h posts as welcome gift
            self._send_welcome_posts(user_data, chat_id)
        else:
            self._send_message(chat_id, "❌ Failed to link account. Please try again.")
    
    def _send_welcome_posts(self, user_data: dict, chat_id: str):
        """Send all matching posts from past 24h as a welcome gift."""
        global _engine_ref
        
        if not _engine_ref:
            logger.warning("Engine reference not set, skipping welcome posts")
            return
        
        try:
            # Update user_data with the new chat_id since it was just linked
            user_data["telegram_chat_id"] = chat_id
            user = User.from_dict(user_data)
            
            # Get all cached posts from the engine
            all_posts = list(_engine_ref.post_cache.values())
            
            if not all_posts:
                logger.info(f"No cached posts to send as welcome gift")
                return
            
            # Import here to avoid circular import
            from .scoring import filter_posts_for_user
            
            # Score and filter posts for this user
            scored_posts = filter_posts_for_user(all_posts, user)
            
            if not scored_posts:
                logger.info(f"No matching posts for welcome gift to {user.email}")
                return
            
            # Send intro message
            count = len(scored_posts)
            self._send_message(chat_id, 
                f"🎁 Welcome Gift!\n\n"
                f"Here are {count} opportunities from the past 24 hours that match your skills:"
            )
            
            # Send each post
            notifier = get_notifier()
            sent = 0
            for scored in scored_posts[:10]:  # Limit to 10 to avoid spam
                if notifier.send_to_user(user, scored):
                    database.update_user_last_notified(user.id, scored.post.id)
                    sent += 1
                time.sleep(0.5)  # Small delay to avoid rate limits
            
            if sent > 0:
                logger.info(f"Sent {sent} welcome posts to {user.email}")
                
            if count > 10:
                self._send_message(chat_id,
                    f"📬 Showing top 10 of {count} matches. You'll get new ones as they come in!"
                )
        except Exception as e:
            logger.error(f"Error sending welcome posts: {e}")
    
    def _send_message(self, chat_id: str, text: str):
        """Send a message to a chat."""
        try:
            url = f"{TELEGRAM_API}/bot{self.bot_token}/sendMessage"
            payload = {"chat_id": chat_id, "text": text}
            requests.post(url, json=payload, timeout=10)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
    
    def run(self):
        """Run the bot polling loop."""
        self.running = True
        logger.info("Telegram bot handler started")
        
        while self.running:
            updates = self._get_updates()
            
            for update in updates:
                self.last_update_id = update.get("update_id", self.last_update_id)
                
                if "message" in update:
                    self._handle_message(update["message"])
            
            time.sleep(1)
    
    def stop(self):
        """Stop the bot."""
        self.running = False


def start_bot_handler():
    """Start the bot handler in a background thread."""
    handler = TelegramBotHandler()
    thread = Thread(target=handler.run, daemon=True)
    thread.start()
    return handler
