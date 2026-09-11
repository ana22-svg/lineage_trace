from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.channel import ChannelCreate, ChannelResponse
from app import crud

router = APIRouter(prefix="/api/channels", tags=["Channels"])

@router.post("/", response_model=ChannelResponse)
async def register_channel(payload: ChannelCreate, db: AsyncSession = Depends(get_db)):
    """Registers a new Telegram channel to monitor."""
    # return await crud_channels.create(db, platform_channel_id, display_name)
    return await crud.create_channel(db, payload.platform_channel_id, payload.display_name)

@router.get("/")
async def list_channels(db: AsyncSession = Depends(get_db)):
    """Lists all monitored channels."""
    # return await crud_channels.get_all(db)
    return await crud.list_channels(db)

@router.patch("/{channel_id}")
async def toggle_channel(channel_id: str, is_active: bool, db: AsyncSession = Depends(get_db)):
    """Toggles is_active without redeploy."""
    # return await crud_channels.update_status(db, channel_id, is_active)
    return await crud.set_channel_active(db, channel_id, is_active)
