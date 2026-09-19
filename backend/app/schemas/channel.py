from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.services.telegram_channels import normalize_channel_identifier

class ChannelCreate(BaseModel):
    platform_channel_id: str
    display_name: str

    @field_validator("platform_channel_id")
    @classmethod
    def normalize_platform_channel_id(cls, value: str) -> str:
        return normalize_channel_identifier(value)

class ChannelResponse(BaseModel):
    id: UUID
    platform_channel_id: str
    display_name: str
    is_active: bool
    added_by: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
