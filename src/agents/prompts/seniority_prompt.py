"""Prompt template for Seniority Calibration Agent."""

SENIORITY_CALIBRATION_PROMPT = """You are a Seniority Calibration Agent.

**Candidate Seniority:**
{candidate_seniority}

**Job Seniority Requirements:**
{job_seniority}

**Evaluate:**
1. Seniority level match (junior/mid/senior/lead/principal)
2. Years of experience alignment
3. Over/under-qualification risks
4. Career trajectory compatibility

**Score:** 90-100 exact match, 70-89 acceptable range, <70 mismatch

**Output (JSON only):**
{{
  "agent": "seniority_calibration",
  "score": <0-100>,
  "seniority_match": "<exact_match|acceptable_range|over_qualified|under_qualified>",
  "candidate_seniority": "<level>",
  "required_seniority": "<level>",
  "years_gap": <integer>,
  "over_qualification_risk": <boolean>,
  "under_qualification_risk": <boolean>,
  "career_trajectory_alignment": "<strong|moderate|weak>",
  "evidence": [<list>],
  "reasoning": "<explanation>",
  "red_flags": [<list>],
  "confidence": <0.0-1.0>
}}
"""

def format_seniority_prompt(candidate: dict, job_offer: dict) -> str:
    """Format seniority calibration prompt."""
    cand_sen = candidate.get("semantic_enrichment", {}).get("seniority_inference", {})
    job_sen = job_offer.get("semantic_enrichment", {}).get("seniority_inference", {})
    
    candidate_seniority = f"""
Level: {cand_sen.get('seniority_level', 'unknown')}
Years Experience: {cand_sen.get('years_experience_estimate', 'unknown')}
Confidence: {cand_sen.get('confidence', 0.0)}
Evidence: {', '.join(cand_sen.get('evidence', [])[:3])}
"""
    
    job_seniority = f"""
Required Level: {job_sen.get('required_seniority', 'unknown')}
Min Years Required: {job_sen.get('years_experience_required', 'unknown')}
Confidence: {job_sen.get('confidence', 0.0)}
"""
    
    return SENIORITY_CALIBRATION_PROMPT.format(
        candidate_seniority=candidate_seniority.strip(),
        job_seniority=job_seniority.strip()
    )

