"""
Semantic matching utilities for comparing skills, sectors, and other attributes.

This module provides functions to perform fuzzy matching, synonym resolution,
and semantic similarity calculations between candidate and job offer attributes.
"""

from typing import Any, Dict, List, Optional, Tuple
import re


def normalize_term(term: str) -> str:
    """
    Normalize a term for comparison by lowercasing and removing special chars.
    
    Args:
        term: The term to normalize
        
    Returns:
        Normalized term
        
    Example:
        >>> normalize_term("React.js")
        'reactjs'
    """
    normalized = term.lower().strip()
    # Remove common punctuation but keep alphanumeric
    normalized = re.sub(r'[^\w\s]', '', normalized)
    # Remove extra whitespace
    normalized = re.sub(r'\s+', ' ', normalized)
    return normalized


def calculate_semantic_similarity(
    term1: str,
    term2: str,
    synonyms1: Optional[List[str]] = None,
    synonyms2: Optional[List[str]] = None
) -> float:
    """
    Calculate semantic similarity between two terms considering synonyms.
    
    Args:
        term1: First term to compare
        term2: Second term to compare
        synonyms1: Optional list of synonyms for term1
        synonyms2: Optional list of synonyms for term2
        
    Returns:
        Similarity score from 0.0 (no match) to 1.0 (exact match)
        
    Example:
        >>> calculate_semantic_similarity("Python", "python", [], [])
        1.0
        >>> calculate_semantic_similarity("React", "ReactJS", ["ReactJS"], ["React"])
        1.0
    """
    # Normalize terms
    norm1 = normalize_term(term1)
    norm2 = normalize_term(term2)
    
    # Exact match
    if norm1 == norm2:
        return 1.0
    
    # Check if term1 is in term2's synonyms or vice versa
    synonyms1_list = [normalize_term(s) for s in (synonyms1 or [])]
    synonyms2_list = [normalize_term(s) for s in (synonyms2 or [])]
    
    if norm1 in synonyms2_list or norm2 in synonyms1_list:
        return 1.0
    
    # Check for partial matches (substring containment)
    if norm1 in norm2 or norm2 in norm1:
        # Calculate overlap ratio
        overlap = min(len(norm1), len(norm2)) / max(len(norm1), len(norm2))
        return 0.7 + (0.2 * overlap)  # 0.7-0.9 for partial matches
    
    # Check for common words (for multi-word terms)
    words1 = set(norm1.split())
    words2 = set(norm2.split())
    
    if words1 and words2:
        common_words = words1 & words2
        if common_words:
            jaccard = len(common_words) / len(words1 | words2)
            return 0.5 + (0.4 * jaccard)  # 0.5-0.9 for word overlap
    
    # No match
    return 0.0


def match_skills(
    candidate_skills: List[Dict[str, Any]],
    required_skills: List[Dict[str, Any]],
    candidate_normalization: Optional[Dict[str, Any]] = None,
    job_normalization: Optional[Dict[str, Any]] = None
) -> Tuple[float, List[Dict[str, Any]], List[str]]:
    """
    Match candidate skills against required job skills.
    
    Args:
        candidate_skills: List of candidate skill dicts with 'name' and optional 'level'
        required_skills: List of required skill dicts with 'name', 'importance', optional 'level'
        candidate_normalization: Optional normalization data from candidate profile
        job_normalization: Optional normalization data from job offer
        
    Returns:
        Tuple of (coverage_ratio, matches, missing_skills)
        - coverage_ratio: 0.0-1.0 indicating % of required skills covered
        - matches: List of matched skills with details
        - missing_skills: List of skill names not found in candidate profile
        
    Example:
        >>> candidate = [{"name": "Python", "level": "advanced"}]
        >>> required = [{"name": "Python", "importance": "required"}]
        >>> coverage, matches, missing = match_skills(candidate, required)
        >>> coverage
        1.0
    """
    if not required_skills:
        return 1.0, [], []
    
    # Build synonym maps from normalization data
    candidate_synonyms: Dict[str, List[str]] = {}
    if candidate_normalization and "normalized_synonyms" in candidate_normalization:
        for skill_data in candidate_normalization.get("normalized_synonyms", []):
            canonical = skill_data.get("canonical_term", "")
            synonyms = skill_data.get("synonyms", [])
            if canonical:
                candidate_synonyms[canonical] = synonyms
    
    job_synonyms: Dict[str, List[str]] = {}
    if job_normalization and "normalized_synonyms" in job_normalization:
        for skill_data in job_normalization.get("normalized_synonyms", []):
            canonical = skill_data.get("canonical_term", "")
            synonyms = skill_data.get("synonyms", [])
            if canonical:
                job_synonyms[canonical] = synonyms
    
    matches: List[Dict[str, Any]] = []
    missing_skills: List[str] = []
    
    for req_skill in required_skills:
        req_name = req_skill.get("name", "")
        req_importance = req_skill.get("importance", "required")
        req_level = req_skill.get("level", None)
        
        best_match_score = 0.0
        best_match_candidate: Optional[Dict[str, Any]] = None
        
        # Try to find best matching candidate skill
        for cand_skill in candidate_skills:
            cand_name = cand_skill.get("name", "")
            
            # Get synonyms for both
            req_syns = job_synonyms.get(req_name, [])
            cand_syns = candidate_synonyms.get(cand_name, [])
            
            similarity = calculate_semantic_similarity(
                req_name, cand_name, req_syns, cand_syns
            )
            
            if similarity > best_match_score:
                best_match_score = similarity
                best_match_candidate = cand_skill
        
        # Consider a match if similarity > 0.7
        if best_match_score >= 0.7 and best_match_candidate:
            match_info = {
                "required_skill": req_name,
                "candidate_skill": best_match_candidate.get("name", ""),
                "similarity": best_match_score,
                "importance": req_importance,
                "required_level": req_level,
                "candidate_level": best_match_candidate.get("level", "unknown"),
            }
            matches.append(match_info)
        else:
            if req_importance in ["required", "must_have"]:
                missing_skills.append(req_name)
    
    # Calculate coverage (weighted by importance if needed)
    required_count = len([s for s in required_skills if s.get("importance") in ["required", "must_have"]])
    if required_count == 0:
        required_count = len(required_skills)
    
    matched_required = len([m for m in matches if m["importance"] in ["required", "must_have"]])
    
    coverage = matched_required / required_count if required_count > 0 else 1.0
    
    return coverage, matches, missing_skills


def match_sectors(
    candidate_sector: str,
    job_sector: str,
    candidate_secondary: Optional[List[str]] = None,
    job_secondary: Optional[List[str]] = None
) -> Tuple[bool, str, List[str]]:
    """
    Match candidate sector against job sector.
    
    Args:
        candidate_sector: Primary sector of candidate
        job_sector: Primary sector required by job
        candidate_secondary: Optional list of candidate's secondary sectors
        job_secondary: Optional list of job's secondary sectors
        
    Returns:
        Tuple of (is_match, alignment_level, overlaps)
        - is_match: Boolean indicating if sectors are compatible
        - alignment_level: "perfect_match" | "strong_match" | "partial_match" | "mismatch"
        - overlaps: List of overlapping secondary sectors
        
    Example:
        >>> match_sectors("construction", "construction", [], [])
        (True, 'perfect_match', [])
    """
    candidate_secondary = candidate_secondary or []
    job_secondary = job_secondary or []
    
    # Normalize sectors
    cand_primary_norm = normalize_term(candidate_sector)
    job_primary_norm = normalize_term(job_sector)
    
    # Perfect match on primary
    if cand_primary_norm == job_primary_norm:
        return True, "perfect_match", []
    
    # Check if candidate primary matches job secondary
    job_secondary_norm = [normalize_term(s) for s in job_secondary]
    if cand_primary_norm in job_secondary_norm:
        return True, "strong_match", [candidate_sector]
    
    # Check if job primary matches candidate secondary
    cand_secondary_norm = [normalize_term(s) for s in candidate_secondary]
    if job_primary_norm in cand_secondary_norm:
        return True, "strong_match", [job_sector]
    
    # Check for secondary sector overlaps
    overlaps = []
    for cand_sec in candidate_secondary:
        cand_sec_norm = normalize_term(cand_sec)
        for job_sec in job_secondary:
            job_sec_norm = normalize_term(job_sec)
            if cand_sec_norm == job_sec_norm:
                overlaps.append(cand_sec)
    
    if overlaps:
        return True, "partial_match", overlaps
    
    # No match
    return False, "mismatch", []


def compare_levels(
    candidate_level: str,
    required_level: str
) -> Tuple[bool, int]:
    """
    Compare skill or experience levels.
    
    Args:
        candidate_level: Level achieved by candidate (e.g., "advanced", "mid")
        required_level: Level required by job
        
    Returns:
        Tuple of (is_sufficient, gap)
        - is_sufficient: Boolean indicating if candidate meets requirement
        - gap: Integer gap (-N if under-qualified, 0 if exact, +N if over-qualified)
        
    Example:
        >>> compare_levels("advanced", "mid")
        (True, 1)
    """
    level_hierarchy = {
        "novice": 0,
        "beginner": 0,
        "junior": 1,
        "mid": 2,
        "intermediate": 2,
        "advanced": 3,
        "senior": 3,
        "expert": 4,
        "lead": 4,
    }
    
    cand_level_norm = normalize_term(candidate_level)
    req_level_norm = normalize_term(required_level)
    
    cand_score = level_hierarchy.get(cand_level_norm, 2)  # Default to mid
    req_score = level_hierarchy.get(req_level_norm, 2)
    
    gap = cand_score - req_score
    is_sufficient = cand_score >= req_score
    
    return is_sufficient, gap

