import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from backend.app.db.database import AsyncSessionLocal
from backend.app.services.plan_service import PlanService
from bot.services.user_service import save_telegram_user


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
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
        "Your account has been successfully registered.\n\n"
        "Use /plans to view our available hotspot packages."
    )


async def plans(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if update.message is None:
        return

    async with AsyncSessionLocal() as session:
        service = PlanService(session)
        available_plans = await service.get_active_plans()

    if not available_plans:
        await update.message.reply_text(
            "😔 Sorry, there are currently no hotspot plans available."
        )
        return

    message_lines = [
        "📡 HotspotHub Hotspot Plans",
        "",
        "Choose a plan that works for you:",
        "",
    ]

    for plan in available_plans:
        message_lines.append(
            f"📶 {plan.name} — ₦{plan.price:,.2f}"
        )
        message_lines.append(
            f"   ⏱️ Duration: {plan.duration_hours} hour(s)"
        )

        if plan.description:
            message_lines.append(
                f"   ℹ️ {plan.description}"
            )

        message_lines.append("")

    message_lines.append(
        "Use /start to return to the main menu."
    )

    await update.message.reply_text(
        "\n".join(message_lines)
    )


def main():
    if not BOT_TOKEN:
        raise ValueError(
            "BOT_TOKEN is not set in the environment."
        )

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("plans", plans)
    )

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
