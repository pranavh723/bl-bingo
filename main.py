import logging
import os
import threading
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from handlers import start, game, settings, leaderboard
from utils import scheduler
from db.db import setup_database  # Import the setup function for database initialization

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get the bot token from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

def main_menu_keyboard():
    """Create the main menu inline keyboard."""
    keyboard = [
        [InlineKeyboardButton("🎮 Start Game", callback_data='start_game')],
        [InlineKeyboardButton("🏆 Leaderboard", callback_data='leaderboard')],
        [InlineKeyboardButton("⚙️ Settings", callback_data='settings')],
        [InlineKeyboardButton("🎯 Daily Quests", callback_data='daily_quests')],
        [InlineKeyboardButton("🪙 Shop", callback_data='shop')],
        [InlineKeyboardButton("📣 Support Group", url='https://t.me/your_support_group')],
        [InlineKeyboardButton("🔔 Updates Channel", url='https://t.me/your_updates_channel')]
    ]
    return InlineKeyboardMarkup(keyboard)

def start_handler(update: Update, context: CallbackContext):
    """Handle the /start command."""
    update.message.reply_text(
        "Welcome to the Bingo Bot! Choose an option:",
        reply_markup=main_menu_keyboard()
    )

def callback_router(update: Update, context: CallbackContext):
    """Route callback queries to the appropriate handler."""
    query = update.callback_query
    data = query.data
    logger.info(f"Received callback data: {data}")

    if not data:
        query.answer()
        return

    if data.startswith('start_game'):
        game.game_callback_handler(update, context)
    elif data.startswith('leaderboard'):
        leaderboard.leaderboard_callback_handler(update, context)
    elif data.startswith('settings'):
        settings.settings_callback_handler(update, context)
    elif data.startswith('daily_quests'):
        query.answer()
        query.edit_message_text("🎯 Daily Quests feature coming soon!")
    elif data.startswith('shop'):
        query.answer()
        query.edit_message_text("🪙 Shop feature coming soon!")
    else:
        query.answer()
        query.edit_message_text("⚠️ Unknown option selected.")

def main():
    """Main function to start the bot."""
    # Setup the database
    setup_database()

    # Create the Updater and pass it your bot's token
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher

    # Register command and callback query handlers
    dp.add_handler(CommandHandler("start", start_handler))
    dp.add_handler(CallbackQueryHandler(callback_router))

    # Start the scheduler in a background thread
    scheduler_thread = threading.Thread(target=scheduler.run_scheduler, daemon=True)
    scheduler_thread.start()

    # Start polling for updates
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
