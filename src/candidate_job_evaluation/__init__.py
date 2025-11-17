"""Candidate-Job Fit Evaluation System.

A multi-agent system using LangGraph to evaluate compatibility between
enriched candidate profiles and enriched job offers.

Architecture:
- Phase 1: Parallel specialized analysis (Sector, Skills, Seniority, Competencies, Red Flags)
- Phase 2: Domain expert analysis (sector-specific)
- Phase 3: Orchestration and synthesis

Key Features:
- Sector-agnostic evaluation
- Semantic disambiguation using enrichment data
- Dynamic weighting based on sector and seniority
- Full explainability and traceability
- Critical red flag detection with early termination
"""

from .config import EvaluationConfig
from .graph import build_evaluation_graph, evaluate_candidate_for_job
from .state import AgentEvaluation, EvaluationState, FinalEvaluation

__all__ = [
    "EvaluationConfig",
    "EvaluationState",
    "AgentEvaluation",
    "FinalEvaluation",
    "build_evaluation_graph",
    "evaluate_candidate_for_job",
]
