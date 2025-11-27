# Candidate Evaluation Service

A production-ready microservice for AI-powered candidate evaluation using LangGraph, FastAPI, and Docker.

## Overview

This service implements a multi-agent workflow to evaluate job candidates against job offers. It uses three specialized agents (Technical, Experience, Cultural) to analyze the candidate, debate their findings, and reach a consensus.

## Architecture

- **Framework**: FastAPI
- **Orchestration**: LangGraph
- **LLM**: OpenAI GPT-4 (configurable)
- **Dependency Management**: uv
- **Containerization**: Docker

### Project Structure

```
candidate_evaluation_service/
├── app/
│   ├── api/            # API Routes
│   ├── core/           # Core logic (Graph, Config, Prompts)
│   ├── schemas/        # Pydantic Models
│   └── main.py         # App Entrypoint
├── tests/              # Tests
├── Dockerfile          # Production Dockerfile
├── docker-compose.yml  # Local development
└── pyproject.toml      # Dependencies
```

## Getting Started

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- OpenAI API Key

### Local Development

1. **Install Dependencies** (using uv):
   ```bash
   pip install uv
   uv sync
   ```

2. **Set Environment Variables**:
   Create a `.env` file:
   ```bash
   OPENAI_API_KEY=sk-...
   MODEL_NAME=openai:gpt-4.1
   ```

3. **Run Locally**:
   ```bash
   uvicorn app.main:app --reload
   ```

### Running with Docker

1. **Build and Run**:
   ```bash
   docker-compose up --build
   ```

2. **Access API**:
   The API will be available at `http://localhost:8000`.
   Docs: `http://localhost:8000/docs`

## API Usage

### POST /api/v1/evaluate

Evaluates a candidate.

**Request Body**:
```json
{
  "enriched_candidate": { ... },
  "enriched_job": { ... },
  "max_debate_rounds": 2
}
```

**Response**:
Returns the full evaluation state, including:
- `consensus_decision`: Final decision and reasoning.
- `agent_evaluations`: Individual agent reports.
- `debate_messages`: Transcript of agent debate.

## Deployment on GCP

### Cloud Run

1. **Build Image**:
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/candidate-eval-service
   ```

2. **Deploy**:
   ```bash
   gcloud run deploy candidate-eval-service \
     --image gcr.io/PROJECT_ID/candidate-eval-service \
     --platform managed \
     --region us-central1 \
     --set-env-vars OPENAI_API_KEY=...
   ```

## License

Proprietary.
