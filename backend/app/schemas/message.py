from pydantic import BaseModel, Field
from typing import Optional, Literal, Dict, Any
from datetime import datetime

class NormalizedMessage(BaseModel):
    source: Literal["telegram", "seed"]
    source_id: str
    channel_id: str
    author_id: Optional[str] = None
    # Populated only when source == "seed". Must be None for Telegram.
    author_account_age_days: Optional[int] = None 
    text: str
    language: str
    timestamp: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)