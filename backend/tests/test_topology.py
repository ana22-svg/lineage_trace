import networkx as nx
from datetime import datetime, timedelta
from app.services.topology import classify_topology_internal, map_to_external_label

def test_topology_burst_on_tree():
    """Asserts 'burst' CAN fire on a tree graph via arrival burstiness."""
    G = nx.DiGraph()
    base_time = datetime(2026, 9, 8, 10, 0, 0)
    
    # Create a simple line tree: 1 -> 2 -> 3 -> 4 -> 5 -> 6 (no triangles)
    for i in range(6):
        # Timestamps are just 5 seconds apart (highly bursty)
        G.add_node(i, timestamp=base_time + timedelta(seconds=i*5))
        if i > 0:
            G.add_edge(i-1, i)
            
    internal_label = classify_topology_internal(G)
    assert internal_label == "burst"

def test_topology_label_mapping():
    """Asserts internal->external label mapping uses pitch-vocabulary."""
    # High coordination density on a burst -> bot_amplified
    assert map_to_external_label("burst", coordination_signal_density=0.6) == "bot_amplified"
    
    # Moderate coordination on a mesh -> coordinated
    assert map_to_external_label("mesh", coordination_signal_density=0.4) == "coordinated"
    
    # Low coordination on a hub_spoke -> organic
    assert map_to_external_label("hub_spoke", coordination_signal_density=0.1) == "organic"