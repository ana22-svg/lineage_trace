from datetime import timedelta
import networkx as nx

def compute_r_claim(G: nx.DiGraph, messages: dict, window_hours: float, cluster_id: str) -> list:
    all_timestamps = sorted([m.timestamp for m in messages.values()])
    if not all_timestamps:
        return []
        
    start = all_timestamps[0]
    end = all_timestamps[-1]
    window = timedelta(hours=window_hours)
    
    snapshots = []
    current = start
    
    while current + window <= end + window:
        window_start = current
        window_end = current + window

        # Denominator: ALL nodes born in this window
        window_nodes = [nid for nid, m in messages.items() if window_start <= m.timestamp < window_end]
        P_t = len(window_nodes)

        # Numerator: edges whose child was posted in this window
        new_edges = sum(1 for _, child in G.edges() if child in window_nodes)

        is_reliable = P_t >= 5 # MIN_ACTIVE_NODES
        r_claim_val = (new_edges / P_t) if is_reliable else None

        snapshots.append({
            "cluster_id": cluster_id,
            "metric_type": "r_claim",
            "window_start": window_start,
            "window_end": window_end,
            "value": round(r_claim_val, 4) if r_claim_val is not None else None,
            "active_node_count": P_t,
            "is_reliable": is_reliable
        })
        current += window

    return snapshots
