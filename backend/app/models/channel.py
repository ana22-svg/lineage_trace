import uuid
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base

class MonitoredChannel(Base):
    __tablename__ = "monitored_channels"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform_channel_id = Column(String, nullable=False, unique=True)
    display_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    added_by = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False)