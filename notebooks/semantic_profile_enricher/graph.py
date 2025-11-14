"""
RAZONAMIENTO DEL GRAFO MODULAR
==============================
1. parse_payload --> asegura tipado estricto del JSON y crea el punto de partida del estado.
2. build_corpus --> consolida toda la evidencia textual en un corpus normalizado y trazable.
3. disambiguate_terms --> nodo especializado en resolver polisemias, generando explicación y confianza.
4. infer_sector_and_seniority --> usa el corpus previo para puntuar sectores e inferir seniority defendible.
5. extract_implicit_competencies --> encuentra habilidades ocultas basándose en patrones semánticos.
6. build_synonym_map --> arma el mapa de sinónimos normalizados para consumo downstream.
7. assemble_output --> compone el JSON enriquecido con trazabilidad completa y taxonomías.

Outputs explainables:
- semantic_enrichment.disambiguation.terms: lista de términos ambiguos con concepto, dominio, evidencia y confianza.
- semantic_enrichment.skill_graph: combinación de skills explícitas, competencias implícitas y sinónimos normalizados.
- semantic_enrichment.sector_summary: ranking sectorial multi-subdominio + seniority estimada.
- semantic_enrichment.taxonomy_summary: proyección del perfil en familias/taxonomías reutilizables.
- audit_trail: cadena de decisiones con evidencia para depuración e IA downstream.
"""

from __future__ import annotations

from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from .models import (
    AuditEntry,
    CandidatePayload,
    DisambiguatedTerm,
    ImplicitCompetency,
    RawProfile,
    SectorPrediction,
    SeniorityAssessment,
)
from . import nodes


class EnrichmentState(TypedDict, total=False):
    """Typed LangGraph state shared across the enrichment nodes."""

    raw_input: dict[str, Any]
    payload: CandidatePayload
    profile: RawProfile
    corpus: str
    normalized_corpus: str
    sentences: list[str]
    disambiguations: list[DisambiguatedTerm]
    sector_predictions: list[SectorPrediction]
    seniority: SeniorityAssessment
    implicit_competencies: list[ImplicitCompetency]
    synonym_map: dict[str, list[str]]
    audit_trail: list[AuditEntry]
    enriched_payload: dict[str, Any]


def build_semantic_enrichment_graph() -> StateGraph:
    """Instantiate the LangGraph pipeline for semantic enrichment."""
    graph: StateGraph = StateGraph(EnrichmentState)
    graph.add_node("parse_payload", nodes.parse_payload)
    graph.add_node("build_corpus", nodes.build_corpus)
    graph.add_node("disambiguate_terms", nodes.disambiguate_terms)
    graph.add_node("infer_sector_and_seniority", nodes.infer_sector_and_seniority)
    graph.add_node("extract_implicit_competencies", nodes.extract_implicit_competencies)
    graph.add_node("build_synonym_map", nodes.build_synonym_map)
    graph.add_node("assemble_output", nodes.assemble_output)

    graph.set_entry_point("parse_payload")
    graph.add_edge("parse_payload", "build_corpus")
    graph.add_edge("build_corpus", "disambiguate_terms")
    graph.add_edge("disambiguate_terms", "infer_sector_and_seniority")
    graph.add_edge("infer_sector_and_seniority", "extract_implicit_competencies")
    graph.add_edge("extract_implicit_competencies", "build_synonym_map")
    graph.add_edge("build_synonym_map", "assemble_output")
    graph.add_edge("assemble_output", END)
    return graph

