from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from pathlib import Path
import json
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db, AsyncSessionLocal
from app.schemas.message import NormalizedMessage
from app.services.ingestion import process_telegram_message
from app.pipeline import process_message

router = APIRouter(prefix="/api/ingest", tags=["Ingestion"])

@router.post("/")
async def ingest_telegram_live(payload: dict, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    """Live endpoint for Telegram Bot API webhooks."""
    # channel_id would be resolved from payload context
    chat = payload.get("chat") or (payload.get("channel") or {})
    resolved_channel_id = str(chat.get("id") or payload.get("channel_id") or "")
    normalized_msg = process_telegram_message(payload, channel_id=resolved_channel_id)
    
    # Pass to the pipeline asynchronously to free up the webhook response
    async def run_pipeline():
        async with AsyncSessionLocal() as session:
            await process_message(normalized_msg, session)
    background_tasks.add_task(run_pipeline)
    return {"status": "accepted"}

@router.post("/seed")
async def ingest_seed_data(messages: list[NormalizedMessage], db: AsyncSession = Depends(get_db)):
    """Retrospective endpoint for the curated seed dataset."""
    results = []
    for msg in messages:
        res = await process_message(msg, db)
        results.append(res)
    return {"processed": len(results)}

@router.post("/seed/{case_id}")
async def ingest_seed_case(case_id: str, db: AsyncSession = Depends(get_db)):
    path = Path(__file__).resolve().parents[2] / "seed_data" / case_id / "messages.json"
    if not path.exists():
        raise HTTPException(404, "Seed case not found")
    try:
        raw_messages = json.loads(path.read_text(encoding="utf-8"))
        messages = [NormalizedMessage.model_validate(m) for m in raw_messages]
        results = [await process_message(message, db) for message in messages]
        return {"case_id": case_id, "processed": len(results), "results": results}
    except Exception as exc:
        await db.rollback()
        raise HTTPException(422, f"Seed case could not be processed: {exc}") from exc
