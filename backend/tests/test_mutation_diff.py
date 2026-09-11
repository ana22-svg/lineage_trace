import pytest
from app.services.mutation_diff import compute_diff

@pytest.mark.asyncio
async def test_compute_diff_returns_structured_json():
    parent_text = "10 workers were injured."
    child_text = "100 workers were injured."
    
    result = await compute_diff(parent_text, child_text)
    
    assert "diff_json" in result
    assert "changes" in result["diff_json"]
    assert result["llm_model"] is not None
    assert isinstance(result["diff_json"]["changes"], list)