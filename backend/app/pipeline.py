from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import networkx as nx
from app.schemas.message import NormalizedMessage
from app.models.message import RawMessage
from app.models.cluster import ClaimCluster
from app.models.edge import LineageEdge
from app.models.diff import MutationDiff
from app.models.lineage_gap import LineageGap
from app.models.channel import MonitoredChannel
from app.models.coordination import CoordinationSignal
from app.models.watchlist import WatchCondition
from app.services import embedding, clustering, lineage, mutation_diff, danger_score, coordination
from app.config import settings
from app.services.watchlist import scan_watch_conditions
from app.services.cluster_refresh import refresh_cluster

async def process_message(msg: NormalizedMessage, db: AsyncSession) -> dict:
    """Persist one message and either a confirmed edge or a lineage gap."""
    existing = await db.scalar(select(RawMessage).where(RawMessage.source == msg.source, RawMessage.source_id == msg.source_id))
    if existing:
        return {"message_id": str(existing.id), "cluster_id": str(existing.cluster_id), "new_edges": 0, "duplicate": True}
    vector = embedding.embedding_service.embed(msg.text).tolist()
    if len(vector) != 768:
        raise ValueError(f"Embedding dimension error: expected 768 dimensions, got {len(vector)}")
    clusters = list((await db.scalars(select(ClaimCluster))).all())
    assignment = clustering.assign_to_cluster(vector, clusters)
    ts = msg.timestamp if msg.timestamp.tzinfo else msg.timestamp.replace(tzinfo=timezone.utc)
    channel_id = None
    if msg.channel_id:
        channel = await db.scalar(select(MonitoredChannel).where(MonitoredChannel.platform_channel_id == msg.channel_id))
        if channel:
            channel_id = channel.id
        elif msg.source == "telegram":
            raise ValueError(f"Telegram channel '{msg.channel_id}' is not registered")
    if assignment["is_new"]:
        cluster = ClaimCluster(centroid=vector, member_count=0, topology_label_internal="unclassified", topology_label_external="unclassified", first_seen=ts, last_seen=ts, created_at=datetime.now(timezone.utc))
        db.add(cluster); await db.flush()
        # Every new cluster is watched for a topology change so the Alerts
        # view works without requiring a separate manual setup step.
        db.add(WatchCondition(
            cluster_id=cluster.id,
            condition_type="topology_shift",
            last_topology_label_external="unclassified",
            is_active=True,
            created_at=datetime.now(timezone.utc),
        ))
    else:
        cluster = (await db.execute(select(ClaimCluster).where(ClaimCluster.id == assignment["assigned_cluster_id"]).with_for_update())).scalar_one()
    raw = RawMessage(source=msg.source, source_id=msg.source_id, channel_id=channel_id, author_id=msg.author_id, author_account_age_days=msg.author_account_age_days, text=msg.text, language=msg.language, embedding=vector, timestamp=ts, cluster_id=cluster.id, metadata_json=msg.metadata, created_at=datetime.now(timezone.utc))
    db.add(raw); await db.flush()
    cluster.member_count += 1; cluster.first_seen = min(cluster.first_seen, ts); cluster.last_seen = max(cluster.last_seen, ts)
    # Running mean keeps the centroid transactionally aligned with membership.
    old_count = cluster.member_count - 1
    if len(cluster.centroid) != len(vector):
        raise ValueError("Embedding dimension does not match cluster centroid")
    # Compute running mean and re-normalize centroid to unit vector:
    new_centroid = np.array([((cluster.centroid[i] * old_count) + vector[i]) / cluster.member_count for i in range(len(vector))], dtype=np.float32)
    norm = np.linalg.norm(new_centroid)
    cluster.centroid = (new_centroid / norm if norm > 0 else new_centroid).tolist()
    parents = list((await db.scalars(select(RawMessage).where(RawMessage.cluster_id == cluster.id, RawMessage.timestamp < ts))).all())
    edge = None
    if parents:
        data = lineage.construct_edges(raw, parents)
        if data:
            parent = next(p for p in parents if p.id == data["parent_id"])
            delta = int((ts-parent.timestamp).total_seconds())
            if data["is_flagged_gap"]:
                db.add(LineageGap(cluster_id=cluster.id, candidate_parent_message_id=parent.id, child_message_id=raw.id, similarity_score=data["similarity_score"], similarity_decay=data["similarity_decay"], timestamp_delta_seconds=delta, detail_json={"reason": "similarity_decay_exceeded", "threshold": settings.EDGE_DECAY_THRESHOLD}))
            else:
                edge = LineageEdge(cluster_id=cluster.id, parent_message_id=parent.id, child_message_id=raw.id, similarity_score=data["similarity_score"], similarity_decay=data["similarity_decay"], timestamp_delta_seconds=delta)
                db.add(edge); await db.flush()
                confirmed_edges = list((await db.scalars(select(LineageEdge).where(LineageEdge.cluster_id == cluster.id))).all())
                graph = nx.DiGraph((e.parent_message_id, e.child_message_id) for e in confirmed_edges)
                downstream_reach = len(nx.descendants(graph, edge.child_message_id))
                diff = await mutation_diff.compute_diff(parent.text, raw.text)
                score = danger_score.compute_danger_score(diff, downstream_reach)
                db.add(MutationDiff(edge_id=edge.id, diff_json=diff["diff_json"], danger_score=score["danger_score"], distortion_magnitude=score["distortion_magnitude"], downstream_reach=downstream_reach, llm_model=diff["llm_model"], llm_raw_response=diff["llm_raw_response"], diff_status="complete"))
                signals = coordination.compute_signals(raw, parents)
                db.add(CoordinationSignal(
                    edge_id=edge.id,
                    signal_type="combined",
                    account_age_stats=signals["account_age_stats"],
                    burst_score=signals["burst_score"],
                    is_coordinated=signals["is_coordinated"],
                    detail_json=signals["detail_json"],
                    created_at=datetime.now(timezone.utc),
                ))
    if edge:
        all_edges = list((await db.scalars(select(LineageEdge).where(LineageEdge.cluster_id == cluster.id))).all())
        graph = nx.DiGraph((e.parent_message_id, e.child_message_id) for e in all_edges)
        diffs = list((await db.scalars(select(MutationDiff).join(LineageEdge, MutationDiff.edge_id == LineageEdge.id).where(LineageEdge.cluster_id == cluster.id))).all())
        for stored in diffs:
            edge_obj = next((e for e in all_edges if e.id == stored.edge_id), None)
            if edge_obj:
                stored.downstream_reach = len(nx.descendants(graph, edge_obj.child_message_id))
                stored.danger_score = danger_score.compute_danger_score({"diff_json": stored.diff_json}, stored.downstream_reach)["danger_score"]
    await db.commit()
    await refresh_cluster(db, cluster)
    await db.commit()
    await scan_watch_conditions(db)
    return {"message_id": str(raw.id), "cluster_id": str(cluster.id), "new_edges": int(edge is not None), "duplicate": False}
