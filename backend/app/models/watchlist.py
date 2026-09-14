import uuid
from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, ENUM
from app.database import Base

class WatchCondition(Base):
    __tablename__ = "watch_conditions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cluster_id = Column(UUID(as_uuid=True), ForeignKey('claim_clusters.id'), nullable=True)
    condition_type = Column(
        ENUM('r_claim_breach', 'debunk_lag_exceeded', 'topology_shift', 'high_danger_edge', 'coordinated_signal', name='watch_condition_enum'),
        nullable=False
    )
    threshold_value = Column(Float, nullable=True)
    last_topology_label_external = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    condition_id = Column(UUID(as_uuid=True), ForeignKey('watch_conditions.id'), nullable=False)
    cluster_id = Column(UUID(as_uuid=True), ForeignKey('claim_clusters.id'), nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    detail_json = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
