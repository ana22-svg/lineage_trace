import uuid
from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, ENUM
from pgvector.sqlalchemy import Vector
from app.database import Base

class RawMessage(Base):
    __tablename__ = "raw_messages"
    __table_args__ = (UniqueConstraint("source", "source_id", name="uq_raw_messages_source_source_id"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(ENUM('telegram', 'seed', name='source_enum'), nullable=False)
    source_id = Column(String, nullable=False)
    channel_id = Column(UUID(as_uuid=True), ForeignKey('monitored_channels.id'), nullable=True)
    author_id = Column(String, nullable=True)
    author_account_age_days = Column(Integer, nullable=True)
    text = Column(String, nullable=False)
    language = Column(String(10), nullable=False)
    embedding = Column(Vector(768), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    cluster_id = Column(UUID(as_uuid=True), ForeignKey('claim_clusters.id'), nullable=True)
    metadata_json = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), nullable=False)
