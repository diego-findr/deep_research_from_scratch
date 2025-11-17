"""Aggregation node to collect all agent evaluations."""

from typing import Any, Dict, List
from src.graph.state import EvaluationState


def aggregate_evaluations(state: EvaluationState) -> Dict[str, Any]:
    """
    Aggregate all agent evaluations into lists for orchestrator.
    
    Args:
        state: Current evaluation state
        
    Returns:
        Updated state with aggregated evaluations
    """
    all_evaluations: List[Dict[str, Any]] = []
    aggregated_scores: Dict[str, int] = {}
    aggregated_red_flags: Dict[str, List[str]] = {
        "critical": [],
        "high": [],
        "medium": [],
    }
    
    # Collect all evaluations
    eval_keys = [
        "sector_eval",
        "skills_eval",
        "seniority_eval",
        "competencies_eval",
        "domain_expert_eval",
        "experience_eval",
        "cultural_eval",
        "salary_eval",
    ]
    
    for key in eval_keys:
        evaluation = state.get(key)
        if evaluation:
            all_evaluations.append(evaluation)
            
            # Extract score
            agent_name = evaluation.get("agent", key.replace("_eval", ""))
            score = evaluation.get("score", 50)
            aggregated_scores[agent_name] = score
            
            # Extract red flags (will be classified by red_flags_detector)
            red_flags = evaluation.get("red_flags", [])
            if red_flags:
                # For now, classify as medium by default
                aggregated_red_flags["medium"].extend(red_flags)
    
    return {
        "all_evaluations": all_evaluations,
        "aggregated_scores": aggregated_scores,
        "aggregated_red_flags": aggregated_red_flags,
        "current_phase": "aggregation",
    }

