# Candidate-Job Matching System with LangGraph Multi-Agent Architecture

A production-ready AI system that evaluates candidate-job compatibility using a swarm of specialized agents built with LangGraph. The system provides explainable, multi-dimensional assessments of fit between candidates and job offers.

## 🎯 Overview

This system implements a **Hybrid Collaborative-Supervisor** architecture where:

1. **Specialized agents** independently evaluate different dimensions (sector, skills, seniority, competencies, etc.)
2. Agents **collaborate** by sharing findings and validating consistency
3. An **orchestrator agent** synthesizes all evaluations into a final decision with full explainability

### Key Features

- ✅ **Multi-dimensional evaluation**: 9 specialized agents covering all aspects of candidate-job fit
- ✅ **Semantic matching**: Robust disambiguation and synonym resolution
- ✅ **Explainable AI**: Every decision is traceable to evidence
- ✅ **Dynamic weighting**: Scoring adapts based on job requirements
- ✅ **Production-ready**: Type-safe, tested, documented, and configurable
- ✅ **Sector-agnostic**: Works across industries (construction, software, healthcare, etc.)

## 📊 System Architecture

```
START
  ↓
[Input Validation]
  ↓
[Parallel Analysis Phase] ─┬─ Sector Alignment Agent
                           ├─ Skills Matching Agent
                           ├─ Seniority Calibration Agent
                           ├─ Competencies Evaluator Agent
                           ├─ Domain Expert Agent (dynamic)
                           ├─ Experience Relevance Agent
                           ├─ Cultural & Soft Fit Agent
                           └─ Salary Compensation Agent
  ↓
[Aggregation]
  ↓
[Red Flags Detector]
  ↓
[Orchestrator Synthesis]
  ↓
[Output Formatting]
  ↓
END
```

### Specialized Agents

1. **Sector Alignment Agent**: Validates sector compatibility between candidate and job
2. **Skills Matching Agent**: Compares technical and functional skills
3. **Seniority Calibration Agent**: Validates experience level alignment
4. **Competencies Evaluator Agent**: Assesses functional and soft competencies
5. **Domain Expert Agent**: Provides sector-specific evaluation (dynamically instantiated)
6. **Experience Relevance Agent**: Evaluates career trajectory and experience depth
7. **Cultural & Soft Fit Agent**: Assesses language, location, and cultural compatibility
8. **Red Flags Detector Agent**: Aggregates and classifies warning signals
9. **Salary Compensation Agent**: Evaluates salary expectations alignment (if available)
10. **Orchestrator Agent**: Synthesizes all evaluations into final decision

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd candidate_job_matching_system

# Install dependencies with Poetry
poetry install

# Or with pip
pip install -r requirements.txt

# Copy environment configuration
cp env.example .env
# Edit .env with your API keys
```

### Configuration

Edit `.env` file:

```bash
# LLM Configuration
LLM_PROVIDER=openai  # or anthropic
OPENAI_API_KEY=your-key-here
LLM_MODEL=gpt-4o
LLM_TEMPERATURE=0.1

# Scoring Weights (must sum to 1.0)
WEIGHT_SECTOR=0.20
WEIGHT_SKILLS=0.25
WEIGHT_SENIORITY=0.15
WEIGHT_COMPETENCIES=0.15
WEIGHT_DOMAIN_EXPERT=0.10
WEIGHT_EXPERIENCE=0.10
WEIGHT_CULTURAL=0.05

# Classification Thresholds
PERFECT_FIT_THRESHOLD=85
GOOD_FIT_THRESHOLD=70
ACCEPTABLE_FIT_THRESHOLD=55
```

### Basic Usage

```python
from src.main import EvaluationSystem
import json

# Initialize system
system = EvaluationSystem()

# Load candidate and job offer (enriched JSONs)
with open("candidate.json") as f:
    candidate = json.load(f)

with open("job_offer.json") as f:
    job_offer = json.load(f)

# Run evaluation
result = system.evaluate(candidate, job_offer)

# Access results
print(f"Score: {result['final_evaluation']['overall_score']}/100")
print(f"Recommendation: {result['final_evaluation']['recommendation']}")
print(f"Fit: {result['final_evaluation']['fit_classification']}")
```

### Command Line Usage

```bash
# Run evaluation from command line
python -m src.main tests/fixtures/sample_candidate.json tests/fixtures/sample_job_offer.json output/result.json

# Output will be saved to output/result.json
```

## 📝 Input Format

### Candidate Profile (Enriched)

The system expects candidates to be **semantically enriched** with:

```json
{
  "candidate_id": "uuid",
  "perfil_raw": {
    "name": "Candidate Name",
    "skills": ["skill1", "skill2"],
    "experiences": [...],
    "languages": [...]
  },
  "semantic_enrichment": {
    "sector_inference": {
      "primary_sector": "construction",
      "confidence": 0.95,
      "secondary_sectors": ["infrastructure"]
    },
    "skills_extraction": {
      "explicit_skills": [...],
      "implicit_skills": [...]
    },
    "seniority_inference": {
      "seniority_level": "lead",
      "years_experience_estimate": 9
    },
    "competencies_analysis": {...},
    "disambiguation": {...},
    "normalization": {...}
  },
  "key_insights": {...},
  "explainability": {...}
}
```

See `tests/fixtures/sample_candidate.json` for a complete example.

### Job Offer (Enriched)

Similarly, job offers must be enriched:

```json
{
  "job_id": "uuid",
  "raw_job_posting": {
    "title": "Job Title",
    "company": "Company Name",
    "description": "...",
    "min_salary_range": 60000,
    "max_salary_range": 80000
  },
  "semantic_enrichment": {
    "sector_inference": {...},
    "skills_extraction": {
      "explicit_skills": [
        {"name": "Python", "importance": "required", "level": "advanced"}
      ]
    },
    "seniority_inference": {
      "required_seniority": "lead",
      "years_experience_required": 10
    },
    "ideal_candidate_profile": {
      "must_have_experience": [...],
      "preferred_experience": [...],
      "potential_red_flags": [...]
    }
  }
}
```

See `tests/fixtures/sample_job_offer.json` for a complete example.

## 📊 Output Format

The system returns a comprehensive evaluation:

```json
{
  "evaluation_id": "uuid",
  "timestamp": "2025-11-17T17:33:00Z",
  "candidate_id": "...",
  "job_id": "...",
  "final_evaluation": {
    "overall_score": 82,
    "fit_classification": "good_fit",
    "recommendation": "recommend",
    "confidence": 0.88
  },
  "agents_evaluations": [
    {
      "agent": "sector_alignment",
      "score": 85,
      "evidence": [...],
      "reasoning": "...",
      "red_flags": []
    },
    ...
  ],
  "orchestrator_synthesis": {
    "final_score": 82,
    "score_breakdown": {...},
    "key_strengths": [...],
    "key_weaknesses": [...],
    "decision_rationale": "...",
    "next_steps_recommendation": [...]
  },
  "explainability": {
    "executive_summary": "...",
    "decision_tree": [...],
    "key_decision_factors": [...],
    "human_readable_rationale": "..."
  }
}
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_agents.py

# Run with verbose output
pytest -v
```

## 🏗️ Project Structure

```
candidate_job_matching_system/
├── pyproject.toml              # Dependencies and project metadata
├── README.md                   # This file
├── env.example                 # Environment configuration template
├── src/
│   ├── __init__.py
│   ├── main.py                # Entry point and EvaluationSystem class
│   ├── config.py              # Configuration management
│   ├── models/                # Pydantic schemas
│   │   ├── candidate_schema.py
│   │   ├── job_schema.py
│   │   └── evaluation_schema.py
│   ├── graph/                 # LangGraph implementation
│   │   ├── state.py           # State schema
│   │   ├── graph_builder.py   # Graph construction
│   │   └── nodes/             # Graph nodes (agents)
│   │       ├── input_validation.py
│   │       ├── sector_agent.py
│   │       ├── skills_agent.py
│   │       ├── seniority_agent.py
│   │       ├── competencies_agent.py
│   │       ├── domain_expert_agent.py
│   │       ├── experience_agent.py
│   │       ├── cultural_agent.py
│   │       ├── red_flags_agent.py
│   │       ├── salary_agent.py
│   │       ├── aggregation.py
│   │       ├── orchestrator.py
│   │       └── output_formatter.py
│   ├── agents/                # Agent base classes
│   │   ├── base_agent.py
│   │   └── prompts/           # Prompt templates
│   │       ├── sector_prompt.py
│   │       ├── skills_prompt.py
│   │       ├── seniority_prompt.py
│   │       ├── competencies_prompt.py
│   │       ├── domain_expert_prompt.py
│   │       ├── experience_prompt.py
│   │       ├── cultural_prompt.py
│   │       ├── red_flags_prompt.py
│   │       ├── salary_prompt.py
│   │       └── orchestrator_prompt.py
│   └── utils/                 # Utility functions
│       ├── semantic_matching.py
│       ├── disambiguation.py
│       └── scoring.py
├── tests/
│   ├── test_utils.py          # Tests for utilities
│   ├── test_agents.py         # Tests for agents
│   ├── test_graph.py          # Tests for graph workflow
│   └── fixtures/              # Sample data
│       ├── sample_candidate.json
│       └── sample_job_offer.json
└── notebooks/                 # Jupyter notebooks for analysis
```

## 🔧 Advanced Configuration

### Custom Weights

Adjust scoring weights based on your use case:

```python
from src.config import config

# For technical roles, emphasize skills
config.weight_skills = 0.35
config.weight_sector = 0.15

# For leadership roles, emphasize competencies
config.weight_competencies = 0.25
config.weight_experience = 0.15
```

### Custom LLM

Use a different LLM provider:

```python
from langchain_anthropic import ChatAnthropic
from src.graph.nodes.sector_agent import SectorAlignmentAgent

# Use Claude instead of GPT
llm = ChatAnthropic(model="claude-3-sonnet-20240229", temperature=0.1)
agent = SectorAlignmentAgent(llm=llm)
```

## 📈 Scoring Logic

### Final Score Calculation

```
final_score = Σ(agent_score * agent_weight) * red_flags_penalty
```

Where:
- Each agent score is 0-100
- Weights sum to 1.0
- Red flags penalty is 0.0-1.0 (1.0 = no penalty)

### Fit Classifications

- **Perfect Fit** (≥85): Exceptional match, all key criteria met
- **Good Fit** (70-84): Strong match, minor gaps acceptable
- **Acceptable Fit** (55-69): Adequate match, notable gaps exist
- **Poor Fit** (<55): Significant mismatches

### Recommendations

- **Strong Recommend**: Perfect fit, proceed to offer
- **Recommend**: Good fit, proceed with interview
- **Conditional Recommend**: Acceptable fit, validate gaps in interview
- **Not Recommend**: Poor fit or critical red flags present

## 🛠️ Development

### Code Quality

The codebase follows strict quality standards:

- **Type hints**: Full mypy strict mode compliance
- **Testing**: >80% code coverage
- **Documentation**: Comprehensive docstrings (PEP 257)
- **Linting**: Black + Ruff
- **Architecture**: Clean separation of concerns

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Run tests and linting (`pytest && black . && ruff check .`)
5. Commit with clear messages
6. Push and create a Pull Request

## 📚 Additional Resources

### Understanding the Architecture

The system uses **LangGraph** for orchestrating multi-agent workflows:

- **StateGraph**: Maintains shared state across agents
- **Nodes**: Individual agent evaluations
- **Edges**: Control flow between agents
- **Conditional edges**: Dynamic routing based on state

### Prompt Engineering

All agents use **Chain-of-Thought (CoT)** prompting for:
- Transparency in reasoning
- Better accuracy
- Explainability

### Semantic Matching

The system handles:
- **Polysemy**: Same term, different meanings (e.g., "automation" in QA vs manufacturing)
- **Synonyms**: Different terms, same meaning (e.g., "React" vs "ReactJS")
- **Fuzzy matching**: Partial matches and similarity scoring

## 🐛 Troubleshooting

### Common Issues

**"Weights don't sum to 1.0"**
```bash
# Check your .env file weights
# They must sum exactly to 1.0
```

**"API rate limit exceeded"**
```bash
# Reduce temperature or use a different model
LLM_TEMPERATURE=0.0
```

**"JSON parsing error"**
```bash
# LLM response wasn't valid JSON
# System automatically falls back to neutral scores
```

## 📄 License

This project is proprietary software owned by findr.

## 🤝 Support

For support, please contact: contact@findr.com

---

**Built with ❤️ using LangGraph, LangChain, and OpenAI/Anthropic LLMs**
