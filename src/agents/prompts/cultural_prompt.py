"""Prompt template for Cultural & Soft Fit Agent."""

CULTURAL_SOFT_FIT_PROMPT = """You are a Cultural & Soft Fit Agent.

**Candidate Profile:**
{candidate_info}

**Job Requirements:**
{job_requirements}

**Evaluate:**
1. Language requirements (mandatory vs optional)
2. Location compatibility and remote work preferences
3. Soft skills assessment
4. Cultural adaptability

**Output (JSON only):**
{{
  "agent": "cultural_soft_fit",
  "score": <0-100>,
  "language_compliance": <boolean>,
  "missing_mandatory_languages": [<list>],
  "location_compatibility": "<full_match|partial_match|mismatch>",
  "remote_preference_match": <boolean>,
  "soft_skills_evaluation": [{{"skill": "<name>", "candidate_level": "<level>", "importance": "<high|medium|low>", "match": "<strong|moderate|weak>"}}],
  "cultural_adaptability": "<high|medium|low>",
  "evidence": [<list>],
  "reasoning": "<explanation>",
  "red_flags": [<list>],
  "confidence": <0.0-1.0>
}}
"""

def format_cultural_prompt(candidate: dict, job_offer: dict) -> str:
    """Format cultural & soft fit prompt."""
    cand_raw = candidate.get("perfil_raw", {})
    job_raw = job_offer.get("raw_job_posting", {})
    
    candidate_info = f"""
Languages: {', '.join([f"{lang.get('language', '')} ({lang.get('proficiency', 'unknown')})" for lang in cand_raw.get('languages', [])])}
Location: {cand_raw.get('location', 'unknown')}
Remote Preference: {cand_raw.get('remote_preference', 'unknown')}
Soft Skills: {', '.join([c.get('name', '') for c in candidate.get('semantic_enrichment', {}).get('competencies_analysis', {}).get('competencies', []) if c.get('type') == 'soft'][:5])}
"""
    
    job_requirements = f"""
Mandatory Languages: {', '.join(job_raw.get('mandatory_languages', []))}
Optional Languages: {', '.join(job_raw.get('optional_languages', []))}
Locations: {', '.join(job_raw.get('locations', []))}
Remote Amount: {job_raw.get('remote_amount', 'unknown')}
Required Soft Skills: {', '.join([c.get('name', '') for c in job_offer.get('semantic_enrichment', {}).get('competencies_analysis', {}).get('required_competencies', []) if c.get('type') == 'soft'][:5])}
"""
    
    return CULTURAL_SOFT_FIT_PROMPT.format(
        candidate_info=candidate_info.strip(),
        job_requirements=job_requirements.strip()
    )

