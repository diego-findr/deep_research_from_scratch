"""LangGraph workflow for candidate-job evaluation."""

from datetime import datetime
from typing import Literal
from uuid import uuid4

from langgraph.graph import END, START, StateGraph

from .agents import EvaluationAgents
from .config import EvaluationConfig
from .state import EvaluationState


def should_terminate_early(state: EvaluationState) -> Literal["terminate", "continue"]:
    """Decide if evaluation should terminate early due to critical red flags.

    Args:
        state: Current evaluation state

    Returns:
        "terminate" if critical red flags found, else "continue"
    """
    if state.get("early_termination", False):
        return "terminate"
    return "continue"


def build_evaluation_graph(config: EvaluationConfig) -> StateGraph:
    """Build the candidate-job evaluation graph.

    Architecture:
    1. Parallel execution of: sector, skills, seniority, competencies, red_flags
    2. Conditional edge: if critical red flags → terminate early
    3. Domain expert evaluation (sector-specific)
    4. Orchestrator synthesis → final evaluation

    Args:
        config: Evaluation configuration

    Returns:
        Compiled StateGraph
    """
    agents = EvaluationAgents(config)

    # Initialize graph
    graph = StateGraph(EvaluationState)

    # Add specialized agent nodes
    graph.add_node("sector_alignment", agents.sector_alignment_agent)
    graph.add_node("skills_matching", agents.skills_matching_agent)
    graph.add_node("seniority_alignment", agents.seniority_alignment_agent)
    graph.add_node("competencies_matching", agents.competencies_matching_agent)
    graph.add_node("red_flags_detector", agents.red_flags_detector_agent)

    # Add domain expert and orchestrator nodes
    graph.add_node("domain_expert", agents.domain_expert_agent)
    graph.add_node("orchestrator", agents.orchestrator_agent)

    # Phase 1: Parallel specialized analysis
    graph.add_edge(START, "sector_alignment")
    graph.add_edge(START, "skills_matching")
    graph.add_edge(START, "seniority_alignment")
    graph.add_edge(START, "competencies_matching")
    graph.add_edge(START, "red_flags_detector")

    # Phase 2: Conditional routing after red flags detection
    # If critical red flags found, skip domain expert and go to orchestrator
    # Otherwise, continue to domain expert
    graph.add_conditional_edges(
        "red_flags_detector",
        should_terminate_early,
        {"terminate": "orchestrator", "continue": "domain_expert"},
    )

    # Wait for all parallel agents before domain expert
    graph.add_edge("sector_alignment", "domain_expert")
    graph.add_edge("skills_matching", "domain_expert")
    graph.add_edge("seniority_alignment", "domain_expert")
    graph.add_edge("competencies_matching", "domain_expert")

    # Phase 3: Final synthesis
    graph.add_edge("domain_expert", "orchestrator")
    graph.add_edge("orchestrator", END)

    return graph.compile()


def evaluate_candidate_for_job(
    candidate: dict, job_offer: dict, config: EvaluationConfig = None
) -> dict:
    """Evaluate a candidate for a job offer.

    Args:
        candidate: Enriched candidate profile
        job_offer: Enriched job offer profile
        config: Evaluation configuration (uses default if None)

    Returns:
        Final evaluation with all agent results
    """
    if config is None:
        config = EvaluationConfig()

    graph = build_evaluation_graph(config)

    initial_state: EvaluationState = {
        "candidate": candidate,
        "job_offer": job_offer,
        "sector_evaluation": None,
        "skills_evaluation": None,
        "seniority_evaluation": None,
        "competencies_evaluation": None,
        "red_flags_evaluation": None,
        "domain_expert_evaluation": None,
        "final_evaluation": None,
        "critical_red_flags_found": False,
        "early_termination": False,
        "evaluation_id": str(uuid4()),
        "timestamp": datetime.now().isoformat(),
        "messages": [],
    }

    result = graph.invoke(initial_state)

    return result
