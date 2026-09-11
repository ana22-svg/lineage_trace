import networkx as nx

def compute_debunk_lag(G: nx.DiGraph, messages: dict, r_claim_snapshots: list) -> dict:
    debunker_nodes = [nid for nid, m in messages.items() if (getattr(m, "metadata", None) or getattr(m, "metadata_json", {}) or {}).get("role") == "debunker"]

    if not debunker_nodes:
        return {
            "has_debunk": False, 
            "debunk_lag_hours": None,
            "pre_debunk_reach": None, 
            "estimation_method": None
        }

    first_debunk = min(messages[nid].timestamp for nid in debunker_nodes)
    reliable_snapshots = [s for s in r_claim_snapshots if s.get("is_reliable")]
    
    if reliable_snapshots:
        peak = max(reliable_snapshots, key=lambda s: s.get("value", 0))
        peak_time = peak["window_start"]
        estimation_method = "peak_velocity"
    else:
        # Fallback explicitly flagged, never silent
        peak_time = min(m.timestamp for m in messages.values())
        estimation_method = "fallback_first_seen"

    lag_hours = (first_debunk - peak_time).total_seconds() / 3600
    pre_debunk_nodes = sum(1 for nid, m in messages.items() if m.timestamp < first_debunk and len(nx.descendants(G, nid)) >= 0)
    # Reach is the accumulated confirmed descendants of pre-debunk nodes.
    pre_debunk_reach = len({d for nid, m in messages.items() if m.timestamp < first_debunk for d in nx.descendants(G, nid)})

    return {
        "has_debunk": True,
        "debunk_lag_hours": round(lag_hours, 2),
        "pre_debunk_reach": pre_debunk_reach,
        "first_debunk_timestamp": first_debunk.isoformat(),
        "peak_velocity_timestamp": peak_time.isoformat(),
        "estimation_method": estimation_method
    }
