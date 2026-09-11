import pytest
from types import SimpleNamespace
from app.services.lineage import construct_edges
from app.config import settings

def test_construct_edges_flags_gap_when_decay_high():
    """Rule enforced: Never force a lineage edge[cite: 1, 2]."""
    current = SimpleNamespace(id="child1", embedding=[1.0, 0.0])
    # Parent is highly dissimilar to child, simulating a large mutation or missed link
    parent = SimpleNamespace(id="parent1", embedding=[0.0, 1.0])
    
    result = construct_edges(current, [parent])
    
    assert result is not None
    assert result["parent_id"] == "parent1"
    assert result["child_id"] == "child1"
    # Decay will be 1.0 (1 - 0.0 similarity), which is > EDGE_DECAY_THRESHOLD
    assert result["similarity_decay"] > settings.EDGE_DECAY_THRESHOLD
    assert result["is_flagged_gap"] is True