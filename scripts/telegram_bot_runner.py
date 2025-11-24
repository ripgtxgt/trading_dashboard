#!/usr/bin/env python3
"""
Telegram Bot Runner - Continuous execution wrapper
Keeps the Telegram bot running continuously for PM2 management
"""

import os
import sys
import time
import signal
from telegram_bot import TelegramBot

# Global flag for graceful shutdown
running = True

def signal_handler(sig, frame):
 """Handle shutdown signals"""
 global running
 print("[TG Bot Runner] Received shutdown signal, stopping...")
 running = False

def main():
 """Main runner function"""
 global running
 
 # Register signal handlers
 signal.signal(signal.SIGINT, signal_handler)
 signal.signal(signal.SIGTERM, signal_handler)
 
 print("=" * 60)
 print("Telegram Bot Runner - Starting")
 print("=" * 60)
 
 # Check environment variables
 bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
 chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
 
 if not bot_token:
 print("[WARNING] TELEGRAM_BOT_TOKEN not set")
 print("Bot will run but cannot send messages")
 
 if not chat_id:
 print("[WARNING] TELEGRAM_CHAT_ID not set")
 print("Bot will run but cannot send messages")
 
 # Initialize bot
 try:
 bot = TelegramBot(bot_token=bot_token, chat_id=chat_id)
 print("[TG Bot Runner] Bot initialized successfully")
 
 # Send startup notification if configured
 if bot_token and chat_id:
 bot.send_message("Telegram Bot started and monitoring")
 
 except Exception as e:
 print(f"[ERROR] Failed to initialize bot: {e}")
 return 1
 
 # Main loop - keep bot alive
 print("[TG Bot Runner] Entering main loop...")
 print("Bot is now running. Press Ctrl+C to stop.")
 
 loop_count = 0
 while running:
 try:
 loop_count += 1
 
 # Heartbeat every 60 seconds
 if loop_count % 60 == 0:
 print(f"[TG Bot Runner] Heartbeat - Running for {loop_count} seconds")
 
 # Sleep for 1 second
 time.sleep(1)
 
 except KeyboardInterrupt:
 print("[TG Bot Runner] Keyboard interrupt received")
 break
 except Exception as e:
 print(f"[ERROR] Error in main loop: {e}")
 time.sleep(5) # Wait before retrying
 
 # Cleanup
 print("[TG Bot Runner] Shutting down...")
 try:
 if bot_token and chat_id:
 bot.send_message("Telegram Bot stopped")
 bot.close()
 except Exception as e:
 print(f"[ERROR] Error during cleanup: {e}")
 
 print("[TG Bot Runner] Stopped")
 return 0

if __name__ == "__main__":
 sys.exit(main())
