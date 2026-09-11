from datetime import timezone
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
from app.services import embedding, clustering, lineage, mutation_diff, danger_score
from app.config import settings

async def process_message(msg: NormalizedMessage, db: AsyncSession) -> dict:
    """Persist one message and either a confirmed edge or a lineage gap."""
    existing = await db.scalar(select(RawMessage).where(RawMessage.source == msg.source, RawMessage.source_id == msg.source_id))
    if existing:
        return {"message_id": str(existing.id), "cluster_id": str(existing.cluster_id), "new_edges": 0, "duplicate": True}
    vector = embedding.embedding_service.embed(msg.text).tolist()
    clusters = list((await db.scalars(select(ClaimCluster))).all())
    assignment = clustering.assign_to_cluster(vector, clusters)
    ts = msg.timestamp if msg.timestamp.tzinfo else msg.timestamp.replace(tzinfo=timezone.utc)
    channel_id = None
    if msg.channel_id:
        channel = await db.scalar(select(MonitoredChannel).where(MonitoredChannel.platform_channel_id == msg.channel_id))
        if channel:
            channel_id = channel.id
    if assignment["is_new"]:
        cluster = ClaimCluster(centroid=vector, member_count=0, topology_label_internal="unclassified", topology_label_external="unclassified", first_seen=ts, last_seen=ts)
        db.add(cluster); await db.flush()
    else:
        cluster = await db.get(ClaimCluster, assignment["assigned_cluster_id"])
    raw = RawMessage(source=msg.source, source_id=msg.source_id, channel_id=channel_id, author_id=msg.author_id, author_account_age_days=msg.author_account_age_days, text=msg.text, language=msg.language, embedding=vector, timestamp=ts, cluster_id=cluster.id, metadata_json=msg.metadata)
    db.add(raw); await db.flush()
    cluster.member_count += 1; cluster.first_seen = min(cluster.first_seen, ts); cluster.last_seen = max(cluster.last_seen, ts)
    # Running mean keeps the centroid transactionally aligned with membership.
    old_count = cluster.member_count - 1
    cluster.centroid = [((cluster.centroid[i] * old_count) + vector[i]) / cluster.member_count for i in range(len(vector))]
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
                edge = LineageEdge(cluster_id=cluster.id, parent_message_id=parent.id, child_message_id=raw.id, similarity_score=data["similarity_score"], similarity_decay=data["similarity_decay"], is_flagged_gap=False, timestamp_delta_seconds=delta)
                db.add(edge); await db.flush()
                confirmed_edges = list((await db.scalars(select(LineageEdge).where(LineageEdge.cluster_id == cluster.id, LineageEdge.is_flagged_gap.is_(False)))).all())
                graph = nx.DiGraph((e.parent_message_id, e.child_message_id) for e in confirmed_edges)
                downstream_reach = len(nx.descendants(graph, edge.child_message_id))
                diff = await mutation_diff.compute_diff(parent.text, raw.text)
                score = danger_score.compute_danger_score(diff, downstream_reach)
                db.add(MutationDiff(edge_id=edge.id, diff_json=diff["diff_json"], danger_score=score["danger_score"], distortion_magnitude=score["distortion_magnitude"], downstream_reach=downstream_reach, llm_model=diff["llm_model"], llm_raw_response=diff["llm_raw_response"], diff_status="complete"))
    await db.commit()
    return {"message_id": str(raw.id), "cluster_id": str(cluster.id), "new_edges": int(edge is not None), "duplicate": False}
