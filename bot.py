# bot.py
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from agent_core import invoke_agent

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_input = update.message.text
    await update.message.reply_text("⏳ Procesando tu mensaje...")
    try:
        response = invoke_agent(user_input, user_id)
        await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error al procesar: {e}")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Bot médico en ejecución...")
    app.run_polling()

if __name__ == "__main__":
    main()
