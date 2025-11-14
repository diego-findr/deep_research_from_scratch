from __future__ import annotations

"""LangGraph node implementations for the semantic enrichment pipeline."""

from typing import Any

from . import constants
from .models import (
    AuditEntry,
    CandidatePayload,
    DisambiguatedTerm,
    DisambiguationSummary,
    EnrichedCandidate,
    ImplicitCompetency,
    RawProfile,
    SectorPrediction,
    SectorSummary,
    SemanticEnrichment,
    SeniorityAssessment,
    SkillGraph,
    TaxonomySummary,
)
from .nlp import contains_any, extract_evidence_snippet, keyword_score, normalize_text, tokenize_sentences


def _updated_audit(state: dict[str, Any], entry: AuditEntry) -> list[AuditEntry]:
    audit = list(state.get("audit_trail", []))
    audit.append(entry)
    return audit


def parse_payload(state: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize incoming candidate payload."""
    payload = CandidatePayload.model_validate(state["raw_input"])
    audit = _updated_audit(
        state,
        AuditEntry(
            step="parse_payload",
            decision="payload_validated",
            evidence=f"perfil_raw.id={payload.perfil_raw.id}",
        ),
    )
    return {"payload": payload, "profile": payload.perfil_raw, "audit_trail": audit}


def build_corpus(state: dict[str, Any]) -> dict[str, Any]:
    """Aggregate textual evidence for downstream heuristics."""
    profile: RawProfile = state["profile"]
    segments: list[str] = []
    if profile.heading:
        segments.append(profile.heading)
    if profile.description:
        segments.append(profile.description)
    for exp in profile.experiences:
        segments.append(exp.role)
        segments.append(exp.description)
        if exp.company:
            segments.append(exp.company)
    corpus = " ".join(segment for segment in segments if segment)
    sentences = tokenize_sentences(corpus)
    audit = _updated_audit(
        state,
        AuditEntry(
            step="build_corpus",
            decision="text_normalized",
            evidence=f"{len(sentences)} sentences extracted",
        ),
    )
    return {
        "corpus": corpus,
        "normalized_corpus": normalize_text(corpus),
        "sentences": sentences,
        "audit_trail": audit,
    }


def disambiguate_terms(state: dict[str, Any]) -> dict[str, Any]:
    """Resolve polysemic skills using keyword heuristics and evidence extraction."""
    corpus: str = state["normalized_corpus"]
    profile: RawProfile = state["profile"]
    disambiguations: list[DisambiguatedTerm] = []
    for skill in profile.skills:
        base = normalize_text(skill.name)
        senses = constants.AMBIGUOUS_TERMS.get(base)
        if not senses:
            continue
        sense_scores: list[tuple[dict[str, Any], float]] = []
        for sense in senses:
            positive = keyword_score(corpus, sense["keywords"])
            negative = keyword_score(corpus, sense.get("negative_keywords", []))
            score = max(0.0, positive - 0.4 * negative)
            sense_scores.append((sense, score))
        if not sense_scores:
            continue
        best_sense, best_score = max(sense_scores, key=lambda item: item[1])
        confidence = min(1.0, best_score / 3.0)
        fallback_label = "precise" if confidence >= 0.35 else "ambiguous"
        evidence = ""
        if best_sense["keywords"]:
            evidence = extract_evidence_snippet(
                corpus,
                best_sense["keywords"][0],
            )
        disambiguations.append(
            DisambiguatedTerm(
                original_term=skill.name,
                resolved_concept=best_sense["concept"],
                domain=best_sense["domain"],
                confidence=round(confidence, 2),
                evidence=evidence,
                synonyms=best_sense.get("synonyms", []),
                fallback_label=fallback_label,  # type: ignore[arg-type]
            ),
        )
    audit = _updated_audit(
        state,
        AuditEntry(
            step="disambiguate_terms",
            decision="polysemic_terms_resolved",
            evidence=f"{len(disambiguations)} ambiguous skills analyzed",
            confidence=len(disambiguations) / max(1, len(profile.skills)),
        ),
    )
    return {"disambiguations": disambiguations, "audit_trail": audit}


def infer_sector_and_seniority(state: dict[str, Any]) -> dict[str, Any]:
    """Infer probable sectors and seniority."""
    corpus: str = state["normalized_corpus"]
    profile: RawProfile = state["profile"]
    predictions: list[SectorPrediction] = []
    for sector, config in constants.SECTOR_ONTOLOGY.items():
        score = keyword_score(corpus, config["keywords"]) * config["weight"]
        if score <= 0.0:
            continue
        evidence_terms = [
            term for term in config["keywords"] if term in corpus
        ][:5]
        predictions.append(
            SectorPrediction(
                sector=sector,
                score=round(min(score, 1.0), 3),
                subdomains=config.get("subdomains", []),
                evidence_terms=evidence_terms,
            ),
        )

    years = profile.experience_years or 0.0
    chosen_assessment: SeniorityAssessment | None = None
    for rule in sorted(constants.SENIORITY_RULES, key=lambda item: item["min_years"], reverse=True):
        meets_years = years >= rule["min_years"]
        meets_keywords = contains_any(corpus, rule["keywords"])
        if not (meets_years or meets_keywords):
            continue
        score = min(1.0, (years / max(1, rule["min_years"] or 1)) * rule["weight"] if rule["min_years"] else 0.5)
        chosen_assessment = SeniorityAssessment(
            label=rule["label"],
            score=round(score, 2),
            evidence=f"years={years}, keywords_match={meets_keywords}",
        )
        break
    if chosen_assessment is None:
        chosen_assessment = SeniorityAssessment(label="junior", score=0.3, evidence="default_fallback")

    audit = _updated_audit(
        state,
        AuditEntry(
            step="infer_sector_and_seniority",
            decision="sector_seniority_estimated",
            evidence=f"predictions={len(predictions)}",
            confidence=chosen_assessment.score,
        ),
    )
    return {
        "sector_predictions": predictions,
        "seniority": chosen_assessment,
        "audit_trail": audit,
    }


def extract_implicit_competencies(state: dict[str, Any]) -> dict[str, Any]:
    """Detect implicit competencies by pattern matching sentences."""
    sentences: list[str] = state["sentences"]
    competencies: list[ImplicitCompetency] = []
    for pattern in constants.IMPLICIT_COMPETENCY_PATTERNS:
        for sentence in sentences:
            if all(keyword in sentence for keyword in map(normalize_text, pattern["keywords"])):
                competencies.append(
                    ImplicitCompetency(
                        competency=pattern["competency"],
                        type=pattern["type"],
                        level=pattern["level"],
                        source_sentence=sentence,
                    ),
                )
                break
    audit = _updated_audit(
        state,
        AuditEntry(
            step="extract_implicit_competencies",
            decision="implicit_competencies_detected",
            evidence=f"{len(competencies)} competencies inferred",
        ),
    )
    return {"implicit_competencies": competencies, "audit_trail": audit}


def build_synonym_map(state: dict[str, Any]) -> dict[str, Any]:
    """Merge normalized synonyms from static tables and disambiguation output."""
    profile: RawProfile = state["profile"]
    synonym_map: dict[str, list[str]] = {}
    for skill in profile.skills:
        normalized = normalize_text(skill.name)
        synonyms = constants.SKILL_SYNONYMS.get(normalized, [])
        if synonyms:
            synonym_map[skill.name] = sorted(set(synonyms))
    for disambiguation in state.get("disambiguations", []):
        if disambiguation.synonyms:
            synonym_map[disambiguation.original_term] = sorted(
                set(disambiguation.synonyms),
            )
    audit = _updated_audit(
        state,
        AuditEntry(
            step="build_synonym_map",
            decision="synonym_map_ready",
            evidence=f"{len(synonym_map)} skills normalized",
        ),
    )
    return {"synonym_map": synonym_map, "audit_trail": audit}


def assemble_output(state: dict[str, Any]) -> dict[str, Any]:
    """Produce the final enriched JSON payload."""
    payload: CandidatePayload = state["payload"]
    profile = payload.perfil_raw
    disambiguations = state.get("disambiguations", [])
    sector_predictions = state.get("sector_predictions", [])
    implicit_competencies = state.get("implicit_competencies", [])
    synonym_map = state.get("synonym_map", {})
    seniority = state.get("seniority")

    skill_graph = SkillGraph(
        explicit_skills=profile.skills,
        implicit_competencies=implicit_competencies,
        normalized_synonyms=synonym_map,
    )
    enrichment = SemanticEnrichment(
        disambiguation=DisambiguationSummary(terms=disambiguations),
        skill_graph=skill_graph,
        sector_summary=SectorSummary(
            predictions=sector_predictions,
            seniority=seniority,
        ),
        taxonomy_summary=TaxonomySummary(families=constants.TAXONOMY_FAMILIES),
    )

    enriched = EnrichedCandidate(
        candidato_id=payload.candidato_id,
        timestamp=payload.timestamp,
        metadata=payload.metadata,
        perfil_raw=profile,
        semantic_enrichment=enrichment,
        audit_trail=state.get("audit_trail", []),
    )
    audit = _updated_audit(
        state,
        AuditEntry(
            step="assemble_output",
            decision="payload_enriched",
            evidence="semantic_enrichment attached",
        ),
    )
    enriched.audit_trail = audit
    return {"enriched_payload": enriched.model_dump(mode="json")}

