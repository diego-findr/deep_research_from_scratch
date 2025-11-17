"""Prompt template for Experience Relevance Agent."""

EXPERIENCE_RELEVANCE_PROMPT = """You are an Experience Relevance Agent.

**Candidate Experience:**
{candidate_experience}

**Job Experience Requirements:**
{job_requirements}

**Evaluate:**
1. Match with must-have experience requirements
2. Match with preferred experience
3. Recency of relevant experience (last 2-3 years weighted higher)
4. Career progression and growth trajectory
5. Gaps or inconsistencies

**Output (JSON only):**
{{
  "agent": "experience_relevance",
  "score": <0-100>,
  "must_have_experience_match": <0.0-1.0>,
  "preferred_experience_match": <0.0-1.0>,
  "experience_depth": "<shallow|moderate|strong|deep>",
  "recency_score": <0.0-1.0>,
  "experience_highlights": [<list>],
  "experience_gaps": [<list>],
  "career_progression": "<negative|stagnant|positive|strong>",
  "evidence": [<list>],
  "reasoning": "<explanation>",
  "red_flags": [<list>],
  "confidence": <0.0-1.0>
}}
"""

def format_experience_prompt(candidate: dict, job_offer: dict) -> str:
    """Format experience relevance prompt."""
    experiences = candidate.get("perfil_raw", {}).get("experiences", [])[:5]
    
    candidate_experience = f"""
Total Years: {candidate.get('semantic_enrichment', {}).get('seniority_inference', {}).get('years_experience_estimate', 'unknown')}
Recent Roles:
{chr(10).join([f"- {e.get('title', '')} at {e.get('company', '')} ({e.get('duration', 'unknown')})" for e in experiences])}
"""
    
    ideal_profile = job_offer.get("semantic_enrichment", {}).get("ideal_candidate_profile", {})
    
    job_requirements = f"""
Must-Have Experience:
{chr(10).join([f"- {exp}" for exp in ideal_profile.get('must_have_experience', [])[:5]])}

Preferred Experience:
{chr(10).join([f"- {exp}" for exp in ideal_profile.get('preferred_experience', [])[:5]])}

Expected Career Trajectory:
{ideal_profile.get('expected_career_trajectory', 'Not specified')}
"""
    
    return EXPERIENCE_RELEVANCE_PROMPT.format(
        candidate_experience=candidate_experience.strip(),
        job_requirements=job_requirements.strip()
    )

