"""Profile Enrichment Agent Implementation.

This module implements the main profile enrichment agent that performs semantic analysis,
disambiguation, skills extraction, and profile enrichment using LangGraph.
"""

import json
from typing import Any, Dict
from pydantic import ValidationError

from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model

# Load environment variables at module level
from dotenv import load_dotenv
load_dotenv()

from profile_enrichment.state import (
    ProfileEnrichmentState,
    ContextAnalysis,
    SectorInference,
    DisambiguationResults,
    SkillsExtraction,
    CompetenciesAnalysis,
    NormalizationResults,
    SeniorityInference,
    IdealRolesInference,
    LanguageInference,
)
from profile_enrichment.prompts import (
    CONTEXT_ANALYSIS_PROMPT,
    SECTOR_INFERENCE_PROMPT,
    DISAMBIGUATION_PROMPT,
    SKILLS_EXTRACTION_PROMPT,
    COMPETENCIES_ANALYSIS_PROMPT,
    NORMALIZATION_PROMPT,
    SENIORITY_INFERENCE_PROMPT,
    IDEAL_ROLES_INFERENCE_PROMPT,
    LANGUAGE_INFERENCE_PROMPT,
)


# ===== CONFIGURATION =====

# Initialize models - Using only OpenAI models
# GPT-4.1 for all operations (structured outputs and reasoning)
structured_model = init_chat_model(model="openai:gpt-4.1")
reasoning_model = init_chat_model(model="openai:gpt-4.1")


# ===== UTILITY FUNCTIONS =====

def format_profile_data(raw_profile: Dict[str, Any]) -> str:
    """Format profile data as a readable string for prompt injection."""
    return json.dumps(raw_profile, indent=2, ensure_ascii=False)


def safe_parse_json_response(response_content: str, pydantic_model: type) -> Any:
    """
    Safely parse JSON response from LLM into Pydantic model.

    Handles both direct JSON objects and JSON wrapped in markdown code blocks.
    """
    try:
        # Try to parse as JSON directly
        if isinstance(response_content, str):
            # Remove markdown code blocks if present
            cleaned = response_content.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            data = json.loads(cleaned)
        else:
            data = response_content

        # Validate with Pydantic
        return pydantic_model.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as e:
        print(f"Error parsing response: {e}")
        print(f"Response content: {response_content[:500]}")
        raise


# ===== AGENT NODES =====

def analyze_context(state: ProfileEnrichmentState) -> Dict[str, Any]:
    """
    Analyze the profile context to extract key indicators and signals.

    This node performs initial analysis of the profile to understand the
    professional context, domain signals, and technology mentions that will
    guide downstream disambiguation.

    Returns updated state with context_analysis.
    """
    profile_data_str = format_profile_data(state["raw_profile"])

    prompt = CONTEXT_ANALYSIS_PROMPT.format(profile_data=profile_data_str)

    # Use structured output with Pydantic model
    model_with_structure = structured_model.with_structured_output(
        ContextAnalysis, method="function_calling"
    )
    response = model_with_structure.invoke(prompt)

    # Convert Pydantic model to dict for storage
    context_analysis_dict = response.model_dump()

    return {"context_analysis": json.dumps(context_analysis_dict, ensure_ascii=False)}


def infer_sector(state: ProfileEnrichmentState) -> Dict[str, Any]:
    """
    Infer the primary professional sector with confidence scoring.

    Uses the context analysis and profile data to determine the candidate's
    primary professional sector, secondary adjacent sectors, and provides
    detailed evidence and reasoning.

    Returns updated state with sector_inference.
    """
    profile_data_str = format_profile_data(state["raw_profile"])
    context_analysis = state["context_analysis"]

    prompt = SECTOR_INFERENCE_PROMPT.format(
        profile_data=profile_data_str,
        context_analysis=context_analysis,
    )

    model_with_structure = structured_model.with_structured_output(
        SectorInference, method="function_calling"
    )
    response = model_with_structure.invoke(prompt)

    sector_inference_dict = response.model_dump()

    return {"sector_inference": json.dumps(sector_inference_dict, ensure_ascii=False)}


def disambiguate_terms(state: ProfileEnrichmentState) -> Dict[str, Any]:
    """
    Disambiguate polysemantic terms in the profile.

    This is the critical node that resolves ambiguous terms like "automation",
    "Python", "Java", "React" etc. based on the inferred sector and context.

    Returns updated state with disambiguation_results.
    """
    profile_data_str = format_profile_data(state["raw_profile"])
    sector_inference = state["sector_inference"]
    context_analysis = state["context_analysis"]

    prompt = DISAMBIGUATION_PROMPT.format(
        profile_data=profile_data_str,
        sector_inference=sector_inference,
        context_analysis=context_analysis,
    )

    model_with_structure = reasoning_model.with_structured_output(
        DisambiguationResults, method="function_calling"
    )
    response = model_with_structure.invoke(prompt)

    disambiguation_dict = response.model_dump()

    return {
        "disambiguation_results": json.dumps(disambiguation_dict, ensure_ascii=False)
    }


def extract_skills(state: ProfileEnrichmentState) -> Dict[str, Any]:
    """
    Extract explicit and implicit skills from the profile.

    Extracts both skills explicitly mentioned and those that can be reliably
    inferred from experience, activities, and role descriptions.

    Returns updated state with skills_extraction.
    """
    profile_data_str = format_profile_data(state["raw_profile"])
    sector_inference = state["sector_inference"]
    disambiguation_results = state["disambiguation_results"]

    prompt = SKILLS_EXTRACTION_PROMPT.format(
        profile_data=profile_data_str,
        sector_inference=sector_inference,
        disambiguation_results=disambiguation_results,
    )

    model_with_structure = reasoning_model.with_structured_output(
        SkillsExtraction, method="function_calling"
    )
    response = model_with_structure.invoke(prompt)

    skills_dict = response.model_dump()

    return {"skills_extraction": json.dumps(skills_dict, ensure_ascii=False)}


def analyze_competencies(state: ProfileEnrichmentState) -> Dict[str, Any]:
    """
    Analyze professional competencies including soft skills and leadership.

    Identifies soft skills, functional competencies, and managerial capabilities
    based on experience descriptions and activities.

    Returns updated state with competencies_analysis.
    """
    profile_data_str = format_profile_data(state["raw_profile"])
    skills_extraction = state["skills_extraction"]

    prompt = COMPETENCIES_ANALYSIS_PROMPT.format(
        profile_data=profile_data_str,
        skills_extraction=skills_extraction,
    )

    model_with_structure = reasoning_model.with_structured_output(
        CompetenciesAnalysis, method="function_calling"
    )
    response = model_with_structure.invoke(prompt)

    competencies_dict = response.model_dump()

    return {
        "competencies_analysis": json.dumps(competencies_dict, ensure_ascii=False)
    }


def normalize_terms(state: ProfileEnrichmentState) -> Dict[str, Any]:
    """
    Create normalized synonym maps and canonical term mappings.

    Generates synonym mappings and technology taxonomy to enable better
    matching and searchability of the profile.

    Returns updated state with normalization_results.
    """
    profile_data_str = format_profile_data(state["raw_profile"])
    disambiguation_results = state["disambiguation_results"]
    skills_extraction = state["skills_extraction"]

    prompt = NORMALIZATION_PROMPT.format(
        profile_data=profile_data_str,
        disambiguation_results=disambiguation_results,
        skills_extraction=skills_extraction,
    )

    model_with_structure = structured_model.with_structured_output(
        NormalizationResults, method="function_calling"
    )
    response = model_with_structure.invoke(prompt)

    normalization_dict = response.model_dump()

    return {
        "normalization_results": json.dumps(normalization_dict, ensure_ascii=False)
    }


def infer_seniority(state: ProfileEnrichmentState) -> Dict[str, Any]:
    """
    Infer the candidate's seniority level.

    Determines professional seniority based on experience years, roles,
    responsibilities, skills, and competencies.

    Returns updated state with seniority_inference.
    """
    profile_data_str = format_profile_data(state["raw_profile"])
    skills_extraction = state["skills_extraction"]
    competencies_analysis = state["competencies_analysis"]

    prompt = SENIORITY_INFERENCE_PROMPT.format(
        profile_data=profile_data_str,
        skills_extraction=skills_extraction,
        competencies_analysis=competencies_analysis,
    )

    model_with_structure = structured_model.with_structured_output(
        SeniorityInference, method="function_calling"
    )
    response = model_with_structure.invoke(prompt)

    seniority_dict = response.model_dump()

    return {"seniority_inference": json.dumps(seniority_dict, ensure_ascii=False)}


def infer_ideal_roles(state: ProfileEnrichmentState) -> Dict[str, Any]:
    """
    Infer ideal roles for the candidate based on their career trajectory.

    Analyzes the candidate's experience with recency weighting (more weight to
    recent roles) to determine the most suitable roles they should pursue.
    Recent experience (last 2-5 years) is weighted more heavily.

    Returns updated state with ideal_roles_inference.
    """
    profile_data_str = format_profile_data(state["raw_profile"])
    
    # Parse previous analysis results
    sector_inference = json.loads(state["sector_inference"])
    seniority_inference = json.loads(state["seniority_inference"])
    skills_extraction = json.loads(state["skills_extraction"])
    competencies_analysis = json.loads(state["competencies_analysis"])
    
    # Format skills and competencies for the prompt
    all_skills = skills_extraction.get("explicit_skills", []) + skills_extraction.get("implicit_skills", [])
    key_skills = "\n".join([f"- {skill['name']} ({skill['level']})" for skill in all_skills[:15]])
    
    key_competencies = "\n".join([
        f"- {comp['competency']} ({comp['type']}, {comp['level']})" 
        for comp in competencies_analysis.get("competencies", [])[:10]
    ])

    prompt = IDEAL_ROLES_INFERENCE_PROMPT.format(
        profile_data=profile_data_str,
        sector=sector_inference.get("primary_sector", "unknown"),
        seniority_level=seniority_inference.get("seniority_level", "unknown"),
        years_experience=seniority_inference.get("years_experience_estimate", 0),
        key_skills=key_skills,
        key_competencies=key_competencies,
    )

    model_with_structure = structured_model.with_structured_output(
        IdealRolesInference, method="function_calling"
    )
    response = model_with_structure.invoke(prompt)

    ideal_roles_dict = response.model_dump()

    return {"ideal_roles_inference": json.dumps(ideal_roles_dict, ensure_ascii=False)}


def infer_languages(state: ProfileEnrichmentState) -> Dict[str, Any]:
    """
    Infer the candidate's language proficiency.

    Analyzes explicit mentions and implicit signals (location, education, companies)
    to determine languages spoken and proficiency levels.

    Returns updated state with language_inference.
    """
    profile_data_str = format_profile_data(state["raw_profile"])
    
    # Extract context for the prompt
    raw_profile = state["raw_profile"]
    sector_inference = json.loads(state["sector_inference"])
    
    # Extract location, companies, education for context
    location = f"{raw_profile.get('current_city', '')}, {raw_profile.get('current_country', '')}"
    
    companies = []
    if "experiences" in raw_profile:
        companies = [exp.get("company", "") for exp in raw_profile["experiences"] if exp.get("company")]
    
    education = []
    if "education" in raw_profile:
        education = [edu.get("school", "") for edu in raw_profile["education"]]
    
    prompt = LANGUAGE_INFERENCE_PROMPT.format(
        profile_data=profile_data_str,
        sector=sector_inference.get("primary_sector", "unknown"),
        location=location,
        companies=", ".join(companies),
        education=", ".join(education),
    )

    model_with_structure = structured_model.with_structured_output(
        LanguageInference, method="function_calling"
    )
    response = model_with_structure.invoke(prompt)

    language_dict = response.model_dump()

    return {"language_inference": json.dumps(language_dict, ensure_ascii=False)}


def assemble_enriched_profile(state: ProfileEnrichmentState) -> Dict[str, Any]:
    """
    Assemble the final enriched profile with all analysis results.

    Combines all analysis outputs into a clean, non-redundant enriched profile
    that maintains the original structure while adding semantic enrichments.

    Returns updated state with enriched_profile.
    """
    # Parse all analysis results
    context_analysis = json.loads(state["context_analysis"])
    sector_inference = json.loads(state["sector_inference"])
    disambiguation_results = json.loads(state["disambiguation_results"])
    skills_extraction = json.loads(state["skills_extraction"])
    competencies_analysis = json.loads(state["competencies_analysis"])
    normalization_results = json.loads(state["normalization_results"])
    seniority_inference = json.loads(state["seniority_inference"])
    ideal_roles_inference = json.loads(state["ideal_roles_inference"])
    language_inference = json.loads(state["language_inference"])

    # Build enriched profile structure (simplified and non-redundant)
    enriched_profile = {
        # Preserve original fields
        "candidato_id": state["candidate_id"],
        "timestamp": state["metadata"].get("timestamp"),
        "metadata": state["metadata"],
        "perfil_raw": state["raw_profile"],
        # Add semantic enrichment section
        "semantic_enrichment": {
            "version": "1.0",
            "enrichment_timestamp": state["metadata"].get("timestamp"),
            
            # High-level summary
            "key_insights": {
                "primary_sector": sector_inference["primary_sector"],
                "sector_confidence": sector_inference["confidence"],
                "seniority_level": seniority_inference["seniority_level"],
                "years_experience": seniority_inference["years_experience_estimate"],
                "total_skills_identified": len(skills_extraction["explicit_skills"])
                + len(skills_extraction["implicit_skills"]),
                "competencies_count": len(competencies_analysis["competencies"]),
                "disambiguated_terms_count": len(
                    disambiguation_results["disambiguated_terms"]
                ),
                "primary_ideal_role": ideal_roles_inference["primary_role"]["role_name"],
                "primary_role_fit_score": ideal_roles_inference["primary_role"]["fit_score"],
            },
            
            # Context information - REMOVED as it is intermediate data
            # "context": { ... },
            
            # Sector (simplified)
            "sector": {
                "primary": sector_inference["primary_sector"],
                "secondary": sector_inference.get("secondary_sectors", []),
                "confidence": sector_inference["confidence"],
                "reasoning": sector_inference["reasoning"],
            },
            
            # Seniority (simplified)
            "seniority": {
                "level": seniority_inference["seniority_level"],
                "years_experience": seniority_inference["years_experience_estimate"],
                "confidence": seniority_inference["confidence"],
                "reasoning": seniority_inference["reasoning"],
            },
            
            # Skills (clean structure)
            "skills": {
                "explicit": skills_extraction["explicit_skills"],
                "implicit": skills_extraction["implicit_skills"],
                "clusters": {
                    cluster["cluster_name"]: cluster["skills"]
                    for cluster in skills_extraction.get("skill_clusters", [])
                },
            },
            
            # Competencies (clean list)
            "competencies": competencies_analysis["competencies"],
            
            # Disambiguation (simplified map)
            "disambiguation": {
                term["original_term"]: {
                    "meaning": term["interpreted_meaning"],
                    "domain": term["domain"],
                    "confidence": term["confidence"],
                }
                for term in disambiguation_results["disambiguated_terms"]
            },
            
            # Normalization (canonical terms only)
            "canonical_terms": {
                canon["variation"]: canon["canonical"]
                for canon in normalization_results.get("canonical_terms", [])
            },
            
            # Ideal roles
            "ideal_roles": {
                "primary": ideal_roles_inference["primary_role"],
                "alternatives": ideal_roles_inference.get("alternative_roles", []),
                "career_trajectory": ideal_roles_inference["career_trajectory"],
                "recent_focus": ideal_roles_inference["recent_focus"],
                "reasoning": ideal_roles_inference["reasoning"],
            },
            
            # Languages
            "languages": language_inference["languages"],
        },
    }

    return {"enriched_profile": enriched_profile}


# ===== GRAPH CONSTRUCTION =====

def build_enrichment_graph() -> StateGraph:
    """
    Build the profile enrichment graph.

    The graph follows this flow:
    1. analyze_context: Extract key indicators and signals
    2. infer_sector: Determine primary professional sector
    3. disambiguate_terms: Resolve polysemantic terms
    4. extract_skills: Extract explicit and implicit skills
    5. analyze_competencies: Identify professional competencies
    6. normalize_terms: Create synonym maps
    7. infer_seniority: Determine seniority level
    8. infer_ideal_roles: Identify ideal roles based on career trajectory (with recency weighting)
    9. assemble_enriched_profile: Build final enriched output

    Returns compiled StateGraph ready for execution.
    """
    # Create graph builder
    graph_builder = StateGraph(ProfileEnrichmentState)

    # Add nodes
    graph_builder.add_node("analyze_context", analyze_context)
    graph_builder.add_node("infer_sector", infer_sector)
    graph_builder.add_node("disambiguate_terms", disambiguate_terms)
    graph_builder.add_node("extract_skills", extract_skills)
    graph_builder.add_node("analyze_competencies", analyze_competencies)
    graph_builder.add_node("normalize_terms", normalize_terms)
    graph_builder.add_node("infer_seniority", infer_seniority)
    graph_builder.add_node("infer_ideal_roles", infer_ideal_roles)
    graph_builder.add_node("infer_languages", infer_languages)
    graph_builder.add_node("assemble_enriched_profile", assemble_enriched_profile)

    # Add edges to define the flow
    graph_builder.add_edge(START, "analyze_context")
    graph_builder.add_edge("analyze_context", "infer_sector")
    graph_builder.add_edge("infer_sector", "disambiguate_terms")
    graph_builder.add_edge("disambiguate_terms", "extract_skills")
    graph_builder.add_edge("extract_skills", "analyze_competencies")
    graph_builder.add_edge("analyze_competencies", "normalize_terms")
    graph_builder.add_edge("normalize_terms", "infer_seniority")
    graph_builder.add_edge("infer_seniority", "infer_ideal_roles")
    graph_builder.add_edge("infer_ideal_roles", "infer_languages")
    graph_builder.add_edge("infer_languages", "assemble_enriched_profile")
    graph_builder.add_edge("assemble_enriched_profile", END)

    # Compile and return
    return graph_builder.compile()


# ===== MAIN AGENT =====

# Build the enrichment agent
enrichment_agent = build_enrichment_graph()


# ===== CONVENIENCE FUNCTION =====

def enrich_profile(
    raw_profile: Dict[str, Any],
    candidate_id: str,
    metadata: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Enrich a professional profile with semantic analysis.

    This is the main entry point for the enrichment system. It takes a raw
    profile and returns a fully enriched profile with disambiguation,
    sector inference, skills extraction, and competencies analysis.

    Args:
        raw_profile: The raw profile data to enrich
        candidate_id: Unique identifier for the candidate
        metadata: Additional metadata about the profile

    Returns:
        Enriched profile with semantic analysis results

    Example:
        >>> raw_profile = {
        ...     "full_name": "Luis Hidalgo",
        ...     "heading": "Técnico de automatización",
        ...     "skills": [{"name": "automatización", "level": "Advanced"}],
        ...     ...
        ... }
        >>> result = enrich_profile(
        ...     raw_profile=raw_profile,
        ...     candidate_id="ec142b18-befd-4f89-9f3d-98a7b53c3fr2",
        ...     metadata={"source": "linkedin_scraper_v2"}
        ... )
        >>> print(result["semantic_enrichment"]["key_insights"]["primary_sector"])
        'industrial_automation'
    """
    # Initialize state
    initial_state = {
        "raw_profile": raw_profile,
        "candidate_id": candidate_id,
        "metadata": metadata,
        "context_analysis": None,
        "sector_inference": None,
        "disambiguation_results": None,
        "skills_extraction": None,
        "competencies_analysis": None,
        "normalization_results": None,
        "seniority_inference": None,
        "ideal_roles_inference": None,
        "language_inference": None,
        "enriched_profile": None,
    }

    # Run the enrichment graph
    result = enrichment_agent.invoke(initial_state)

    return result["enriched_profile"]
