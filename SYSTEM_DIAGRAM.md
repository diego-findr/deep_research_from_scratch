# System Architecture Diagrams

Visual representations of the multi-agent evaluation system.

## High-Level System Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         INPUT LAYER                              │
│  ┌────────────────────┐           ┌─────────────────────────┐  │
│  │  Enriched          │           │  Enriched Job Offer     │  │
│  │  Candidate Profile │           │  (semantic enrichment)  │  │
│  │  (semantic         │           │                         │  │
│  │   enrichment)      │           │  - Sector inference     │  │
│  │                    │           │  - Skills required      │  │
│  │  - Sector          │           │  - Seniority required   │  │
│  │  - Skills          │           │  - Competencies needed  │  │
│  │  - Seniority       │           │  - Ideal profile        │  │
│  │  - Experience      │           │                         │  │
│  └────────────────────┘           └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     INPUT VALIDATION                             │
│  ✓ Check semantic_enrichment exists                             │
│  ✓ Validate required fields                                     │
│  ✓ Early termination on failure                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              PARALLEL EVALUATION PHASE (8 agents)                │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────┐  │
│  │ Sector          │  │ Skills          │  │ Seniority     │  │
│  │ Alignment       │  │ Matching        │  │ Calibration   │  │
│  │                 │  │                 │  │               │  │
│  │ Score: 0-100    │  │ Score: 0-100    │  │ Score: 0-100  │  │
│  │ Evidence: [...]  │  │ Evidence: [...] │  │ Evidence: [...] │
│  │ Red flags: []   │  │ Red flags: []   │  │ Red flags: [] │  │
│  └─────────────────┘  └─────────────────┘  └───────────────┘  │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────┐  │
│  │ Competencies    │  │ Domain Expert   │  │ Experience    │  │
│  │ Evaluator       │  │ (Dynamic)       │  │ Relevance     │  │
│  │                 │  │                 │  │               │  │
│  │ Score: 0-100    │  │ Score: 0-100    │  │ Score: 0-100  │  │
│  │ Evidence: [...]  │  │ Evidence: [...] │  │ Evidence: [...] │
│  │ Red flags: []   │  │ Red flags: []   │  │ Red flags: [] │  │
│  └─────────────────┘  └─────────────────┘  └───────────────┘  │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐                      │
│  │ Cultural &      │  │ Salary          │                      │
│  │ Soft Fit        │  │ Compensation    │                      │
│  │                 │  │                 │                      │
│  │ Score: 0-100    │  │ Score: 0-100    │                      │
│  │ Evidence: [...]  │  │ Evidence: [...] │                      │
│  │ Red flags: []   │  │ Red flags: []   │                      │
│  └─────────────────┘  └─────────────────┘                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      AGGREGATION LAYER                           │
│  ✓ Collect all agent evaluations                                │
│  ✓ Build unified scores dictionary                              │
│  ✓ Aggregate red flags                                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   RED FLAGS DETECTOR                             │
│  ✓ Classify flags by severity (critical/high/medium)            │
│  ✓ Determine disqualifying conditions                           │
│  ✓ Calculate penalty multiplier (0.0-1.0)                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   ORCHESTRATOR SYNTHESIS                         │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  1. Apply Dynamic Weights:                             │    │
│  │     - Sector: 20%                                      │    │
│  │     - Skills: 25%                                      │    │
│  │     - Seniority: 15%                                   │    │
│  │     - Competencies: 15%                                │    │
│  │     - Domain Expert: 10%                               │    │
│  │     - Experience: 10%                                  │    │
│  │     - Cultural: 5%                                     │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  2. Calculate Final Score:                             │    │
│  │     final_score = Σ(agent_score × weight) × penalty   │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  3. Classify Fit:                                      │    │
│  │     ≥85 → Perfect Fit → Strong Recommend              │    │
│  │     ≥70 → Good Fit → Recommend                        │    │
│  │     ≥55 → Acceptable Fit → Conditional Recommend      │    │
│  │     <55 → Poor Fit → Not Recommend                    │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  4. Generate Insights:                                 │    │
│  │     - Key strengths (top 3-5)                         │    │
│  │     - Key weaknesses (top 3-5)                        │    │
│  │     - Decision rationale                               │    │
│  │     - Next steps recommendations                       │    │
│  │     - Consensus analysis                               │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    OUTPUT FORMATTING                             │
│  ✓ Structure final evaluation JSON                              │
│  ✓ Build explainability section                                 │
│  ✓ Create decision tree                                         │
│  ✓ Generate executive summary                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                         OUTPUT LAYER                             │
│  {                                                               │
│    "evaluation_id": "uuid",                                      │
│    "final_evaluation": {                                         │
│      "overall_score": 82,                                        │
│      "fit_classification": "good_fit",                           │
│      "recommendation": "recommend",                              │
│      "confidence": 0.88                                          │
│    },                                                            │
│    "agents_evaluations": [...],                                  │
│    "orchestrator_synthesis": {...},                              │
│    "explainability": {...}                                       │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
```

## Agent Interaction Pattern

```
┌─────────────────────────────────────────────────────────────────┐
│                    SHARED STATE (EvaluationState)                │
│                                                                  │
│  candidate: {...}                                                │
│  job_offer: {...}                                                │
│  sector_eval: null → {...}                                       │
│  skills_eval: null → {...}                                       │
│  ...                                                             │
└─────────────────────────────────────────────────────────────────┘
                    ↑                    ↑
                    │                    │
         ┌──────────┴─────────┬──────────┴──────────┐
         │                    │                     │
    ┌────▼────┐          ┌────▼────┐          ┌────▼────┐
    │ Agent 1 │          │ Agent 2 │          │ Agent N │
    │         │          │         │          │         │
    │ Read:   │          │ Read:   │          │ Read:   │
    │ - cand  │          │ - cand  │          │ - cand  │
    │ - job   │          │ - job   │          │ - job   │
    │         │          │         │          │         │
    │ Write:  │          │ Write:  │          │ Write:  │
    │ - eval  │          │ - eval  │          │ - eval  │
    └─────────┘          └─────────┘          └─────────┘
```

## Scoring Flow Diagram

```
┌──────────────────────────────────────────────────────────────┐
│              Individual Agent Scores (0-100)                  │
├──────────────────────────────────────────────────────────────┤
│  Sector:        85                                            │
│  Skills:        78                                            │
│  Seniority:     92                                            │
│  Competencies:  75                                            │
│  Domain Expert: 88                                            │
│  Experience:    80                                            │
│  Cultural:      95                                            │
└──────────────────────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────────────────┐
│                  Apply Weights                                │
├──────────────────────────────────────────────────────────────┤
│  85 × 0.20 = 17.0                                            │
│  78 × 0.25 = 19.5                                            │
│  92 × 0.15 = 13.8                                            │
│  75 × 0.15 = 11.25                                           │
│  88 × 0.10 = 8.8                                             │
│  80 × 0.10 = 8.0                                             │
│  95 × 0.05 = 4.75                                            │
│  ─────────────────                                            │
│  Sum = 83.1                                                   │
└──────────────────────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────────────────┐
│               Apply Red Flags Penalty                         │
├──────────────────────────────────────────────────────────────┤
│  Penalty = 0.90  (1 high severity flag)                      │
│  Final = 83.1 × 0.90 = 74.8 ≈ 75                            │
└──────────────────────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────────────────┐
│                    Classification                             │
├──────────────────────────────────────────────────────────────┤
│  Score: 75                                                    │
│  Fit: "good_fit" (70-84 range)                               │
│  Recommendation: "recommend"                                  │
└──────────────────────────────────────────────────────────────┘
```

## Explainability Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXPLAINABILITY PYRAMID                        │
│                                                                  │
│                          ┌─────────┐                             │
│                          │Executive│                             │
│                          │ Summary │                             │
│                          └─────────┘                             │
│                      (One sentence overview)                     │
│                                                                  │
│                    ┌───────────────────┐                         │
│                    │  Decision Tree    │                         │
│                    │  (Step-by-step)   │                         │
│                    └───────────────────┘                         │
│                                                                  │
│            ┌─────────────────────────────────┐                  │
│            │    Key Decision Factors         │                  │
│            │    (Top strengths/weaknesses)   │                  │
│            └─────────────────────────────────┘                  │
│                                                                  │
│    ┌───────────────────────────────────────────────┐           │
│    │         Agent Evidence & Reasoning             │           │
│    │         (Detailed per-agent analysis)          │           │
│    └───────────────────────────────────────────────┘           │
│                                                                  │
│ ┌──────────────────────────────────────────────────────┐       │
│ │            Complete Score Breakdown                   │       │
│ │            (Transparent weight application)           │       │
│ └──────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘

    Most concise ↑
                  │
                  │ Increasing
                  │ Detail
                  │
                  ↓
    Most detailed
```

## Data Flow Through System

```
Enriched JSONs
       ↓
   Validation ────────────> [fail] → Error response
       ↓ [pass]
   State Init (evaluation_id, timestamp)
       ↓
   Parallel Agents (8 concurrent LLM calls)
       ↓
   Aggregation (collect evaluations)
       ↓
   Red Flags Classification
       ↓
   Orchestrator (weighted scoring + LLM synthesis)
       ↓
   Output Formatter (structure explainability)
       ↓
   Final JSON Result
```

## Agent-LLM Interaction

```
┌──────────────┐
│    Agent     │
└──────┬───────┘
       │
       │ 1. Generate prompt (with candidate + job data)
       ↓
┌──────────────┐
│   Prompt     │  "You are a Sector Alignment Agent..."
│   Template   │  + Chain-of-Thought instructions
└──────┬───────┘  + JSON output schema
       │
       │ 2. Invoke LLM
       ↓
┌──────────────┐
│     LLM      │  (OpenAI GPT-4 / Anthropic Claude)
│  (External)  │
└──────┬───────┘
       │
       │ 3. Return structured response
       ↓
┌──────────────┐
│   Response   │  {
│   (JSON)     │    "agent": "sector_alignment",
└──────┬───────┘    "score": 85,
       │            "reasoning": "...",
       │            ...
       │          }
       │ 4. Parse JSON
       ↓
┌──────────────┐
│  Evaluation  │  Validated dict conforming
│    Dict      │  to AgentEvaluation schema
└──────┬───────┘
       │
       │ 5. Add to state
       ↓
┌──────────────┐
│    State     │  state["sector_eval"] = evaluation
└──────────────┘
```

## Error Handling Flow

```
Agent Evaluation
       ↓
   Try LLM Call
       ↓
  ┌────────────┐
  │  Success?  │
  └─────┬──────┘
        │
    ┌───┴───┐
    │       │
   Yes     No
    │       │
    │       ↓
    │   [Exception caught]
    │       ↓
    │   Create Fallback Evaluation:
    │   - score: 50 (neutral)
    │   - reasoning: "Error occurred"
    │   - red_flags: ["evaluation_error"]
    │   - fallback: true
    │       │
    └───────┴──→ Return Evaluation Dict
                       ↓
                 Add to State
                       ↓
              Workflow Continues
             (Never blocks system)
```

---

These diagrams illustrate the complete flow and interaction patterns in the multi-agent evaluation system.

