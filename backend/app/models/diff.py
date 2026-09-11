import uuid
from sqlalchemy import Column, Float, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base

class MutationDiff(Base):
    __tablename__ = "mutation_diffs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # UNIQUE constraint enforces one diff per edge
    edge_id = Column(UUID(as_uuid=True), ForeignKey('lineage_edges.id'), unique=True, nullable=False)
    diff_json = Column(JSONB, nullable=False, default=dict)
    danger_score = Column(Float, nullable=True)
    distortion_magnitude = Column(Float, nullable=False)
    downstream_reach = Column(Integer, nullable=False, default=0)
    llm_model = Column(String, nullable=False)
    llm_raw_response = Column(String, nullable=False)
    diff_status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
