"""Tests for evaluation agents."""

import pytest
from unittest.mock import Mock, patch
from src.graph.nodes.sector_agent import SectorAlignmentAgent
from src.graph.nodes.skills_agent import SkillsMatchingAgent
from src.graph.nodes.seniority_agent import SeniorityCalibrationAgent


class TestSectorAlignmentAgent:
    """Tests for Sector Alignment Agent."""
    
    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM."""
        llm = Mock()
        response = Mock()
        response.content = """{
            "agent": "sector_alignment",
            "score": 85,
            "alignment_level": "strong_match",
            "primary_sector_match": true,
            "secondary_sector_overlap": [],
            "transferability_analysis": "Both in construction",
            "evidence": ["Primary sectors match"],
            "reasoning": "Strong alignment",
            "red_flags": [],
            "confidence": 0.95
        }"""
        llm.invoke.return_value = response
        return llm
    
    def test_sector_agent_evaluate(self, mock_llm):
        """Test sector agent evaluation."""
        agent = SectorAlignmentAgent(llm=mock_llm)
        
        candidate = {
            "semantic_enrichment": {
                "sector_inference": {
                    "primary_sector": "construction",
                    "confidence": 0.95,
                    "secondary_sectors": [],
                    "evidence": []
                }
            }
        }
        
        job_offer = {
            "semantic_enrichment": {
                "sector_inference": {
                    "primary_sector": "construction",
                    "confidence": 0.98,
                    "secondary_sectors": [],
                    "evidence": []
                }
            }
        }
        
        result = agent.evaluate(candidate, job_offer)
        
        assert result["agent"] == "sector_alignment"
        assert result["score"] == 85
        assert result["alignment_level"] == "strong_match"
    
    def test_sector_agent_fallback(self):
        """Test sector agent fallback on error."""
        # Create agent with broken LLM
        llm = Mock()
        llm.invoke.side_effect = Exception("API error")
        
        agent = SectorAlignmentAgent(llm=llm)
        
        candidate = {"semantic_enrichment": {"sector_inference": {}}}
        job_offer = {"semantic_enrichment": {"sector_inference": {}}}
        
        result = agent.evaluate(candidate, job_offer)
        
        # Should return fallback
        assert result["score"] == 50
        assert "error" in result["details"] or "fallback" in result["details"]


class TestSkillsMatchingAgent:
    """Tests for Skills Matching Agent."""
    
    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM."""
        llm = Mock()
        response = Mock()
        response.content = """{
            "agent": "skills_matching",
            "score": 78,
            "must_have_coverage": 0.9,
            "preferred_coverage": 0.6,
            "missing_critical_skills": [],
            "skill_gaps": [],
            "skill_overlaps": [],
            "evidence": [],
            "reasoning": "Good coverage",
            "red_flags": [],
            "confidence": 0.85
        }"""
        llm.invoke.return_value = response
        return llm
    
    def test_skills_agent_evaluate(self, mock_llm):
        """Test skills agent evaluation."""
        agent = SkillsMatchingAgent(llm=mock_llm)
        
        candidate = {
            "semantic_enrichment": {
                "skills_extraction": {
                    "explicit_skills": [{"name": "Python"}],
                    "implicit_skills": []
                }
            }
        }
        
        job_offer = {
            "semantic_enrichment": {
                "skills_extraction": {
                    "explicit_skills": [{"name": "Python", "importance": "required"}]
                }
            }
        }
        
        result = agent.evaluate(candidate, job_offer)
        
        assert result["agent"] == "skills_matching"
        assert result["score"] == 78


class TestSeniorityCalibrationAgent:
    """Tests for Seniority Calibration Agent."""
    
    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM."""
        llm = Mock()
        response = Mock()
        response.content = """{
            "agent": "seniority_calibration",
            "score": 92,
            "seniority_match": "exact_match",
            "candidate_seniority": "lead",
            "required_seniority": "lead",
            "years_gap": 0,
            "over_qualification_risk": false,
            "under_qualification_risk": false,
            "career_trajectory_alignment": "strong",
            "evidence": [],
            "reasoning": "Perfect match",
            "red_flags": [],
            "confidence": 0.95
        }"""
        llm.invoke.return_value = response
        return llm
    
    def test_seniority_agent_evaluate(self, mock_llm):
        """Test seniority agent evaluation."""
        agent = SeniorityCalibrationAgent(llm=mock_llm)
        
        candidate = {
            "semantic_enrichment": {
                "seniority_inference": {
                    "seniority_level": "lead",
                    "years_experience_estimate": 10,
                    "confidence": 0.9,
                    "evidence": []
                }
            }
        }
        
        job_offer = {
            "semantic_enrichment": {
                "seniority_inference": {
                    "required_seniority": "lead",
                    "years_experience_required": 10,
                    "confidence": 0.95
                }
            }
        }
        
        result = agent.evaluate(candidate, job_offer)
        
        assert result["agent"] == "seniority_calibration"
        assert result["score"] == 92
        assert result["seniority_match"] == "exact_match"

