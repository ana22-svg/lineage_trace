from types import SimpleNamespace
from app.services.coordination import account_age_signal

def test_account_age_unavailable_for_telegram():
    """
    Rule enforced: Telegram account age must short-circuit, 
    as the bot API does not expose it[cite: 2].
    """
    msg = SimpleNamespace(source="telegram", author_account_age_days=None)
    result = account_age_signal(msg, [])
    
    assert result["flagged"] is False
    assert result["reason"] == "unavailable_for_telegram_source"

def test_account_age_flags_coordinated_seed_data():
    """Seed data with tightly clustered new accounts should flag[cite: 2]."""
    child = SimpleNamespace(source="seed", author_account_age_days=2)
    siblings = [
        SimpleNamespace(source="seed", author_account_age_days=1),
        SimpleNamespace(source="seed", author_account_age_days=3)
    ]
    
    result = account_age_signal(child, siblings)
    
    assert result["flagged"] is True
    assert result["count"] == 3
    assert result["mean"] < 90
    assert result["std"] < 30