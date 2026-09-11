from pydantic import BaseModel
from typing import List
from uuid import UUID

class DiffChange(BaseModel):
    field: str
    old: str
    new: str
    category: str

class MutationDiffResponse(BaseModel):
    edge_id: UUID
    changes: List[DiffChange]
    danger_score: float
    distortion_magnitude: float
    downstream_reach: int