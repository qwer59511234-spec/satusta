import os
import logging
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image
import io

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API keys
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Gemini sozlash
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

SYSTEM_PROMPT = """Sen SAT imtihoni bo'yicha mutaxassis o'qituvchisan.
Foydalanuvchi SAT savol yuboradi (matn yoki rasm ko'rinishida).
Sening vazifang:
1. To'g'ri javobni top
2. Nima uchun shu javob to'g'ri ekanligini tushuntir
3. Boshqa variantlar nima uchun noto'g'ri ekanini tushuntir
4. Kerakli formulalar yoki qoidalarni eslatib o't

Javobingni o'zbek tilida ber. Aniq, tushunarli va qisqa bo'l."""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Salom! Men SAT savolarini yechadigan botman!\n\n"
        "📝 Menga SAT savolini yubor:\n"
        "• Matn ko'rinishida yoz\n"
        "• Yoki rasm yuklat (screenshot)\n\n"
        "Men javobini topib, tushuntirib beraman! 🎯"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 Qanday foydalanish:\n\n"
        "1️⃣ SAT savolini yoz yoki rasm yuklat\n"
        "2️⃣ Men javobini topaman\n"
        "3️⃣ Tushuntirishni o'qib o'rgan\n\n"
        "✅ Math, Reading, Writing — hammasi ishlaydi!"
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    await update.message.reply_text("⏳ Tahlil qilyapman...")

    try:
        prompt = f"{SYSTEM_PROMPT}\n\nSavol:\n{user_message}"
        response = model.generate_content(prompt)
        await update.message.reply_text(response.text)
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("❌ Xatolik yuz berdi. Qaytadan urining.")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Rasmni o'qiyapman...")

    try:
        # Rasmni yuklab olish
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        file_bytes = await file.download_as_bytearray()

        # PIL bilan ochish
        image = Image.open(io.BytesIO(file_bytes))

        # Gemini ga yuborish
        prompt = f"{SYSTEM_PROMPT}\n\nRasmdagi SAT savolini hal qil."
        response = model.generate_content([prompt, image])
        await update.message.reply_text(response.text)

    except Exception as e:
        logger.error(f"Photo error: {e}")
        await update.message.reply_text("❌ Rasmni o'qishda xatolik. Aniqroq rasm yuboring.")


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    logger.info("Bot ishga tushdi!")
    app.run_polling()


if __name__ == "__main__":
    main()
