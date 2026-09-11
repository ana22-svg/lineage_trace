from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class ChannelCreate(BaseModel):
    platform_channel_id: str
    display_name: str

class ChannelResponse(BaseModel):
    id: UUID
    platform_channel_id: str
    display_name: str
    is_active: bool
    added_by: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True