"""
LangGraph builder for the multi-agent evaluation system.

This module constructs the StateGraph with all specialized agents
and orchestrates the evaluation workflow.
"""

from typing import Any, Dict
from langgraph.graph import StateGraph, END
from src.graph.state import EvaluationState
from src.graph.nodes.input_validation import validate_inputs
from src.graph.nodes.sector_agent import evaluate_sector_alignment
from src.graph.nodes.skills_agent import evaluate_skills_matching
from src.graph.nodes.seniority_agent import evaluate_seniority_calibration
from src.graph.nodes.competencies_agent import evaluate_competencies
from src.graph.nodes.domain_expert_agent import evaluate_domain_expertise
from src.graph.nodes.experience_agent import evaluate_experience_relevance
from src.graph.nodes.cultural_agent import evaluate_cultural_fit
from src.graph.nodes.salary_agent import evaluate_salary_compensation
from src.graph.nodes.aggregation import aggregate_evaluations
from src.graph.nodes.red_flags_agent import evaluate_red_flags
from src.graph.nodes.orchestrator import orchestrate_synthesis
from src.graph.nodes.output_formatter import format_output


def build_evaluation_graph() -> StateGraph:
    """
    Build the LangGraph StateGraph for candidate-job evaluation.
    
    The graph architecture follows this flow:
    
    START
      ↓
    [Input Validation]
      ↓
    [Parallel Analysis Phase] ─┬─ [Sector Alignment Agent]
                               ├─ [Skills Matching Agent]
                               ├─ [Seniority Calibration Agent]
                               ├─ [Competencies Evaluator Agent]
                               ├─ [Domain Expert Agent]
                               ├─ [Experience Relevance Agent]
                               ├─ [Cultural Soft Fit Agent]
                               └─ [Salary Compensation Agent]
      ↓
    [Aggregation Node]
      ↓
    [Red Flags Detector]
      ↓
    [Orchestrator Agent]
      ↓
    [Output Formatting]
      ↓
    END
    
    Returns:
        Compiled StateGraph ready for execution
        
    Example:
        >>> graph = build_evaluation_graph()
        >>> result = graph.invoke({"candidate": {...}, "job_offer": {...}})
        >>> result["final_evaluation"]["overall_score"]
        82
    """
    
    # Initialize graph
    workflow = StateGraph(EvaluationState)
    
    # Add nodes
    workflow.add_node("validate_inputs", validate_inputs)
    
    # Parallel evaluation agents
    workflow.add_node("evaluate_sector", evaluate_sector_alignment)
    workflow.add_node("evaluate_skills", evaluate_skills_matching)
    workflow.add_node("evaluate_seniority", evaluate_seniority_calibration)
    workflow.add_node("evaluate_competencies", evaluate_competencies)
    workflow.add_node("evaluate_domain", evaluate_domain_expertise)
    workflow.add_node("evaluate_experience", evaluate_experience_relevance)
    workflow.add_node("evaluate_cultural", evaluate_cultural_fit)
    workflow.add_node("evaluate_salary", evaluate_salary_compensation)
    
    # Aggregation and synthesis
    workflow.add_node("aggregate", aggregate_evaluations)
    workflow.add_node("evaluate_red_flags", evaluate_red_flags)
    workflow.add_node("orchestrate", orchestrate_synthesis)
    workflow.add_node("format_output", format_output)
    
    # Define edges
    
    # Entry point
    workflow.set_entry_point("validate_inputs")
    
    # After validation, branch based on success
    workflow.add_conditional_edges(
        "validate_inputs",
        _should_continue_after_validation,
        {
            "continue": "evaluate_sector",
            "end": END,
        }
    )
    
    # Parallel evaluation phase - all agents run in parallel
    # After sector eval, trigger all other evaluations
    workflow.add_edge("evaluate_sector", "evaluate_skills")
    workflow.add_edge("evaluate_sector", "evaluate_seniority")
    workflow.add_edge("evaluate_sector", "evaluate_competencies")
    workflow.add_edge("evaluate_sector", "evaluate_domain")
    workflow.add_edge("evaluate_sector", "evaluate_experience")
    workflow.add_edge("evaluate_sector", "evaluate_cultural")
    workflow.add_edge("evaluate_sector", "evaluate_salary")
    
    # All evaluations flow to aggregation
    workflow.add_edge("evaluate_skills", "aggregate")
    workflow.add_edge("evaluate_seniority", "aggregate")
    workflow.add_edge("evaluate_competencies", "aggregate")
    workflow.add_edge("evaluate_domain", "aggregate")
    workflow.add_edge("evaluate_experience", "aggregate")
    workflow.add_edge("evaluate_cultural", "aggregate")
    workflow.add_edge("evaluate_salary", "aggregate")
    
    # Aggregation to red flags detection
    workflow.add_edge("aggregate", "evaluate_red_flags")
    
    # Red flags to orchestrator
    workflow.add_edge("evaluate_red_flags", "orchestrate")
    
    # Orchestrator to output formatting
    workflow.add_edge("orchestrate", "format_output")
    
    # Output formatting to end
    workflow.add_edge("format_output", END)
    
    # Compile graph
    return workflow.compile()


def _should_continue_after_validation(state: EvaluationState) -> str:
    """
    Conditional edge function to determine if evaluation should continue.
    
    Args:
        state: Current evaluation state
        
    Returns:
        "continue" if validation passed, "end" if failed
    """
    errors = state.get("errors", [])
    current_phase = state.get("current_phase", "")
    
    if errors or current_phase == "validation_failed":
        return "end"
    
    return "continue"

