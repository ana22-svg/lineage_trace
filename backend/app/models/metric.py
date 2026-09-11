import uuid
from sqlalchemy import Column, Float, Integer, Boolean, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, ENUM
from app.database import Base

class MetricSnapshot(Base):
    __tablename__ = "metric_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cluster_id = Column(UUID(as_uuid=True), ForeignKey('claim_clusters.id'), nullable=False)
    metric_type = Column(
        ENUM('r_claim', 'debunk_lag', name='metric_type_enum'),
        nullable=False
    )
    window_start = Column(DateTime(timezone=True), nullable=True)
    window_end = Column(DateTime(timezone=True), nullable=True)
    value = Column(Float, nullable=True)
    active_node_count = Column(Integer, nullable=True) # Denominator: all nodes born in window
    is_reliable = Column(Boolean, nullable=False, default=True)
    estimation_method = Column(String, nullable=True) # e.g., 'peak_velocity' or 'fallback_first_seen'
    metadata_json = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), nullable=False)