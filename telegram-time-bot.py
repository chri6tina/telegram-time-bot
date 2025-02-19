import logging
import pytz
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext
import os
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# Define time zones
PHT = pytz.timezone("Asia/Manila")
EST = pytz.timezone("America/New_York")  # Your local timezone


# Store user states for input handling
user_states = {}


async def start(update: Update, context: CallbackContext) -> None:
    """Send a welcome message only when /start is used."""
    welcome_message = (
        "👋 **Welcome to the EST ↔ PHT Time Converter Bot!**\n\n"
        "This bot helps you quickly convert times between **Eastern Standard Time (EST)** and **Philippine Time (PHT)**.\n\n"
        "✅ **How to Use:**\n"
        "1️⃣ **Tap 'Time Right Now in PHT'** to see the current PHT time.\n"
        "2️⃣ **Tap 'Custom EST to PHT'** and type a time (e.g., `3pm`, `1 AM`).\n"
        "3️⃣ **Tap 'Custom PHT to EST'** and type a time (e.g., `15:00`, `7 AM`).\n"
        "4️⃣ The bot will reply with the **converted time and whether it’s today or tomorrow**.\n\n"
        "Let's get started! 🚀"
    )


    if update.message:
        await update.message.reply_text(welcome_message)
        await show_main_menu(update)


async def show_main_menu(update):
    """Displays the main menu buttons after the welcome message or actions."""
    keyboard = [
        [InlineKeyboardButton("⏰ Time Right Now in PHT", callback_data="current_pht")],
        [InlineKeyboardButton("🕒 Custom EST to PHT", callback_data="custom_est_to_pht")],
        [InlineKeyboardButton("🕒 Custom PHT to EST", callback_data="custom_pht_to_est")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)


    if update.message:
        await update.message.reply_text("🔄 What would you like to do next?", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text("🔄 What would you like to do next?", reply_markup=reply_markup)


async def button_click(update: Update, context: CallbackContext) -> None:
    """Handles button clicks for current PHT time."""
    query = update.callback_query
    await query.answer()


    if query.data == "current_pht":
        current_pht_time = datetime.now(PHT)
        await query.message.reply_text(f"⏰ **Current Time in PHT:** {current_pht_time.strftime('%I:%M %p PHT')}")
        await show_main_menu(update)


async def request_custom_time(update: Update, context: CallbackContext) -> None:
    """Ask the user to input a custom time for EST to PHT or PHT to EST."""
    query = update.callback_query
    user_id = query.from_user.id


    if query.data == "custom_est_to_pht":
        user_states[user_id] = "waiting_for_est_to_pht"
        await query.message.reply_text("⌨️ **Enter a time (e.g., `3pm`, `4 PM`, `1am`) to convert it from EST to PHT:**")
   
    elif query.data == "custom_pht_to_est":
        user_states[user_id] = "waiting_for_pht_to_est"
        await query.message.reply_text("⌨️ **Enter a time (e.g., `15:00`, `7 AM`) to convert it from PHT to EST:**")


async def handle_custom_time(update: Update, context: CallbackContext) -> None:
    """Converts user-provided time from EST to PHT or PHT to EST with a single-line response."""
    user_id = update.message.from_user.id


    if user_id in user_states:
        conversion_type = user_states[user_id]


        try:
            user_input = update.message.text.strip().lower()
            today = datetime.now().strftime("%Y-%m-%d")


            # Try parsing the input time
            try:
                if conversion_type == "waiting_for_est_to_pht":
                    input_time = datetime.strptime(user_input, "%I%p")  # Example: 3pm, 1am
                elif conversion_type == "waiting_for_pht_to_est":
                    input_time = datetime.strptime(user_input, "%H:%M")  # Example: 15:00 (24-hour format)
            except ValueError:
                try:
                    input_time = datetime.strptime(user_input, "%I %p")  # Example: 3 PM, 1 AM, 7 AM, 10 PM
                except ValueError:
                    await update.message.reply_text("⚠️ Invalid format. Please enter a time correctly.")
                    return


            # Combine today's date with the input time
            full_time_str = f"{today} {input_time.strftime('%H:%M')}"
            user_time = datetime.strptime(full_time_str, "%Y-%m-%d %H:%M")


            if conversion_type == "waiting_for_est_to_pht":
                est_time = EST.localize(user_time)
                pht_time = est_time.astimezone(PHT)
                day_status = "same day" if est_time.day == pht_time.day else "next day"
                response = f"⏳ **{est_time.strftime('%I:%M %p EST')} → {pht_time.strftime('%I:%M %p PHT')}** ({day_status} in PHT)"
           
            elif conversion_type == "waiting_for_pht_to_est":
                pht_time = PHT.localize(user_time)
                est_time = pht_time.astimezone(EST)
                day_status = "same day" if pht_time.day == est_time.day else "previous day"
                response = f"⏳ **{pht_time.strftime('%I:%M %p PHT')} → {est_time.strftime('%I:%M %p EST')}** ({day_status} in EST)"


            # Send response and show main menu again
            await update.message.reply_text(response)
            del user_states[user_id]
            await show_main_menu(update)


        except Exception as e:
            logger.error(f"Error parsing time: {e}")
            await update.message.reply_text("⚠️ Something went wrong. Please try again.")


def main():
    """Run the bot."""
   


    app = Application.builder().token(BOT_TOKEN).build()


    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click, pattern="current_pht"))  # Current time in PHT
    app.add_handler(CallbackQueryHandler(request_custom_time, pattern="custom_est_to_pht"))  # EST to PHT
    app.add_handler(CallbackQueryHandler(request_custom_time, pattern="custom_pht_to_est"))  # PHT to EST
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_custom_time))  # Handles user input


    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()


