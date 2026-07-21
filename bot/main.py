import os

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

from backend.app.db.database import AsyncSessionLocal
from backend.app.services.plan_service import PlanService
from backend.app.services.purchase_service import PurchaseService
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

    keyboard = []

    for plan in available_plans:
        message_lines.append(
            f"📶 {plan.name} — ₦{plan.price:,.2f}"
        )

        if plan.description:
            message_lines.append(
                f"   ℹ️ {plan.description}"
            )

        message_lines.append("")

        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"🛒 Buy {plan.name}",
                    callback_data=f"buy_plan:{plan.id}",
                )
            ]
        )

    await update.message.reply_text(
        "\n".join(message_lines),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
async def buy_plan(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query

    if query is None:
        return

    await query.answer()

    data = query.data

    if not data or not data.startswith("buy_plan:"):
        return

    plan_id = int(data.split(":")[1])

    async with AsyncSessionLocal() as session:
        service = PlanService(session)
        plan = await service.get_plan(plan_id)

    if plan is None:
        await query.message.reply_text(
            "❌ Sorry, this plan could not be found."
        )
        return

    if not plan.is_active:
        await query.message.reply_text(
            "❌ Sorry, this plan is no longer available."
        )
        return

    keyboard = [
        [
            InlineKeyboardButton(
                text="✅ Confirm Purchase",
                callback_data=f"confirm_purchase:{plan.id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="❌ Cancel",
                callback_data="cancel_purchase",
            ),
        ],
    ]

    await query.message.reply_text(
        f"🛒 Purchase Confirmation\n\n"
        f"📶 Plan: {plan.name}\n"
        f"⏱️ Duration: {plan.duration_hours} hour(s)\n"
        f"💰 Price: ₦{plan.price:,.2f}\n\n"
        "Are you sure you want to continue?",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
async def confirm_purchase(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query

    if query is None or query.from_user is None:
        return

    await query.answer()

    data = query.data

    if not data or not data.startswith("confirm_purchase:"):
        return

    plan_id = int(data.split(":")[1])

    telegram_user = query.from_user

    async with AsyncSessionLocal() as session:
        user = await save_telegram_user(
            session=session,
            telegram_id=telegram_user.id,
            username=telegram_user.username,
            first_name=telegram_user.first_name,
            last_name=telegram_user.last_name,
        )

        purchase_service = PurchaseService(session)

        try:
            purchase = await purchase_service.create_purchase(
                user_id=user.id,
                plan_id=plan_id,
            )

        except ValueError as error:
            await query.message.reply_text(
                f"❌ {error}"
            )
            return

    await query.message.reply_text(
        f"✅ Purchase created successfully!\n\n"
        f"🧾 Purchase ID: {purchase.id}\n"
        f"💰 Amount: ₦{purchase.amount:,.2f}\n"
        f"📌 Status: {purchase.status}\n\n"
        "Your payment is now pending."
    )

async def cancel_purchase(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query

    if query is None:
        return

    await query.answer()

    await query.message.reply_text(
        "❌ Purchase cancelled.\n\n"
        "No payment has been made and no purchase was created."
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

    app.add_handler(
        CallbackQueryHandler(
            buy_plan,
            pattern=r"^buy_plan:\d+$",
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            confirm_purchase,
            pattern=r"^confirm_purchase:\d+$",
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            cancel_purchase,
            pattern=r"^cancel_purchase$",
        )
    )

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
