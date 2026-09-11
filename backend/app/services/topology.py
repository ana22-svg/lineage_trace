import networkx as nx
import statistics
from types import SimpleNamespace
from app.config import settings
from app.services.burstiness import compute_arrival_burstiness

def classify_topology_internal(G: nx.DiGraph) -> str:
    """Graph-theoretic label. Uses out-degree and arrival burstiness, NOT clustering coefficient."""
    if G.number_of_nodes() < 3:
        return "unclassified"

    out_degrees = [d for _, d in G.out_degree()]
    max_out = max(out_degrees) if out_degrees else 0
    total_edges = G.number_of_edges()

    if total_edges > 0 and max_out > 0.5 * total_edges:
        return "hub_spoke"

    node_timestamps = [G.nodes[n].get("timestamp") for n in G.nodes() if "timestamp" in G.nodes[n]]
    burst_result = compute_arrival_burstiness(
        [SimpleNamespace(timestamp=t) for t in node_timestamps],
        inter_arrival_threshold_sec=settings.BURSTINESS_INTER_ARRIVAL_THRESHOLD_SECONDS,
        min_count=5
    )
    
    if burst_result.get("flagged"):
        return "burst"

    degree_cv = statistics.stdev(out_degrees) / max(statistics.mean(out_degrees), 0.01) if len(out_degrees) > 1 else 0
    if degree_cv < 1.0:
        return "mesh"

    return "unclassified"

def map_to_external_label(internal_label: str, coordination_signal_density: float) -> str:
    """Maps to pitch-deck vocabulary based on internal shape and coordination density."""
    if internal_label == "unclassified":
        return "unclassified"
    if internal_label == "burst" and coordination_signal_density > 0.5:
        return "bot_amplified"
    if coordination_signal_density > 0.3:
        return "coordinated"
    return "organic"