from pydantic import BaseModel
from typing import Literal
from datetime import datetime
from uuid import UUID

class TopologyLabels(BaseModel):
    internal: Literal['hub_spoke', 'mesh', 'burst', 'unclassified']
    external: Literal['organic', 'coordinated', 'bot_amplified', 'unclassified']

class ClusterResponse(BaseModel):
    id: UUID
    member_count: int
    topology: TopologyLabels
    first_seen: datetime
    last_seen: datetime

    class Config:
        from_attributes = True