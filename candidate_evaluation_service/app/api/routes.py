from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional

from app.core.graph import create_evaluation_graph, CandidateEvaluationState
from app.core.config import settings

router = APIRouter()

class EvaluationRequest(BaseModel):
    enriched_candidate: Dict[str, Any]
    enriched_job: Dict[str, Any]
    max_debate_rounds: Optional[int] = None

@router.post("/evaluate", response_model=Dict[str, Any])
async def evaluate_candidate(request: EvaluationRequest):
    """
    Evaluate a candidate against a job offer using the multi-agent system.
    """
    try:
        graph = create_evaluation_graph()
        
        initial_state: CandidateEvaluationState = {
            "enriched_candidate": request.enriched_candidate,
            "enriched_job": request.enriched_job,
            "agent_evaluations": [],
            "debate_messages": [],
            "questions_asked": [],
            "consensus_decision": None,
            "reasoning_log": [],
            "debate_round": 1,
            "max_debate_rounds": request.max_debate_rounds or settings.MAX_DEBATE_ROUNDS,
            "gatekeeper_decision": None
        }
        
        # Use ainvoke for async execution
        import time
        from app.core.logger import get_logger
        
        logger = get_logger("api")
        start_time = time.time()
        
        result = await graph.ainvoke(initial_state)
        
        duration = time.time() - start_time
        logger.info(f"[success]⏱️ Evaluation completed in {duration:.2f} seconds[/success]")
        
        # Filter out internal state if needed, or return full state
        # For now, returning full state is fine as it contains the results
        return result
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")
