import asyncio
import logging
import sys
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters
from app.config import settings
from app.database import AsyncSessionLocal
from app.pipeline import process_message
from app.services.ingestion import process_telegram_message

logger = logging.getLogger(__name__)

def allowed_channel(channel_id: str) -> bool:
    configured = {x.strip() for x in settings.TELEGRAM_ALLOWED_CHANNEL_IDS.split(",") if x.strip()}
    return not configured or channel_id in configured

async def handle_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.channel_post or update.message
    if message is None or not message.chat:
        return
    channel_id = str(message.chat.id)
    if not allowed_channel(channel_id):
        logger.warning("telegram_channel_not_allowed", extra={"channel_id": channel_id})
        return
    payload = {
        "message_id": message.message_id,
        "date": int(message.date.timestamp()),
        "chat": {"id": message.chat.id},
        "from": {"id": message.from_user.id} if message.from_user else {},
        "text": message.text,
        "caption": message.caption,
    }
    try:
        normalized = process_telegram_message(payload, channel_id)
        async with AsyncSessionLocal() as db:
            await process_message(normalized, db)
    except Exception:
        logger.exception("telegram_update_processing_failed", extra={"channel_id": channel_id, "message_id": message.message_id})

async def run():
    if not settings.TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required")
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.ALL, handle_update))
    await application.initialize()
    await application.start()
    await application.updater.start_polling(timeout=settings.TELEGRAM_POLL_TIMEOUT_SECONDS, drop_pending_updates=False, allowed_updates=["message", "channel_post"])
    logger.info("telegram_polling_started")
    try:
        await asyncio.Event().wait()
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()

if __name__ == "__main__":
    # psycopg's async driver requires a selector loop on Windows.
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run())
