"""Input validation node for the evaluation graph."""

from typing import Any, Dict
from src.graph.state import EvaluationState


def validate_inputs(state: EvaluationState) -> Dict[str, Any]:
    """
    Validate that inputs have required structure.
    
    Args:
        state: Current evaluation state
        
    Returns:
        Updated state with validation results
    """
    errors = []
    
    # Validate candidate
    candidate = state.get("candidate", {})
    if not candidate:
        errors.append("Missing candidate data")
    elif not candidate.get("semantic_enrichment"):
        errors.append("Candidate missing semantic_enrichment")
    
    # Validate job offer
    job_offer = state.get("job_offer", {})
    if not job_offer:
        errors.append("Missing job_offer data")
    elif not job_offer.get("semantic_enrichment"):
        errors.append("Job offer missing semantic_enrichment")
    
    if errors:
        return {
            "current_phase": "validation_failed",
            "errors": errors,
        }
    
    return {
        "current_phase": "analysis",
        "errors": [],
    }

