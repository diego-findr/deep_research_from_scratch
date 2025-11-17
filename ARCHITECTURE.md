# System Architecture Documentation

## Overview

This document provides a detailed technical overview of the multi-agent candidate-job matching system built with LangGraph.

## Architecture Pattern

**Hybrid Collaborative-Supervisor Architecture**

The system combines:
1. **Autonomous specialist agents** that independently evaluate specific dimensions
2. **Peer-to-peer collaboration** through shared state
3. **Supervisor synthesis** via the Orchestrator Agent

## System Layers

### Layer 1: Input Processing
- **Input Validation Node**: Validates structure of enriched candidate and job offer JSONs
- **Early termination**: Fails fast if required data is missing

### Layer 2: Parallel Analysis (Specialist Agents)
All agents execute in parallel for optimal performance:

1. **Sector Alignment Agent**
   - Validates sector compatibility
   - Detects critical sector mismatches
   - Considers transferability between adjacent sectors

2. **Skills Matching Agent**
   - Compares must-have vs nice-to-have skills
   - Performs semantic matching with synonyms
   - Analyzes skill level gaps

3. **Seniority Calibration Agent**
   - Validates experience level alignment
   - Detects over/under-qualification
   - Evaluates career trajectory

4. **Competencies Evaluator Agent**
   - Assesses functional, managerial, and soft competencies
   - Maps competency levels
   - Identifies critical gaps

5. **Domain Expert Agent** (Dynamic)
   - Instantiated based on job sector
   - Provides sector-specific validation
   - Applies industry-specific knowledge

6. **Experience Relevance Agent**
   - Evaluates work experience depth
   - Applies recency weighting
   - Analyzes career progression

7. **Cultural & Soft Fit Agent**
   - Validates language requirements
   - Checks location compatibility
   - Assesses soft skills and cultural fit

8. **Salary Compensation Agent**
   - Evaluates salary alignment (if available)
   - Considers market standards
   - Non-blocking if data unavailable

### Layer 3: Aggregation & Cross-Validation

**Aggregation Node**
- Collects all specialist evaluations
- Builds unified scores dictionary
- Aggregates red flags

**Red Flags Detector Agent**
- Classifies flags by severity (critical/high/medium)
- Determines disqualifying conditions
- Calculates penalty multiplier

### Layer 4: Synthesis

**Orchestrator Agent**
- Applies dynamic weights to agent scores
- Integrates red flags penalty
- Calculates final score
- Determines fit classification and recommendation
- Analyzes consensus between agents
- Generates key strengths/weaknesses
- Provides actionable next steps

### Layer 5: Output Formatting

**Output Formatter Node**
- Structures final evaluation JSON
- Builds explainability section
- Creates decision tree
- Generates executive summary

## State Management

### State Schema (TypedDict)

```python
class EvaluationState(TypedDict):
    # Inputs
    candidate: Dict[str, Any]
    job_offer: Dict[str, Any]
    
    # Metadata
    evaluation_id: str
    timestamp: str
    current_phase: str
    
    # Agent evaluations
    sector_eval: Optional[Dict]
    skills_eval: Optional[Dict]
    # ... (one per agent)
    
    # Aggregated
    all_evaluations: List[Dict]
    aggregated_scores: Dict[str, int]
    aggregated_red_flags: Dict[str, List[str]]
    
    # Final outputs
    orchestrator_output: Optional[Dict]
    final_evaluation: Optional[Dict]
    
    # Error handling
    errors: List[str]
```

### State Flow

1. **Initialization**: Create state with candidate and job_offer
2. **Validation**: Add errors if validation fails
3. **Analysis**: Each agent adds its evaluation to state
4. **Aggregation**: Collect evaluations into lists
5. **Synthesis**: Orchestrator produces final output
6. **Formatting**: Structure final JSON

## LangGraph Structure

### Nodes

- `validate_inputs`: Input validation
- `evaluate_sector`: Sector alignment
- `evaluate_skills`: Skills matching
- `evaluate_seniority`: Seniority calibration
- `evaluate_competencies`: Competencies evaluation
- `evaluate_domain`: Domain expert analysis
- `evaluate_experience`: Experience relevance
- `evaluate_cultural`: Cultural & soft fit
- `evaluate_salary`: Salary compensation
- `aggregate`: Aggregation
- `evaluate_red_flags`: Red flags detection
- `orchestrate`: Orchestrator synthesis
- `format_output`: Output formatting

### Edges

#### Sequential Edges
- `validate_inputs` → `evaluate_sector` (conditional)
- `aggregate` → `evaluate_red_flags`
- `evaluate_red_flags` → `orchestrate`
- `orchestrate` → `format_output`
- `format_output` → END

#### Parallel Edges
All evaluation agents trigger simultaneously after sector agent:
- `evaluate_sector` → `evaluate_skills`
- `evaluate_sector` → `evaluate_seniority`
- `evaluate_sector` → `evaluate_competencies`
- `evaluate_sector` → `evaluate_domain`
- `evaluate_sector` → `evaluate_experience`
- `evaluate_sector` → `evaluate_cultural`
- `evaluate_sector` → `evaluate_salary`

All converge to:
- `evaluate_*` → `aggregate`

#### Conditional Edges
- `validate_inputs` branches on validation success/failure

## Agent Implementation

### Base Agent Class

```python
class BaseEvaluationAgent(ABC):
    def __init__(self, llm: Optional[BaseChatModel] = None)
    
    @abstractmethod
    def get_prompt(self, candidate, job_offer) -> str
    
    @abstractmethod
    def parse_response(self, response: str) -> Dict
    
    def evaluate(self, candidate, job_offer) -> Dict
    
    def _create_fallback_evaluation(self, error_msg: str) -> Dict
```

### Prompt Engineering

All agents use **Chain-of-Thought (CoT)** prompting:

1. **Step-by-step reasoning**: Agents think through evaluation logically
2. **Evidence-based**: Every conclusion must cite evidence
3. **Structured JSON output**: Ensures parseable responses
4. **Fallback handling**: Graceful degradation on errors

### Error Handling

Each agent implements fallback:
- On LLM failure: Return neutral score (50/100)
- On parsing error: Return conservative evaluation
- Continue execution: Don't block entire workflow

## Scoring System

### Weighted Score Calculation

```
final_score = Σ(agent_score × agent_weight) × red_flags_penalty
```

### Default Weights

```python
WEIGHT_SECTOR = 0.20       # 20%
WEIGHT_SKILLS = 0.25       # 25%
WEIGHT_SENIORITY = 0.15    # 15%
WEIGHT_COMPETENCIES = 0.15 # 15%
WEIGHT_DOMAIN_EXPERT = 0.10 # 10%
WEIGHT_EXPERIENCE = 0.10   # 10%
WEIGHT_CULTURAL = 0.05     # 5%
# Total = 1.00 (100%)
```

### Red Flags Penalty

```python
penalty = 1.0  # Start with no penalty

if critical_flags:
    penalty = 0.0  # Disqualifying

elif high_flags:
    penalty -= 0.10 per flag

elif medium_flags:
    penalty -= 0.03 per flag

# Cap at minimum 0.5
penalty = max(0.5, penalty)
```

### Classification Thresholds

```python
score >= 85  → "perfect_fit"     → "strong_recommend"
score >= 70  → "good_fit"        → "recommend"
score >= 55  → "acceptable_fit"  → "conditional_recommend"
score < 55   → "poor_fit"        → "not_recommend"
```

## Semantic Matching

### Disambiguation Strategy

1. **Context-aware resolution**: Use sector context to disambiguate polysemous terms
2. **Synonym mapping**: Use normalization data from enrichment
3. **Fuzzy matching**: Calculate similarity scores for partial matches

### Matching Algorithm

```python
similarity = calculate_semantic_similarity(term1, term2, synonyms1, synonyms2)

if similarity >= 0.7:
    # Consider a match
    match_type = "exact" if similarity == 1.0 else "semantic"
```

## Explainability

### Multi-Level Explainability

1. **Executive Summary**: One-sentence overview
2. **Decision Tree**: Step-by-step pass/fail checkpoints
3. **Key Factors**: Top positive and negative factors
4. **Agent Evidence**: Each agent provides evidence list
5. **Reasoning**: Natural language explanation per agent
6. **Score Breakdown**: Transparent weight application

### Decision Tree Format

```
1. Sector Alignment: ✓ PASS (score 85)
2. Seniority Check: ✓ PASS (score 92)
3. Skills Matching: ✓ PASS with gaps (score 78)
4. Competencies: ✓ PASS with gaps (score 75)
...
10. Final Synthesis: ✓ RECOMMEND (score 82)
```

## Performance Considerations

### Parallelization
- All specialist agents run simultaneously
- Reduces total latency significantly
- LangGraph handles parallel execution automatically

### Caching
- LLM responses could be cached for repeated evaluations
- State is lightweight (just JSON)

### Scalability
- Stateless execution (no DB required for core evaluation)
- Can process multiple candidates in parallel
- Batch processing supported for multiple candidates per job

## Testing Strategy

### Unit Tests
- Utility functions (semantic matching, scoring)
- Individual agent logic
- State transitions

### Integration Tests
- Full graph execution
- Node communication
- State propagation

### Fixtures
- Sample candidate profiles
- Sample job offers
- Expected evaluation outputs

## Configuration Management

### Environment Variables
All configurable via `.env`:
- LLM provider and model
- API keys
- Scoring weights
- Classification thresholds

### Dynamic Adaptation
- Weights can be adjusted per sector
- Thresholds can be tuned per use case
- New agents can be added without breaking existing flow

## Extensibility

### Adding New Agents

1. Create agent class extending `BaseEvaluationAgent`
2. Implement `get_prompt()` and `parse_response()`
3. Add node function in `graph/nodes/`
4. Add node to graph builder
5. Add weight to config
6. Update orchestrator to include new agent score

### Custom Prompts
All prompts are in separate files under `agents/prompts/`
- Easy to customize per use case
- Version control friendly
- A/B testing friendly

### Alternative LLMs
System supports both OpenAI and Anthropic out of the box
- Easy to add new providers
- Provider-agnostic agent implementation

## Best Practices

### Code Quality
- Full type hints (mypy strict mode)
- Comprehensive docstrings (PEP 257)
- Test coverage >80%
- Linting (Black + Ruff)

### Prompt Engineering
- Chain-of-thought reasoning
- Structured JSON outputs
- Few-shot examples where needed
- Clear evaluation criteria

### Error Handling
- Graceful degradation
- Fallback scores
- Comprehensive logging
- Never block entire workflow

## Future Enhancements

Potential improvements:
1. **Async execution**: Use async LLM calls for even better performance
2. **Caching layer**: Cache LLM responses for identical inputs
3. **Feedback loop**: Learn from human corrections
4. **Multi-language support**: Evaluate in candidate's native language
5. **Confidence calibration**: Tune confidence scores based on historical accuracy
6. **Explainability UI**: Interactive visualization of decision process
7. **A/B testing framework**: Compare different prompt versions
8. **Human-in-the-loop**: Optional manual review for edge cases

---

**Document Version**: 1.0  
**Last Updated**: November 2025  
**Maintained By**: findr Engineering Team

