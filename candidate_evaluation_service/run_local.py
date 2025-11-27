import asyncio
import json
import sys
from pathlib import Path
from rich.console import Console

# Add the service directory to the python path so we can import app modules
SERVICE_DIR = Path(__file__).parent
sys.path.append(str(SERVICE_DIR))

from app.core.graph import create_evaluation_graph, CandidateEvaluationState
from app.core.logger import setup_logging
from app.core.config import settings

# Setup logging
setup_logging()
console = Console()

async def run_local_evaluation(job_path: str, candidate_path: str):
    """Run evaluation locally using JSON files."""
    
    # Load data
    try:
        with open(candidate_path, 'r', encoding='utf-8') as f:
            enriched_candidate = json.load(f)
        
        with open(job_path, 'r', encoding='utf-8') as f:
            enriched_job = json.load(f)
            
        console.print(f"\n[bold cyan]Running Local Evaluation[/bold cyan]")
        console.print(f"Job: {job_path}")
        console.print(f"Candidate: {candidate_path}\n")
        
        # Create graph
        graph = create_evaluation_graph()
        
        # Initialize state
        initial_state: CandidateEvaluationState = {
            "enriched_candidate": enriched_candidate,
            "enriched_job": enriched_job,
            "agent_evaluations": [],
            "debate_messages": [],
            "questions_asked": [],
            "consensus_decision": None,
            "reasoning_log": [],
            "debate_round": 1,
            "max_debate_rounds": settings.MAX_DEBATE_ROUNDS,
            "gatekeeper_decision": None
        }
        
        # Run graph
        result = await graph.ainvoke(initial_state)
        
        # Save result
        output_path = Path("local_evaluation_result.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            # Convert result to serializable dict (handle any non-serializable objects if needed)
            json.dump(result, f, indent=2, ensure_ascii=False, default=str)
            
        console.print(f"\n[bold green]✅ Evaluation Complete![/bold green]")
        console.print(f"Results saved to: {output_path.absolute()}")
        
    except Exception as e:
        console.print(f"[bold red]Error running evaluation:[/bold red] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python run_local.py <job_json_path> <candidate_json_path>")
        print("Example: python run_local.py tests/data/enriched_prl_valid_1.json tests/data/enriched_acciona_prl.json")
        sys.exit(1)
        
    job_file = sys.argv[1]
    candidate_file = sys.argv[2]
    
    asyncio.run(run_local_evaluation(job_file, candidate_file))
