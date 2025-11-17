"""Tests for utility functions."""

import pytest
from src.utils.semantic_matching import (
    normalize_term,
    calculate_semantic_similarity,
    match_skills,
    match_sectors,
    compare_levels,
)
from src.utils.scoring import (
    calculate_weighted_score,
    classify_fit_level,
    determine_recommendation,
    calculate_red_flags_penalty,
    normalize_confidence_scores,
    analyze_consensus,
)
from src.utils.disambiguation import resolve_term_ambiguity


class TestSemanticMatching:
    """Tests for semantic matching utilities."""
    
    def test_normalize_term(self):
        """Test term normalization."""
        assert normalize_term("React.js") == "reactjs"
        assert normalize_term("  Python  ") == "python"
        assert normalize_term("Node-JS") == "nodejs"
    
    def test_calculate_semantic_similarity_exact(self):
        """Test exact match similarity."""
        similarity = calculate_semantic_similarity("Python", "python")
        assert similarity == 1.0
    
    def test_calculate_semantic_similarity_synonym(self):
        """Test synonym matching."""
        similarity = calculate_semantic_similarity(
            "React", "ReactJS", [], ["React", "React.js"]
        )
        assert similarity == 1.0
    
    def test_calculate_semantic_similarity_partial(self):
        """Test partial match."""
        similarity = calculate_semantic_similarity("JavaScript", "Java")
        assert 0.5 < similarity < 1.0
    
    def test_calculate_semantic_similarity_no_match(self):
        """Test no match."""
        similarity = calculate_semantic_similarity("Python", "Rust")
        assert similarity == 0.0
    
    def test_match_skills_perfect(self):
        """Test perfect skills match."""
        candidate = [{"name": "Python", "level": "advanced"}]
        required = [{"name": "Python", "importance": "required"}]
        
        coverage, matches, missing = match_skills(candidate, required)
        
        assert coverage == 1.0
        assert len(matches) == 1
        assert len(missing) == 0
    
    def test_match_skills_missing(self):
        """Test missing required skills."""
        candidate = [{"name": "Python"}]
        required = [
            {"name": "Python", "importance": "required"},
            {"name": "Java", "importance": "required"},
        ]
        
        coverage, matches, missing = match_skills(candidate, required)
        
        assert coverage == 0.5
        assert "Java" in missing
    
    def test_match_sectors_perfect(self):
        """Test perfect sector match."""
        is_match, level, overlaps = match_sectors("construction", "construction")
        
        assert is_match is True
        assert level == "perfect_match"
    
    def test_match_sectors_secondary(self):
        """Test secondary sector match."""
        is_match, level, overlaps = match_sectors(
            "construction",
            "infrastructure",
            ["infrastructure"],
            []
        )
        
        assert is_match is True
        assert level == "strong_match"
    
    def test_match_sectors_mismatch(self):
        """Test sector mismatch."""
        is_match, level, overlaps = match_sectors("healthcare", "software_development")
        
        assert is_match is False
        assert level == "mismatch"
    
    def test_compare_levels(self):
        """Test level comparison."""
        is_sufficient, gap = compare_levels("advanced", "mid")
        
        assert is_sufficient is True
        assert gap > 0


class TestScoring:
    """Tests for scoring utilities."""
    
    def test_calculate_weighted_score(self):
        """Test weighted score calculation."""
        scores = {"sector": 85, "skills": 78}
        weights = {"sector": 0.5, "skills": 0.5}
        
        final_score, breakdown = calculate_weighted_score(scores, weights)
        
        assert final_score == 81.5
        assert "sector" in breakdown
        assert breakdown["sector"]["weighted_score"] == 42.5
    
    def test_classify_fit_level(self):
        """Test fit classification."""
        assert classify_fit_level(90) == "perfect_fit"
        assert classify_fit_level(75) == "good_fit"
        assert classify_fit_level(60) == "acceptable_fit"
        assert classify_fit_level(40) == "poor_fit"
    
    def test_determine_recommendation(self):
        """Test recommendation determination."""
        assert determine_recommendation(90, "perfect_fit", []) == "strong_recommend"
        assert determine_recommendation(75, "good_fit", []) == "recommend"
        assert determine_recommendation(90, "perfect_fit", ["critical"]) == "not_recommend"
    
    def test_calculate_red_flags_penalty(self):
        """Test red flags penalty calculation."""
        # No flags
        penalty = calculate_red_flags_penalty([], [], [])
        assert penalty == 1.0
        
        # Critical flag
        penalty = calculate_red_flags_penalty(["sector_mismatch"], [], [])
        assert penalty == 0.0
        
        # High flags
        penalty = calculate_red_flags_penalty([], ["gap1"], [])
        assert penalty == 0.9
    
    def test_normalize_confidence_scores(self):
        """Test confidence normalization."""
        confidence = normalize_confidence_scores([0.9, 0.8, 0.95])
        assert 0.8 < confidence < 0.95
    
    def test_analyze_consensus(self):
        """Test consensus analysis."""
        scores = {"sector": 90, "skills": 50, "seniority": 75}
        consensus = analyze_consensus(scores)
        
        assert "sector" in consensus["unanimous_positive"]
        assert "skills" in consensus["unanimous_negative"]


class TestDisambiguation:
    """Tests for disambiguation utilities."""
    
    def test_resolve_term_ambiguity_software(self):
        """Test disambiguation in software context."""
        result = resolve_term_ambiguity("automation", "software_development", None)
        
        assert "test" in result["resolved_term"].lower() or "qa" in result["resolved_term"].lower()
    
    def test_resolve_term_ambiguity_construction(self):
        """Test disambiguation in construction context."""
        result = resolve_term_ambiguity("automation", "construction", None)
        
        assert "industrial" in result["resolved_term"].lower()
    
    def test_resolve_term_ambiguity_unambiguous(self):
        """Test unambiguous term."""
        result = resolve_term_ambiguity("python_programming", "software", None)
        
        assert result["resolved_term"] == "python_programming"
        assert result["confidence"] == 1.0

