from datetime import datetime, timedelta
from types import SimpleNamespace
from app.services.burstiness import compute_arrival_burstiness

def test_burstiness_flags_tight_timestamps():
    """Ensures burstiness logic accurately catches rapid arrivals[cite: 2]."""
    base_time = datetime(2026, 9, 8, 10, 0, 0)
    messages = [SimpleNamespace(timestamp=base_time + timedelta(seconds=i*5)) for i in range(6)]
    
    result = compute_arrival_burstiness(
        messages, 
        inter_arrival_threshold_sec=60.0, 
        min_count=5
    )
    
    assert result["flagged"] is True
    assert result["mean_delta_sec"] == 5.0
    assert result["count"] == 6

def test_burstiness_insufficient_data():
    """Should return safely if minimum node count isn't met[cite: 2]."""
    base_time = datetime(2026, 9, 8, 10, 0, 0)
    messages = [SimpleNamespace(timestamp=base_time)]
    
    result = compute_arrival_burstiness(
        messages, 
        inter_arrival_threshold_sec=60.0, 
        min_count=5
    )
    
    assert result["flagged"] is False
    assert result["reason"] == "insufficient_data"