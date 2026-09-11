def compute_danger_score(diff_data: dict, downstream_reach: int) -> dict:
    """
    Computes danger score based STRICTLY on the parsed diff output and downstream reach.
    A danger score cannot be calculated without a MutationDiff as input.
    """
    changes = diff_data.get("diff_json", {}).get("changes", [])
    weights = {"number": 0.35, "qualifier": 0.20, "attribution": 0.20, "context": 0.15, "language": 0.10}
    distortion_magnitude = min(1.0, sum(weights.get(c.get("category"), 0.10) for c in changes))
    reach_signal = min(1.0, downstream_reach / 20.0)
    raw_score = distortion_magnitude * 0.7 + reach_signal * 0.3
    danger_score = min(max(raw_score, 0.0), 1.0)
    
    return {
        "danger_score": danger_score,
        "distortion_magnitude": distortion_magnitude,
        "downstream_reach": downstream_reach
    }
