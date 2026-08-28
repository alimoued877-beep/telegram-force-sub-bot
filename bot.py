import os
import threading

from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.error import TelegramError


BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])
CHANNEL_INVITE_LINK = os.environ["CHANNEL_INVITE_LINK"]
CHANNEL_TITLE = os.environ.get("CHANNEL_TITLE", "القناة")


web = Flask(__name__)


@web.route("/")
def home():
    return "Bot is running!", 200


def subscribe_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                f"📢 اشترك في {CHANNEL_TITLE}",
                url=CHANNEL_INVITE_LINK
            )
        ]
    ])


async def is_subscribed(user_id, context):
    try:
        member = await context.bot.get_chat_member(
            chat_id=CHANNEL_ID,
            user_id=user_id
        )

        return member.status in (
            "member",
            "administrator",
            "creator"
        )

    except TelegramError:
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"👋 أهلاً بك\n\n"
        f"حتى تگدر تستخدم المجموعة، لازم تشترك أولاً في:\n"
        f"📢 {CHANNEL_TITLE}\n\n"
        f"بعد الاشتراك ارجع للمجموعة."
        ,
        reply_markup=subscribe_keyboard()
    )


async def check_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.effective_user:
        return

    # نتأكد أن المستخدم مشترك بالقناة
    subscribed = await is_subscribed(
        update.effective_user.id,
        context
    )

    if subscribed:
        return

    # إذا غير مشترك نحذف رسالته
    try:
        await update.message.delete()
    except TelegramError:
        pass

    # نرسل له رسالة خاصة
    try:
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=(
                f"🔒 ما تگدر تراسل بالمجموعة حالياً.\n\n"
                f"لازم تشترك أولاً في:\n"
                f"📢 {CHANNEL_TITLE}\n\n"
                f"بعد الاشتراك تگدر ترجع للمجموعة وتراسل."
            ),
            reply_markup=subscribe_keyboard()
        )

    except TelegramError:
        # إذا المستخدم ما فاتح البوت من قبل
        pass


def run_web():
    port = int(os.environ.get("PORT", "10000"))

    web.run(
        host="0.0.0.0",
        port=port
    )


def main():

    threading.Thread(
        target=run_web,
        daemon=True
    ).start()

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        MessageHandler(
            filters.ALL & ~filters.COMMAND,
            check_message
        )
    )

    print("Bot started!")

    application.run_polling()


if __name__ == "__main__":
    main()
