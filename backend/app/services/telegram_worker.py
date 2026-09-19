import asyncio
import logging
import sys
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters
from sqlalchemy import select
from app.config import settings
from app.database import AsyncSessionLocal
from app.models.channel import MonitoredChannel
from app.pipeline import process_message
from app.services.ingestion import process_telegram_message
from app.services.telegram_channels import channel_identifier_variants

logger = logging.getLogger(__name__)

def configured_channel_allowed(identifiers: set[str]) -> bool:
    configured = set()
    for item in settings.TELEGRAM_ALLOWED_CHANNEL_IDS.split(","):
        configured.update(channel_identifier_variants(item))
    return not configured or bool(configured & identifiers)

def channel_identifiers(message) -> set[str]:
    identifiers = channel_identifier_variants(str(message.chat.id))
    username = getattr(message.chat, "username", None)
    if username:
        identifiers.update(channel_identifier_variants(username))
    return identifiers

async def get_registered_channel(message) -> MonitoredChannel | None:
    identifiers = channel_identifiers(message)
    if not configured_channel_allowed(identifiers):
        logger.warning("telegram_channel_not_allowed_by_env", extra={"channel_identifiers": sorted(identifiers)})
        return None
    async with AsyncSessionLocal() as db:
        return await db.scalar(
            select(MonitoredChannel).where(
                MonitoredChannel.is_active.is_(True),
                MonitoredChannel.platform_channel_id.in_(identifiers),
            )
        )

async def handle_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.channel_post or update.message
    if message is None or not message.chat:
        return
    channel = await get_registered_channel(message)
    if channel is None:
        logger.warning("telegram_channel_not_registered_or_inactive", extra={"channel_identifiers": sorted(channel_identifiers(message))})
        return
    payload = {
        "message_id": message.message_id,
        "date": int(message.date.timestamp()),
        "chat": {"id": message.chat.id, "username": getattr(message.chat, "username", None), "title": getattr(message.chat, "title", None)},
        "from": {"id": message.from_user.id} if message.from_user else {},
        "text": message.text,
        "caption": message.caption,
    }
    try:
        normalized = process_telegram_message(payload, channel.platform_channel_id)
        async with AsyncSessionLocal() as db:
            result = await process_message(normalized, db)
        logger.info(
            "telegram_message_processed message_id=%s cluster_id=%s duplicate=%s new_edges=%s",
            message.message_id,
            result.get("cluster_id"),
            result.get("duplicate"),
            result.get("new_edges"),
        )
    except Exception:
        logger.exception("telegram_update_processing_failed", extra={"channel_id": channel.platform_channel_id, "message_id": message.message_id})

async def run():
    if not settings.TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required")
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.ALL, handle_update))
    await application.initialize()
    await application.start()
    await application.updater.start_polling(timeout=settings.TELEGRAM_POLL_TIMEOUT_SECONDS, drop_pending_updates=True, allowed_updates=["message", "channel_post"])
    logger.info("telegram_polling_started")
    try:
        await asyncio.Event().wait()
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    # psycopg's async driver requires a selector loop on Windows.
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run())
