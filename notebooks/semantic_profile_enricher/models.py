from __future__ import annotations

"""Typed schemas supporting semantic enrichment workflow."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class SkillEntry(BaseModel):
    """Skill declared by the candidate."""

    name: str
    level: str | None = None


class ExperienceEntry(BaseModel):
    """Work experience with optional description."""

    role: str
    description: str
    company: str | None = None


class RawProfile(BaseModel):
    """Raw candidate payload extracted from the source."""

    id: str
    full_name: str
    heading: str | None = None
    description: str | None = None
    experience_years: float | None = None
    skills: list[SkillEntry] = Field(default_factory=list)
    experiences: list[ExperienceEntry] = Field(default_factory=list)


class CandidatePayload(BaseModel):
    """Top-level candidate JSON envelope."""

    candidato_id: str
    timestamp: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)
    perfil_raw: RawProfile


class DisambiguatedTerm(BaseModel):
    """Result of polysemic skill disambiguation."""

    original_term: str
    resolved_concept: str
    domain: str
    confidence: float
    evidence: str
    synonyms: list[str] = Field(default_factory=list)
    fallback_label: Literal["precise", "ambiguous"] = "precise"


class SectorPrediction(BaseModel):
    """Sector inference with supporting evidence."""

    sector: str
    score: float
    subdomains: list[str]
    evidence_terms: list[str] = Field(default_factory=list)


class SeniorityAssessment(BaseModel):
    """Estimated seniority band."""

    label: Literal["junior", "mid", "senior"]
    score: float
    evidence: str


class ImplicitCompetency(BaseModel):
    """Competencies inferred indirectly."""

    competency: str
    type: Literal["functional", "technical", "soft"]
    level: str
    source_sentence: str


class SkillGraph(BaseModel):
    """Structured aggregation of skills."""

    explicit_skills: list[SkillEntry] = Field(default_factory=list)
    implicit_competencies: list[ImplicitCompetency] = Field(default_factory=list)
    normalized_synonyms: dict[str, list[str]] = Field(default_factory=dict)


class DisambiguationSummary(BaseModel):
    """Container for disambiguation insights."""

    terms: list[DisambiguatedTerm] = Field(default_factory=list)


class SectorSummary(BaseModel):
    """Container for sector inference."""

    predictions: list[SectorPrediction] = Field(default_factory=list)
    seniority: SeniorityAssessment | None = None


class TaxonomySummary(BaseModel):
    """Higher-level taxonomies that downstream systems can use."""

    families: dict[str, Any] = Field(default_factory=dict)


class SemanticEnrichment(BaseModel):
    """Aggregate structure added to the enriched JSON."""

    disambiguation: DisambiguationSummary
    skill_graph: SkillGraph
    sector_summary: SectorSummary
    taxonomy_summary: TaxonomySummary


class AuditEntry(BaseModel):
    """Traceability log for enrichment decisions."""

    step: str
    decision: str
    evidence: str
    confidence: float | None = None


class EnrichedCandidate(BaseModel):
    """Final enriched payload mirroring the original JSON interface."""

    candidato_id: str
    timestamp: datetime
    metadata: dict[str, Any]
    perfil_raw: RawProfile
    semantic_enrichment: SemanticEnrichment
    audit_trail: list[AuditEntry] = Field(default_factory=list)

