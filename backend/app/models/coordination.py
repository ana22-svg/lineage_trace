import uuid
from sqlalchemy import Column, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, ENUM
from app.database import Base

class CoordinationSignal(Base):
    __tablename__ = "coordination_signals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    edge_id = Column(UUID(as_uuid=True), ForeignKey('lineage_edges.id'), nullable=False)
    signal_type = Column(
        ENUM('account_age_cluster', 'timestamp_burst', 'combined', name='coordination_signal_enum'),
        nullable=False
    )
    account_age_stats = Column(JSONB, nullable=True) # Nullable for Telegram sources
    burst_score = Column(Float, nullable=True)
    is_coordinated = Column(Boolean, nullable=False)
    detail_json = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)