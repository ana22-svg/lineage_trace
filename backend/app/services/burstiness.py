import statistics
from typing import List, Dict, Any
from types import SimpleNamespace

def compute_arrival_burstiness(
    messages: List[Any], 
    inter_arrival_threshold_sec: float,
    min_count: int
) -> Dict[str, Any]:
    """
    Measures how tightly clustered a set of messages' arrival times are.
    """
    timestamps = sorted([m.timestamp for m in messages])
    
    if len(timestamps) < min_count:
        return {"flagged": False, "reason": "insufficient_data", "count": len(timestamps)}

    deltas = [(timestamps[i+1] - timestamps[i]).total_seconds() for i in range(len(timestamps) - 1)]
    mean_delta = statistics.mean(deltas)
    coefficient_of_variation = (statistics.stdev(deltas) / mean_delta) if mean_delta > 0 else 0.0

    flagged = mean_delta < inter_arrival_threshold_sec and len(timestamps) >= min_count
    
    return {
        "flagged": flagged,
        "mean_delta_sec": mean_delta,
        "coefficient_of_variation": coefficient_of_variation,
        "count": len(timestamps)
    }