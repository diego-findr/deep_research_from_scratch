"""Multi-Agent Candidate Evaluation System.

This package provides a collaborative evaluation system with three specialized
recruiter agents that evaluate candidates, debate findings, and reach consensus
decisions.
"""

from .evaluation_agent import evaluate_candidate, create_evaluation_graph
from .state import (
    CandidateEvaluationState,
    AgentEvaluation,
    DebateMessage,
    Question,
    ConsensusDecision,
    ReasoningLogEntry,
)

__all__ = [
    "evaluate_candidate",
    "create_evaluation_graph",
    "CandidateEvaluationState",
    "AgentEvaluation",
    "DebateMessage",
    "Question",
    "ConsensusDecision",
    "ReasoningLogEntry",
]
