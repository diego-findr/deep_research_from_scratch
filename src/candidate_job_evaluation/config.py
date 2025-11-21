"""Configuration for evaluation system."""

from typing import Dict, List, Literal

from pydantic import BaseModel, Field


class EvaluationConfig(BaseModel):
    """Configuration for candidate-job evaluation system."""

    # LLM settings
    llm_provider: Literal["openai"] = "openai"
    llm_model: str = "gpt-4o"
    llm_temperature: float = Field(
        default=0.1, description="Low temperature for consistency"
    )

    # Scoring thresholds
    highly_recommend_threshold: int = 85
    recommend_threshold: int = 70
    acceptable_threshold: int = 55

    # Default agent weights (sector-agnostic baseline)
    default_weights: Dict[str, float] = Field(
        default={
            "sector": 0.25,
            "skills": 0.30,
            "seniority": 0.15,
            "competencies": 0.20,
            "domain_expert": 0.10,
        }
    )

    # Sector-specific weight adjustments
    sector_weight_adjustments: Dict[str, Dict[str, float]] = Field(
        default={
            "software": {"skills": 0.40, "competencies": 0.15},
            "construction": {"sector": 0.30, "competencies": 0.25, "skills": 0.20},
            "finance": {"competencies": 0.30, "skills": 0.25},
        }
    )

    # Critical red flags (auto-disqualify)
    critical_red_flag_types: List[str] = Field(
        default=[
            "sector_complete_mismatch",
            "missing_mandatory_certification",
            "insufficient_experience_years",
        ]
    )

    # Error handling
    agent_failure_default_score: int = 50
    max_retries: int = 2
