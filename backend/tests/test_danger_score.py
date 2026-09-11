from app.services.danger_score import compute_danger_score

def test_danger_score_requires_diff():
    """Rule enforced: Never assert a danger score without a diff[cite: 1, 2]."""
    mock_diff = {
        "diff_json": {
            "changes": [
                {"field": "number", "old": "10", "new": "100", "category": "exaggeration"}
            ]
        }
    }
    
    result = compute_danger_score(mock_diff, downstream_reach=5)
    
    assert 0.0 <= result["danger_score"] <= 1.0
    assert result["distortion_magnitude"] > 0
    assert result["downstream_reach"] == 5