"""
Pydantic schemas for evaluation results and agent outputs.

These schemas define the structure of outputs from individual agents
and the final evaluation result.
"""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class AgentEvaluation(BaseModel):
    """
    Base model for evaluation output from any specialized agent.
    
    All agents must produce outputs conforming to this schema to ensure
    consistent structure and enable proper aggregation.
    """
    
    agent: str = Field(..., description="Name of the agent (e.g., 'sector_alignment')")
    score: int = Field(..., ge=0, le=100, description="Score from 0-100")
    evidence: List[str] = Field(default_factory=list, description="Evidence supporting the score")
    reasoning: str = Field(..., description="Step-by-step reasoning for the evaluation")
    red_flags: List[str] = Field(default_factory=list, description="Warning flags detected")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence in evaluation")
    
    # Additional fields specific to each agent type (stored as dict for flexibility)
    details: Dict[str, Any] = Field(default_factory=dict, description="Agent-specific details")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "agent": "sector_alignment",
                "score": 85,
                "evidence": [
                    "Candidate primary sector: construction (confidence: 0.95)",
                    "Job primary sector: construction (confidence: 0.98)"
                ],
                "reasoning": "Both profiles aligned in construction sector...",
                "red_flags": [],
                "confidence": 0.95,
                "details": {
                    "alignment_level": "strong_match",
                    "primary_sector_match": True
                }
            }
        }


class ScoreBreakdown(BaseModel):
    """Detailed breakdown of a single agent's contribution to final score."""
    
    score: int = Field(..., ge=0, le=100, description="Raw agent score")
    weight: float = Field(..., ge=0.0, le=1.0, description="Weight applied to this agent")
    weighted_score: float = Field(..., description="Contribution to final score")


class OrchestratorOutput(BaseModel):
    """
    Output from the Orchestrator Agent with final synthesis.
    
    This represents the final decision after integrating all specialist
    agent evaluations with dynamic weighting and conflict resolution.
    """
    
    agent: str = Field(default="orchestrator", description="Agent name")
    final_score: int = Field(..., ge=0, le=100, description="Final weighted score")
    fit_classification: Literal["perfect_fit", "good_fit", "acceptable_fit", "poor_fit"] = Field(
        ..., description="Classification of candidate-job fit"
    )
    recommendation: Literal[
        "strong_recommend", "recommend", "conditional_recommend", "not_recommend"
    ] = Field(..., description="Hiring recommendation")
    
    score_breakdown: Dict[str, ScoreBreakdown] = Field(
        ..., description="Breakdown of each agent's contribution"
    )
    
    key_strengths: List[str] = Field(
        default_factory=list, description="Top strengths of the candidate"
    )
    key_weaknesses: List[str] = Field(
        default_factory=list, description="Areas of concern or gaps"
    )
    
    decision_rationale: str = Field(..., description="Executive summary of the decision")
    
    next_steps_recommendation: List[str] = Field(
        default_factory=list, description="Recommended next steps in hiring process"
    )
    
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in final decision")
    
    agents_consensus: Dict[str, Any] = Field(
        default_factory=dict, description="Analysis of agreement between agents"
    )
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "agent": "orchestrator",
                "final_score": 82,
                "fit_classification": "good_fit",
                "recommendation": "recommend",
                "score_breakdown": {
                    "sector_alignment": {
                        "score": 85,
                        "weight": 0.20,
                        "weighted_score": 17.0
                    }
                },
                "key_strengths": ["Seniority aligned", "Sector compatible"],
                "key_weaknesses": ["Limited experience in specific project type"],
                "decision_rationale": "Candidate shows good fit with 82/100...",
                "next_steps_recommendation": ["Interview to validate experience"],
                "confidence": 0.88,
                "agents_consensus": {"consensus_level": "high"}
            }
        }


class EvaluationResult(BaseModel):
    """
    Complete evaluation result returned by the system.
    
    This is the top-level output containing all agent evaluations,
    orchestrator synthesis, and explainability information.
    """
    
    evaluation_id: str = Field(..., description="Unique identifier for this evaluation")
    timestamp: str = Field(..., description="ISO 8601 timestamp of evaluation")
    candidate_id: str = Field(..., description="Candidate identifier")
    job_id: str = Field(..., description="Job offer identifier")
    
    final_evaluation: Dict[str, Any] = Field(
        ..., description="Summary of final evaluation results"
    )
    
    agents_evaluations: List[AgentEvaluation] = Field(
        ..., description="Detailed outputs from all specialist agents"
    )
    
    orchestrator_synthesis: OrchestratorOutput = Field(
        ..., description="Orchestrator's final synthesis"
    )
    
    explainability: Dict[str, Any] = Field(
        default_factory=dict, description="Complete explainability information"
    )
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "evaluation_id": "eval-uuid-2025",
                "timestamp": "2025-11-17T17:33:00Z",
                "candidate_id": "1e038af0-717e-49ed-a00e-775cb00c1488",
                "job_id": "be2baa17-8bc6-4d5a-ab92-2dc40a2177e2",
                "final_evaluation": {
                    "overall_score": 82,
                    "fit_classification": "good_fit",
                    "recommendation": "recommend",
                    "confidence": 0.88
                },
                "agents_evaluations": [],
                "orchestrator_synthesis": {},
                "explainability": {}
            }
        }

