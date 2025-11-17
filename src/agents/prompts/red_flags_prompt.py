"""Prompt template for Red Flags Detector Agent."""

RED_FLAGS_DETECTOR_PROMPT = """You are a Red Flags Detector Agent.

**All Agent Evaluations:**
{all_evaluations}

**Job's Potential Red Flags:**
{job_red_flags}

**Your task:** Aggregate and classify all red flags by severity.

**Severity Levels:**
- CRITICAL: Automatic disqualification (e.g., missing mandatory license, sector incompatible)
- HIGH: Significant concern, substantial score reduction
- MEDIUM: Minor concern, warrants attention but not disqualifying

**Output (JSON only):**
{{
  "agent": "red_flags_detector",
  "score": <0-100, based on severity_score>,
  "critical_flags": [<list>],
  "high_flags": [<list>],
  "medium_flags": [<list>],
  "total_flags": <integer>,
  "disqualifying": <boolean>,
  "severity_score": <0.0-1.0, where 1.0=no flags, 0.0=critical>,
  "evidence": [<list>],
  "reasoning": "<explanation>",
  "red_flags": [],
  "confidence": <0.0-1.0>
}}
"""

def format_red_flags_prompt(all_evaluations: list, job_offer: dict) -> str:
    """Format red flags detector prompt."""
    evaluations_summary = []
    for eval_data in all_evaluations:
        agent = eval_data.get("agent", "unknown")
        flags = eval_data.get("red_flags", [])
        if flags:
            evaluations_summary.append(f"{agent}: {', '.join(flags)}")
    
    all_evaluations_str = "\n".join(evaluations_summary) if evaluations_summary else "No red flags detected by other agents"
    
    ideal_profile = job_offer.get("semantic_enrichment", {}).get("ideal_candidate_profile", {})
    job_red_flags = "\n".join([f"- {flag}" for flag in ideal_profile.get("potential_red_flags", [])])
    
    return RED_FLAGS_DETECTOR_PROMPT.format(
        all_evaluations=all_evaluations_str,
        job_red_flags=job_red_flags if job_red_flags else "None specified"
    )

