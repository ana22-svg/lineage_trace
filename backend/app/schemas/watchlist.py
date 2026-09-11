from pydantic import BaseModel
from typing import Optional, Literal, Dict, Any
from uuid import UUID

class WatchConditionCreate(BaseModel):
    cluster_id: Optional[UUID] = None
    condition_type: Literal['r_claim_breach', 'debunk_lag_exceeded', 'topology_shift', 'high_danger_edge']
    threshold_value: Optional[float] = None

class AlertResponse(BaseModel):
    id: UUID
    condition_id: UUID
    cluster_id: UUID
    is_read: bool
    detail_json: Dict[str, Any]

    class Config:
        from_attributes = True