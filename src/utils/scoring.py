"""
Scoring utilities for calculating final scores and classifications.

This module provides functions to aggregate agent scores with weights,
classify fit levels, and determine hiring recommendations.
"""

from typing import Dict, List, Literal, Tuple
from src.config import config


def calculate_weighted_score(
    agent_scores: Dict[str, int],
    weights: Dict[str, float],
    red_flags_penalty: float = 1.0
) -> Tuple[float, Dict[str, Dict[str, float]]]:
    """
    Calculate final weighted score from individual agent scores.
    
    Args:
        agent_scores: Dict mapping agent names to scores (0-100)
        weights: Dict mapping agent names to weights (0.0-1.0, must sum to 1.0)
        red_flags_penalty: Multiplier for red flags (0.0-1.0, lower = more penalty)
        
    Returns:
        Tuple of (final_score, breakdown)
        - final_score: Weighted final score after penalties
        - breakdown: Dict of each agent's contribution
        
    Example:
        >>> scores = {"sector": 85, "skills": 78}
        >>> weights = {"sector": 0.5, "skills": 0.5}
        >>> score, breakdown = calculate_weighted_score(scores, weights)
        >>> score
        81.5
    """
    breakdown: Dict[str, Dict[str, float]] = {}
    weighted_sum = 0.0
    
    for agent_name, score in agent_scores.items():
        weight = weights.get(agent_name, 0.0)
        weighted_contribution = score * weight
        weighted_sum += weighted_contribution
        
        breakdown[agent_name] = {
            "score": float(score),
            "weight": weight,
            "weighted_score": weighted_contribution,
        }
    
    # Apply red flags penalty
    final_score = weighted_sum * red_flags_penalty
    
    return final_score, breakdown


def classify_fit_level(
    score: float,
    perfect_threshold: int = 85,
    good_threshold: int = 70,
    acceptable_threshold: int = 55
) -> Literal["perfect_fit", "good_fit", "acceptable_fit", "poor_fit"]:
    """
    Classify candidate-job fit based on score.
    
    Args:
        score: Overall score (0-100)
        perfect_threshold: Minimum score for perfect_fit (default from config)
        good_threshold: Minimum score for good_fit (default from config)
        acceptable_threshold: Minimum score for acceptable_fit (default from config)
        
    Returns:
        Fit classification: "perfect_fit" | "good_fit" | "acceptable_fit" | "poor_fit"
        
    Example:
        >>> classify_fit_level(87)
        'perfect_fit'
        >>> classify_fit_level(75)
        'good_fit'
    """
    if score >= perfect_threshold:
        return "perfect_fit"
    elif score >= good_threshold:
        return "good_fit"
    elif score >= acceptable_threshold:
        return "acceptable_fit"
    else:
        return "poor_fit"


def determine_recommendation(
    score: float,
    fit_classification: Literal["perfect_fit", "good_fit", "acceptable_fit", "poor_fit"],
    critical_red_flags: List[str]
) -> Literal["strong_recommend", "recommend", "conditional_recommend", "not_recommend"]:
    """
    Determine hiring recommendation based on score, fit, and red flags.
    
    Args:
        score: Overall score (0-100)
        fit_classification: Fit level classification
        critical_red_flags: List of critical red flags found
        
    Returns:
        Recommendation: "strong_recommend" | "recommend" | "conditional_recommend" | "not_recommend"
        
    Example:
        >>> determine_recommendation(87, "perfect_fit", [])
        'strong_recommend'
        >>> determine_recommendation(87, "perfect_fit", ["sector_mismatch"])
        'not_recommend'
    """
    # Critical red flags override everything
    if critical_red_flags:
        return "not_recommend"
    
    # Map fit classification to recommendation
    recommendation_map = {
        "perfect_fit": "strong_recommend",
        "good_fit": "recommend",
        "acceptable_fit": "conditional_recommend",
        "poor_fit": "not_recommend",
    }
    
    return recommendation_map[fit_classification]


def calculate_red_flags_penalty(
    critical_flags: List[str],
    high_flags: List[str],
    medium_flags: List[str]
) -> float:
    """
    Calculate penalty multiplier based on red flags severity.
    
    Args:
        critical_flags: List of critical severity flags
        high_flags: List of high severity flags
        medium_flags: List of medium severity flags
        
    Returns:
        Penalty multiplier (0.0-1.0, where 1.0 = no penalty)
        
    Example:
        >>> calculate_red_flags_penalty([], ["exp_gap"], [])
        0.9
        >>> calculate_red_flags_penalty(["sector_mismatch"], [], [])
        0.0
    """
    # Critical flags are disqualifying
    if critical_flags:
        return 0.0
    
    # High flags: -10% penalty
    high_penalty = len(high_flags) * 0.10
    
    # Medium flags: -3% penalty
    medium_penalty = len(medium_flags) * 0.03
    
    total_penalty = high_penalty + medium_penalty
    
    # Cap penalty at 50% (minimum multiplier of 0.5)
    penalty_multiplier = max(0.5, 1.0 - total_penalty)
    
    return penalty_multiplier


def normalize_confidence_scores(
    confidence_scores: List[float]
) -> float:
    """
    Calculate aggregate confidence from multiple agent confidence scores.
    
    Uses harmonic mean to be conservative - low confidence in any agent
    pulls down the overall confidence.
    
    Args:
        confidence_scores: List of confidence scores (0.0-1.0)
        
    Returns:
        Aggregate confidence score (0.0-1.0)
        
    Example:
        >>> normalize_confidence_scores([0.9, 0.8, 0.95])
        0.88...
    """
    if not confidence_scores:
        return 0.5  # Default to medium confidence
    
    # Remove zeros to avoid division by zero
    valid_scores = [s for s in confidence_scores if s > 0]
    
    if not valid_scores:
        return 0.5
    
    # Harmonic mean
    harmonic_mean = len(valid_scores) / sum(1.0 / s for s in valid_scores)
    
    return harmonic_mean


def analyze_consensus(
    agent_scores: Dict[str, int],
    threshold_high: int = 80,
    threshold_low: int = 60
) -> Dict[str, List[str]]:
    """
    Analyze consensus level between agents.
    
    Args:
        agent_scores: Dict mapping agent names to scores
        threshold_high: Score above which agent is considered positive
        threshold_low: Score below which agent is considered negative
        
    Returns:
        Dict with keys:
            - unanimous_positive: Agents with high scores
            - unanimous_negative: Agents with low scores
            - conflicting: Agents with middle scores
            
    Example:
        >>> scores = {"sector": 90, "skills": 50, "seniority": 75}
        >>> consensus = analyze_consensus(scores)
        >>> "sector" in consensus["unanimous_positive"]
        True
    """
    unanimous_positive: List[str] = []
    unanimous_negative: List[str] = []
    conflicting: List[str] = []
    
    for agent, score in agent_scores.items():
        if score >= threshold_high:
            unanimous_positive.append(agent)
        elif score <= threshold_low:
            unanimous_negative.append(agent)
        else:
            conflicting.append(agent)
    
    return {
        "unanimous_positive": unanimous_positive,
        "unanimous_negative": unanimous_negative,
        "conflicting": conflicting,
    }

