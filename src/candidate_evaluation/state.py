"""
State Definitions and Pydantic Schemas for Candidate Evaluation System.
"""

from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel, Field


# ===== STATE DEFINITIONS =====

class CandidateEvaluationState(TypedDict):
    """
    State for the candidate evaluation pipeline.
    """
    # Input data
    candidate: Dict[str, Any]
    offer: Dict[str, Any]
    
    # Intermediate evaluation results
    hard_skills_eval: Optional[str]  # JSON string of HardSkillsEvaluation
    experience_eval: Optional[str]   # JSON string of ExperienceEvaluation
    potential_eval: Optional[str]    # JSON string of PotentialEvaluation
    
    # Final output
    final_evaluation: Optional[Dict[str, Any]]


# ===== STRUCTURED OUTPUT SCHEMAS =====

class HardSkillsEvaluation(BaseModel):
    """Evaluation of hard skills, languages, and explicit requirements."""
    liked: bool = Field(description="True if candidate meets hard skill requirements")
    reason: str = Field(description="Explanation of the decision based on hard skills")
    compatibility: int = Field(description="Compatibility score (0-100) for hard skills")
    missing_skills: List[str] = Field(description="List of mandatory skills missing", default_factory=list)

class ExperienceEvaluation(BaseModel):
    """Evaluation of professional experience, education, and cultural fit."""
    liked: bool = Field(description="True if candidate experience is relevant and sufficient")
    reason: str = Field(description="Explanation of the decision based on experience")
    compatibility: int = Field(description="Compatibility score (0-100) for experience")
    years_match: bool = Field(description="True if years of experience align with requirements")

class PotentialEvaluation(BaseModel):
    """Evaluation of potential, adaptability, and growth capacity."""
    liked: bool = Field(description="True if candidate shows good potential and adaptability")
    reason: str = Field(description="Explanation of the decision based on potential")
    compatibility: int = Field(description="Compatibility score (0-100) for potential")
    overqualification_risk: str = Field(description="Risk level: 'Low', 'Medium', 'High'")

class FinalEvaluation(BaseModel):
    """Final aggregated evaluation output."""
    liked: bool = Field(description="True if the majority of models voted in favor")
    models_liked: int = Field(description="Number of models that gave a 'true' liked verdict")
    models_evaluated: int = Field(description="Total number of models consulted")
    ai_swipe_reasons: List[str] = Field(description="List of individual reasons from each model")
    reason: str = Field(description="Summary of the decision")
    compatibility: int = Field(description="Average compatibility score (0-100)")
