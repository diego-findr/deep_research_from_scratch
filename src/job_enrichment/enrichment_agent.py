"""Job Enrichment Agent Implementation.

This module implements the main job enrichment agent that performs semantic analysis,
skills extraction, competency inference, and job posting enrichment using LangGraph.
"""

import json
from typing import Any, Dict
from pydantic import ValidationError

from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model

# Load environment variables at module level
from dotenv import load_dotenv
load_dotenv()

try:
    from job_enrichment.state import (
        JobEnrichmentState,
        JobContextAnalysis,
        JobSectorInference,
        JobSkillsExtraction,
        JobSeniorityInference,
        JobCompetenciesAnalysis,
        IdealCandidateProfile,
        JobNormalizationResults,
    )
    from job_enrichment.prompts import (
        JOB_CONTEXT_ANALYSIS_PROMPT,
        JOB_SECTOR_INFERENCE_PROMPT,
        JOB_SKILLS_EXTRACTION_PROMPT,
        JOB_SENIORITY_INFERENCE_PROMPT,
        JOB_COMPETENCIES_ANALYSIS_PROMPT,
        JOB_IDEAL_CANDIDATE_PROMPT,
        JOB_NORMALIZATION_PROMPT,
    )
except ImportError:
    from .state import (
        JobEnrichmentState,
        JobContextAnalysis,
        JobSectorInference,
        JobSkillsExtraction,
        JobSeniorityInference,
        JobCompetenciesAnalysis,
        IdealCandidateProfile,
        JobNormalizationResults,
    )
    from .prompts import (
        JOB_CONTEXT_ANALYSIS_PROMPT,
        JOB_SECTOR_INFERENCE_PROMPT,
        JOB_SKILLS_EXTRACTION_PROMPT,
        JOB_SENIORITY_INFERENCE_PROMPT,
        JOB_COMPETENCIES_ANALYSIS_PROMPT,
        JOB_IDEAL_CANDIDATE_PROMPT,
        JOB_NORMALIZATION_PROMPT,
    )


# ===== CONFIGURATION =====

# Initialize models - Using GPT-4.1 for all operations
structured_model = init_chat_model(model="openai:gpt-4.1")
reasoning_model = init_chat_model(model="openai:gpt-4.1")


# ===== UTILITY FUNCTIONS =====

def format_job_data(raw_job: Dict[str, Any]) -> str:
    """Format job data as a readable string for prompt injection."""
    return json.dumps(raw_job, indent=2, ensure_ascii=False)


# ===== AGENT NODES =====

def analyze_job_context(state: JobEnrichmentState) -> Dict[str, Any]:
    """
    Analyze the job posting context to extract key indicators and signals.
    
    Returns updated state with context_analysis.
    """
    job_data_str = format_job_data(state["raw_job_posting"])

    prompt = JOB_CONTEXT_ANALYSIS_PROMPT.format(job_data=job_data_str)

    model_with_structure = structured_model.with_structured_output(
        JobContextAnalysis, method="function_calling"
    )
    response = model_with_structure.invoke(prompt)

    context_dict = response.model_dump()

    print("✓ Job context analyzed")
    
    return {"context_analysis": json.dumps(context_dict, ensure_ascii=False)}


def infer_job_sector(state: JobEnrichmentState) -> Dict[str, Any]:
    """
    Infer the primary sector/industry for the job posting.
    
    Returns updated state with sector_inference.
    """
    job_data_str = format_job_data(state["raw_job_posting"])
    context_analysis = state["context_analysis"]

    prompt = JOB_SECTOR_INFERENCE_PROMPT.format(
        job_data=job_data_str,
        context_analysis=context_analysis,
    )

    model_with_structure = structured_model.with_structured_output(
        JobSectorInference, method="function_calling"
    )
    response = model_with_structure.invoke(prompt)

    sector_dict = response.model_dump()

    print(f"✓ Sector inferred: {sector_dict['primary_sector']}")

    return {"sector_inference": json.dumps(sector_dict, ensure_ascii=False)}


def extract_job_skills(state: JobEnrichmentState) -> Dict[str, Any]:
    """
    Extract explicit and implicit skill requirements from job posting.
    
    Returns updated state with skills_extraction.
    """
    job_data_str = format_job_data(state["raw_job_posting"])
    context_analysis = state["context_analysis"]

    prompt = JOB_SKILLS_EXTRACTION_PROMPT.format(
        job_data=job_data_str,
        context_analysis=context_analysis,
    )

    model_with_structure = structured_model.with_structured_output(
        JobSkillsExtraction, method="function_calling"
    )
    response = model_with_structure.invoke(prompt)

    skills_dict = response.model_dump()

    total_skills = len(skills_dict.get("explicit_skills", [])) + len(skills_dict.get("implicit_skills", []))
    print(f"✓ Skills extracted: {total_skills} total")

    return {"skills_extraction": json.dumps(skills_dict, ensure_ascii=False)}


def infer_job_seniority(state: JobEnrichmentState) -> Dict[str, Any]:
    """
    Infer the required seniority level for the job.
    
    Returns updated state with seniority_inference.
    """
    job_data_str = format_job_data(state["raw_job_posting"])
    skills_extraction = state["skills_extraction"]

    prompt = JOB_SENIORITY_INFERENCE_PROMPT.format(
        job_data=job_data_str,
        skills_extraction=skills_extraction,
    )

    model_with_structure = structured_model.with_structured_output(
        JobSeniorityInference, method="function_calling"
    )
    response = model_with_structure.invoke(prompt)

    seniority_dict = response.model_dump()

    print(f"✓ Seniority inferred: {seniority_dict['required_seniority']}")

    return {"seniority_inference": json.dumps(seniority_dict, ensure_ascii=False)}


def analyze_job_competencies(state: JobEnrichmentState) -> Dict[str, Any]:
    """
    Analyze required competencies for the job.
    
    Returns updated state with competencies_analysis.
    """
    job_data_str = format_job_data(state["raw_job_posting"])
    skills_extraction = state["skills_extraction"]

    prompt = JOB_COMPETENCIES_ANALYSIS_PROMPT.format(
        job_data=job_data_str,
        skills_extraction=skills_extraction,
    )

    model_with_structure = structured_model.with_structured_output(
        JobCompetenciesAnalysis, method="function_calling"
    )
    response = model_with_structure.invoke(prompt)

    competencies_dict = response.model_dump()

    print(f"✓ Competencies analyzed: {len(competencies_dict.get('required_competencies', []))} identified")

    return {"competencies_analysis": json.dumps(competencies_dict, ensure_ascii=False)}


def define_ideal_candidate(state: JobEnrichmentState) -> Dict[str, Any]:
    """
    Define the ideal candidate profile for this job.
    
    Returns updated state with ideal_candidate_profile.
    """
    job_data_str = format_job_data(state["raw_job_posting"])
    
    # Parse previous analysis results
    sector_inference = json.loads(state["sector_inference"])
    seniority_inference = json.loads(state["seniority_inference"])
    skills_extraction = json.loads(state["skills_extraction"])
    competencies_analysis = json.loads(state["competencies_analysis"])
    
    # Format skills and competencies for the prompt
    all_skills = skills_extraction.get("explicit_skills", []) + skills_extraction.get("implicit_skills", [])
    key_skills = "\n".join([f"- {skill['name']} ({skill['importance']})" for skill in all_skills[:15]])
    
    key_competencies = "\n".join([
        f"- {comp['competency']} ({comp['type']}, {comp['importance']})" 
        for comp in competencies_analysis.get("required_competencies", [])[:10]
    ])

    prompt = JOB_IDEAL_CANDIDATE_PROMPT.format(
        job_data=job_data_str,
        sector=sector_inference.get("primary_sector", "unknown"),
        seniority=seniority_inference.get("required_seniority", "unknown"),
        years_experience=seniority_inference.get("years_experience_required", 0),
        key_skills=key_skills,
        key_competencies=key_competencies,
    )

    model_with_structure = structured_model.with_structured_output(
        IdealCandidateProfile, method="function_calling"
    )
    response = model_with_structure.invoke(prompt)

    candidate_profile_dict = response.model_dump()

    print("✓ Ideal candidate profile defined")

    return {"ideal_candidate_profile": json.dumps(candidate_profile_dict, ensure_ascii=False)}


def normalize_job_terms(state: JobEnrichmentState) -> Dict[str, Any]:
    """
    Create normalized synonym maps and canonical term mappings.
    
    Returns updated state with normalization_results.
    """
    job_data_str = format_job_data(state["raw_job_posting"])
    skills_extraction = state["skills_extraction"]

    prompt = JOB_NORMALIZATION_PROMPT.format(
        job_data=job_data_str,
        skills_extraction=skills_extraction,
    )

    model_with_structure = structured_model.with_structured_output(
        JobNormalizationResults, method="function_calling"
    )
    response = model_with_structure.invoke(prompt)

    normalization_dict = response.model_dump()

    print("✓ Terms normalized")

    return {"normalization_results": json.dumps(normalization_dict, ensure_ascii=False)}


def assemble_enriched_job(state: JobEnrichmentState) -> Dict[str, Any]:
    """
    Assemble the final enriched job posting with all analysis results.
    
    Combines all analysis outputs into a clean, non-redundant enriched job posting
    that maintains the original structure while adding semantic enrichments.
    
    Returns updated state with enriched_job_posting.
    """
    # Parse all analysis results
    context_analysis = json.loads(state["context_analysis"])
    sector_inference = json.loads(state["sector_inference"])
    skills_extraction = json.loads(state["skills_extraction"])
    seniority_inference = json.loads(state["seniority_inference"])
    competencies_analysis = json.loads(state["competencies_analysis"])
    ideal_candidate_profile = json.loads(state["ideal_candidate_profile"])
    normalization_results = json.loads(state["normalization_results"])

    # Build enriched job posting structure (simplified and non-redundant)
    enriched_job = {
        # Preserve original fields
        "job_id": state["job_id"],
        "timestamp": state["metadata"].get("timestamp"),
        "metadata": state["metadata"],
        "raw_job_posting": state["raw_job_posting"],
        # Add semantic enrichment section
        "semantic_enrichment": {
            "version": "1.0",
            "enrichment_timestamp": state["metadata"].get("timestamp"),
            
            # High-level summary
            "key_insights": {
                "primary_sector": sector_inference["primary_sector"],
                "sector_confidence": sector_inference["confidence"],
                "required_seniority": seniority_inference["required_seniority"],
                "years_experience_required": seniority_inference["years_experience_required"],
                "total_skills_identified": len(skills_extraction["explicit_skills"])
                + len(skills_extraction["implicit_skills"]),
                "required_competencies_count": len(competencies_analysis["required_competencies"]),
                "leadership_level": competencies_analysis["leadership_level"],
            },
            
            # Context information
            "context": {
                "key_indicators": context_analysis["key_indicators"],
                "domain_signals": context_analysis["domain_signals"],
                "technology_mentions": context_analysis["technology_mentions"],
            },
            
            # Sector (simplified)
            "sector": {
                "primary": sector_inference["primary_sector"],
                "secondary": sector_inference.get("secondary_sectors", []),
                "confidence": sector_inference["confidence"],
                "reasoning": sector_inference["reasoning"],
            },
            
            # Seniority (simplified)
            "seniority": {
                "required_level": seniority_inference["required_seniority"],
                "years_experience_required": seniority_inference["years_experience_required"],
                "confidence": seniority_inference["confidence"],
                "reasoning": seniority_inference["reasoning"],
            },
            
            # Skills (clean structure)
            "skills": {
                "explicit": skills_extraction["explicit_skills"],
                "implicit": skills_extraction["implicit_skills"],
                "clusters": skills_extraction.get("skill_clusters", []),
            },
            
            # Competencies (clean list)
            "competencies": competencies_analysis["required_competencies"],
            
            # Ideal candidate profile
            "ideal_candidate": {
                "background": ideal_candidate_profile["ideal_background"],
                "must_have_experience": ideal_candidate_profile["must_have_experience"],
                "preferred_experience": ideal_candidate_profile["preferred_experience"],
                "career_trajectory": ideal_candidate_profile["career_trajectory"],
                "key_differentiators": ideal_candidate_profile["key_differentiators"],
                "potential_red_flags": ideal_candidate_profile["potential_red_flags"],
                "reasoning": ideal_candidate_profile["reasoning"],
            },
            
            # Normalization (synonyms and canonical terms)
            "synonyms": {
                syn["term"]: syn["synonyms"]
                for syn in normalization_results.get("normalized_synonyms", [])
                if isinstance(syn, dict) and "term" in syn and "synonyms" in syn
            },
            "canonical_terms": {
                canon["variation"]: canon["canonical"]
                for canon in normalization_results.get("canonical_terms", [])
                if isinstance(canon, dict) and "variation" in canon and "canonical" in canon
            },
        },
    }

    print("✓ Enriched job posting assembled")

    return {"enriched_job_posting": enriched_job}


# ===== GRAPH CONSTRUCTION =====

def build_job_enrichment_graph() -> StateGraph:
    """
    Build the job enrichment graph.

    The graph follows this flow:
    1. analyze_job_context: Extract key indicators and signals
    2. infer_job_sector: Determine primary sector/industry
    3. extract_job_skills: Extract explicit and implicit skill requirements
    4. infer_job_seniority: Determine required seniority level
    5. analyze_job_competencies: Identify required competencies
    6. define_ideal_candidate: Create ideal candidate profile
    7. normalize_job_terms: Create synonym maps
    8. assemble_enriched_job: Build final enriched output

    Returns compiled StateGraph ready for execution.
    """
    # Create graph builder
    graph_builder = StateGraph(JobEnrichmentState)

    # Add nodes
    graph_builder.add_node("analyze_job_context", analyze_job_context)
    graph_builder.add_node("infer_job_sector", infer_job_sector)
    graph_builder.add_node("extract_job_skills", extract_job_skills)
    graph_builder.add_node("infer_job_seniority", infer_job_seniority)
    graph_builder.add_node("analyze_job_competencies", analyze_job_competencies)
    graph_builder.add_node("define_ideal_candidate", define_ideal_candidate)
    graph_builder.add_node("normalize_job_terms", normalize_job_terms)
    graph_builder.add_node("assemble_enriched_job", assemble_enriched_job)

    # Add edges to define the flow
    graph_builder.add_edge(START, "analyze_job_context")
    graph_builder.add_edge("analyze_job_context", "infer_job_sector")
    graph_builder.add_edge("infer_job_sector", "extract_job_skills")
    graph_builder.add_edge("extract_job_skills", "infer_job_seniority")
    graph_builder.add_edge("infer_job_seniority", "analyze_job_competencies")
    graph_builder.add_edge("analyze_job_competencies", "define_ideal_candidate")
    graph_builder.add_edge("define_ideal_candidate", "normalize_job_terms")
    graph_builder.add_edge("normalize_job_terms", "assemble_enriched_job")
    graph_builder.add_edge("assemble_enriched_job", END)

    # Compile and return
    return graph_builder.compile()


# ===== MAIN AGENT =====

# Build the enrichment agent
job_enrichment_agent = build_job_enrichment_graph()


# ===== CONVENIENCE FUNCTION =====

def enrich_job_posting(
    raw_job_posting: Dict[str, Any],
    job_id: str,
    metadata: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Enrich a job posting with semantic analysis.

    This is the main entry point for the job enrichment system. It takes a raw
    job posting and returns a fully enriched posting with sector inference,
    skills extraction, competencies analysis, and ideal candidate profile.

    Args:
        raw_job_posting: The raw job posting data to enrich
        job_id: Unique identifier for the job posting
        metadata: Additional metadata about the job posting

    Returns:
        Enriched job posting with semantic analysis results

    Example:
        >>> raw_job = {
        ...     "job_title": "Gerente de Soporte Técnico",
        ...     "company_name": "Acciona",
        ...     "description": "...",
        ...     ...
        ... }
        >>> result = enrich_job_posting(
        ...     raw_job_posting=raw_job,
        ...     job_id="be2baa17-8bc6-4d5a-ab92-2dc40a2177e2",
        ...     metadata={"source": "job_board"}
        ... )
        >>> print(result["semantic_enrichment"]["key_insights"]["primary_sector"])
        'construction'
    """
    # Initialize state
    initial_state = {
        "raw_job_posting": raw_job_posting,
        "job_id": job_id,
        "metadata": metadata,
        "context_analysis": None,
        "sector_inference": None,
        "skills_extraction": None,
        "seniority_inference": None,
        "competencies_analysis": None,
        "ideal_candidate_profile": None,
        "normalization_results": None,
        "enriched_job_posting": None,
    }

    # Run the enrichment graph
    result = job_enrichment_agent.invoke(initial_state)

    return result["enriched_job_posting"]

