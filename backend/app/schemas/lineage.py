from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from app.schemas.cluster import TopologyLabels

class DebunkLagSummary(BaseModel):
    has_debunk: bool
    debunk_lag_hours: Optional[float] = None
    estimation_method: Optional[str] = None # e.g., 'peak_velocity' or 'fallback_first_seen'

class LineageGraphResponse(BaseModel):
    cluster_id: UUID
    topology: TopologyLabels
    node_count: int
    edge_count: int
    nodes: List[dict] # Simplified for brevity; would contain message details
    edges: List[dict] # Contains similarity, decay, and boolean flagged_gap
    r_claim_series: List[dict]
    debunk_lag: DebunkLagSummary