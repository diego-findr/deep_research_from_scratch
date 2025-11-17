"""
Pydantic schemas for job offer data.

These schemas validate the enriched job offer JSON structure that serves
as input to the evaluation system.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class JobOffer(BaseModel):
    """
    Complete job offer with semantic enrichment.
    
    This model represents a job posting that has been processed through
    semantic enrichment pipelines, including sector inference, skills
    extraction, and ideal candidate profile generation.
    """
    
    # Required fields
    job_id: str = Field(..., description="Unique identifier for the job offer")
    raw_job_posting: Dict[str, Any] = Field(..., description="Raw job posting data")
    semantic_enrichment: Dict[str, Any] = Field(..., description="Semantic analysis results")
    key_insights: Dict[str, Any] = Field(..., description="Executive summary of requirements")
    explainability: Dict[str, Any] = Field(..., description="Reasoning for requirements")
    
    # Optional metadata
    last_updated: Optional[str] = None
    version: Optional[str] = None
    
    class Config:
        """Pydantic config."""
        extra = "allow"  # Allow additional fields for flexibility
        json_schema_extra = {
            "example": {
                "job_id": "be2baa17-8bc6-4d5a-ab92-2dc40a2177e2",
                "raw_job_posting": {
                    "title": "Gerente de Soporte Técnico",
                    "company": "Acciona",
                    "description": "...",
                    "min_salary_range": 60000,
                    "max_salary_range": 80000
                },
                "semantic_enrichment": {
                    "sector_inference": {
                        "primary_sector": "construction",
                        "confidence": 0.98
                    },
                    "skills_extraction": {
                        "explicit_skills": [],
                        "implicit_skills": []
                    },
                    "seniority_inference": {
                        "required_seniority": "lead",
                        "years_experience_required": 10
                    },
                    "ideal_candidate_profile": {
                        "must_have": [],
                        "preferred": [],
                        "potential_red_flags": []
                    }
                },
                "key_insights": {},
                "explainability": {}
            }
        }
    
    def get_sector_inference(self) -> Dict[str, Any]:
        """Extract sector inference data from semantic enrichment."""
        return self.semantic_enrichment.get("sector_inference", {})
    
    def get_skills_extraction(self) -> Dict[str, Any]:
        """Extract skills data from semantic enrichment."""
        return self.semantic_enrichment.get("skills_extraction", {})
    
    def get_seniority_inference(self) -> Dict[str, Any]:
        """Extract seniority requirements from semantic enrichment."""
        return self.semantic_enrichment.get("seniority_inference", {})
    
    def get_competencies_analysis(self) -> Dict[str, Any]:
        """Extract competencies requirements from semantic enrichment."""
        return self.semantic_enrichment.get("competencies_analysis", {})
    
    def get_ideal_candidate_profile(self) -> Dict[str, Any]:
        """Extract ideal candidate profile from semantic enrichment."""
        return self.semantic_enrichment.get("ideal_candidate_profile", {})
    
    def get_normalization(self) -> Dict[str, Any]:
        """Extract normalization data from semantic enrichment."""
        return self.semantic_enrichment.get("normalization", {})

