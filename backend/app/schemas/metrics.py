from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime
from uuid import UUID

class RClaimSnapshot(BaseModel):
    window_start: datetime
    window_end: datetime
    value: Optional[float] = None
    active_node_count: int
    is_reliable: bool

class DebunkLagResponse(BaseModel):
    has_debunk: bool
    debunk_lag_hours: Optional[float] = None
    pre_debunk_reach: Optional[int] = None
    first_debunk_timestamp: Optional[datetime] = None
    peak_velocity_timestamp: Optional[datetime] = None
    estimation_method: Optional[Literal['peak_velocity', 'fallback_first_seen']] = None
