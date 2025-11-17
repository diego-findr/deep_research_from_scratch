"""Tests for the LangGraph evaluation workflow."""

import pytest
from unittest.mock import Mock, patch
from src.graph.state import create_initial_state
from src.graph.nodes.input_validation import validate_inputs
from src.graph.nodes.aggregation import aggregate_evaluations
from src.graph.nodes.output_formatter import format_output


class TestGraphNodes:
    """Tests for graph node functions."""
    
    def test_create_initial_state(self):
        """Test initial state creation."""
        candidate = {"candidate_id": "123"}
        job_offer = {"job_id": "456"}
        
        state = create_initial_state(candidate, job_offer)
        
        assert state["candidate"] == candidate
        assert state["job_offer"] == job_offer
        assert state["current_phase"] == "input_validation"
        assert "evaluation_id" in state
        assert "timestamp" in state
        assert state["errors"] == []
    
    def test_validate_inputs_success(self):
        """Test successful input validation."""
        state = {
            "candidate": {
                "semantic_enrichment": {"sector_inference": {}}
            },
            "job_offer": {
                "semantic_enrichment": {"sector_inference": {}}
            },
        }
        
        result = validate_inputs(state)
        
        assert result["current_phase"] == "analysis"
        assert result["errors"] == []
    
    def test_validate_inputs_failure(self):
        """Test failed input validation."""
        state = {
            "candidate": {},  # Missing semantic_enrichment
            "job_offer": {},
        }
        
        result = validate_inputs(state)
        
        assert result["current_phase"] == "validation_failed"
        assert len(result["errors"]) > 0
    
    def test_aggregate_evaluations(self):
        """Test evaluation aggregation."""
        state = {
            "sector_eval": {
                "agent": "sector_alignment",
                "score": 85,
                "red_flags": []
            },
            "skills_eval": {
                "agent": "skills_matching",
                "score": 78,
                "red_flags": ["missing_skill"]
            },
        }
        
        result = aggregate_evaluations(state)
        
        assert len(result["all_evaluations"]) == 2
        assert "sector_alignment" in result["aggregated_scores"]
        assert result["aggregated_scores"]["sector_alignment"] == 85
        assert result["current_phase"] == "aggregation"
    
    def test_format_output(self):
        """Test output formatting."""
        state = {
            "evaluation_id": "test-123",
            "timestamp": "2025-01-01T00:00:00Z",
            "candidate": {
                "candidate_id": "cand-123",
                "perfil_raw": {"name": "John Doe"}
            },
            "job_offer": {
                "job_id": "job-456",
                "raw_job_posting": {
                    "title": "Software Engineer",
                    "company": "TechCorp"
                }
            },
            "all_evaluations": [
                {"agent": "sector", "score": 85, "reasoning": "Good match"}
            ],
            "orchestrator_output": {
                "final_score": 82,
                "fit_classification": "good_fit",
                "recommendation": "recommend",
                "key_strengths": ["Strength 1"],
                "key_weaknesses": ["Weakness 1"],
                "decision_rationale": "Good candidate",
                "confidence": 0.88,
            },
        }
        
        result = format_output(state)
        
        assert "final_evaluation" in result
        assert result["current_phase"] == "complete"
        
        final_eval = result["final_evaluation"]
        assert final_eval["evaluation_id"] == "test-123"
        assert final_eval["candidate_id"] == "cand-123"
        assert final_eval["job_id"] == "job-456"
        assert "explainability" in final_eval
        assert "executive_summary" in final_eval["explainability"]


class TestGraphIntegration:
    """Integration tests for the complete graph."""
    
    @pytest.fixture
    def sample_candidate(self):
        """Sample candidate data."""
        return {
            "candidate_id": "test-candidate-1",
            "perfil_raw": {
                "name": "Test Candidate",
                "experiences": [],
                "languages": [],
            },
            "semantic_enrichment": {
                "sector_inference": {
                    "primary_sector": "construction",
                    "confidence": 0.95,
                    "secondary_sectors": [],
                    "evidence": []
                },
                "skills_extraction": {
                    "explicit_skills": [{"name": "Python"}],
                    "implicit_skills": []
                },
                "seniority_inference": {
                    "seniority_level": "mid",
                    "years_experience_estimate": 5,
                    "confidence": 0.9,
                    "evidence": []
                },
                "competencies_analysis": {
                    "competencies": []
                },
                "disambiguation": {},
                "normalization": {}
            },
            "key_insights": {},
            "explainability": {}
        }
    
    @pytest.fixture
    def sample_job_offer(self):
        """Sample job offer data."""
        return {
            "job_id": "test-job-1",
            "raw_job_posting": {
                "title": "Software Engineer",
                "company": "TechCorp",
                "description": "Build software",
                "mandatory_languages": [],
                "optional_languages": [],
                "locations": [],
                "remote_amount": "hybrid"
            },
            "semantic_enrichment": {
                "sector_inference": {
                    "primary_sector": "software_development",
                    "confidence": 0.98,
                    "secondary_sectors": [],
                    "evidence": []
                },
                "skills_extraction": {
                    "explicit_skills": [{"name": "Python", "importance": "required"}]
                },
                "seniority_inference": {
                    "required_seniority": "mid",
                    "years_experience_required": 5,
                    "confidence": 0.95
                },
                "competencies_analysis": {
                    "required_competencies": []
                },
                "ideal_candidate_profile": {
                    "must_have_experience": [],
                    "preferred_experience": [],
                    "potential_red_flags": []
                },
                "normalization": {}
            },
            "key_insights": {},
            "explainability": {}
        }
    
    def test_initial_state_creation(self, sample_candidate, sample_job_offer):
        """Test creating initial state with sample data."""
        state = create_initial_state(sample_candidate, sample_job_offer)
        
        assert state["candidate"]["candidate_id"] == "test-candidate-1"
        assert state["job_offer"]["job_id"] == "test-job-1"
        assert state["current_phase"] == "input_validation"

