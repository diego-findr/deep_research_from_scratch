"""
Disambiguation utilities for resolving polysemous terms.

This module helps resolve ambiguous terms by leveraging context from
the semantic enrichment data.
"""

from typing import Any, Dict, List, Optional


def resolve_term_ambiguity(
    term: str,
    context_sector: str,
    disambiguation_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Resolve ambiguous terms using sector context and disambiguation data.
    
    Args:
        term: The term to disambiguate (e.g., "automatización")
        context_sector: The sector context (e.g., "construction" vs "software")
        disambiguation_data: Optional disambiguation data from semantic enrichment
        
    Returns:
        Dict with keys:
            - resolved_term: The disambiguated term
            - confidence: Confidence in the disambiguation (0.0-1.0)
            - alternatives_rejected: List of rejected interpretations
            - reasoning: Explanation of the disambiguation
            
    Example:
        >>> resolve_term_ambiguity("automation", "construction", None)
        {'resolved_term': 'industrial_automation', 'confidence': 0.8, ...}
    """
    # If disambiguation data is provided, use it
    if disambiguation_data:
        disambiguated_terms = disambiguation_data.get("disambiguated_terms", [])
        for disambig in disambiguated_terms:
            original = disambig.get("original_term", "").lower()
            if term.lower() == original:
                return {
                    "resolved_term": disambig.get("resolved_meaning", term),
                    "confidence": disambig.get("confidence", 0.9),
                    "alternatives_rejected": disambig.get("alternatives_rejected", []),
                    "reasoning": disambig.get("reasoning", "From disambiguation data"),
                }
    
    # Fallback: Use sector-based heuristics
    term_lower = term.lower()
    
    # Common ambiguous terms
    if "automation" in term_lower or "automatización" in term_lower:
        if context_sector in ["software_development", "qa", "testing"]:
            return {
                "resolved_term": "test_automation",
                "confidence": 0.75,
                "alternatives_rejected": ["industrial_automation", "process_automation"],
                "reasoning": f"In {context_sector} context, automation typically refers to test/QA automation",
            }
        elif context_sector in ["construction", "manufacturing", "industrial"]:
            return {
                "resolved_term": "industrial_automation",
                "confidence": 0.75,
                "alternatives_rejected": ["test_automation", "office_automation"],
                "reasoning": f"In {context_sector} context, automation refers to industrial/process automation",
            }
    
    if "cloud" in term_lower:
        if context_sector in ["software_development", "devops", "it"]:
            return {
                "resolved_term": "cloud_computing",
                "confidence": 0.9,
                "alternatives_rejected": [],
                "reasoning": "In technical context, cloud refers to cloud computing/infrastructure",
            }
    
    if "safety" in term_lower or "seguridad" in term_lower:
        if context_sector in ["construction", "manufacturing", "healthcare"]:
            return {
                "resolved_term": "occupational_safety",
                "confidence": 0.8,
                "alternatives_rejected": ["cybersecurity", "data_security"],
                "reasoning": f"In {context_sector} context, safety refers to occupational/workplace safety",
            }
        elif context_sector in ["software_development", "it", "fintech"]:
            return {
                "resolved_term": "cybersecurity",
                "confidence": 0.8,
                "alternatives_rejected": ["occupational_safety"],
                "reasoning": f"In {context_sector} context, security refers to cybersecurity/data security",
            }
    
    # No disambiguation needed
    return {
        "resolved_term": term,
        "confidence": 1.0,
        "alternatives_rejected": [],
        "reasoning": "Term is unambiguous or no disambiguation data available",
    }


def extract_canonical_terms(
    normalization_data: Optional[Dict[str, Any]] = None
) -> Dict[str, List[str]]:
    """
    Extract canonical terms and their synonyms from normalization data.
    
    Args:
        normalization_data: Normalization data from semantic enrichment
        
    Returns:
        Dict mapping canonical terms to lists of synonyms
        
    Example:
        >>> data = {"normalized_synonyms": [{"canonical_term": "Python", "synonyms": ["py"]}]}
        >>> extract_canonical_terms(data)
        {'Python': ['py']}
    """
    if not normalization_data:
        return {}
    
    canonical_map: Dict[str, List[str]] = {}
    
    normalized_synonyms = normalization_data.get("normalized_synonyms", [])
    for entry in normalized_synonyms:
        canonical = entry.get("canonical_term", "")
        synonyms = entry.get("synonyms", [])
        if canonical:
            canonical_map[canonical] = synonyms
    
    return canonical_map


def resolve_skill_disambiguation(
    candidate_skills: List[Dict[str, Any]],
    job_skills: List[Dict[str, Any]],
    candidate_sector: str,
    job_sector: str,
    candidate_disambiguation: Optional[Dict[str, Any]] = None,
    job_disambiguation: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Resolve ambiguities in skills matching between candidate and job.
    
    This function helps identify when skills might have the same name but
    different meanings in different contexts.
    
    Args:
        candidate_skills: Candidate's skills list
        job_skills: Job's required skills list
        candidate_sector: Candidate's sector
        job_sector: Job's sector
        candidate_disambiguation: Candidate's disambiguation data
        job_disambiguation: Job's disambiguation data
        
    Returns:
        List of potential ambiguity issues with recommendations
        
    Example:
        >>> cand_skills = [{"name": "automation"}]
        >>> job_skills = [{"name": "automation"}]
        >>> issues = resolve_skill_disambiguation(cand_skills, job_skills, "manufacturing", "qa")
        >>> len(issues) > 0
        True
    """
    ambiguity_issues: List[Dict[str, Any]] = []
    
    # If sectors are different, check for potentially ambiguous skill matches
    if candidate_sector != job_sector:
        for job_skill in job_skills:
            job_skill_name = job_skill.get("name", "").lower()
            
            for cand_skill in candidate_skills:
                cand_skill_name = cand_skill.get("name", "").lower()
                
                # If skill names match but sectors differ, flag potential ambiguity
                if job_skill_name == cand_skill_name:
                    # Resolve both in their contexts
                    cand_resolved = resolve_term_ambiguity(
                        cand_skill_name, candidate_sector, candidate_disambiguation
                    )
                    job_resolved = resolve_term_ambiguity(
                        job_skill_name, job_sector, job_disambiguation
                    )
                    
                    # If resolutions differ, flag ambiguity
                    if cand_resolved["resolved_term"] != job_resolved["resolved_term"]:
                        ambiguity_issues.append({
                            "skill_name": cand_skill_name,
                            "candidate_interpretation": cand_resolved["resolved_term"],
                            "job_interpretation": job_resolved["resolved_term"],
                            "candidate_sector": candidate_sector,
                            "job_sector": job_sector,
                            "severity": "high",
                            "recommendation": (
                                f"Skill '{cand_skill_name}' may have different meanings. "
                                f"Candidate context: {cand_resolved['resolved_term']} in {candidate_sector}. "
                                f"Job context: {job_resolved['resolved_term']} in {job_sector}. "
                                "Manual review recommended."
                            ),
                        })
    
    return ambiguity_issues

