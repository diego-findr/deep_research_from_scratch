"""Prompt template for Competencies Evaluator Agent."""

COMPETENCIES_EVALUATOR_PROMPT = """You are a Competencies Evaluator Agent.

**Candidate Competencies:**
{candidate_competencies}

**Required Competencies:**
{job_competencies}

**Evaluate:** functional, managerial, and soft skills competencies.

**Output (JSON only):**
{{
  "agent": "competencies_evaluator",
  "score": <0-100>,
  "required_competencies_coverage": <0.0-1.0>,
  "missing_competencies": [{{"competency": "<name>", "type": "<functional|managerial|soft>", "importance": "<required|preferred>", "impact": "<high|medium|low>"}}],
  "competency_gaps": [{{"competency": "<name>", "candidate_level": "<level>", "required_level": "<level>", "gap_severity": "<critical|moderate|minor>"}}],
  "strengths": [<list>],
  "evidence": [<list>],
  "reasoning": "<explanation>",
  "red_flags": [<list>],
  "confidence": <0.0-1.0>
}}
"""

def format_competencies_prompt(candidate: dict, job_offer: dict) -> str:
    """Format competencies evaluator prompt."""
    cand_comp = candidate.get("semantic_enrichment", {}).get("competencies_analysis", {})
    job_comp = job_offer.get("semantic_enrichment", {}).get("competencies_analysis", {})
    
    candidate_competencies = f"""
Competencies ({len(cand_comp.get('competencies', []))} total):
{', '.join([f"{c.get('name', '')} (level: {c.get('level', 'unknown')})" for c in cand_comp.get('competencies', [])[:10]])}
"""
    
    job_competencies = f"""
Required Competencies ({len(job_comp.get('required_competencies', []))} total):
{', '.join([f"{c.get('name', '')} (importance: {c.get('importance', 'required')})" for c in job_comp.get('required_competencies', [])[:10]])}
"""
    
    return COMPETENCIES_EVALUATOR_PROMPT.format(
        candidate_competencies=candidate_competencies.strip(),
        job_competencies=job_competencies.strip()
    )

