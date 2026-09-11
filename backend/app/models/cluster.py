import uuid
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID, ENUM
from pgvector.sqlalchemy import Vector
from app.database import Base

class ClaimCluster(Base):
    __tablename__ = "claim_clusters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    centroid = Column(Vector(768), nullable=False)
    member_count = Column(Integer, default=1)
    topology_label_internal = Column(
        ENUM('hub_spoke', 'mesh', 'burst', 'unclassified', name='internal_topology_enum'),
        nullable=False
    )
    topology_label_external = Column(
        ENUM('organic', 'coordinated', 'bot_amplified', 'unclassified', name='external_topology_enum'),
        nullable=False
    )
    first_seen = Column(DateTime(timezone=True), nullable=False)
    last_seen = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)