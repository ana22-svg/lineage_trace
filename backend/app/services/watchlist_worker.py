import asyncio
from app.database import AsyncSessionLocal, check_database
from app.services.watchlist import scan_watch_conditions

async def main():
    await check_database()
    from app.config import settings
    while True:
        async with AsyncSessionLocal() as db:
            await scan_watch_conditions(db)
        await asyncio.sleep(settings.WATCHLIST_SCAN_INTERVAL_SECONDS)

if __name__ == "__main__":
    asyncio.run(main())
