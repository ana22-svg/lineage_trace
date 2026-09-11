import statistics
from app.config import settings
from app.services.burstiness import compute_arrival_burstiness

def account_age_signal(child_msg, sibling_msgs) -> dict:
    """
    Only meaningful for source == 'seed'. For source == 'telegram', 
    this returns 'unavailable' since the Bot API does not expose account creation date.
    """
    if child_msg.source == "telegram":
        return {"flagged": False, "reason": "unavailable_for_telegram_source"}

    ages = [m.author_account_age_days for m in [child_msg] + sibling_msgs if m.author_account_age_days is not None]
    
    if len(ages) < 3:
        return {"flagged": False, "reason": "insufficient_data"}
        
    std = statistics.stdev(ages)
    mean = statistics.mean(ages)
    
    if std < 30 and mean < 90:
        return {"flagged": True, "mean": mean, "std": std, "count": len(ages)}
    return {"flagged": False, "mean": mean, "std": std, "count": len(ages)}

def timestamp_burst_signal(child_msg, sibling_msgs) -> dict:
    return compute_arrival_burstiness(
        [child_msg] + sibling_msgs,
        inter_arrival_threshold_sec=settings.BURSTINESS_INTER_ARRIVAL_THRESHOLD_SECONDS,
        min_count=5
    )

def compute_signals(child_msg, sibling_msgs) -> dict:
    age_signal = account_age_signal(child_msg, sibling_msgs)
    burst_signal = timestamp_burst_signal(child_msg, sibling_msgs)
    
    return {
        "account_age_stats": age_signal,
        "burst_score": burst_signal.get("coefficient_of_variation"),
        "is_coordinated": age_signal.get("flagged", False) or burst_signal.get("flagged", False),
        "detail_json": {"age": age_signal, "burst": burst_signal}
    }