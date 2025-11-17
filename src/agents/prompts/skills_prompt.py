"""Prompt template for Skills Matching Agent."""

SKILLS_MATCHING_PROMPT = """You are a specialized Skills Matching Agent evaluating candidate-job compatibility.

**Candidate Skills:**
{candidate_skills}

**Job Required Skills:**
{job_skills}

**Evaluation Steps:**
1. **Must-Have Coverage**: Check coverage of required/must-have skills
2. **Preferred Coverage**: Check coverage of preferred/nice-to-have skills
3. **Skill Level Gaps**: Compare proficiency levels (novice/mid/advanced/expert)
4. **Missing Critical Skills**: Identify critical gaps
5. **Scoring**: 
   - 90-100: All must-haves + most preferred covered
   - 70-89: All must-haves covered, some preferred
   - 50-69: Most must-haves covered, gaps exist
   - <50: Critical must-haves missing

**Output (JSON only):**
{{
  "agent": "skills_matching",
  "score": <0-100>,
  "must_have_coverage": <0.0-1.0>,
  "preferred_coverage": <0.0-1.0>,
  "missing_critical_skills": [<list>],
  "skill_gaps": [
    {{"skill": "<name>", "required_level": "<level>", "candidate_level": "<level>", "gap": "<explanation>"}}
  ],
  "skill_overlaps": [
    {{"candidate_skill": "<name>", "job_skill": "<name>", "match_type": "<exact|semantic|partial>", "confidence": <0.0-1.0>}}
  ],
  "evidence": [<list>],
  "reasoning": "<step-by-step explanation>",
  "red_flags": [<list>],
  "confidence": <0.0-1.0>
}}
"""

def format_skills_prompt(candidate: dict, job_offer: dict) -> str:
    """Format skills matching prompt."""
    cand_skills = candidate.get("semantic_enrichment", {}).get("skills_extraction", {})
    job_skills = job_offer.get("semantic_enrichment", {}).get("skills_extraction", {})
    
    explicit = cand_skills.get("explicit_skills", [])[:15]
    implicit = cand_skills.get("implicit_skills", [])[:10]
    
    candidate_skills = f"""
Explicit Skills ({len(cand_skills.get('explicit_skills', []))} total, showing first 15):
{', '.join([s.get('name', '') for s in explicit]) if explicit else 'none'}

Implicit Skills ({len(cand_skills.get('implicit_skills', []))} total, showing first 10):
{', '.join([s.get('name', '') for s in implicit]) if implicit else 'none'}
"""
    
    required = job_skills.get("explicit_skills", [])[:15]
    
    job_skills_str = f"""
Required/Must-Have Skills ({len([s for s in job_skills.get('explicit_skills', []) if s.get('importance') in ['required', 'must_have']])} total):
{', '.join([f"{s.get('name', '')} (level: {s.get('level', 'any')})" for s in required if s.get('importance') in ['required', 'must_have']])}

Preferred Skills:
{', '.join([f"{s.get('name', '')}" for s in required if s.get('importance') in ['preferred', 'nice_to_have']])}
"""
    
    return SKILLS_MATCHING_PROMPT.format(
        candidate_skills=candidate_skills.strip(),
        job_skills=job_skills_str.strip()
    )

