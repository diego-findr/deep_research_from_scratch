"""
Utility functions for semantic matching, disambiguation, and scoring.
"""

from src.utils.semantic_matching import (
    calculate_semantic_similarity,
    match_skills,
    match_sectors,
)
from src.utils.disambiguation import resolve_term_ambiguity
from src.utils.scoring import (
    calculate_weighted_score,
    classify_fit_level,
    determine_recommendation,
)

__all__ = [
    "calculate_semantic_similarity",
    "match_skills",
    "match_sectors",
    "resolve_term_ambiguity",
    "calculate_weighted_score",
    "classify_fit_level",
    "determine_recommendation",
]

