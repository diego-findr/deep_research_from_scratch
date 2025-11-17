"""Prompt template for Salary & Compensation Agent."""

SALARY_COMPENSATION_PROMPT = """You are a Salary & Compensation Agent.

**Candidate Info:**
{candidate_info}

**Job Offer:**
{job_info}

**Evaluate:** salary alignment (if candidate expectations available).

**Output (JSON only):**
{{
  "agent": "salary_compensation",
  "score": <0-100>,
  "salary_alignment": "<within_range|below_range|above_range|unknown>",
  "candidate_expectation": "<amount or 'unknown'>",
  "offer_range": "<range>",
  "market_alignment": "<assessment>",
  "evidence": [<list>],
  "reasoning": "<explanation>",
  "red_flags": [<list>],
  "confidence": <0.0-1.0>
}}
"""

def format_salary_prompt(candidate: dict, job_offer: dict) -> str:
    """Format salary compensation prompt."""
    cand_salary = candidate.get("perfil_raw", {}).get("salary_expectation", "unknown")
    
    candidate_info = f"""
Salary Expectation: {cand_salary}
Seniority: {candidate.get('semantic_enrichment', {}).get('seniority_inference', {}).get('seniority_level', 'unknown')}
"""
    
    job_raw = job_offer.get("raw_job_posting", {})
    min_sal = job_raw.get("min_salary_range", "unknown")
    max_sal = job_raw.get("max_salary_range", "unknown")
    
    job_info = f"""
Salary Range: {min_sal} - {max_sal}
Seniority Required: {job_offer.get('semantic_enrichment', {}).get('seniority_inference', {}).get('required_seniority', 'unknown')}
Sector: {job_offer.get('semantic_enrichment', {}).get('sector_inference', {}).get('primary_sector', 'unknown')}
"""
    
    return SALARY_COMPENSATION_PROMPT.format(
        candidate_info=candidate_info.strip(),
        job_info=job_info.strip()
    )

