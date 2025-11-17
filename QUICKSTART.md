# Quick Start Guide

Get up and running with the Candidate-Job Matching System in 5 minutes.

## Prerequisites

- Python 3.11 or higher
- OpenAI API key or Anthropic API key
- pip or Poetry for package management

## Installation (3 steps)

### 1. Install Dependencies

```bash
# Using pip
pip install -r requirements.txt

# OR using Poetry
poetry install
```

### 2. Configure Environment

```bash
# Copy the example environment file
cp env.example .env

# Edit .env with your editor
# Add your API key:
# OPENAI_API_KEY=sk-your-key-here
```

Minimal `.env` configuration:
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=your-key-here
LLM_MODEL=gpt-4o
LLM_TEMPERATURE=0.1
```

### 3. Run Example

```bash
# Run the included example
python notebooks/example_evaluation.py

# OR use the helper scripts
./run_example.sh        # Unix/Linux/Mac
run_example.bat         # Windows
```

## Basic Usage

### Option 1: Python Script

Create a file `my_evaluation.py`:

```python
from src.main import EvaluationSystem
import json

# Initialize system
system = EvaluationSystem()

# Load your data (must be enriched JSONs)
with open("my_candidate.json") as f:
    candidate = json.load(f)

with open("my_job.json") as f:
    job = json.load(f)

# Evaluate
result = system.evaluate(candidate, job)

# Print results
print(f"Score: {result['final_evaluation']['overall_score']}/100")
print(f"Recommendation: {result['final_evaluation']['recommendation']}")
```

Run it:
```bash
python my_evaluation.py
```

### Option 2: Command Line

```bash
python -m src.main candidate.json job.json output.json
```

This will:
1. Load `candidate.json` and `job.json`
2. Run the multi-agent evaluation
3. Save complete results to `output.json`
4. Print a summary to console

## Understanding the Output

The system returns a comprehensive JSON with:

```json
{
  "final_evaluation": {
    "overall_score": 82,           // 0-100 composite score
    "fit_classification": "good_fit", // perfect/good/acceptable/poor
    "recommendation": "recommend",    // strong_recommend/recommend/conditional/not_recommend
    "confidence": 0.88               // 0.0-1.0
  },
  "agents_evaluations": [
    // Individual agent scores and reasoning
  ],
  "orchestrator_synthesis": {
    "key_strengths": [...],
    "key_weaknesses": [...],
    "decision_rationale": "...",
    "next_steps_recommendation": [...]
  },
  "explainability": {
    "executive_summary": "...",
    "decision_tree": [...],
    "key_decision_factors": [...]
  }
}
```

## Input Format

Your inputs must be **enriched** candidate and job offer JSONs. See:
- `tests/fixtures/sample_candidate.json` for candidate format
- `tests/fixtures/sample_job_offer.json` for job format

Key requirements:
- Both must have `semantic_enrichment` section
- Candidate needs: sector_inference, skills_extraction, seniority_inference
- Job needs: same fields plus ideal_candidate_profile

## Common Tasks

### Adjust Scoring Weights

Edit `.env`:
```bash
# Give more weight to skills
WEIGHT_SKILLS=0.30
WEIGHT_SECTOR=0.15

# Weights must sum to 1.0
```

### Change LLM Model

Edit `.env`:
```bash
LLM_MODEL=gpt-4o-mini       # Faster, cheaper
# OR
LLM_MODEL=gpt-4             # More accurate
```

### Use Anthropic Instead

Edit `.env`:
```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-key-here
LLM_MODEL=claude-3-sonnet-20240229
```

### Save Results to File

```python
system = EvaluationSystem()
result = system.evaluate_from_files(
    "candidate.json",
    "job.json",
    "output/result.json"  # Will be created automatically
)
```

## Troubleshooting

### "Weights don't sum to 1.0"

Check your `.env` file. All `WEIGHT_*` variables must add up to exactly 1.0.

```bash
WEIGHT_SECTOR=0.20
WEIGHT_SKILLS=0.25
WEIGHT_SENIORITY=0.15
WEIGHT_COMPETENCIES=0.15
WEIGHT_DOMAIN_EXPERT=0.10
WEIGHT_EXPERIENCE=0.10
WEIGHT_CULTURAL=0.05
# Total = 1.00 ✓
```

### "Missing API key"

Ensure your `.env` file has the correct key for your provider:
```bash
# For OpenAI
OPENAI_API_KEY=sk-...

# For Anthropic
ANTHROPIC_API_KEY=sk-ant-...
```

### "Validation failed"

Your input JSONs must be **enriched** (have semantic_enrichment section). 

Check that your JSONs match the format in `tests/fixtures/`.

### Rate Limiting

If you hit API rate limits:
1. Reduce temperature: `LLM_TEMPERATURE=0.0`
2. Use a smaller model: `LLM_MODEL=gpt-3.5-turbo`
3. Add delays between evaluations

## Next Steps

- 📖 Read [README.md](README.md) for detailed usage
- 🏗️ Read [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- 🧪 Run tests: `pytest`
- 📊 Check sample files in `tests/fixtures/`

## Example: Complete Workflow

```python
#!/usr/bin/env python
"""Complete evaluation workflow example."""

import json
from pathlib import Path
from src.main import EvaluationSystem

def main():
    # 1. Initialize
    print("Initializing system...")
    system = EvaluationSystem()
    
    # 2. Load data
    print("Loading candidate and job...")
    with open("tests/fixtures/sample_candidate.json") as f:
        candidate = json.load(f)
    
    with open("tests/fixtures/sample_job_offer.json") as f:
        job = json.load(f)
    
    # 3. Evaluate
    print("Running evaluation (this may take 30-60 seconds)...")
    result = system.evaluate(candidate, job)
    
    # 4. Extract key info
    score = result['final_evaluation']['overall_score']
    fit = result['final_evaluation']['fit_classification']
    rec = result['final_evaluation']['recommendation']
    
    # 5. Display
    print(f"\n{'='*60}")
    print(f"EVALUATION COMPLETE")
    print(f"{'='*60}")
    print(f"Score: {score}/100")
    print(f"Fit: {fit}")
    print(f"Recommendation: {rec}")
    
    # 6. Save
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / "evaluation_result.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\nFull results saved to: {output_file}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
```

Save as `evaluate.py` and run:
```bash
python evaluate.py
```

## Getting Help

- 📧 Support: contact@findr.com
- 📚 Full docs: See README.md and ARCHITECTURE.md
- 🐛 Issues: Check troubleshooting section above

---

**Ready to start? Run the example:**
```bash
python notebooks/example_evaluation.py
```

