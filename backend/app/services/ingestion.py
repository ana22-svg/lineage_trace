from app.schemas.message import NormalizedMessage
from datetime import datetime, timezone
try:
    from langdetect import detect
except ImportError:
    detect = None

def process_telegram_message(raw_telegram_data: dict, channel_id: str) -> NormalizedMessage:
    """
    Normalizes a live Telegram Bot API message.
    author_account_age_days is structurally unavailable and must be None.
    """
    text = raw_telegram_data.get("text") or raw_telegram_data.get("caption") or ""
    language = "unknown"
    if detect and text:
        try: language = detect(text)
        except Exception: pass
    return NormalizedMessage(
        source="telegram",
        source_id=str(raw_telegram_data.get("message_id")),
        channel_id=channel_id,
        author_id=str(raw_telegram_data.get("from", {}).get("id")),
        author_account_age_days=None, # Guarded: API does not provide this
        text=text,
        language=language,
        timestamp=datetime.fromtimestamp(raw_telegram_data.get("date"), tz=timezone.utc),
        metadata=raw_telegram_data
    )
