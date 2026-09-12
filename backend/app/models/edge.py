import uuid
from sqlalchemy import Column, Float, Integer, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base

class LineageEdge(Base):
    __tablename__ = "lineage_edges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cluster_id = Column(UUID(as_uuid=True), ForeignKey('claim_clusters.id'), nullable=False)
    parent_message_id = Column(UUID(as_uuid=True), ForeignKey('raw_messages.id'), nullable=False)
    child_message_id = Column(UUID(as_uuid=True), ForeignKey('raw_messages.id'), nullable=False)
    similarity_score = Column(Float, nullable=False)
    similarity_decay = Column(Float, nullable=False)
    timestamp_delta_seconds = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
