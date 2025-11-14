"""
State Definitions and Pydantic Schemas for Job Enrichment System.

This module defines the state objects and structured schemas used for
the job posting enrichment workflow.
"""

import operator
from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict, Annotated
from pydantic import BaseModel, Field


# ===== STATE DEFINITIONS =====

class JobEnrichmentState(TypedDict):
    """
    State for the job enrichment pipeline containing job posting data and analysis results.
    """

    # Input data
    raw_job_posting: Dict[str, Any]
    job_id: str
    metadata: Dict[str, Any]

    # Intermediate analysis results
    context_analysis: Optional[str]
    sector_inference: Optional[str]
    skills_extraction: Optional[str]
    seniority_inference: Optional[str]
    competencies_analysis: Optional[str]
    ideal_candidate_profile: Optional[str]
    normalization_results: Optional[str]

    # Final enriched output
    enriched_job_posting: Optional[Dict[str, Any]]


# ===== STRUCTURED OUTPUT SCHEMAS =====

class JobContextAnalysis(BaseModel):
    """Schema for initial context analysis from job posting."""

    key_indicators: List[str] = Field(
        description="Key indicators extracted from job posting (company, role level, responsibilities)",
    )
    domain_signals: List[str] = Field(
        description="Signals indicating the professional domain and industry",
    )
    technology_mentions: List[str] = Field(
        description="All technology and tool mentions found in job posting",
    )
    responsibility_patterns: List[str] = Field(
        description="Patterns in responsibilities (leadership, technical, strategic)",
    )
    company_context: str = Field(
        description="Context about the company and its industry",
    )


class JobSectorInference(BaseModel):
    """Schema for sector/industry inference for job posting."""

    primary_sector: str = Field(
        description="Primary sector/industry (e.g., 'construction', 'renewable_energy', 'tech')",
    )
    secondary_sectors: List[str] = Field(
        description="Secondary/adjacent sectors",
    )
    confidence: float = Field(
        description="Confidence score 0.0-1.0 for primary sector inference",
    )
    evidence: List[str] = Field(
        description="Specific evidence from job posting supporting sector inference",
    )
    reasoning: str = Field(
        description="Explanation of sector inference",
    )


class JobSkill(BaseModel):
    """Schema for a skill required in the job."""

    name: str = Field(description="Skill name")
    category: str = Field(
        description="Category: 'technical', 'soft', 'functional', 'domain_specific'",
    )
    importance: str = Field(
        description="Importance: 'required', 'preferred', 'nice_to_have'",
    )
    source: str = Field(
        description="Source: 'explicit' (stated) or 'implicit' (inferred from responsibilities)",
    )
    evidence: str = Field(
        description="Evidence from job posting for this skill requirement",
    )


class JobSkillsExtraction(BaseModel):
    """Schema for skills extraction from job posting."""

    explicit_skills: List[JobSkill] = Field(
        description="Skills explicitly mentioned in the job posting",
    )
    implicit_skills: List[JobSkill] = Field(
        description="Skills inferred from responsibilities and context",
    )
    skill_clusters: List[Dict[str, Any]] = Field(
        description="Related skills grouped by domain/category",
        default_factory=list,
    )


class JobSeniorityInference(BaseModel):
    """Schema for required seniority level inference."""

    required_seniority: str = Field(
        description="Required seniority: 'junior', 'mid', 'senior', 'lead', 'principal', 'executive'",
    )
    confidence: float = Field(
        description="Confidence score 0.0-1.0",
    )
    evidence: List[str] = Field(
        description="Evidence supporting seniority requirement",
    )
    years_experience_required: int = Field(
        description="Required years of experience stated or inferred",
    )
    reasoning: str = Field(
        description="Explanation of seniority determination",
    )


class JobCompetency(BaseModel):
    """Schema for a competency required in the job."""

    competency: str = Field(
        description="Competency name (e.g., 'team_leadership', 'strategic_planning')",
    )
    type: str = Field(
        description="Type: 'soft', 'functional', 'managerial', 'strategic'",
    )
    importance: str = Field(
        description="Importance: 'required', 'preferred', 'nice_to_have'",
    )
    evidence: str = Field(
        description="Specific evidence from job posting",
    )


class JobCompetenciesAnalysis(BaseModel):
    """Schema for competencies required for the job."""

    required_competencies: List[JobCompetency] = Field(
        description="All required competencies",
    )
    leadership_level: str = Field(
        description="Leadership level required: 'individual_contributor', 'team_lead', 'manager', 'director', 'executive'",
    )
    autonomy_level: str = Field(
        description="Expected autonomy level: 'supervised', 'autonomous', 'independent_leader'",
    )
    collaboration_scope: str = Field(
        description="Collaboration scope: 'team', 'cross_functional', 'organizational', 'external'",
    )


class IdealCandidateProfile(BaseModel):
    """Schema for ideal candidate profile for this job."""

    ideal_background: str = Field(
        description="Description of ideal professional background",
    )
    must_have_experience: List[str] = Field(
        description="Must-have experience areas",
    )
    preferred_experience: List[str] = Field(
        description="Preferred but not required experience",
    )
    career_trajectory: str = Field(
        description="Typical career trajectory that would lead to this role",
    )
    key_differentiators: List[str] = Field(
        description="Key factors that would make a candidate stand out",
    )
    potential_red_flags: List[str] = Field(
        description="Potential concerns or mismatches to watch for",
    )
    reasoning: str = Field(
        description="Overall reasoning for ideal candidate profile",
    )


class JobNormalizationResults(BaseModel):
    """Schema for term normalization in job posting."""

    normalized_synonyms: List[Dict[str, Any]] = Field(
        description="Synonym maps for key terms",
        default_factory=list,
    )
    canonical_terms: List[Dict[str, Any]] = Field(
        description="Mapping from variations to canonical term",
        default_factory=list,
    )
    technology_taxonomy: List[Dict[str, Any]] = Field(
        description="Technologies grouped by category",
        default_factory=list,
    )

