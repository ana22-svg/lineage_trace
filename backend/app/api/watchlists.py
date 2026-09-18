from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.watchlist import WatchConditionCreate, AlertResponse
from app import crud

router = APIRouter(prefix="/api/watchlists", tags=["Watchlists"])

@router.post("/")
async def create_watch_condition(payload: WatchConditionCreate, db: AsyncSession = Depends(get_db)):
    """Creates a new condition (e.g., r_claim_breach, topology_shift)."""
    return await crud.create_watch_condition(db, payload.model_dump())

@router.get("/alerts")
async def get_active_alerts(page: int = 1, page_size: int = 50, db: AsyncSession = Depends(get_db)):
    """Retrieves alerts triggered by the background worker."""
    page_size = min(max(page_size, 1), 100)
    return await crud.list_alerts(db, (max(page, 1)-1)*page_size, page_size)

@router.patch("/{alert_id}/read")
@router.patch("/alerts/{alert_id}/read")
async def mark_alert_read(alert_id: str, db: AsyncSession = Depends(get_db)):
    """Marks a specific alert as read."""
    from app.models.watchlist import Alert
    import uuid
    try:
        u = uuid.UUID(alert_id)
        alert = await db.get(Alert, u)
    except Exception:
        alert = await db.get(Alert, alert_id)
    if not alert:
        from fastapi import HTTPException
        raise HTTPException(404, "Alert not found")
    alert.is_read = True
    await db.commit()
    await db.refresh(alert)
    return {"id": str(alert.id), "is_read": alert.is_read}

