"""Output formatting node to create final evaluation result."""

from typing import Any, Dict, List
from src.graph.state import EvaluationState


def format_output(state: EvaluationState) -> Dict[str, Any]:
    """
    Format final evaluation output.
    
    Args:
        state: Current evaluation state
        
    Returns:
        Updated state with final_evaluation formatted
    """
    orchestrator_output = state.get("orchestrator_output", {})
    all_evaluations = state.get("all_evaluations", [])
    
    # Build explainability section
    decision_tree = _build_decision_tree(all_evaluations, orchestrator_output)
    key_factors = _extract_key_factors(orchestrator_output)
    rationale = orchestrator_output.get("decision_rationale", "")
    
    explainability = {
        "executive_summary": _build_executive_summary(state, orchestrator_output),
        "decision_tree": decision_tree,
        "key_decision_factors": key_factors,
        "human_readable_rationale": rationale,
    }
    
    # Build final evaluation result
    final_evaluation = {
        "evaluation_id": state.get("evaluation_id", ""),
        "timestamp": state.get("timestamp", ""),
        "candidate_id": state["candidate"].get("candidate_id", "unknown"),
        "job_id": state["job_offer"].get("job_id", "unknown"),
        "final_evaluation": {
            "overall_score": orchestrator_output.get("final_score", 0),
            "fit_classification": orchestrator_output.get("fit_classification", "poor_fit"),
            "recommendation": orchestrator_output.get("recommendation", "not_recommend"),
            "confidence": orchestrator_output.get("confidence", 0.0),
        },
        "agents_evaluations": all_evaluations,
        "orchestrator_synthesis": orchestrator_output,
        "explainability": explainability,
    }
    
    return {
        "final_evaluation": final_evaluation,
        "current_phase": "complete",
    }


def _build_executive_summary(state: EvaluationState, orchestrator: dict) -> str:
    """Build executive summary."""
    candidate_name = state["candidate"].get("perfil_raw", {}).get("name", "Candidate")
    job_title = state["job_offer"].get("raw_job_posting", {}).get("title", "Position")
    company = state["job_offer"].get("raw_job_posting", {}).get("company", "Company")
    
    score = orchestrator.get("final_score", 0)
    fit = orchestrator.get("fit_classification", "").replace("_", " ").title()
    rec = orchestrator.get("recommendation", "").replace("_", " ").upper()
    
    return (
        f"{candidate_name} evaluated for {job_title} position at {company}. "
        f"Final Score: {score}/100 ({fit}). Recommendation: {rec}."
    )


def _build_decision_tree(evaluations: List[dict], orchestrator: dict) -> List[str]:
    """Build decision tree steps."""
    tree: List[str] = []
    
    step_map = {
        "sector": "Sector Alignment",
        "seniority": "Seniority Check",
        "skills": "Skills Matching",
        "competencies": "Competencies",
        "domain_expert": "Domain Expert",
        "experience": "Experience",
        "cultural": "Cultural Fit",
        "red_flags": "Red Flags",
        "salary": "Salary",
    }
    
    for i, eval_data in enumerate(evaluations, 1):
        agent = eval_data.get("agent", "")
        score = eval_data.get("score", 0)
        
        # Find step name
        step_name = "Unknown"
        for key, name in step_map.items():
            if key in agent:
                step_name = name
                break
        
        # Determine pass/alert status
        if score >= 70:
            status = "✓ PASS"
        elif score >= 50:
            status = "⚠ ALERT"
        else:
            status = "✗ FAIL"
        
        tree.append(f"{i}. {step_name}: {status} (score {score})")
    
    # Final synthesis
    final_score = orchestrator.get("final_score", 0)
    rec = orchestrator.get("recommendation", "not_recommend").upper().replace("_", " ")
    tree.append(f"{len(tree)+1}. Final Synthesis: ✓ {rec} (score {final_score})")
    
    return tree


def _extract_key_factors(orchestrator: dict) -> List[str]:
    """Extract key decision factors."""
    factors: List[str] = []
    
    strengths = orchestrator.get("key_strengths", [])[:2]
    weaknesses = orchestrator.get("key_weaknesses", [])[:2]
    
    for i, strength in enumerate(strengths, 1):
        factors.append(f"Factor positivo #{i}: {strength}")
    
    for i, weakness in enumerate(weaknesses, 1):
        factors.append(f"Factor negativo #{i}: {weakness}")
    
    return factors

