"""Prompt template for Domain Expert Agent (dynamic)."""

DOMAIN_EXPERT_PROMPT = """You are a Domain Expert Agent specializing in the {sector} sector.

**Candidate Profile (sector-specific view):**
{candidate_info}

**Job Requirements (sector-specific view):**
{job_info}

**Your specialized evaluation:**
As a {sector} industry expert, evaluate:
1. Domain-specific technical knowledge
2. Sector-specific certifications/qualifications
3. Industry-specific project experience
4. Familiarity with sector regulations/standards
5. Specialized tooling/technology knowledge

**Output (JSON only):**
{{
  "agent": "domain_expert_{sector}",
  "sector": "{sector}",
  "score": <0-100>,
  "domain_expertise_level": "<novice|intermediate|advanced|expert>",
  "sector_specific_validations": [
    {{"aspect": "<name>", "evaluation": "<assessment>", "score": <0-100>}}
  ],
  "sector_red_flags": [<list>],
  "sector_strengths": [<list>],
  "evidence": [<list>],
  "reasoning": "<expert analysis>",
  "confidence": <0.0-1.0>
}}
"""

def format_domain_expert_prompt(candidate: dict, job_offer: dict, sector: str) -> str:
    """Format domain expert prompt for specific sector."""
    
    # Extract sector-relevant information
    cand_exp = candidate.get("perfil_raw", {}).get("experiences", [])[:3]
    job_desc = job_offer.get("raw_job_posting", {}).get("description", "")[:500]
    
    candidate_info = f"""
Sector: {candidate.get('semantic_enrichment', {}).get('sector_inference', {}).get('primary_sector', '')}
Recent Experience: {', '.join([f"{e.get('title', '')} at {e.get('company', '')}" for e in cand_exp])}
Key Skills: {', '.join([s.get('name', '') for s in candidate.get('semantic_enrichment', {}).get('skills_extraction', {}).get('explicit_skills', [])[:5]])}
"""
    
    job_info = f"""
Sector: {job_offer.get('semantic_enrichment', {}).get('sector_inference', {}).get('primary_sector', '')}
Job Description: {job_desc[:300]}...
Critical Skills: {', '.join([s.get('name', '') for s in job_offer.get('semantic_enrichment', {}).get('skills_extraction', {}).get('explicit_skills', [])[:5] if s.get('importance') == 'required'])}
"""
    
    return DOMAIN_EXPERT_PROMPT.format(
        sector=sector,
        candidate_info=candidate_info.strip(),
        job_info=job_info.strip()
    )

