import json
import logging
import asyncio
from app.config import settings
# import anthropic  # Assuming anthropic SDK is installed
logger = logging.getLogger(__name__)

async def compute_diff(parent_text: str, child_text: str) -> dict:
    """
    Calls Anthropic API to generate a structured mutation diff between two messages.
    """
    if not settings.ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY is required for mutation diffing")
    import anthropic
    client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY, timeout=settings.ANTHROPIC_TIMEOUT_SECONDS)
    
    prompt = f"""
    Compare these two claims and output a JSON array of changes.
    Parent: {parent_text}
    Child: {child_text}
    Format: {{ "changes": [ {{ "field": "...", "old": "...", "new": "...", "category": "..." }} ] }}
    """
    
    response = None
    for attempt in range(settings.ANTHROPIC_MAX_RETRIES):
        try:
            response = await client.messages.create(model=settings.ANTHROPIC_MODEL, max_tokens=1200, system="Return only valid JSON.", messages=[{"role": "user", "content": prompt}])
            break
        except Exception:
            logger.exception("anthropic_diff_attempt_failed", extra={"attempt": attempt + 1})
            if attempt + 1 == settings.ANTHROPIC_MAX_RETRIES:
                raise
            await asyncio.sleep(settings.ANTHROPIC_RETRY_BASE_SECONDS * (2 ** attempt))
    raw_response = "".join(getattr(block, "text", "") for block in response.content)
    try:
        parsed = json.loads(raw_response)
        if not isinstance(parsed.get("changes"), list):
            raise ValueError("Diff response must contain a changes array")
    except (TypeError, json.JSONDecodeError, ValueError):
        logger.exception("mutation_diff_parse_failed")
        raise
    return {
        "diff_json": parsed,
        "llm_model": settings.ANTHROPIC_MODEL,
        "llm_raw_response": raw_response
    }
