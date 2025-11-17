# Project Documentation Index

Complete guide to navigating the Candidate-Job Matching System documentation.

## 🚀 Quick Navigation

### For First-Time Users
1. **[QUICKSTART.md](QUICKSTART.md)** - Get running in 5 minutes
2. **[README.md](README.md)** - Complete user guide
3. Run the example: `python notebooks/example_evaluation.py`

### For Developers
1. **[ARCHITECTURE.md](ARCHITECTURE.md)** - Technical deep dive
2. **[IMPLEMENTATION_LOG.md](IMPLEMENTATION_LOG.md)** - Complete implementation record
3. **[SYSTEM_DIAGRAM.md](SYSTEM_DIAGRAM.md)** - Visual architecture diagrams
4. Source code: `src/` directory

### For Project Managers
1. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Executive summary
2. **[README.md](README.md)** - Feature overview
3. **[IMPLEMENTATION_LOG.md](IMPLEMENTATION_LOG.md)** - Deliverables checklist

## 📚 Documentation Files

### User Documentation

| File | Description | Audience |
|------|-------------|----------|
| **[QUICKSTART.md](QUICKSTART.md)** | 5-minute getting started guide | New users |
| **[README.md](README.md)** | Comprehensive user guide with examples | All users |
| **env.example** | Environment configuration template | Developers |

### Technical Documentation

| File | Description | Audience |
|------|-------------|----------|
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | System architecture, patterns, and algorithms | Technical leads, architects |
| **[SYSTEM_DIAGRAM.md](SYSTEM_DIAGRAM.md)** | Visual diagrams of system flow | Developers, architects |
| **[IMPLEMENTATION_LOG.md](IMPLEMENTATION_LOG.md)** | Complete implementation record | Project managers, developers |
| **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** | High-level project overview | All stakeholders |

### Code Documentation

| Location | Description |
|----------|-------------|
| **src/** | Source code with inline docstrings |
| **tests/** | Test suite with examples |
| **tests/fixtures/** | Sample input data |

## 🎯 Documentation by Use Case

### "I want to run an evaluation"
→ [QUICKSTART.md](QUICKSTART.md) → Run `python notebooks/example_evaluation.py`

### "I want to understand how it works"
→ [README.md](README.md) (Overview) → [ARCHITECTURE.md](ARCHITECTURE.md) (Details)

### "I want to integrate this into my system"
→ [README.md](README.md) (Usage section) → `src/main.py` (EvaluationSystem class)

### "I want to customize scoring weights"
→ [QUICKSTART.md](QUICKSTART.md) (Configuration) → `env.example`

### "I want to add a new agent"
→ [ARCHITECTURE.md](ARCHITECTURE.md) (Extensibility section)

### "I want to understand the codebase"
→ [ARCHITECTURE.md](ARCHITECTURE.md) → [IMPLEMENTATION_LOG.md](IMPLEMENTATION_LOG.md) → Source code

### "I want to see sample data"
→ `tests/fixtures/sample_candidate.json` and `tests/fixtures/sample_job_offer.json`

### "I want to visualize the system"
→ [SYSTEM_DIAGRAM.md](SYSTEM_DIAGRAM.md)

## 📁 Project Structure Overview

```
candidate_job_matching_system/
├── 📚 Documentation
│   ├── README.md                   # Main user guide
│   ├── QUICKSTART.md              # Quick start (5 min)
│   ├── ARCHITECTURE.md            # Technical deep dive
│   ├── SYSTEM_DIAGRAM.md          # Visual diagrams
│   ├── PROJECT_SUMMARY.md         # Executive summary
│   ├── IMPLEMENTATION_LOG.md      # Implementation record
│   └── INDEX.md                   # This file
│
├── ⚙️ Configuration
│   ├── pyproject.toml             # Poetry dependencies
│   ├── requirements.txt           # Pip dependencies
│   ├── env.example                # Environment template
│   └── .gitignore                 # Git exclusions
│
├── 💻 Source Code
│   └── src/
│       ├── main.py                # Entry point
│       ├── config.py              # Configuration
│       ├── models/                # Pydantic schemas (3 files)
│       ├── graph/                 # LangGraph (state + builder + 13 nodes)
│       ├── agents/                # Agent base + 10 prompts
│       └── utils/                 # Utilities (3 files)
│
├── 🧪 Tests
│   └── tests/
│       ├── test_utils.py          # Utility tests
│       ├── test_agents.py         # Agent tests
│       ├── test_graph.py          # Graph tests
│       └── fixtures/              # Sample data (2 files)
│
├── 📓 Examples
│   ├── notebooks/
│   │   └── example_evaluation.py # Standalone example
│   ├── run_example.sh             # Unix helper
│   └── run_example.bat            # Windows helper
│
└── 📊 Output
    └── output/                    # Generated results
```

## 🔍 Code Documentation Navigation

### Entry Points
- **CLI**: `python -m src.main candidate.json job.json`
- **Programmatic**: `from src.main import EvaluationSystem`
- **Example**: `python notebooks/example_evaluation.py`

### Core Components
- **Graph Builder**: `src/graph/graph_builder.py`
- **State Schema**: `src/graph/state.py`
- **Base Agent**: `src/agents/base_agent.py`
- **Configuration**: `src/config.py`

### Agents (in `src/graph/nodes/`)
1. `input_validation.py` - Input validation
2. `sector_agent.py` - Sector alignment
3. `skills_agent.py` - Skills matching
4. `seniority_agent.py` - Seniority calibration
5. `competencies_agent.py` - Competencies evaluation
6. `domain_expert_agent.py` - Domain-specific evaluation
7. `experience_agent.py` - Experience relevance
8. `cultural_agent.py` - Cultural & soft fit
9. `salary_agent.py` - Salary compensation
10. `red_flags_agent.py` - Red flags detection
11. `aggregation.py` - Evaluation aggregation
12. `orchestrator.py` - Final synthesis
13. `output_formatter.py` - Output formatting

### Utilities (in `src/utils/`)
- `semantic_matching.py` - Matching algorithms
- `disambiguation.py` - Polysemy resolution
- `scoring.py` - Scoring and classification

### Prompts (in `src/agents/prompts/`)
- One prompt file per agent (10 files total)
- Chain-of-Thought templates
- Structured JSON output schemas

## 🎓 Learning Path

### Beginner
1. Read [QUICKSTART.md](QUICKSTART.md)
2. Run example: `python notebooks/example_evaluation.py`
3. Review sample data: `tests/fixtures/`
4. Read [README.md](README.md) Overview section

### Intermediate
1. Read [README.md](README.md) completely
2. Review [SYSTEM_DIAGRAM.md](SYSTEM_DIAGRAM.md)
3. Explore `src/main.py` and `src/config.py`
4. Run tests: `pytest tests/`

### Advanced
1. Read [ARCHITECTURE.md](ARCHITECTURE.md)
2. Study [IMPLEMENTATION_LOG.md](IMPLEMENTATION_LOG.md)
3. Review graph builder: `src/graph/graph_builder.py`
4. Study agent implementations: `src/graph/nodes/`
5. Review utilities: `src/utils/`

## 📊 Key Metrics

- **Documentation Pages**: 7 major docs + inline docstrings
- **Total Documentation**: ~5,000+ lines
- **Code Files**: 35+
- **Lines of Code**: ~3,000+ (excluding tests)
- **Test Files**: 3
- **Sample Data**: 2 complete examples

## 🔗 External References

### LangGraph Resources
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangGraph Academy](https://github.com/langchain-ai/langgraph-academy)

### Python Resources
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Poetry Documentation](https://python-poetry.org/docs/)

### LLM Providers
- [OpenAI API](https://platform.openai.com/docs)
- [Anthropic API](https://docs.anthropic.com/)

## 🤝 Support

For questions or issues:
- 📧 Email: contact@findr.com
- 📚 Documentation: See files above
- 🐛 Issues: Check [README.md](README.md) Troubleshooting section

## ✅ Document Status

| Document | Status | Last Updated |
|----------|--------|--------------|
| INDEX.md | ✅ Complete | Nov 2025 |
| QUICKSTART.md | ✅ Complete | Nov 2025 |
| README.md | ✅ Complete | Nov 2025 |
| ARCHITECTURE.md | ✅ Complete | Nov 2025 |
| SYSTEM_DIAGRAM.md | ✅ Complete | Nov 2025 |
| IMPLEMENTATION_LOG.md | ✅ Complete | Nov 2025 |
| PROJECT_SUMMARY.md | ✅ Complete | Nov 2025 |

---

**Project Version**: 1.0  
**Documentation Version**: 1.0  
**Status**: Production Ready ✅

**Start here**: [QUICKSTART.md](QUICKSTART.md)

