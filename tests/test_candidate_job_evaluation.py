"""Tests for candidate-job evaluation system."""

import json
from pathlib import Path

import pytest

from src.candidate_job_evaluation import (
    EvaluationConfig,
    evaluate_candidate_for_job,
)


@pytest.fixture
def test_data_dir():
    """Get test data directory."""
    return Path(__file__).parent


@pytest.fixture
def candidate_natalia(test_data_dir):
    """Load enriched Natalia candidate."""
    with open(test_data_dir / "candidates" / "outputs" / "enriched_natalia.json") as f:
        return json.load(f)


@pytest.fixture
def job_acciona(test_data_dir):
    """Load enriched Acciona job."""
    with open(test_data_dir / "jobs" / "outputs" / "enriched_acciona_job.json") as f:
        return json.load(f)


@pytest.fixture
def evaluation_config():
    """Create test evaluation configuration."""
    return EvaluationConfig(
        llm_model="gpt-4o",
        llm_temperature=0.1,
    )


def test_evaluation_config_defaults():
    """Test that EvaluationConfig has proper defaults."""
    config = EvaluationConfig()
    
    assert config.llm_model == "gpt-4o"
    assert config.llm_temperature == 0.1
    assert config.highly_recommend_threshold == 85
    assert config.recommend_threshold == 70
    assert config.acceptable_threshold == 55
    
    # Check default weights
    assert "sector" in config.default_weights
    assert "skills" in config.default_weights
    assert "seniority" in config.default_weights
    assert "competencies" in config.default_weights
    assert "domain_expert" in config.default_weights
    
    # Check sector adjustments exist
    assert "software" in config.sector_weight_adjustments
    assert "construction" in config.sector_weight_adjustments
    assert "finance" in config.sector_weight_adjustments


def test_evaluation_config_custom():
    """Test custom configuration."""
    config = EvaluationConfig(
        llm_temperature=0.5,
        highly_recommend_threshold=90,
    )
    
    assert config.llm_temperature == 0.5
    assert config.highly_recommend_threshold == 90
    # Defaults should still work
    assert config.recommend_threshold == 70


@pytest.mark.skipif(
    not Path(__file__).parent / "candidates" / "outputs" / "enriched_natalia.json",
    reason="Test data not available"
)
def test_natalia_acciona_evaluation_structure(candidate_natalia, job_acciona, evaluation_config):
    """Test that evaluation returns proper structure (without LLM call)."""
    # This test validates the structure without actually calling LLM
    # In a real test environment with API keys, you would call:
    # result = evaluate_candidate_for_job(candidate_natalia, job_acciona, evaluation_config)
    
    # For now, just validate input structure
    assert "candidato_id" in candidate_natalia
    assert "semantic_enrichment" in candidate_natalia
    assert "perfil_raw" in candidate_natalia
    
    assert "job_id" in job_acciona
    assert "semantic_enrichment" in job_acciona
    assert "raw_job_posting" in job_acciona
    
    # Validate enrichment structure
    candidate_enrichment = candidate_natalia["semantic_enrichment"]
    assert "analysis_components" in candidate_enrichment
    assert "sector_inference" in candidate_enrichment["analysis_components"]
    assert "skills_extraction" in candidate_enrichment["analysis_components"]
    assert "seniority_inference" in candidate_enrichment["analysis_components"]
    
    job_enrichment = job_acciona["semantic_enrichment"]
    assert "analysis_components" in job_enrichment
    assert "sector_inference" in job_enrichment["analysis_components"]


def test_sector_matching_logic(candidate_natalia, job_acciona):
    """Test sector matching logic."""
    candidate_sector = candidate_natalia["semantic_enrichment"]["analysis_components"]["sector_inference"]["primary_sector"]
    job_sector = job_acciona["semantic_enrichment"]["analysis_components"]["sector_inference"]["primary_sector"]
    
    # Natalia: occupational_health_and_safety_in_construction
    # Job: construction
    # Should be a strong match
    assert "construction" in candidate_sector
    assert job_sector == "construction"


def test_seniority_matching_logic(candidate_natalia, job_acciona):
    """Test seniority matching logic."""
    candidate_seniority = candidate_natalia["semantic_enrichment"]["analysis_components"]["seniority_inference"]["seniority_level"]
    candidate_years = candidate_natalia["semantic_enrichment"]["analysis_components"]["seniority_inference"]["years_experience_estimate"]
    
    job_seniority = job_acciona["semantic_enrichment"]["analysis_components"]["seniority_inference"]["required_seniority"]
    job_years = job_acciona["semantic_enrichment"]["analysis_components"]["seniority_inference"]["years_experience_required"]
    
    # Natalia: lead with 9 years
    # Job: lead with 10 years required
    # Should be close match
    assert candidate_seniority == "lead"
    assert job_seniority == "lead"
    assert candidate_years >= 8  # Lead level minimum
    assert abs(candidate_years - job_years) <= 2  # Within 2 years


def test_skills_extraction(candidate_natalia, job_acciona):
    """Test skills extraction structure."""
    candidate_skills = candidate_natalia["semantic_enrichment"]["structured_skills"]
    job_skills = job_acciona["semantic_enrichment"]["structured_skills"]
    
    assert "explicit" in candidate_skills
    assert "implicit" in candidate_skills
    assert "explicit" in job_skills
    assert "implicit" in job_skills
    
    # Should have some skills
    assert len(candidate_skills["explicit"]) > 0
    assert len(candidate_skills["implicit"]) > 0


def test_competencies_structure(candidate_natalia, job_acciona):
    """Test competencies structure."""
    candidate_comps = candidate_natalia["semantic_enrichment"]["structured_competencies"]
    job_comps = job_acciona["semantic_enrichment"]["structured_competencies"]
    
    assert isinstance(candidate_comps, list)
    assert isinstance(job_comps, list)
    assert len(candidate_comps) > 0
    assert len(job_comps) > 0
    
    # Check competency structure
    for comp in candidate_comps[:1]:  # Check first one
        assert "competency" in comp
        assert "type" in comp
        assert "level" in comp


def test_red_flags_structure(job_acciona):
    """Test red flags structure in job."""
    ideal_candidate = job_acciona["semantic_enrichment"]["ideal_candidate"]
    
    assert "must_have_experience" in ideal_candidate
    assert "preferred_experience" in ideal_candidate
    assert "potential_red_flags" in ideal_candidate
    
    assert isinstance(ideal_candidate["potential_red_flags"], list)


def test_disambiguation_map(candidate_natalia):
    """Test disambiguation map structure."""
    disambiguation = candidate_natalia["semantic_enrichment"]["disambiguation_map"]
    
    assert isinstance(disambiguation, dict)
    # Should have PRL disambiguated
    assert "PRL" in disambiguation
    assert disambiguation["PRL"]["meaning"] is not None
    assert disambiguation["PRL"]["confidence"] > 0.8


def test_synonym_map(candidate_natalia):
    """Test synonym map structure."""
    synonyms = candidate_natalia["semantic_enrichment"]["synonym_map"]
    
    assert isinstance(synonyms, dict)
    # Should have some synonym mappings
    assert len(synonyms) > 0


@pytest.mark.integration
@pytest.mark.skipif(
    not Path(__file__).parent / "candidates" / "outputs" / "enriched_natalia.json",
    reason="Integration test requires test data and API key"
)
def test_full_evaluation_integration(candidate_natalia, job_acciona, evaluation_config):
    """
    Integration test for full evaluation.
    
    This test requires:
    - OpenAI API key set in environment
    - Test data available
    
    Run with: pytest tests/test_candidate_job_evaluation.py::test_full_evaluation_integration -m integration
    """
    pytest.skip("Requires OpenAI API key - run manually in dev environment")
    
    # Uncomment to run with API key:
    # result = evaluate_candidate_for_job(
    #     candidate=candidate_natalia,
    #     job_offer=job_acciona,
    #     config=evaluation_config
    # )
    # 
    # # Validate result structure
    # assert "final_evaluation" in result
    # final = result["final_evaluation"]
    # 
    # # Check required fields
    # assert 0 <= final.overall_score <= 100
    # assert final.recommendation in ["highly_recommend", "recommend", "acceptable", "not_recommend"]
    # assert len(final.summary) > 0
    # assert isinstance(final.strengths, list)
    # assert isinstance(final.concerns, list)
    # assert isinstance(final.agent_scores, dict)
    # 
    # # Check agent evaluations present
    # assert result.get("sector_evaluation") is not None
    # assert result.get("skills_evaluation") is not None
    # assert result.get("seniority_evaluation") is not None
    # assert result.get("competencies_evaluation") is not None
    # assert result.get("red_flags_evaluation") is not None
    # 
    # # For construction sector, should expect reasonable match
    # # (Natalia is construction health & safety, job is construction management)
    # assert final.overall_score >= 60  # Should be at least acceptable


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
