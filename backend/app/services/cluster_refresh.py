import networkx as nx
from datetime import datetime, timezone
from sqlalchemy import select, delete
from app.models.message import RawMessage
from app.models.edge import LineageEdge
from app.models.metric import MetricSnapshot
from app.models.cluster import ClaimCluster
from app.services.r_claim import compute_r_claim
from app.services.debunk_lag import compute_debunk_lag
from app.services.topology import classify_topology_internal, map_to_external_label
from types import SimpleNamespace

async def refresh_cluster(db, cluster):
    messages = list((await db.scalars(select(RawMessage).where(RawMessage.cluster_id == cluster.id))).all())
    edges = list((await db.scalars(select(LineageEdge).where(LineageEdge.cluster_id == cluster.id))).all())
    graph = nx.DiGraph()
    graph.add_nodes_from((m.id, {"timestamp": m.timestamp, "metadata": m.metadata_json}) for m in messages)
    graph.add_edges_from((e.parent_message_id, e.child_message_id) for e in edges)
    internal = classify_topology_internal(graph)
    cluster.topology_label_internal = internal
    cluster.topology_label_external = map_to_external_label(internal, 0.0)
    message_map = {m.id: SimpleNamespace(timestamp=m.timestamp, metadata=m.metadata_json) for m in messages}
    snapshots = compute_r_claim(graph, message_map, 6.0, str(cluster.id))
    await db.execute(delete(MetricSnapshot).where(MetricSnapshot.cluster_id == cluster.id, MetricSnapshot.metric_type == "r_claim"))
    for item in snapshots:
        db.add(MetricSnapshot(**{k: item[k] for k in ("cluster_id", "metric_type", "window_start", "window_end", "value", "active_node_count", "is_reliable")}, created_at=datetime.now(timezone.utc)))
    lag = compute_debunk_lag(graph, message_map, snapshots)
    if lag["has_debunk"]:
        db.add(MetricSnapshot(cluster_id=cluster.id, metric_type="debunk_lag", value=lag["debunk_lag_hours"], is_reliable=True, estimation_method=lag["estimation_method"], metadata_json=lag, created_at=datetime.now(timezone.utc)))
