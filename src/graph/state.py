"""
State schema for the LangGraph evaluation workflow.

This module defines the state that flows through the multi-agent graph,
containing inputs, intermediate evaluations, and final outputs.
"""

from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict
from datetime import datetime
import uuid


class EvaluationState(TypedDict, total=False):
    """
    State for the candidate-job evaluation graph.
    
    This state flows through all nodes in the LangGraph, with each agent
    adding its evaluation to the appropriate field.
    
    Attributes:
        # Inputs
        candidate: Complete candidate profile (enriched JSON)
        job_offer: Complete job offer (enriched JSON)
        
        # Metadata
        evaluation_id: Unique identifier for this evaluation
        timestamp: ISO 8601 timestamp of evaluation start
        current_phase: Current phase of evaluation workflow
        
        # Agent evaluations (each agent populates its own)
        sector_eval: Output from Sector Alignment Agent
        skills_eval: Output from Skills Matching Agent
        seniority_eval: Output from Seniority Calibration Agent
        competencies_eval: Output from Competencies Evaluator Agent
        domain_expert_eval: Output from Domain Expert Agent
        experience_eval: Output from Experience Relevance Agent
        cultural_eval: Output from Cultural & Soft Fit Agent
        red_flags_eval: Output from Red Flags Detector Agent
        salary_eval: Output from Salary & Compensation Agent
        
        # Aggregated data
        all_evaluations: List of all agent evaluations
        aggregated_scores: Dict of agent scores
        aggregated_red_flags: All red flags collected
        
        # Final outputs
        orchestrator_output: Output from Orchestrator Agent
        final_evaluation: Top-level evaluation result
        
        # Error handling
        errors: List of errors encountered during evaluation
    """
    
    # Required inputs
    candidate: Dict[str, Any]
    job_offer: Dict[str, Any]
    
    # Metadata
    evaluation_id: str
    timestamp: str
    current_phase: str  # "input_validation" | "analysis" | "aggregation" | "synthesis" | "complete"
    
    # Individual agent evaluations
    sector_eval: Optional[Dict[str, Any]]
    skills_eval: Optional[Dict[str, Any]]
    seniority_eval: Optional[Dict[str, Any]]
    competencies_eval: Optional[Dict[str, Any]]
    domain_expert_eval: Optional[Dict[str, Any]]
    experience_eval: Optional[Dict[str, Any]]
    cultural_eval: Optional[Dict[str, Any]]
    red_flags_eval: Optional[Dict[str, Any]]
    salary_eval: Optional[Dict[str, Any]]
    
    # Aggregated data
    all_evaluations: List[Dict[str, Any]]
    aggregated_scores: Dict[str, int]
    aggregated_red_flags: Dict[str, List[str]]  # severity -> list of flags
    
    # Final outputs
    orchestrator_output: Optional[Dict[str, Any]]
    final_evaluation: Optional[Dict[str, Any]]
    
    # Error handling
    errors: List[str]


def create_initial_state(
    candidate: Dict[str, Any],
    job_offer: Dict[str, Any]
) -> EvaluationState:
    """
    Create initial evaluation state from inputs.
    
    Args:
        candidate: Enriched candidate profile JSON
        job_offer: Enriched job offer JSON
        
    Returns:
        Initial EvaluationState with metadata populated
        
    Example:
        >>> state = create_initial_state({"candidate_id": "123"}, {"job_id": "456"})
        >>> state["current_phase"]
        'input_validation'
    """
    return EvaluationState(
        # Inputs
        candidate=candidate,
        job_offer=job_offer,
        
        # Metadata
        evaluation_id=str(uuid.uuid4()),
        timestamp=datetime.utcnow().isoformat() + "Z",
        current_phase="input_validation",
        
        # Initialize optional fields
        sector_eval=None,
        skills_eval=None,
        seniority_eval=None,
        competencies_eval=None,
        domain_expert_eval=None,
        experience_eval=None,
        cultural_eval=None,
        red_flags_eval=None,
        salary_eval=None,
        
        # Initialize aggregated data
        all_evaluations=[],
        aggregated_scores={},
        aggregated_red_flags={"critical": [], "high": [], "medium": []},
        
        # Initialize outputs
        orchestrator_output=None,
        final_evaluation=None,
        
        # Initialize errors
        errors=[],
    )

