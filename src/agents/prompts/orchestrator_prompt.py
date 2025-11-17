"""Prompt template for Orchestrator Agent."""

ORCHESTRATOR_SYNTHESIS_PROMPT = """You are the Orchestrator Agent responsible for final synthesis.

**All Agent Evaluations:**
{all_evaluations}

**Scoring Weights:**
{weights}

**Your task:**
1. Calculate weighted final score
2. Identify key strengths and weaknesses
3. Classify fit level and recommendation
4. Analyze consensus between agents
5. Provide actionable next steps

**Output (JSON only):**
{{
  "agent": "orchestrator",
  "final_score": <0-100, weighted average>,
  "fit_classification": "<perfect_fit|good_fit|acceptable_fit|poor_fit>",
  "recommendation": "<strong_recommend|recommend|conditional_recommend|not_recommend>",
  "score_breakdown": {{
    "sector_alignment": {{"score": <int>, "weight": <float>, "weighted_score": <float>}},
    "skills_matching": {{"score": <int>, "weight": <float>, "weighted_score": <float>}},
    "seniority_calibration": {{"score": <int>, "weight": <float>, "weighted_score": <float>}},
    "competencies_evaluator": {{"score": <int>, "weight": <float>, "weighted_score": <float>}},
    "domain_expert": {{"score": <int>, "weight": <float>, "weighted_score": <float>}},
    "experience_relevance": {{"score": <int>, "weight": <float>, "weighted_score": <float>}},
    "cultural_soft_fit": {{"score": <int>, "weight": <float>, "weighted_score": <float>}},
    "red_flags_penalty": {{"severity_score": <float>, "penalty": <float>}}
  }},
  "key_strengths": [<list of top 3-5 strengths>],
  "key_weaknesses": [<list of top 3-5 weaknesses>],
  "decision_rationale": "<executive summary explaining the decision>",
  "next_steps_recommendation": [<list of recommended actions>],
  "confidence": <0.0-1.0>,
  "agents_consensus": {{
    "unanimous_positive": [<agents with high scores>],
    "unanimous_negative": [<agents with low scores>],
    "conflicting": [<agents with middle scores>],
    "consensus_level": "<high|medium|low>"
  }}
}}
"""

def format_orchestrator_prompt(all_evaluations: list, weights: dict) -> str:
    """Format orchestrator synthesis prompt."""
    evaluations_str = ""
    for eval_data in all_evaluations:
        agent = eval_data.get("agent", "unknown")
        score = eval_data.get("score", 0)
        reasoning = eval_data.get("reasoning", "")[:200]
        evaluations_str += f"\n{agent}: Score={score}\nReasoning: {reasoning}...\n"
    
    weights_str = "\n".join([f"{agent}: {weight}" for agent, weight in weights.items()])
    
    return ORCHESTRATOR_SYNTHESIS_PROMPT.format(
        all_evaluations=evaluations_str.strip(),
        weights=weights_str
    )

