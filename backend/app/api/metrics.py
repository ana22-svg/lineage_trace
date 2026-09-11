from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.metrics import RClaimSnapshot, DebunkLagResponse
from sqlalchemy import select
from app.models.metric import MetricSnapshot

router = APIRouter(prefix="/api/clusters", tags=["Metrics"])

@router.get("/{cluster_id}/r_claim", response_model=List[RClaimSnapshot])
async def get_r_claim(cluster_id: str, db: AsyncSession = Depends(get_db)):
    """Returns the windowed R_claim velocity metric series."""
    return list((await db.scalars(select(MetricSnapshot).where(MetricSnapshot.cluster_id == cluster_id, MetricSnapshot.metric_type == "r_claim").order_by(MetricSnapshot.window_start))).all())

@router.get("/{cluster_id}/debunk-lag", response_model=DebunkLagResponse)
async def get_debunk_lag(cluster_id: str, db: AsyncSession = Depends(get_db)):
    """Returns debunk-lag, explicitly surfacing the estimation method used[cite: 2]."""
    snapshot = await db.scalar(select(MetricSnapshot).where(MetricSnapshot.cluster_id == cluster_id, MetricSnapshot.metric_type == "debunk_lag").order_by(MetricSnapshot.created_at.desc()))
    if snapshot is None:
        return {"has_debunk": False, "debunk_lag_hours": None, "pre_debunk_reach": None, "first_debunk_timestamp": None, "peak_velocity_timestamp": None, "estimation_method": None}
    return {"has_debunk": True, "debunk_lag_hours": snapshot.value, "pre_debunk_reach": (snapshot.metadata_json or {}).get("pre_debunk_reach"), "first_debunk_timestamp": (snapshot.metadata_json or {}).get("first_debunk_timestamp"), "peak_velocity_timestamp": (snapshot.metadata_json or {}).get("peak_velocity_timestamp"), "estimation_method": snapshot.estimation_method}
