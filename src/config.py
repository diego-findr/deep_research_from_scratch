"""
Configuration management for the evaluation system.

This module provides centralized configuration using Pydantic Settings
for environment variables, scoring weights, and thresholds.
"""

from typing import List, Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class EvaluationConfig(BaseSettings):
    """
    Configuration for the candidate-job evaluation system.
    
    All settings can be overridden via environment variables.
    Weights must sum to 1.0 for proper scoring calculation.
    """
    
    # LLM settings
    llm_provider: Literal["openai", "anthropic"] = "openai"
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    llm_model: str = "gpt-4o"
    llm_temperature: float = 0.1  # Low temperature for consistency
    
    # Scoring weights (must sum to 1.0)
    weight_sector: float = 0.20
    weight_skills: float = 0.25
    weight_seniority: float = 0.15
    weight_competencies: float = 0.15
    weight_domain_expert: float = 0.10
    weight_experience: float = 0.10
    weight_cultural: float = 0.05
    
    # Classification thresholds
    perfect_fit_threshold: int = 85
    good_fit_threshold: int = 70
    acceptable_fit_threshold: int = 55
    
    # Red flags criticality - sectors that are critical mismatches
    critical_red_flag_sectors: List[str] = [
        "sector_mismatch",
        "missing_mandatory_license",
        "insufficient_years_experience"
    ]
    
    # Logging
    log_level: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    def validate_weights(self) -> bool:
        """
        Validate that all weights sum to approximately 1.0.
        
        Returns:
            True if weights sum is valid (within 0.01 tolerance)
            
        Raises:
            ValueError: If weights don't sum to 1.0
        """
        total = (
            self.weight_sector +
            self.weight_skills +
            self.weight_seniority +
            self.weight_competencies +
            self.weight_domain_expert +
            self.weight_experience +
            self.weight_cultural
        )
        
        if abs(total - 1.0) > 0.01:
            raise ValueError(
                f"Weights must sum to 1.0, got {total}. "
                f"Check WEIGHT_* environment variables."
            )
        
        return True


# Global config instance
config = EvaluationConfig()

