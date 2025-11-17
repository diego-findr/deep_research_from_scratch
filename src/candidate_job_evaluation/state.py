"""State schema for candidate-job evaluation system."""

import operator
from datetime import datetime
from typing import Annotated, Any, Dict, List, Literal, Optional, TypedDict

from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field


class AgentEvaluation(BaseModel):
    """Output from a specialized evaluation agent."""

    agent_name: str = Field(description="Name of the agent")
    score: int = Field(ge=0, le=100, description="Score from 0-100")
    alignment_level: Literal[
        "perfect_match", "strong_match", "partial_match", "weak_match", "mismatch"
    ] = Field(description="Categorical alignment level")
    reasoning: str = Field(description="Step-by-step reasoning (Chain-of-Thought)")
    evidence: List[str] = Field(description="Evidence points from inputs")
    red_flags: List[str] = Field(
        default_factory=list, description="Identified red flags"
    )
    confidence: float = Field(
        ge=0.0, le=1.0, description="Confidence in evaluation"
    )


class FinalEvaluation(BaseModel):
    """Final synthesized evaluation."""

    overall_score: int = Field(ge=0, le=100, description="Weighted overall score")
    recommendation: Literal[
        "highly_recommend", "recommend", "acceptable", "not_recommend"
    ] = Field(description="Final recommendation")
    summary: str = Field(description="Executive summary")
    strengths: List[str] = Field(description="Key strengths identified")
    concerns: List[str] = Field(description="Key concerns identified")
    missing_skills: List[str] = Field(
        description="Critical skills candidate is missing"
    )
    all_red_flags: List[str] = Field(description="All red flags collected")
    agent_scores: Dict[str, int] = Field(
        description="Individual agent scores for transparency"
    )
    decision_tree: str = Field(description="Human-readable decision explanation")


class EvaluationState(TypedDict):
    """State that flows through the evaluation graph."""

    # Inputs
    candidate: Dict[str, Any]
    job_offer: Dict[str, Any]

    # Agent evaluations (accumulated)
    sector_evaluation: Optional[AgentEvaluation]
    skills_evaluation: Optional[AgentEvaluation]
    seniority_evaluation: Optional[AgentEvaluation]
    competencies_evaluation: Optional[AgentEvaluation]
    red_flags_evaluation: Optional[AgentEvaluation]
    domain_expert_evaluation: Optional[AgentEvaluation]

    # Final synthesis
    final_evaluation: Optional[FinalEvaluation]

    # Control flags
    critical_red_flags_found: bool
    early_termination: bool

    # Metadata
    evaluation_id: str
    timestamp: str
    messages: Annotated[List[BaseMessage], operator.add]
