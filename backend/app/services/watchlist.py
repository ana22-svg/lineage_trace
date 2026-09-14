import logging
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.watchlist import WatchCondition, Alert
from app.models.cluster import ClaimCluster
from app.models.metric import MetricSnapshot
from app.models.diff import MutationDiff
from app.models.edge import LineageEdge
from app.models.coordination import CoordinationSignal

logger = logging.getLogger(__name__)

async def scan_watch_conditions(db: AsyncSession):
    # Backfill the default topology watch for clusters created before the
    # automatic watchlist behavior was added.
    clusters = list((await db.scalars(select(ClaimCluster))).all())
    existing_topology_ids = set((await db.scalars(select(WatchCondition.cluster_id).where(WatchCondition.condition_type == "topology_shift", WatchCondition.cluster_id.is_not(None)))).all())
    existing_coordination_ids = set((await db.scalars(select(WatchCondition.cluster_id).where(WatchCondition.condition_type == "coordinated_signal", WatchCondition.cluster_id.is_not(None)))).all())
    for cluster in clusters:
        if cluster.id not in existing_topology_ids:
            db.add(WatchCondition(
                cluster_id=cluster.id,
                condition_type="topology_shift",
                last_topology_label_external="unclassified",
                is_active=True,
                created_at=datetime.now(timezone.utc),
            ))
        if cluster.id not in existing_coordination_ids:
            db.add(WatchCondition(
                cluster_id=cluster.id,
                condition_type="coordinated_signal",
                is_active=True,
                created_at=datetime.now(timezone.utc),
            ))
    await db.flush()
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
        elif condition.condition_type == "coordinated_signal":
            latest = await db.scalar(select(CoordinationSignal).join(LineageEdge, CoordinationSignal.edge_id == LineageEdge.id).where(LineageEdge.cluster_id == cluster.id, CoordinationSignal.is_coordinated.is_(True)).order_by(CoordinationSignal.created_at.desc()))
            triggered = latest is not None
            if latest:
                detail.update(signal_id=str(latest.id), edge_id=str(latest.edge_id), signal_type=latest.signal_type, evidence=latest.detail_json)
        if triggered:
            recent = await db.scalar(select(Alert).where(Alert.condition_id == condition.id, Alert.cluster_id == cluster.id).order_by(Alert.created_at.desc()))
            if not recent or recent.detail_json != detail:
                db.add(Alert(
                    condition_id=condition.id,
                    cluster_id=cluster.id,
                    detail_json=detail,
                    created_at=datetime.now(timezone.utc),
                ))
                logger.info("watchlist_alert_created", extra={"condition_id": str(condition.id), "cluster_id": str(cluster.id)})
    await db.commit()
