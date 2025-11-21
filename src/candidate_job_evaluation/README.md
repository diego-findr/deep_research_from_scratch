# Candidate-Job Fit Evaluation System

A production-ready multi-agent system using LangGraph to evaluate compatibility between enriched candidate profiles and enriched job offers.

## Overview

This system implements a **Hybrid Collaborative-Supervisor** architecture where specialized agents analyze different dimensions of candidate-job fit, then synthesize their findings into a comprehensive evaluation with full explainability.

### Key Features

- ✅ **Sector-Agnostic**: Works across all industries (construction, software, finance, healthcare, etc.)
- ✅ **Semantic Disambiguation**: Leverages enrichment data to resolve ambiguous terms
- ✅ **Dynamic Weighting**: Adapts scoring based on sector and seniority requirements
- ✅ **Full Explainability**: Every decision traced to evidence from inputs
- ✅ **Critical Red Flag Detection**: Early termination for disqualifying issues
- ✅ **Conditional Routing**: Smart graph flow based on evaluation state
- ✅ **Production-Ready**: Type-safe, tested, documented, error-handled

## Architecture

### Three-Phase Evaluation Process

```
┌─────────────────────────────────────────────────────────────┐
│                    PHASE 1: PARALLEL ANALYSIS                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Sector     │  │    Skills    │  │  Seniority   │      │
│  │  Alignment   │  │   Matching   │  │  Alignment   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │ Competencies │  │  Red Flags   │                        │
│  │   Matching   │  │   Detector   │                        │
│  └──────────────┘  └──────────────┘                        │
│                            │                                 │
└────────────────────────────┼─────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │ Critical Flags?│
                    └────────────────┘
                       │         │
              ┌────────┘         └────────┐
              │ YES                       │ NO
              │ (Early Termination)       │
              ▼                           ▼
┌─────────────────────────┐   ┌─────────────────────────┐
│  PHASE 2: CONDITIONAL   │   │  PHASE 2: DOMAIN EXPERT │
│                         │   │                         │
│  Skip Domain Expert     │   │  ┌──────────────┐      │
│                         │   │  │    Domain    │      │
│                         │   │  │    Expert    │      │
│                         │   │  │  (Sector-    │      │
│                         │   │  │   Specific)  │      │
│                         │   │  └──────────────┘      │
└─────────────────────────┘   └─────────────────────────┘
              │                           │
              └───────────┬───────────────┘
                          ▼
            ┌─────────────────────────┐
            │ PHASE 3: ORCHESTRATION  │
            │                         │
            │  ┌──────────────┐      │
            │  │ Orchestrator │      │
            │  │  (Synthesis) │      │
            │  └──────────────┘      │
            │                         │
            │  • Apply Weights        │
            │  • Aggregate Scores     │
            │  • Generate Report      │
            └─────────────────────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ Final Evaluation│
                 └─────────────────┘
```

### Specialized Agents

1. **Sector Alignment Agent**: Evaluates industry/domain compatibility
   - Primary/secondary sector matching
   - Transferability analysis
   - Disambiguation of sector-specific terms

2. **Skills Matching Agent**: Evaluates technical and functional skills
   - Required vs preferred skills coverage
   - Semantic matching using synonym maps
   - Skill level comparison
   - Gap analysis

3. **Seniority Alignment Agent**: Evaluates experience level fit
   - Years of experience comparison
   - Seniority level matching (junior/mid/senior/lead/executive)
   - Career trajectory validation
   - Over/under-qualification detection

4. **Competencies Matching Agent**: Evaluates soft skills and competencies
   - Functional competencies (40% weight)
   - Soft competencies (30% weight)
   - Managerial competencies (30% weight)
   - Leadership indicators

5. **Red Flags Detector Agent**: Identifies disqualifying issues
   - Job-defined red flags
   - Experience gaps
   - Qualification mismatches
   - Critical vs minor flags

6. **Domain Expert Agent** (Conditional): Provides sector-specific analysis
   - Dynamically instantiated based on job sector
   - Validates other agents' findings
   - Deep sector expertise

7. **Orchestrator Agent**: Synthesizes all evaluations
   - Applies dynamic weighting
   - Aggregates scores
   - Generates final recommendation
   - Creates decision tree

## Installation

```bash
# Ensure dependencies are installed
uv sync

# Or with pip
pip install -e .
```

## Quick Start

### Basic Usage

```python
from candidate_job_evaluation import evaluate_candidate_for_job, EvaluationConfig
import json

# Load enriched candidate and job
with open("candidate.json") as f:
    candidate = json.load(f)
    
with open("job.json") as f:
    job_offer = json.load(f)

# Configure (optional, uses defaults if not provided)
config = EvaluationConfig(
    llm_model="gpt-4o",
    llm_temperature=0.1,
)

# Run evaluation
result = evaluate_candidate_for_job(
    candidate=candidate,
    job_offer=job_offer,
    config=config
)

# Access results
final_eval = result["final_evaluation"]
print(f"Score: {final_eval.overall_score}/100")
print(f"Recommendation: {final_eval.recommendation}")
print(f"Summary: {final_eval.summary}")
```

### Run Example

```bash
# From repository root
python -m src.candidate_job_evaluation.example
```

## Configuration

### EvaluationConfig

```python
from candidate_job_evaluation import EvaluationConfig

config = EvaluationConfig(
    # LLM settings
    llm_model="gpt-4o",
    llm_temperature=0.1,
    
    # Scoring thresholds
    highly_recommend_threshold=85,
    recommend_threshold=70,
    acceptable_threshold=55,
    
    # Default weights (sector-agnostic baseline)
    default_weights={
        "sector": 0.25,
        "skills": 0.30,
        "seniority": 0.15,
        "competencies": 0.20,
        "domain_expert": 0.10,
    },
    
    # Sector-specific weight adjustments
    sector_weight_adjustments={
        "software": {"skills": 0.40, "competencies": 0.15},
        "construction": {"sector": 0.30, "competencies": 0.25, "skills": 0.20},
        "finance": {"competencies": 0.30, "skills": 0.25},
    },
    
    # Critical red flag types (auto-disqualify)
    critical_red_flag_types=[
        "sector_complete_mismatch",
        "missing_mandatory_certification",
        "insufficient_experience_years",
    ],
    
    # Error handling
    agent_failure_default_score=50,
    max_retries=2,
)
```

### Dynamic Weighting

Weights are automatically adjusted based on:

1. **Job Sector**: Different sectors prioritize different dimensions
   - Software: Skills (40%) > Competencies (15%)
   - Construction: Sector (30%), Competencies (25%) > Skills (20%)
   - Finance: Competencies (30%) > Skills (25%)

2. **Job Seniority**: Higher seniority emphasizes competencies over skills
3. **Must-Have Requirements**: Explicit requirements increase relevant agent weight

## Input Schema

### Enriched Candidate

Expected structure (from profile enrichment system):

```json
{
  "candidato_id": "uuid",
  "perfil_raw": { /* basic candidate data */ },
  "semantic_enrichment": {
    "analysis_components": {
      "sector_inference": {
        "primary_sector": "string",
        "secondary_sectors": ["string"],
        "confidence": 0.0-1.0,
        "evidence": ["string"]
      },
      "skills_extraction": {
        "explicit_skills": [/* skill objects */],
        "implicit_skills": [/* skill objects */]
      },
      "seniority_inference": {
        "seniority_level": "junior|mid|senior|lead|principal",
        "years_experience_estimate": int,
        "evidence": ["string"]
      },
      "competencies_analysis": {
        "competencies": [/* competency objects */]
      }
    },
    "structured_skills": {
      "explicit": [/* skill objects */],
      "implicit": [/* skill objects */]
    },
    "structured_competencies": [/* competency objects */],
    "disambiguation_map": { /* term → meaning */ },
    "synonym_map": { /* term → [synonyms] */ }
  },
  "key_insights": { /* summary */ }
}
```

### Enriched Job Offer

Expected structure (from job enrichment system):

```json
{
  "job_id": "uuid",
  "raw_job_posting": { /* basic job data */ },
  "semantic_enrichment": {
    "analysis_components": {
      "sector_inference": {
        "primary_sector": "string",
        "confidence": 0.0-1.0
      },
      "skills_extraction": {
        "explicit_skills": [/* with importance: required|preferred */],
        "implicit_skills": [/* with importance */]
      },
      "seniority_inference": {
        "required_seniority": "junior|mid|senior|lead|executive",
        "years_experience_required": int
      },
      "competencies_analysis": {
        "required_competencies": [/* competency objects */]
      }
    },
    "structured_skills": { /* same as candidate */ },
    "structured_competencies": [/* same as candidate */],
    "ideal_candidate": {
      "must_have_experience": ["string"],
      "preferred_experience": ["string"],
      "potential_red_flags": ["string"]
    }
  },
  "key_insights": { /* summary */ }
}
```

## Output Schema

### FinalEvaluation

```python
{
  "overall_score": int (0-100),
  "recommendation": "highly_recommend" | "recommend" | "acceptable" | "not_recommend",
  "summary": str,  # Executive summary (2-3 sentences)
  "strengths": [str],  # 3-5 key strengths
  "concerns": [str],  # 3-5 key concerns
  "missing_skills": [str],  # Critical missing skills
  "all_red_flags": [str],  # All red flags from all agents
  "agent_scores": {
    "sector": int,
    "skills": int,
    "seniority": int,
    "competencies": int,
    "red_flags": int,
    "domain_expert": int
  },
  "decision_tree": str  # Human-readable explanation
}
```

### AgentEvaluation

Each specialized agent returns:

```python
{
  "agent_name": str,
  "score": int (0-100),
  "alignment_level": "perfect_match" | "strong_match" | "partial_match" | "weak_match" | "mismatch",
  "reasoning": str,  # Chain-of-Thought explanation
  "evidence": [str],  # Evidence from inputs
  "red_flags": [str],  # Identified red flags
  "confidence": float (0.0-1.0)
}
```

## Chain-of-Thought Prompting

All agents use explicit Chain-of-Thought reasoning:

1. **Step-by-Step Analysis**: Agents break down evaluation into discrete steps
2. **Evidence-Based**: Every conclusion linked to specific input data
3. **Transparent Reasoning**: Full reasoning included in output
4. **Validation**: Agents cross-check their findings

Example reasoning from Sector Agent:
```
1. Primary Sector Match: Candidate is in 'occupational_health_and_safety_in_construction' 
   (0.95 confidence), job requires 'construction' (0.98 confidence) → STRONG MATCH
2. Secondary Sector Overlap: Candidate has 'construction_management' in secondary, 
   job emphasizes infrastructure → OVERLAP CONFIRMED
3. Transferability: Candidate's PRL experience in construction projects directly 
   transfers to technical support manager role → HIGH TRANSFERABILITY
4. Score: 88/100 (strong_match)
```

## Error Handling

The system implements robust error handling:

1. **Agent Failures**: If an agent fails, it returns a fallback score (default: 50) with error annotation
2. **Missing Data**: Gracefully handles missing enrichment fields with conservative scoring
3. **LLM Errors**: Retries with exponential backoff (configurable `max_retries`)
4. **Orchestrator Fallback**: If orchestrator fails, calculates simple weighted average

## Testing

```bash
# Run tests
pytest tests/

# Run specific test
pytest tests/test_evaluation.py::test_natalia_acciona_evaluation
```

## Extending the System

### Adding a New Specialized Agent

1. Create agent method in `agents.py`:
```python
def new_agent(self, state: EvaluationState) -> Dict[str, Any]:
    # Implement logic
    evaluation = self._safe_agent_call(prompt, "new_agent", state)
    return {"new_evaluation": evaluation, "messages": [...]}
```

2. Add to state schema in `state.py`:
```python
class EvaluationState(TypedDict):
    new_evaluation: Optional[AgentEvaluation]
```

3. Update graph in `graph.py`:
```python
graph.add_node("new_agent", agents.new_agent)
graph.add_edge(START, "new_agent")
graph.add_edge("new_agent", "orchestrator")
```

### Adding Sector-Specific Considerations

Update `SECTOR_CONSIDERATIONS` in `prompts.py`:

```python
SECTOR_CONSIDERATIONS = {
    "your_sector": """
    - Prioritize: Key skills for this sector
    - Check: Important experience indicators
    - Red flags: Disqualifying factors
    """,
}
```

## Performance

- **Latency**: ~20-30 seconds per evaluation (5 parallel agents + domain expert + orchestrator)
- **Cost**: ~$0.10-0.20 per evaluation with GPT-4o (depending on input size)
- **Throughput**: Supports batch processing for multiple candidates per job

## Best Practices

1. **Use Enriched Data**: System designed for enriched inputs; raw data may produce poor results
2. **Configure Weights**: Adjust sector-specific weights based on your domain expertise
3. **Review Thresholds**: Tune recommendation thresholds to your organization's hiring bar
4. **Validate Red Flags**: Regularly review red flags to ensure they're appropriate
5. **Monitor Agent Failures**: Track agent failure rates to identify prompt/LLM issues

## Architecture Decisions

### Why Hybrid Collaborative-Supervisor?

- **Parallel Efficiency**: Independent agents run simultaneously (5x faster than sequential)
- **Specialization**: Each agent focuses on one dimension (better quality)
- **Validation**: Domain expert can validate/challenge other agents
- **Explainability**: Clear separation of concerns makes reasoning transparent
- **Extensibility**: Easy to add new agents without rewriting system

### Why Conditional Routing?

- **Efficiency**: Early termination saves costs when candidate clearly unqualified
- **Flexibility**: Domain expert only invoked when needed
- **Quality**: Critical red flags immediately visible, not buried in final report

### Why Dynamic Weighting?

- **Sector Variance**: Software values skills differently than construction
- **Seniority Variance**: Junior roles emphasize skills, senior roles emphasize competencies
- **Job-Specific**: Must-have requirements increase relevant dimension weight

## Troubleshooting

### Agent Returns Default Score (50)

- **Cause**: Agent failed (LLM error, invalid JSON, timeout)
- **Solution**: Check logs for error details; verify LLM API key and model access

### Missing Enrichment Fields

- **Cause**: Input candidate/job not properly enriched
- **Solution**: Run enrichment pipeline first; ensure all required fields present

### Low Scores Despite Good Match

- **Cause**: Synonym mismatch (e.g., "PRL" not mapped to "Occupational Health")
- **Solution**: Verify synonym maps in enrichment; update disambiguation

### Orchestrator Fallback Activated

- **Cause**: Orchestrator agent failed to parse or generate valid output
- **Solution**: Check prompt formatting; verify weights configuration

## License

See repository root LICENSE file.

## Contributing

This system is part of the Deep Research From Scratch repository. Follow the repository's contribution guidelines.

## Support

For issues, questions, or feature requests, open an issue in the repository.
