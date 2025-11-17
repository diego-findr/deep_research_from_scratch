"""
Pydantic schemas for candidate profile data.

These schemas validate the enriched candidate JSON structure that serves
as input to the evaluation system.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CandidateProfile(BaseModel):
    """
    Complete candidate profile with semantic enrichment.
    
    This model represents a candidate that has already been processed
    through semantic enrichment pipelines, including sector inference,
    skills extraction, and seniority calibration.
    """
    
    # Required fields
    candidate_id: str = Field(..., description="Unique identifier for the candidate")
    perfil_raw: Dict[str, Any] = Field(..., description="Raw profile data")
    semantic_enrichment: Dict[str, Any] = Field(..., description="Semantic analysis results")
    key_insights: Dict[str, Any] = Field(..., description="Executive summary of profile")
    explainability: Dict[str, Any] = Field(..., description="Reasoning for inferences")
    
    # Optional metadata
    last_updated: Optional[str] = None
    version: Optional[str] = None
    
    class Config:
        """Pydantic config."""
        extra = "allow"  # Allow additional fields for flexibility
        json_schema_extra = {
            "example": {
                "candidate_id": "1e038af0-717e-49ed-a00e-775cb00c1488",
                "perfil_raw": {
                    "name": "Natalia [Apellido]",
                    "skills": ["PRL", "Gestión de equipos"],
                    "experiences": []
                },
                "semantic_enrichment": {
                    "sector_inference": {
                        "primary_sector": "construction",
                        "confidence": 0.95
                    },
                    "skills_extraction": {
                        "explicit_skills": [],
                        "implicit_skills": []
                    },
                    "seniority_inference": {
                        "seniority_level": "lead",
                        "years_experience_estimate": 9
                    }
                },
                "key_insights": {
                    "sector": "construction",
                    "seniority": "lead",
                    "total_skills": 25
                },
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
        """Extract seniority data from semantic enrichment."""
        return self.semantic_enrichment.get("seniority_inference", {})
    
    def get_competencies_analysis(self) -> Dict[str, Any]:
        """Extract competencies data from semantic enrichment."""
        return self.semantic_enrichment.get("competencies_analysis", {})
    
    def get_disambiguation(self) -> Dict[str, Any]:
        """Extract disambiguation data from semantic enrichment."""
        return self.semantic_enrichment.get("disambiguation", {})
    
    def get_normalization(self) -> Dict[str, Any]:
        """Extract normalization data from semantic enrichment."""
        return self.semantic_enrichment.get("normalization", {})

