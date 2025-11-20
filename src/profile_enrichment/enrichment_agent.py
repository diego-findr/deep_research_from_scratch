"""Profile Enrichment Agent Implementation.

This module implements the main profile enrichment agent that performs semantic analysis,
disambiguation, skills extraction, and profile enrichment using LangGraph.
"""

import json
from datetime import datetime
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
    raw_profile = state["raw_profile"]

    # Helper to calculate years between dates
    def calculate_years(start_date_str: str, end_date_str: str = None) -> float:
        try:
            # Assume format YYYY-MM or YYYY
            start = datetime.strptime(start_date_str[:7], "%Y-%m") if len(start_date_str) >= 7 else datetime.strptime(start_date_str, "%Y")
            if end_date_str and end_date_str.lower() != "present":
                end = datetime.strptime(end_date_str[:7], "%Y-%m") if len(end_date_str) >= 7 else datetime.strptime(end_date_str, "%Y")
            else:
                end = datetime(2025, 11, 20) # Fixed "today" as per rules
            
            diff = end - start
            return round(diff.days / 365.25, 1)
        except (ValueError, TypeError):
            return 0.0

    # 1. Metadata
    metadata = {
        "processed_at": datetime.now().isoformat(),
        "profile_version": "2.0-optimized",
        "source": state["metadata"].get("source", "unknown")
    }

    # 2. Candidate Snapshot
    location = raw_profile.get("location", "Unknown, Unknown")
    # Simple heuristic for timezone group
    timezone_group = "EMEA" # Default
    if "USA" in location or "Canada" in location or "Brazil" in location or "Argentina" in location or "Mexico" in location:
        timezone_group = "AMER"
    elif "India" in location or "China" in location or "Japan" in location or "Australia" in location:
        timezone_group = "APAC"
    
    candidate_snapshot = {
        "full_name": raw_profile.get("full_name"),
        "headline": raw_profile.get("heading"),
        "location": location,
        "timezone_group": timezone_group,
        "linkedin_url": raw_profile.get("linkedin_url"),
        "email": raw_profile.get("email")
    }

    # 3. Pre-computed Metrics
    experiences = raw_profile.get("experiences", [])
    total_experience_years = 0.0
    management_experience_years = 0.0
    is_manager = False
    
    if experiences:
        # Sort by date if possible, but usually they are reverse chronological
        # We need start date of first role.
        # Let's iterate and sum up durations or find min start date.
        # Assuming reverse chronological order
        
        # Calculate total experience from earliest start date
        earliest_start = None
        for exp in experiences:
            start_date = exp.get("start_date")
            if start_date:
                try:
                    dt = datetime.strptime(start_date[:7], "%Y-%m") if len(start_date) >= 7 else datetime.strptime(start_date, "%Y")
                    if earliest_start is None or dt < earliest_start:
                        earliest_start = dt
                except:
                    pass
        
        if earliest_start:
            total_experience_years = round((datetime(2025, 11, 20) - earliest_start).days / 365.25, 1)
        else:
            total_experience_years = float(raw_profile.get("experience_years", 0))

        # Management experience
        mgmt_keywords = ["Manager", "Lead", "Head", "Director", "Coordinator", "Gerente", "Jefe", "Líder"]
        for exp in experiences:
            role = exp.get("role", "")
            if any(kw in role for kw in mgmt_keywords):
                start = exp.get("start_date")
                end = exp.get("end_date", "Present")
                duration = calculate_years(start, end) if start else 0
                management_experience_years += duration

        # Is Manager (current or previous role)
        if experiences:
            latest_role = experiences[0].get("role", "")
            is_manager = any(kw in latest_role for kw in mgmt_keywords)
            if not is_manager and len(experiences) > 1:
                 prev_role = experiences[1].get("role", "")
                 is_manager = any(kw in prev_role for kw in mgmt_keywords)

    pre_computed_metrics = {
        "total_experience_years": total_experience_years,
        "management_experience_years": round(management_experience_years, 1),
        "is_manager": is_manager,
        "technical_depth_score": seniority_inference.get("technical_depth_score", 5) # Default to 5 if missing
    }

    # 4. Inferred Filters
    # Work authorization heuristic
    work_auth = "Unknown"
    if "Spain" in location or "España" in location:
        work_auth = "EU_Authorized"
    elif "USA" in location:
        work_auth = "US_Authorized"
    
    # Languages
    languages = []
    # Native language heuristic
    if "Spain" in location or "Argentina" in location or "Colombia" in location or "Mexico" in location:
        languages.append({"language": "Spanish", "level": "Native"})
    else:
         languages.append({"language": "English", "level": "Native"}) # Fallback
    
    # Inferred English
    if "English" not in [l["language"] for l in languages]:
        # If worked at multinational or tech, assume some English
        languages.append({"language": "English", "level": "Professional Working"})

    inferred_filters = {
        "work_authorization": work_auth,
        "languages": languages,
        "environment_fit": context_analysis.get("environment_fit", []),
        "primary_sector": sector_inference.get("primary_sector")
    }

    # 5. Stability Analysis
    current_tenure = 0.0
    if experiences:
        current = experiences[0]
        end_date = current.get("end_date")
        if not end_date or (isinstance(end_date, str) and end_date.lower() in ["present", "actualidad", ""]):
             current_tenure = calculate_years(current.get("start_date", ""), "Present")
    
    # Job hopping risk
    avg_tenure = 0
    if len(experiences) > 0:
        total_tenure_sum = 0
        count = 0
        for exp in experiences:
            s = exp.get("start_date")
            e = exp.get("end_date", "Present")
            if s:
                total_tenure_sum += calculate_years(s, e)
                count += 1
        if count > 0:
            avg_tenure = total_tenure_sum / count
    
    job_hopping_risk = "High" if avg_tenure < 1.5 and len(experiences) > 2 else "Low"

    stability_analysis = {
        "trajectory_trend": seniority_inference.get("trajectory_trend", "Flat"),
        "job_hopping_risk": job_hopping_risk,
        "current_tenure_years": current_tenure
    }

    # 6. Competency Profile
    technical_hard_skills = []
    for skill in skills_extraction.get("explicit_skills", []) + skills_extraction.get("implicit_skills", []):
        if skill["category"] == "technical":
            technical_hard_skills.append({
                "name": skill["name"],
                "level": skill["level"],
                "context": skill.get("evidence", "")[:50] + "...", # Truncate context
                "validated": skill["source"] == "explicit"
            })
    
    functional_skills = []
    for skill in skills_extraction.get("explicit_skills", []) + skills_extraction.get("implicit_skills", []):
        if skill["category"] == "functional":
             functional_skills.append(skill["name"])
    
    soft_skills_and_leadership = []
    for comp in competencies_analysis.get("competencies", []):
        if comp["type"] in ["soft", "managerial"]:
            soft_skills_and_leadership.append({
                "name": comp["competency"],
                "evidence": comp["evidence"]
            })

    competency_profile = {
        "technical_hard_skills": technical_hard_skills,
        "functional_skills": functional_skills,
        "soft_skills_and_leadership": soft_skills_and_leadership
    }

    # 7. Work History Timeline
    work_history_timeline = []
    for exp in experiences:
        start = exp.get("start_date")
        end = exp.get("end_date", "Present")
        duration = calculate_years(start, end) if start else 0
        
        work_history_timeline.append({
            "role": exp.get("role"),
            "company": exp.get("company"),
            "start_date": start,
            "end_date": end,
            "duration_years": duration,
            "description_digest": exp.get("description", "")[:200] + "..." if exp.get("description") else "No description"
        })

    # 8. Missing Data Warnings
    missing_data = []
    if not raw_profile.get("education"):
        missing_data.append("Education not specified")
    if not raw_profile.get("certifications"):
        missing_data.append("No certifications listed")
    if not raw_profile.get("languages"): # Explicit languages
        missing_data.append("Languages not explicitly listed")

    missing_data_warnings = {
        "critical_missing_fields": missing_data
    }

    # 9. Agent Decision Support
    agent_decision_support = {
        "ideal_role_match": [ideal_roles_inference["primary_role"]["role_name"]] + [r["role_name"] for r in ideal_roles_inference.get("alternative_roles", [])[:2]],
        "overqualification_risk": "High" if seniority_inference.get("seniority_level") in ["expert", "principal"] else "Low",
        "seniority_level": seniority_inference.get("seniority_level")
    }

    # Build final enriched profile
    enriched_profile = {
        "metadata": metadata,
        "candidate_snapshot": candidate_snapshot,
        "pre_computed_metrics": pre_computed_metrics,
        "inferred_filters": inferred_filters,
        "stability_analysis": stability_analysis,
        "competency_profile": competency_profile,
        "work_history_timeline": work_history_timeline,
        "missing_data_warnings": missing_data_warnings,
        "agent_decision_support": agent_decision_support
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
    graph_builder.add_edge("infer_ideal_roles", "assemble_enriched_profile")
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
        "enriched_profile": None,
    }

    # Run the enrichment graph
    result = enrichment_agent.invoke(initial_state)

    return result["enriched_profile"]
