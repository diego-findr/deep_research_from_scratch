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
    MiscEnrichment,
    EducationInference,
    SkillsCuration,
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
    MISC_ENRICHMENT_PROMPT,
    EDUCATION_INFERENCE_PROMPT,
    SKILLS_CURATION_PROMPT,
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


def calculate_stability_metrics(experiences: list) -> Dict[str, Any]:
    """Calculate career stability metrics from experience list."""
    if not experiences:
        return {
            "average_tenure_years": 0.0,
            "roles_count": 0,
            "companies_count": 0,
            "job_hopping_risk": "unknown"
        }

    # Sort experiences by start date if possible, but for now just count
    # Assuming standard format with start_date
    
    # Calculate durations (simplified)
    # In a real system, we'd parse ISO dates properly.
    # Here we just count items for now as a placeholder or use simple year math if available.
    # Let's assume the LLM or pre-processing handles date parsing, but here we'll just return counts
    # and a mock tenure if we can't parse.
    
    # Actually, let's try to parse years if they exist in start_date "YYYY-MM-DD"
    import datetime
    
    total_years = 0.0
    valid_durations = 0
    
    for exp in experiences:
        start = exp.get("start_date")
        end = exp.get("end_date")
        
        if start:
            try:
                start_dt = datetime.datetime.fromisoformat(start.replace("Z", "+00:00")).date()
                end_dt = datetime.date.today()
                if end:
                    end_dt = datetime.datetime.fromisoformat(end.replace("Z", "+00:00")).date()
                
                duration_days = (end_dt - start_dt).days
                years = duration_days / 365.25
                total_years += years
                valid_durations += 1
            except (ValueError, TypeError):
                continue

    avg_tenure = round(total_years / valid_durations, 1) if valid_durations > 0 else 0.0
    
    risk = "low"
    if avg_tenure < 1.5 and valid_durations > 2:
        risk = "high"
    elif avg_tenure < 3.0:
        risk = "medium"
        
    return {
        "average_tenure_years": avg_tenure,
        "roles_count": len(experiences),
        "companies_count": len(set(e.get("company", "") for e in experiences if e.get("company"))),
        "job_hopping_risk": risk
    }


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


def infer_misc_enrichment(state: ProfileEnrichmentState) -> Dict[str, Any]:
    """
    Infer miscellaneous enrichment details (credentials, work environment).
    """
    profile_data_str = format_profile_data(state["raw_profile"])
    sector_inference = json.loads(state["sector_inference"])
    raw_profile = state["raw_profile"]
    
    location = f"{raw_profile.get('current_city', '')}, {raw_profile.get('current_country', '')}"
    
    prompt = MISC_ENRICHMENT_PROMPT.format(
        profile_data=profile_data_str,
        sector=sector_inference.get("primary_sector", "unknown"),
        location=location,
    )

    model_with_structure = structured_model.with_structured_output(
        MiscEnrichment, method="function_calling"
    )
    response = model_with_structure.invoke(prompt)

    misc_dict = response.model_dump()

    return {"misc_enrichment": json.dumps(misc_dict, ensure_ascii=False)}


def infer_education(state: ProfileEnrichmentState) -> Dict[str, Any]:
    """
    Infer and structure education using LLM.
    """
    profile_data_str = format_profile_data(state["raw_profile"])
    sector_inference = json.loads(state["sector_inference"])
    raw_profile = state["raw_profile"]
    
    current_role = raw_profile.get("heading", "Unknown")
    
    prompt = EDUCATION_INFERENCE_PROMPT.format(
        profile_data=profile_data_str,
        sector=sector_inference.get("primary_sector", "unknown"),
        current_role=current_role,
    )

    model_with_structure = structured_model.with_structured_output(
        EducationInference, method="function_calling"
    )
    response = model_with_structure.invoke(prompt)

    education_dict = response.model_dump()

    return {"education_inference": json.dumps(education_dict, ensure_ascii=False)}


def curate_skills(state: ProfileEnrichmentState) -> Dict[str, Any]:
    """
    Curate top skills using LLM instead of mechanical filtering.
    """
    skills_extraction = json.loads(state["skills_extraction"])
    sector_inference = json.loads(state["sector_inference"])
    seniority_inference = json.loads(state["seniority_inference"])
    ideal_roles_inference = json.loads(state["ideal_roles_inference"])
    raw_profile = state["raw_profile"]
    
    # Prepare all skills for LLM curation
    all_skills = []
    for skill in skills_extraction.get("explicit_skills", []):
        all_skills.append({
            "name": skill["name"],
            "type": skill["category"],
            "level": skill["level"],
            "source": "explicit",
            "confidence": skill["confidence"]
        })
    
    for skill in skills_extraction.get("implicit_skills", []):
        if not any(s["name"] == skill["name"] for s in all_skills):
            all_skills.append({
                "name": skill["name"],
                "type": skill["category"],
                "level": skill["level"],
                "source": "implicit",
                "confidence": skill["confidence"]
            })
    
    prompt = SKILLS_CURATION_PROMPT.format(
        current_role=raw_profile.get("heading", "Unknown"),
        sector=sector_inference.get("primary_sector", "unknown"),
        seniority=seniority_inference.get("seniority_level", "unknown"),
        career_trajectory=ideal_roles_inference.get("career_trajectory", "Unknown"),
        all_skills=json.dumps(all_skills, indent=2, ensure_ascii=False)
    )

    model_with_structure = structured_model.with_structured_output(
        SkillsCuration, method="function_calling"
    )
    response = model_with_structure.invoke(prompt)

    curation_dict = response.model_dump()

    return {"skills_curation": json.dumps(curation_dict, ensure_ascii=False)}


def assemble_enriched_profile(state: ProfileEnrichmentState) -> Dict[str, Any]:
    """
    Assemble the final enriched profile with all analysis results.
    
    OPTIMIZED OUTPUT FORMAT:
    - Removes redundant fields (disambiguation, canonical_terms, raw_profile).
    - Unifies skills into a single matrix.
    - Adds stability metrics and inferred credentials.
    """
    # Parse all analysis results
    # context_analysis = json.loads(state["context_analysis"]) # Not used in final output
    sector_inference = json.loads(state["sector_inference"])
    # disambiguation_results = json.loads(state["disambiguation_results"]) # Pruned
    skills_extraction = json.loads(state["skills_extraction"])
    competencies_analysis = json.loads(state["competencies_analysis"])
    # normalization_results = json.loads(state["normalization_results"]) # Pruned
    seniority_inference = json.loads(state["seniority_inference"])
    ideal_roles_inference = json.loads(state["ideal_roles_inference"])
    language_inference = json.loads(state["language_inference"])
    misc_enrichment = json.loads(state["misc_enrichment"])
    education_inference = json.loads(state["education_inference"])
    skills_curation = json.loads(state["skills_curation"])

    # Calculate stability metrics
    stability = calculate_stability_metrics(state["raw_profile"].get("experiences", []))
    
    # FILTER: Keep only top competencies (senior-level prioritized)
    competencies = competencies_analysis["competencies"]
    senior_competencies = [c for c in competencies if c.get("level") in ["senior", "lead"]]
    other_competencies = [c for c in competencies if c.get("level") not in ["senior", "lead"]]
    
    # Keep top 8 competencies (prioritize senior)
    top_competencies = senior_competencies[:6] + other_competencies[:2]

    # Build enriched profile structure (Optimized)
    enriched_profile = {
        "candidate_id": state["candidate_id"],
        "enrichment_version": "2.0-optimized",
        "timestamp": state["metadata"].get("timestamp"),
        
        # 1. Core Profile Identity
        "identity": {
            "full_name": state["raw_profile"].get("full_name"),
            "current_role": state["raw_profile"].get("heading"),
            "location": f"{state['raw_profile'].get('current_city', '')}, {state['raw_profile'].get('current_country', '')}",
            "sector": sector_inference["primary_sector"],
            "seniority": seniority_inference["seniority_level"],
            "years_experience": seniority_inference["years_experience_estimate"],
        },
        
        # 2. Career Analysis (NO DUPLICATE HISTORY)
        "career_trajectory": {
            "summary": ideal_roles_inference["career_trajectory"],
            "recent_focus": ideal_roles_inference["recent_focus"],
            "stability_metrics": stability
            # Removed: "history" - already in raw profile
        },
        
        # 2b. Education (VALUE-ADDED ONLY)
        "education": {
            "highest_degree": education_inference.get("highest_degree"),
            "level_summary": education_inference.get("education_level_summary", "Unknown")
            # Removed: "all_education" - already in raw profile
        },
        
        # 3. Skills & Competencies (LLM-CURATED)
        "top_skills": skills_curation.get("top_skills", []),  # LLM-selected skills
        "top_competencies": top_competencies,  # Top 8 competencies only
        "languages": language_inference["languages"],
        
        # 4. Inferred Context (New)
        "inferred_context": {
            "credentials": misc_enrichment["inferred_credentials"],
            "work_environment": misc_enrichment["work_environment"],
        },
        
        # 5. Matching Intelligence
        "matching_intelligence": {
            "ideal_role": ideal_roles_inference["primary_role"],
            "alternative_roles": ideal_roles_inference.get("alternative_roles", []),
            "sector_fit_reasoning": sector_inference["reasoning"]
        }
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
    graph_builder.add_node("infer_misc_enrichment", infer_misc_enrichment)
    graph_builder.add_node("infer_education", infer_education)
    graph_builder.add_node("curate_skills", curate_skills)
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
    graph_builder.add_edge("infer_languages", "infer_misc_enrichment")
    graph_builder.add_edge("infer_misc_enrichment", "infer_education")
    graph_builder.add_edge("infer_education", "curate_skills")
    graph_builder.add_edge("curate_skills", "assemble_enriched_profile")
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
        "misc_enrichment": None,
        "education_inference": None,
        "skills_curation": None,
        "enriched_profile": None,
    }

    # Run the enrichment graph
    result = enrichment_agent.invoke(initial_state)

    return result["enriched_profile"]
