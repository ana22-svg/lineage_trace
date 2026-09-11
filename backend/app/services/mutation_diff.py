import json
import logging
from app.config import settings
# import anthropic  # Assuming anthropic SDK is installed
logger = logging.getLogger(__name__)

async def compute_diff(parent_text: str, child_text: str) -> dict:
    """
    Calls Anthropic API to generate a structured mutation diff between two messages.
    """
    # Mocking the Anthropic call for structural demonstration
    # client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    prompt = f"""
    Compare these two claims and output a JSON array of changes.
    Parent: {parent_text}
    Child: {child_text}
    Format: {{ "changes": [ {{ "field": "...", "old": "...", "new": "...", "category": "..." }} ] }}
    """
    
    # response = await client.messages.create(
    #     model=settings.ANTHROPIC_MODEL,
    #     messages=[{"role": "user", "content": prompt}]
    # )
    
    # Temporary deterministic fallback until the Anthropic client is enabled.
    mock_response = '{"changes": [{"field": "number", "old": "10", "new": "100", "category": "number"}]}'
    
    try:
        parsed = json.loads(mock_response)
    except (TypeError, json.JSONDecodeError):
        logger.exception("mutation_diff_parse_failed")
        raise
    return {
        "diff_json": parsed,
        "llm_model": settings.ANTHROPIC_MODEL,
        "llm_raw_response": mock_response
    }
