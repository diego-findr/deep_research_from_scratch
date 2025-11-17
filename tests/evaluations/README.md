# Candidate-Job Evaluations

This directory contains evaluation results from the multi-agent candidate-job fit evaluation system.

## Structure

```
evaluations/
├── outputs/           # Evaluation results (JSON)
└── README.md         # This file
```

## Output Format

Each evaluation file contains:

```json
{
  "evaluation_id": "unique-uuid",
  "timestamp": "ISO-8601 timestamp",
  "candidate_id": "candidate UUID",
  "job_id": "job UUID",
  
  "sector_evaluation": {
    "agent_name": "sector_alignment",
    "score": 0-100,
    "alignment_level": "perfect_match|strong_match|partial_match|weak_match|mismatch",
    "reasoning": "step-by-step explanation",
    "evidence": ["evidence points"],
    "red_flags": ["flags if any"],
    "confidence": 0.0-1.0
  },
  
  "skills_evaluation": { /* same structure */ },
  "seniority_evaluation": { /* same structure */ },
  "competencies_evaluation": { /* same structure */ },
  "red_flags_evaluation": { /* same structure */ },
  "domain_expert_evaluation": { /* same structure */ },
  
  "final_evaluation": {
    "overall_score": 0-100,
    "recommendation": "highly_recommend|recommend|acceptable|not_recommend",
    "summary": "executive summary",
    "strengths": ["key strengths"],
    "concerns": ["key concerns"],
    "missing_skills": ["critical missing skills"],
    "all_red_flags": ["all red flags collected"],
    "agent_scores": {
      "sector": 0-100,
      "skills": 0-100,
      "seniority": 0-100,
      "competencies": 0-100,
      "red_flags": 0-100,
      "domain_expert": 0-100
    },
    "decision_tree": "human-readable decision explanation"
  }
}
```

## Running Evaluations

From the repository root:

```bash
# Run the example evaluation
python -m src.candidate_job_evaluation.example

# Or programmatically
python
>>> from src.candidate_job_evaluation import evaluate_candidate_for_job, EvaluationConfig
>>> result = evaluate_candidate_for_job(candidate, job_offer, EvaluationConfig())
```

## Interpreting Results

### Overall Scores

- **85-100**: Highly Recommend - Excellent fit across all dimensions
- **70-84**: Recommend - Strong fit with minor gaps
- **55-69**: Acceptable - Adequate fit with some concerns
- **0-54**: Not Recommend - Significant gaps or critical red flags

### Agent Scores

Each specialized agent evaluates a specific dimension:

- **Sector Alignment**: Industry/domain compatibility
- **Skills Matching**: Technical and functional skills coverage
- **Seniority Alignment**: Experience level and career stage fit
- **Competencies Matching**: Soft skills and competencies alignment
- **Red Flags Detector**: Critical disqualifiers and concerns
- **Domain Expert**: Sector-specific deep evaluation

### Red Flags

- **Critical**: Auto-disqualify (e.g., complete sector mismatch, missing mandatory certifications)
- **Minor**: Reduce score but don't disqualify (e.g., over-qualification concerns)

## Example Evaluations

See `outputs/evaluation_natalia_acciona.json` for a complete example evaluation.
