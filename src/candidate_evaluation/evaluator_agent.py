"""
Candidate Evaluation Agent Implementation.
"""

import json
from typing import Any, Dict, List
from pydantic import ValidationError

from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from candidate_evaluation.state import (
    CandidateEvaluationState,
    HardSkillsEvaluation,
    ExperienceEvaluation,
    PotentialEvaluation,
    FinalEvaluation
)
from candidate_evaluation.prompts import (
    HARD_SKILLS_PROMPT,
    EXPERIENCE_PROMPT,
    POTENTIAL_PROMPT,
    AGGREGATION_PROMPT
)

# Initialize model
# Using gpt-4o for high quality as requested
model = init_chat_model(model="openai:gpt-4o")

# ===== UTILITY FUNCTIONS =====

def format_data(data: Dict[str, Any]) -> str:
    """Format data as a readable string."""
    return json.dumps(data, indent=2, ensure_ascii=False)

# ===== AGENT NODES =====

def evaluate_hard_skills(state: CandidateEvaluationState) -> Dict[str, Any]:
    """Evaluate hard skills."""
    candidate_str = format_data(state["candidate"])
    offer_str = format_data(state["offer"])
    
    prompt = HARD_SKILLS_PROMPT.format(
        candidate_data=candidate_str,
        offer_data=offer_str
    )
    
    model_with_structure = model.with_structured_output(
        HardSkillsEvaluation, method="function_calling"
    )
    response = model_with_structure.invoke(prompt)
    
    return {"hard_skills_eval": json.dumps(response.model_dump(), ensure_ascii=False)}

def evaluate_experience(state: CandidateEvaluationState) -> Dict[str, Any]:
    """Evaluate experience."""
    candidate_str = format_data(state["candidate"])
    offer_str = format_data(state["offer"])
    
    prompt = EXPERIENCE_PROMPT.format(
        candidate_data=candidate_str,
        offer_data=offer_str
    )
    
    model_with_structure = model.with_structured_output(
        ExperienceEvaluation, method="function_calling"
    )
    response = model_with_structure.invoke(prompt)
    
    return {"experience_eval": json.dumps(response.model_dump(), ensure_ascii=False)}

def evaluate_potential(state: CandidateEvaluationState) -> Dict[str, Any]:
    """Evaluate potential."""
    candidate_str = format_data(state["candidate"])
    offer_str = format_data(state["offer"])
    
    prompt = POTENTIAL_PROMPT.format(
        candidate_data=candidate_str,
        offer_data=offer_str
    )
    
    model_with_structure = model.with_structured_output(
        PotentialEvaluation, method="function_calling"
    )
    response = model_with_structure.invoke(prompt)
    
    return {"potential_eval": json.dumps(response.model_dump(), ensure_ascii=False)}

def aggregate_results(state: CandidateEvaluationState) -> Dict[str, Any]:
    """Aggregate results from all evaluators."""
    hard_skills = json.loads(state["hard_skills_eval"])
    experience = json.loads(state["experience_eval"])
    potential = json.loads(state["potential_eval"])
    
    # Calculate metrics manually to ensure accuracy before passing to LLM for summary
    evaluations = [hard_skills, experience, potential]
    likes = sum(1 for e in evaluations if e["liked"])
    total = len(evaluations)
    avg_compatibility = int(sum(e["compatibility"] for e in evaluations) / total)
    
    reasons = [
        f"Hard Skills: {hard_skills['reason']}",
        f"Experience: {experience['reason']}",
        f"Potential: {potential['reason']}"
    ]
    
    # We can use the LLM to generate the final summary reason, 
    # but we can also construct the FinalEvaluation object directly 
    # if we want deterministic aggregation logic.
    # However, the prompt asks for a "Lead Recruitment Manager" persona to summarize.
    # Let's use the LLM to synthesize the 'reason' field, but enforce the 'liked' and 'compatibility' logic.
    
    prompt = AGGREGATION_PROMPT.format(
        hard_skills_eval=json.dumps(hard_skills, indent=2),
        experience_eval=json.dumps(experience, indent=2),
        potential_eval=json.dumps(potential, indent=2)
    )
    
    model_with_structure = model.with_structured_output(
        FinalEvaluation, method="function_calling"
    )
    response = model_with_structure.invoke(prompt)
    
    # Enforce the logic requested in the prompt to be 100% sure
    final_decision = likes >= 2
    
    # Update the response with calculated metrics to ensure consistency
    final_output = response.model_dump()
    final_output["liked"] = final_decision
    final_output["models_liked"] = likes
    final_output["models_evaluated"] = total
    final_output["compatibility"] = avg_compatibility
    final_output["ai_swipe_reasons"] = [e["reason"] for e in evaluations]
    
    return {"final_evaluation": final_output}

# ===== GRAPH CONSTRUCTION =====

def build_evaluation_graph() -> StateGraph:
    """Build the candidate evaluation graph."""
    builder = StateGraph(CandidateEvaluationState)
    
    # Add nodes
    builder.add_node("evaluate_hard_skills", evaluate_hard_skills)
    builder.add_node("evaluate_experience", evaluate_experience)
    builder.add_node("evaluate_potential", evaluate_potential)
    builder.add_node("aggregate_results", aggregate_results)
    
    # Add edges
    # Parallel execution
    builder.add_edge(START, "evaluate_hard_skills")
    builder.add_edge(START, "evaluate_experience")
    builder.add_edge(START, "evaluate_potential")
    
    # Fan-in to aggregation
    builder.add_edge("evaluate_hard_skills", "aggregate_results")
    builder.add_edge("evaluate_experience", "aggregate_results")
    builder.add_edge("evaluate_potential", "aggregate_results")
    
    builder.add_edge("aggregate_results", END)
    
    return builder.compile()

# ===== MAIN AGENT =====

evaluation_agent = build_evaluation_graph()

# ===== CONVENIENCE FUNCTION =====

def evaluate_candidate(candidate: Dict[str, Any], offer: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate a candidate against an offer using 3 expert AI agents.
    """
    initial_state = {
        "candidate": candidate,
        "offer": offer,
        "hard_skills_eval": None,
        "experience_eval": None,
        "potential_eval": None,
        "final_evaluation": None
    }
    
    result = evaluation_agent.invoke(initial_state)
    return result["final_evaluation"]
