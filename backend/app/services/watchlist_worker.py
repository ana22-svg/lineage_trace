import asyncio
import logging
import signal
from app.database import AsyncSessionLocal, check_database
from app.services.watchlist import scan_watch_conditions

async def main():
    await check_database()
    from app.config import settings
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop.set)
    delay = 1
    while not stop.is_set():
        try:
            async with AsyncSessionLocal() as db:
                await scan_watch_conditions(db)
            delay = 1
        except Exception:
            logging.getLogger(__name__).exception("watchlist_scan_failed")
            await asyncio.sleep(min(delay, 60))
            delay *= 2
            continue
        try:
            await asyncio.wait_for(stop.wait(), timeout=settings.WATCHLIST_SCAN_INTERVAL_SECONDS)
        except asyncio.TimeoutError:
            pass
    logging.getLogger(__name__).info("watchlist_worker_stopped")

if __name__ == "__main__":
    asyncio.run(main())
