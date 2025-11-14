"""
State Definitions and Pydantic Schemas for Profile Enrichment System.

This module defines the state objects and structured schemas used for
the profile enrichment workflow, including profile state management and output schemas.
"""

import operator
from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict, Annotated
from pydantic import BaseModel, Field


# ===== STATE DEFINITIONS =====

class ProfileEnrichmentState(TypedDict):
    """
    State for the profile enrichment pipeline containing profile data and analysis results.

    This state tracks the original profile, intermediate analysis results,
    and final enriched output throughout the enrichment process.
    """

    # Input data
    raw_profile: Dict[str, Any]
    candidate_id: str
    metadata: Dict[str, Any]

    # Intermediate analysis results
    context_analysis: Optional[str]
    sector_inference: Optional[str]
    disambiguation_results: Optional[str]
    skills_extraction: Optional[str]
    competencies_analysis: Optional[str]
    normalization_results: Optional[str]
    seniority_inference: Optional[str]

    # Final enriched output
    enriched_profile: Optional[Dict[str, Any]]


# ===== STRUCTURED OUTPUT SCHEMAS =====

class ContextAnalysis(BaseModel):
    """Schema for initial context analysis from profile data."""

    key_indicators: List[str] = Field(
        description="Key indicators extracted from profile (companies, roles, technologies, activities)",
    )
    domain_signals: List[str] = Field(
        description="Signals that indicate professional domain (e.g., 'plant desalination', 'SCADA systems')",
    )
    technology_mentions: List[str] = Field(
        description="All technology and tool mentions found in profile",
    )
    activity_patterns: List[str] = Field(
        description="Patterns in activities and responsibilities",
    )
    language_context: str = Field(
        description="Overall linguistic and professional context",
    )


class SectorInference(BaseModel):
    """Schema for sector/domain inference with confidence scoring."""

    primary_sector: str = Field(
        description="Primary professional sector inferred (e.g., 'industrial_automation', 'software_development')",
    )
    secondary_sectors: List[str] = Field(
        description="Secondary/adjacent sectors the candidate could operate in",
    )
    confidence: float = Field(
        description="Confidence score 0.0-1.0 for primary sector inference",
    )
    evidence: List[str] = Field(
        description="Specific evidence from profile supporting sector inference",
    )
    reasoning: str = Field(
        description="Explanation of how sector was inferred",
    )


class DisambiguatedTerm(BaseModel):
    """Schema for a single disambiguated term."""

    original_term: str = Field(
        description="Original term from profile",
    )
    interpreted_meaning: str = Field(
        description="Disambiguated meaning in professional context",
    )
    domain: str = Field(
        description="Professional domain this term belongs to",
    )
    confidence: float = Field(
        description="Confidence score 0.0-1.0 for disambiguation",
    )
    evidence: str = Field(
        description="Textual evidence from profile supporting this interpretation",
    )
    alternative_meanings_rejected: List[str] = Field(
        description="Other possible meanings that were ruled out",
    )


class DisambiguationResults(BaseModel):
    """Schema for complete disambiguation analysis."""

    disambiguated_terms: List[DisambiguatedTerm] = Field(
        description="All disambiguated terms from profile",
    )
    summary: str = Field(
        description="Overall summary of disambiguation process",
    )


class Skill(BaseModel):
    """Schema for a single skill with metadata."""

    name: str = Field(description="Skill name")
    category: str = Field(
        description="Category: 'technical', 'soft', 'functional', 'domain_specific'",
    )
    level: str = Field(
        description="Proficiency level: 'novice', 'intermediate', 'advanced', 'expert'",
    )
    source: str = Field(
        description="Source: 'explicit' (stated) or 'implicit' (inferred)",
    )
    evidence: str = Field(
        description="Evidence from profile supporting this skill",
    )
    confidence: float = Field(
        description="Confidence score 0.0-1.0 for skill inference",
    )


class SkillCluster(BaseModel):
    """Schema for a skill cluster."""

    cluster_name: str = Field(description="Name of the skill cluster")
    skills: List[str] = Field(description="List of skills in this cluster")


class SkillsExtraction(BaseModel):
    """Schema for comprehensive skills extraction."""

    explicit_skills: List[Skill] = Field(
        description="Skills explicitly mentioned in profile",
    )
    implicit_skills: List[Skill] = Field(
        description="Skills inferred from experience and activities",
    )
    skill_clusters: List[SkillCluster] = Field(
        description="Related skills grouped by domain/category",
        default_factory=list,
    )


class Competency(BaseModel):
    """Schema for a single competency (soft skill or professional capability)."""

    competency: str = Field(
        description="Competency name (e.g., 'team_leadership', 'project_management')",
    )
    type: str = Field(
        description="Type: 'soft', 'functional', 'managerial'",
    )
    level: str = Field(
        description="Level: 'junior', 'mid', 'senior', 'expert'",
    )
    source: str = Field(
        description="Source context (e.g., 'experience', 'project', 'role')",
    )
    evidence: str = Field(
        description="Specific evidence from profile",
    )


class CompetenciesAnalysis(BaseModel):
    """Schema for competencies and soft skills analysis."""

    competencies: List[Competency] = Field(
        description="All inferred competencies",
    )
    leadership_indicators: List[str] = Field(
        description="Evidence of leadership and management experience",
    )
    collaboration_indicators: List[str] = Field(
        description="Evidence of teamwork and collaboration",
    )


class SynonymMap(BaseModel):
    """Schema for synonym mapping."""

    term: str = Field(description="Primary term")
    synonyms: List[str] = Field(description="List of synonym variations")


class CanonicalMapping(BaseModel):
    """Schema for canonical term mapping."""

    variation: str = Field(description="Term variation")
    canonical: str = Field(description="Canonical term")


class TechnologyCategory(BaseModel):
    """Schema for technology taxonomy category."""

    category: str = Field(description="Category name")
    technologies: List[str] = Field(description="Technologies in this category")


class NormalizationResults(BaseModel):
    """Schema for term normalization and synonym mapping."""

    normalized_synonyms: List[SynonymMap] = Field(
        description="Synonym maps for key terms (e.g., 'React': ['React', 'React.js', 'ReactJS'])",
        default_factory=list,
    )
    canonical_terms: List[CanonicalMapping] = Field(
        description="Mapping from variations to canonical term",
        default_factory=list,
    )
    technology_taxonomy: List[TechnologyCategory] = Field(
        description="Technology grouped by category",
        default_factory=list,
    )


class SeniorityInference(BaseModel):
    """Schema for seniority level inference."""

    seniority_level: str = Field(
        description="Inferred seniority: 'junior', 'mid', 'senior', 'lead', 'principal', 'expert'",
    )
    confidence: float = Field(
        description="Confidence score 0.0-1.0",
    )
    evidence: List[str] = Field(
        description="Evidence supporting seniority assessment",
    )
    years_experience_estimate: int = Field(
        description="Estimated years of relevant experience",
    )
    reasoning: str = Field(
        description="Explanation of seniority determination",
    )
