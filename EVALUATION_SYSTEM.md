# Candidate-Job Fit Evaluation System

## Overview

This document describes the **multi-agent candidate-job fit evaluation system** built using LangGraph. The system evaluates compatibility between enriched candidate profiles and enriched job offers using a swarm of specialized AI agents.

## Quick Start

```python
from src.candidate_job_evaluation import evaluate_candidate_for_job, EvaluationConfig
import json

# Load enriched data
with open("tests/candidates/outputs/enriched_natalia.json") as f:
    candidate = json.load(f)
    
with open("tests/jobs/outputs/enriched_acciona_job.json") as f:
    job_offer = json.load(f)

# Run evaluation
result = evaluate_candidate_for_job(candidate, job_offer)

# Access results
print(f"Score: {result['final_evaluation'].overall_score}/100")
print(f"Recommendation: {result['final_evaluation'].recommendation}")
```

## System Architecture

### Multi-Agent Evaluation Pipeline

```
INPUT: Enriched Candidate + Enriched Job
              │
              ▼
┌─────────────────────────────────────────┐
│   PHASE 1: PARALLEL ANALYSIS (Swarm)    │
├─────────────────────────────────────────┤
│  • Sector Alignment Agent               │
│  • Skills Matching Agent                │
│  • Seniority Alignment Agent            │
│  • Competencies Matching Agent          │
│  • Red Flags Detector Agent             │
└─────────────────────────────────────────┘
              │
              ▼
      [Conditional Routing]
              │
      ┌───────┴───────┐
      │               │
Critical Red Flags?   No Critical Flags
      │               │
      ▼               ▼
  Early Exit    Domain Expert Agent
                      │
                      ▼
┌─────────────────────────────────────────┐
│   PHASE 3: SYNTHESIS (Supervisor)       │
├─────────────────────────────────────────┤
│  Orchestrator Agent:                    │
│  • Applies dynamic weighting            │
│  • Aggregates scores                    │
│  • Generates final recommendation       │
│  • Creates decision tree                │
└─────────────────────────────────────────┘
              │
              ▼
OUTPUT: Final Evaluation with Full Explainability
```

### Specialized Agents

| Agent | Purpose | Output |
|-------|---------|--------|
| **Sector Alignment** | Evaluates industry/domain compatibility | Score + alignment level + evidence |
| **Skills Matching** | Matches technical and functional skills | Score + matched/missing skills |
| **Seniority Alignment** | Validates experience level fit | Score + over/under-qualification flags |
| **Competencies Matching** | Evaluates soft skills and competencies | Score + competency gaps |
| **Red Flags Detector** | Identifies critical disqualifiers | Red flags + criticality assessment |
| **Domain Expert** | Sector-specific deep evaluation | Score + domain-specific insights |
| **Orchestrator** | Synthesizes all evaluations | Final score + recommendation + decision tree |

## Key Features

### 1. Sector-Agnostic Design

The system works across all industries without modification:
- **Construction**: Prioritizes safety certifications, field experience, project scale
- **Software**: Emphasizes technical stack, architecture patterns, system design
- **Finance**: Focuses on regulatory knowledge, risk management, certifications
- **Healthcare**: Validates licenses, clinical experience, patient safety

### 2. Semantic Disambiguation

Leverages enrichment data to resolve ambiguities:
- **Example**: "PRL" → "Prevención de Riesgos Laborales" (not "Physical Review Letters")
- **Example**: "AWS" in construction → "Amazon Web Services data center construction" (not cloud tech)
- Uses synonym maps and canonical terms for accurate matching

### 3. Dynamic Weighting

Adapts scoring based on context:

**Default Weights (Sector-Agnostic)**:
- Sector: 25%
- Skills: 30%
- Seniority: 15%
- Competencies: 20%
- Domain Expert: 10%

**Sector Adjustments**:
- **Software**: Skills ↑40%, Competencies ↓15%
- **Construction**: Sector ↑30%, Competencies ↑25%, Skills ↓20%
- **Finance**: Competencies ↑30%, Skills ↑25%

### 4. Full Explainability

Every decision is traced to evidence:
- **Chain-of-Thought reasoning** in every agent
- **Evidence-based conclusions** linked to input data
- **Decision tree** explains final recommendation
- **Agent transparency** with individual scores visible

### 5. Red Flag Detection

Identifies critical disqualifiers early:

**Critical Red Flags (Auto-Disqualify)**:
- Complete sector mismatch
- Missing mandatory certifications
- <50% of required experience years
- Multiple job-defined red flags

**Minor Red Flags (Reduce Score)**:
- Over-qualification concerns
- Minor skill gaps
- Limited international experience (if preferred)

### 6. Conditional Routing

Smart graph flow based on evaluation state:
- **Early Termination**: Critical red flags skip domain expert
- **Dynamic Expert**: Domain expert instantiated based on job sector
- **Efficient**: Saves costs by avoiding unnecessary LLM calls

## Architecture Decisions

### Why Hybrid Collaborative-Supervisor?

**Parallel Efficiency**:
- 5 agents run simultaneously
- 5x faster than sequential execution
- ~20-30 seconds total latency

**Specialization**:
- Each agent focuses on one dimension
- Better quality through focused prompts
- Easier to maintain and extend

**Validation**:
- Domain expert validates other agents
- Cross-checking increases accuracy
- Reduces false positives

**Explainability**:
- Clear separation of concerns
- Each agent's reasoning is transparent
- Easy to debug and improve

### Why LangGraph?

- **State Management**: Clean state flow through agents
- **Conditional Edges**: Smart routing based on red flags
- **Parallel Execution**: Built-in support for parallel nodes
- **Extensibility**: Easy to add new agents
- **Visualization**: Can visualize graph structure

## Input Requirements

### Enriched Candidate Profile

Must contain:
```json
{
  "semantic_enrichment": {
    "analysis_components": {
      "sector_inference": { "primary_sector": "...", "confidence": 0.95 },
      "seniority_inference": { "seniority_level": "lead", "years_experience_estimate": 9 },
      "skills_extraction": { "explicit_skills": [...], "implicit_skills": [...] },
      "competencies_analysis": { "competencies": [...] }
    },
    "structured_skills": { "explicit": [...], "implicit": [...] },
    "structured_competencies": [...],
    "disambiguation_map": { "PRL": { "meaning": "...", "confidence": 1.0 } },
    "synonym_map": { "Prevención de Riesgos Laborales": ["PRL", "OHS", ...] }
  }
}
```

### Enriched Job Offer

Must contain:
```json
{
  "semantic_enrichment": {
    "analysis_components": {
      "sector_inference": { "primary_sector": "construction" },
      "seniority_inference": { "required_seniority": "lead", "years_experience_required": 10 },
      "skills_extraction": { "explicit_skills": [...], "implicit_skills": [...] },
      "competencies_analysis": { "required_competencies": [...] }
    },
    "structured_skills": { /* with importance: required|preferred */ },
    "structured_competencies": [...],
    "ideal_candidate": {
      "must_have_experience": [...],
      "preferred_experience": [...],
      "potential_red_flags": [...]
    }
  }
}
```

## Output Schema

### Final Evaluation

```python
{
  "overall_score": 78,  # 0-100
  "recommendation": "recommend",  # highly_recommend|recommend|acceptable|not_recommend
  "summary": "Candidate is a strong fit for this construction management role...",
  "strengths": [
    "Extensive construction sector experience (9 years)",
    "Direct PRL (health & safety) expertise aligns with technical support needs",
    "Leadership experience managing large-scale projects"
  ],
  "concerns": [
    "Primary focus on safety vs. general technical support",
    "1 year short of required 10 years experience",
    "No explicit roads/bridges infrastructure mentioned"
  ],
  "missing_skills": [
    "Gestión de ofertas técnicas y licitaciones (technical bids)",
    "Diseño constructivo (constructive design)"
  ],
  "all_red_flags": [
    "Specialization in safety rather than general construction management"
  ],
  "agent_scores": {
    "sector": 88,
    "skills": 72,
    "seniority": 85,
    "competencies": 80,
    "red_flags": 75,
    "domain_expert": 78
  },
  "decision_tree": "1. Sector alignment strong (88/100) - both construction...\n2. Skills partial match (72/100) - safety skills present but missing bid management...\n3. Seniority close match (85/100) - lead level, 9 vs 10 years...\n4. Weighted score: 78/100 → RECOMMEND"
}
```

## Performance

- **Latency**: ~20-30 seconds per evaluation
- **Cost**: ~$0.10-0.20 per evaluation (GPT-4o)
- **Throughput**: Batch processing supported
- **Scalability**: Stateless, horizontally scalable

## Configuration

```python
from src.candidate_job_evaluation import EvaluationConfig

config = EvaluationConfig(
    llm_model="gpt-4o",
    llm_temperature=0.1,  # Low for consistency
    
    # Customize thresholds
    highly_recommend_threshold=85,
    recommend_threshold=70,
    acceptable_threshold=55,
    
    # Adjust sector weights
    sector_weight_adjustments={
        "construction": {
            "sector": 0.30,
            "competencies": 0.25,
            "skills": 0.20
        }
    },
    
    # Define critical red flags
    critical_red_flag_types=[
        "sector_complete_mismatch",
        "missing_mandatory_certification"
    ]
)
```

## Extending the System

### Add a New Agent

1. Create agent method in `src/candidate_job_evaluation/agents.py`
2. Add to state schema in `src/candidate_job_evaluation/state.py`
3. Update graph in `src/candidate_job_evaluation/graph.py`
4. Add prompt in `src/candidate_job_evaluation/prompts.py`

### Add Sector-Specific Logic

Update `SECTOR_CONSIDERATIONS` in `prompts.py`:

```python
SECTOR_CONSIDERATIONS = {
    "your_sector": """
    - Prioritize: Key skills for this sector
    - Check: Important experience indicators
    - Red flags: Disqualifying factors
    """
}
```

## Testing

```bash
# Run all tests
pytest tests/test_candidate_job_evaluation.py -v

# Run specific test
pytest tests/test_candidate_job_evaluation.py::test_sector_matching_logic -v

# Run integration tests (requires API key)
pytest tests/test_candidate_job_evaluation.py -m integration
```

## Files Structure

```
deep_research_from_scratch/
├── notebooks/
│   └── candidate_job_evaluation.ipynb     # Source of truth (modify this)
├── src/
│   └── candidate_job_evaluation/          # Generated code (DO NOT modify)
│       ├── __init__.py
│       ├── state.py                       # State schema and models
│       ├── config.py                      # Configuration
│       ├── prompts.py                     # Agent prompts
│       ├── agents.py                      # Specialized agents
│       ├── graph.py                       # LangGraph workflow
│       ├── example.py                     # Example usage
│       └── README.md                      # Detailed documentation
├── tests/
│   ├── candidates/
│   │   └── outputs/
│   │       └── enriched_natalia.json
│   ├── jobs/
│   │   └── outputs/
│   │       └── enriched_acciona_job.json
│   ├── evaluations/
│   │   ├── outputs/
│   │   │   └── evaluation_natalia_acciona.json
│   │   └── README.md
│   └── test_candidate_job_evaluation.py
└── EVALUATION_SYSTEM.md                   # This file
```

## Example Usage

### Basic Evaluation

```python
from src.candidate_job_evaluation import evaluate_candidate_for_job
import json

# Load data
with open("tests/candidates/outputs/enriched_natalia.json") as f:
    candidate = json.load(f)
with open("tests/jobs/outputs/enriched_acciona_job.json") as f:
    job = json.load(f)

# Evaluate
result = evaluate_candidate_for_job(candidate, job)

# Display
final = result["final_evaluation"]
print(f"Score: {final.overall_score}/100")
print(f"Recommendation: {final.recommendation}")
for strength in final.strengths:
    print(f"  ✓ {strength}")
for concern in final.concerns:
    print(f"  ! {concern}")
```

### Batch Evaluation

```python
candidates = [load_candidate(id) for id in candidate_ids]
job = load_job(job_id)

results = []
for candidate in candidates:
    result = evaluate_candidate_for_job(candidate, job)
    results.append({
        "candidate_id": candidate["candidato_id"],
        "score": result["final_evaluation"].overall_score,
        "recommendation": result["final_evaluation"].recommendation
    })

# Rank candidates
ranked = sorted(results, key=lambda x: x["score"], reverse=True)
print("Top 5 candidates:")
for i, r in enumerate(ranked[:5], 1):
    print(f"{i}. {r['candidate_id']}: {r['score']}/100 ({r['recommendation']})")
```

### Custom Configuration

```python
config = EvaluationConfig(
    llm_temperature=0.2,  # Slightly more creative
    highly_recommend_threshold=90,  # Stricter bar
)

result = evaluate_candidate_for_job(candidate, job, config)
```

## Best Practices

1. **Always Use Enriched Data**: System designed for enriched inputs
2. **Configure Sector Weights**: Adjust based on your domain expertise
3. **Review Red Flags**: Regularly validate red flag definitions
4. **Monitor Agent Failures**: Track failure rates to identify issues
5. **Tune Thresholds**: Adjust recommendation thresholds to your hiring bar

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Default score (50) | Agent failed | Check logs, verify API key |
| Missing enrichment fields | Input not enriched | Run enrichment pipeline first |
| Low scores despite match | Synonym mismatch | Verify synonym maps in enrichment |
| Orchestrator fallback | Parsing error | Check weights configuration |

## Related Systems

This evaluation system integrates with:

- **Profile Enrichment** (`src/profile_enrichment/`): Enriches candidate profiles
- **Job Enrichment** (`src/job_enrichment/`): Enriches job offers
- Together they form a complete candidate-job matching pipeline

## References

- **LangGraph Documentation**: https://langchain-ai.github.io/langgraph/
- **LangGraph Academy**: Repository best practices and patterns
- **Repository Structure**: See `README.md` for development workflow

## Support

For issues or questions, open an issue in the repository with:
- Input data (anonymized)
- Configuration used
- Error logs
- Expected vs actual behavior
