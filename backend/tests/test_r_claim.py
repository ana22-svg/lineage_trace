import networkx as nx
from datetime import datetime, timedelta
from types import SimpleNamespace
from app.services.r_claim import compute_r_claim

def test_r_claim_denominator_includes_zero_out_degree():
    """Asserts denominator includes zero-out-degree nodes[cite: 2]."""
    G = nx.DiGraph()
    base_time = datetime(2026, 9, 8, 10, 0, 0)
    
    messages = {}
    # Create 6 nodes all in the same 6-hour window
    for i in range(6):
        msg_time = base_time + timedelta(hours=1)
        messages[f"n{i}"] = SimpleNamespace(timestamp=msg_time, id=f"n{i}")
        G.add_node(f"n{i}")
        
    # Only n0 produces children (n1, n2). The rest are dead ends.
    G.add_edge("n0", "n1")
    G.add_edge("n0", "n2")
    
    snapshots = compute_r_claim(G, messages, window_hours=6.0, cluster_id="c1")
    
    assert len(snapshots) > 0
    snapshot = snapshots[0]
    
    # Denominator must be 6 (ALL nodes), not just the 1 node that had children
    assert snapshot["active_node_count"] == 6
    assert snapshot["is_reliable"] is True  # >= 5 nodes[cite: 2, 3]
    # Numerator is 2 (new edges pointing to children in this window)
    assert snapshot["value"] == round(2 / 6, 4)