from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv
import os

from backend.app.db.database import AsyncSessionLocal
from bot.services.user_service import save_telegram_user


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user is None or update.message is None:
        return

    telegram_user = update.effective_user

    async with AsyncSessionLocal() as session:
        user = await save_telegram_user(
            session=session,
            telegram_id=telegram_user.id,
            username=telegram_user.username,
            first_name=telegram_user.first_name,
            last_name=telegram_user.last_name,
        )

    await update.message.reply_text(
        f"🚀 Welcome to HotspotHub, {user.first_name}!\n\n"
        "Your account has been successfully registered."
    )


def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is not set in the environment.")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
