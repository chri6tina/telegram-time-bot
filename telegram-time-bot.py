# Environment setup MUST COME FIRST
import os
from dotenv import load_dotenv

# Load environment variables from .env file (local development)
load_dotenv()  # <-- Critical for local testing

# Now import other dependencies
import logging
import pytz
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Initialize bot token from environment
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Railway will auto-set this in production

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define time zones
PHT = pytz.timezone("Asia/Manila")
EST = pytz.timezone("America/New_York")

async def start(update: Update, context: CallbackContext) -> None:
    """Send a welcome message when /start is used."""
    welcome_message = (
        "👋 **Welcome to the EST ↔ PHT Time Converter Bot!**\n\n"
        "This bot helps you quickly convert times between **Eastern Standard Time (EST)** and **Philippine Time (PHT)**.\n\n"
        "✅ **How to Use:**\n"
        "1️⃣ Type a time (e.g., `7pm`, `1 AM`) to convert it from EST to PHT or PHT to EST.\n"
        "2️⃣ Use `/time` to see the current time in PHT.\n\n"
        "Let's get started! 🚀"
    )
    await update.message.reply_text(welcome_message)

async def current_time(update: Update, context: CallbackContext) -> None:
    """Send the current time in PHT when /time is used."""
    current_pht_time = datetime.now(PHT)
    await update.message.reply_text(f"{current_pht_time.strftime('%I:%M%p PHT (%B %d)')}".lower())

async def handle_time_input(update: Update, context: CallbackContext) -> None:
    """Automatically converts user-provided time to both PHT and EST with dates."""
    user_input = update.message.text.strip().lower()

    try:
        # Try parsing the input time
        try:
            input_time = datetime.strptime(user_input, "%I%p")  # Example: 7pm, 1am
        except ValueError:
            try:
                input_time = datetime.strptime(user_input, "%I %p")  # Example: 7 PM, 1 AM
            except ValueError:
                await update.message.reply_text("⚠️ Invalid format. Please enter a time like `7pm` or `7 PM`.")
                return

        # Combine today's date with the input time
        today = datetime.now().strftime("%Y-%m-%d")
        full_time_str = f"{today} {input_time.strftime('%H:%M')}"
        user_time = datetime.strptime(full_time_str, "%Y-%m-%d %H:%M")

        # Convert PHT to EST
        pht_time = PHT.localize(user_time)
        est_time_from_pht = pht_time.astimezone(EST)
        day_status_pht_to_est = "same day" if pht_time.day == est_time_from_pht.day else (
            "next day" if est_time_from_pht.day > pht_time.day else "previous day"
        )
        pht_to_est_response = (
            f"{pht_time.strftime('%I:%M%p PHT')} ➡️ {est_time_from_pht.strftime('%I:%M%p EST')} ({day_status_pht_to_est})"
        ).lower()

        # Convert EST to PHT
        est_time = EST.localize(user_time)
        pht_time_from_est = est_time.astimezone(PHT)
        day_status_est_to_pht = "same day" if est_time.day == pht_time_from_est.day else (
            "next day" if pht_time_from_est.day > est_time.day else "previous day"
        )
        est_to_pht_response = (
            f"{est_time.strftime('%I:%M%p EST')} ➡️ {pht_time_from_est.strftime('%I:%M%p PHT')} ({day_status_est_to_pht})"
        ).lower()

        # Send both responses
        await update.message.reply_text(pht_to_est_response)
        await update.message.reply_text(est_to_pht_response)

    except Exception as e:
        logger.error(f"Error parsing time: {e}")
        await update.message.reply_text("⚠️ Something went wrong. Please try again.")

def main():
    """Run the bot."""
    app = Application.builder().token(BOT_TOKEN).build()

    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("time", current_time))

    # Automatically handle any text input (no commands needed)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_time_input))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
