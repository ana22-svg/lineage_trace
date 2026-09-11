import networkx as nx
from datetime import datetime, timedelta
from types import SimpleNamespace
from app.services.debunk_lag import compute_debunk_lag

def test_debunk_lag_peak_velocity_method():
    """Asserts estimation_method is 'peak_velocity' when reliable snapshots exist[cite: 2]."""
    G = nx.DiGraph()
    base_time = datetime(2026, 9, 8, 10, 0, 0)
    
    messages = {
        "n1": SimpleNamespace(timestamp=base_time, metadata={}),
        "debunker": SimpleNamespace(
            timestamp=base_time + timedelta(hours=5), 
            metadata={"role": "debunker"}
        )
    }
    
    mock_snapshots = [
        {"window_start": base_time + timedelta(hours=1), "value": 2.5, "is_reliable": True}
    ]
    
    result = compute_debunk_lag(G, messages, mock_snapshots)
    
    assert result["has_debunk"] is True
    assert result["estimation_method"] == "peak_velocity"
    assert result["debunk_lag_hours"] == 4.0  # 5 hours - 1 hour

def test_debunk_lag_fallback_method():
    """Asserts estimation_method is 'fallback_first_seen' when data is unreliable[cite: 2]."""
    G = nx.DiGraph()
    base_time = datetime(2026, 9, 8, 10, 0, 0)
    
    messages = {
        "n1": SimpleNamespace(timestamp=base_time, metadata={}),
        "debunker": SimpleNamespace(
            timestamp=base_time + timedelta(hours=3), 
            metadata={"role": "debunker"}
        )
    }
    
    # No reliable snapshots
    mock_snapshots = [
        {"window_start": base_time, "value": 1.5, "is_reliable": False}
    ]
    
    result = compute_debunk_lag(G, messages, mock_snapshots)
    
    assert result["has_debunk"] is True
    assert result["estimation_method"] == "fallback_first_seen"
    assert result["debunk_lag_hours"] == 3.0