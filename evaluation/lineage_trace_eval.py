import json
import asyncio
from pathlib import Path
from baseline_llm import run_baseline_verdict
from backend.app.pipeline import process_message
from backend.app.schemas.message import NormalizedMessage
from backend.app.database import SessionLocal

async def evaluate_case(case_name: str, case_path: Path):
    """
    Runs the full Lineage Trace pipeline per case and compares it against the baseline LLM.
    """
    print(f"--- Evaluating {case_name} ---")
    
    messages_file = case_path / "messages.json"
    with open(messages_file, "r") as f:
        messages_data = json.load(f)
    
    # 1. Run Baseline on the earliest known claim variant
    earliest_claim = min(messages_data, key=lambda x: x["timestamp"])
    print("\n[Baseline LLM Verdict]")
    baseline_result = run_baseline_verdict(earliest_claim["text"])
    print(baseline_result)
    
    # 2. Run Lineage Trace Pipeline
    print("\n[Lineage Trace Pipeline Execution]")
    async with SessionLocal() as db:
        cluster_id = None
        for msg_dict in messages_data:
            msg = NormalizedMessage(**msg_dict)
            result = await process_message(msg, db)
            cluster_id = result["cluster_id"]
            
        # Fetch final metrics for the cluster
        # Assuming getter functions exist in your services
        from backend.app.services.topology import classify_and_update
        from backend.app.services.debunk_lag import compute_debunk_lag
        from backend.app.services.coordination import get_coordination_signal_density
        
        print(f"Pipeline finished for cluster: {cluster_id}")
        # Results will be manually compiled into comparison_report.md
        
async def run_evaluation_suite():
    cases_dir = Path(__file__).parent / "cases"
    for case_dir in cases_dir.iterdir():
        if case_dir.is_dir():
            await evaluate_case(case_dir.name, case_dir)

if __name__ == "__main__":
    asyncio.run(run_evaluation_suite())