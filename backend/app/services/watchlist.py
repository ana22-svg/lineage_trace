import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.watchlist import WatchCondition, Alert
from app.models.cluster import ClaimCluster
from app.models.metric import MetricSnapshot
from app.models.diff import MutationDiff
from app.models.edge import LineageEdge

logger = logging.getLogger(__name__)

async def scan_watch_conditions(db: AsyncSession):
    conditions = list((await db.scalars(select(WatchCondition).where(WatchCondition.is_active.is_(True)))).all())
    for condition in conditions:
        if condition.cluster_id is None: continue
        cluster = await db.get(ClaimCluster, condition.cluster_id)
        if not cluster: continue
        triggered = False; detail = {"condition_type": condition.condition_type}
        if condition.condition_type == "topology_shift":
            triggered = condition.last_topology_label_external not in (None, cluster.topology_label_external)
            detail.update(old=condition.last_topology_label_external, new=cluster.topology_label_external)
            condition.last_topology_label_external = cluster.topology_label_external
        elif condition.condition_type == "r_claim_breach":
            latest = await db.scalar(select(MetricSnapshot).where(MetricSnapshot.cluster_id == cluster.id, MetricSnapshot.metric_type == "r_claim", MetricSnapshot.is_reliable.is_(True)).order_by(MetricSnapshot.window_end.desc()))
            triggered = bool(latest and condition.threshold_value is not None and latest.value is not None and latest.value >= condition.threshold_value)
            if latest: detail.update(value=latest.value, threshold=condition.threshold_value)
        elif condition.condition_type == "debunk_lag_exceeded":
            latest = await db.scalar(select(MetricSnapshot).where(MetricSnapshot.cluster_id == cluster.id, MetricSnapshot.metric_type == "debunk_lag").order_by(MetricSnapshot.created_at.desc()))
            triggered = bool(latest and condition.threshold_value is not None and latest.value is not None and latest.value >= condition.threshold_value)
            if latest: detail.update(value=latest.value, threshold=condition.threshold_value)
        elif condition.condition_type == "high_danger_edge":
            latest = await db.scalar(select(MutationDiff).join(LineageEdge, MutationDiff.edge_id == LineageEdge.id).where(LineageEdge.cluster_id == cluster.id, MutationDiff.danger_score >= condition.threshold_value).order_by(MutationDiff.created_at.desc()))
            triggered = latest is not None
            if latest: detail.update(edge_id=str(latest.edge_id), danger_score=latest.danger_score, threshold=condition.threshold_value)
        if triggered:
            recent = await db.scalar(select(Alert).where(Alert.condition_id == condition.id, Alert.cluster_id == cluster.id).order_by(Alert.created_at.desc()))
            if not recent or recent.detail_json != detail:
                db.add(Alert(condition_id=condition.id, cluster_id=cluster.id, detail_json=detail))
                logger.info("watchlist_alert_created", extra={"condition_id": str(condition.id), "cluster_id": str(cluster.id)})
    await db.commit()
