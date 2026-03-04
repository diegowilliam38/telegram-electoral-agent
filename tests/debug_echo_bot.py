import logging
import asyncio
import sys
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters, MessageHandler
from src.config import TELEGRAM_BOT_TOKEN

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Start received from {update.effective_user.id}")
    await context.bot.send_message(chat_id=update.effective_chat.id, text="✅ TESTE: Conexão bem sucedida!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    logger.info(f"Echoing: {msg}")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Recebi: {msg}")

if __name__ == '__main__':
    print("🚀 Starting DEBUG ECHO BOT...")
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))
    
    print("🤖 ECHO BOT RUNNING.")
    application.run_polling()
