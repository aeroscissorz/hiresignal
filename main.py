#!/usr/bin/env python3
"""Entry point for Intent Engine."""
import logging
import signal
import sys

from intent_engine.engine import IntentEngine
from intent_engine.telegram_bot import start_bot_handler, set_engine_ref

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point."""
    # Start the main engine first
    engine = IntentEngine()
    
    # Set engine reference for telegram bot (for welcome posts)
    set_engine_ref(engine)
    
    # Start Telegram bot handler (for /start linking)
    bot_handler = start_bot_handler()
    
    def shutdown(signum, frame):
        logger.info("Shutdown signal received")
        engine.stop()
        bot_handler.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)
    
    try:
        engine.run()
    except KeyboardInterrupt:
        engine.stop()
        bot_handler.stop()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
