import asyncio
import json
import logging
from app.config import settings

logger = logging.getLogger(__name__)

def _prompt(parent_text: str, child_text: str) -> str:
    return f"""Compare these two claims and return only valid JSON.
Parent: {parent_text}
Child: {child_text}
Return this exact shape:
{{"changes":[{{"field":"number|qualifier|attribution|context|language","old":"...","new":"...","category":"number|qualifier|attribution|context|language"}}]}}
Use an empty changes array when the meaning did not materially change."""

def _client_and_model():
    provider = settings.LLM_PROVIDER.lower()
    if provider == "groq":
        if not settings.GROQ_API_KEY:
            raise RuntimeError("GROQ_API_KEY is required when LLM_PROVIDER=groq")
        from groq import AsyncGroq
        return AsyncGroq(api_key=settings.GROQ_API_KEY, timeout=settings.ANTHROPIC_TIMEOUT_SECONDS), settings.GROQ_MODEL
    if provider == "anthropic":
        if not settings.ANTHROPIC_API_KEY:
            raise RuntimeError("ANTHROPIC_API_KEY is required when LLM_PROVIDER=anthropic")
        import anthropic
        return anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY, timeout=settings.ANTHROPIC_TIMEOUT_SECONDS), settings.ANTHROPIC_MODEL
    raise ValueError(f"Unsupported LLM_PROVIDER: {settings.LLM_PROVIDER}")

async def compute_diff(parent_text: str, child_text: str) -> dict:
    client, model = _client_and_model()
    provider = settings.LLM_PROVIDER.lower()
    prompt = _prompt(parent_text, child_text)
    response = None
    for attempt in range(settings.ANTHROPIC_MAX_RETRIES):
        try:
            if provider == "groq":
                response = await client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "Return only valid JSON. Do not include markdown."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0,
                    max_tokens=1200,
                    response_format={"type": "json_object"},
                )
                raw_response = response.choices[0].message.content or ""
            else:
                response = await client.messages.create(
                    model=model,
                    max_tokens=1200,
                    temperature=0,
                    system="Return only valid JSON. Do not include markdown.",
                    messages=[{"role": "user", "content": prompt}],
                )
                raw_response = "".join(getattr(block, "text", "") for block in response.content)
            parsed = json.loads(raw_response)
            if not isinstance(parsed, dict) or not isinstance(parsed.get("changes"), list):
                raise ValueError("LLM response must contain a changes array")
            return {
                "diff_json": parsed,
                "llm_model": model,
                "llm_provider": provider,
                "llm_raw_response": raw_response,
            }
        except Exception:
            logger.exception("mutation_diff_attempt_failed", extra={"provider": provider, "attempt": attempt + 1})
            if attempt + 1 == settings.ANTHROPIC_MAX_RETRIES:
                raise
            await asyncio.sleep(settings.ANTHROPIC_RETRY_BASE_SECONDS * (2 ** attempt))
