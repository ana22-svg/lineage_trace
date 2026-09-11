import os
import anthropic

def run_baseline_verdict(claim_text: str) -> str:
    """
    Single-call LLM verdict baseline.
    Evaluates a claim in isolation to simulate standard consumer fact-checking tools.
    """
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
    
    prompt = f"""
    Evaluate the following claim in isolation. Provide a definitive True/False verdict 
    and a brief 1-2 sentence explanation.
    
    Claim: "{claim_text}"
    """
    
    response = client.messages.create(
        model=model,
        max_tokens=250,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.content[0].text

if __name__ == "__main__":
    # Test execution
    sample_claim = "A newly discovered coordination tactic involves replacing text with emojis."
    print("Baseline Verdict:")
    print(run_baseline_verdict(sample_claim))