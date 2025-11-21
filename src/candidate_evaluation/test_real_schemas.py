"""
Test candidate evaluation with real enriched schemas.
"""

import json
import sys
from pathlib import Path

# Add src directory to path
src_dir = Path(__file__).parent.parent
sys.path.insert(0, str(src_dir))

from candidate_evaluation.evaluator_agent import evaluate_candidate

# Load real enriched job
job_path = Path(__file__).parent.parent.parent / "tests" / "jobs" / "outputs" / "enriched_acciona_job.json"
with open(job_path, 'r', encoding='utf-8') as f:
    enriched_job = json.load(f)

# Load real enriched candidate
candidate_path = Path(__file__).parent.parent.parent / "tests" / "candidates" / "outputs" / "enriched_natalia.json"
with open(candidate_path, 'r', encoding='utf-8') as f:
    enriched_candidate = json.load(f)

# Extract relevant fields for evaluation
# For the offer, we'll use the semantic enrichment data
offer = {
    "job_title": enriched_job["raw_job_posting"]["job_title"],
    "company_name": enriched_job["raw_job_posting"]["company_name"],
    "description": enriched_job["raw_job_posting"]["description"],
    "responsibilities": enriched_job["raw_job_posting"]["responsibilities"],
    "experience_required": enriched_job["raw_job_posting"]["experience_required"],
    "min_salary_range": enriched_job["raw_job_posting"]["min_salary_range"],
    "max_salary_range": enriched_job["raw_job_posting"]["max_salary_range"],
    "location": enriched_job["raw_job_posting"]["locations"],
    "remote": enriched_job["raw_job_posting"]["remote"],
    "primary_sector": enriched_job["semantic_enrichment"]["key_insights"]["primary_sector"],
    "required_seniority": enriched_job["semantic_enrichment"]["key_insights"]["required_seniority"],
    "years_experience_required": enriched_job["semantic_enrichment"]["key_insights"]["years_experience_required"],
    "explicit_skills": enriched_job["semantic_enrichment"]["structured_skills"]["explicit"],
    "implicit_skills": enriched_job["semantic_enrichment"]["structured_skills"]["implicit"],
    "required_competencies": enriched_job["semantic_enrichment"]["structured_competencies"],
    "ideal_candidate": enriched_job["semantic_enrichment"]["ideal_candidate"]
}

# For the candidate, we'll use the enriched profile data
candidate = {
    "full_name": enriched_candidate["candidate_snapshot"]["full_name"],
    "headline": enriched_candidate["candidate_snapshot"]["headline"],
    "location": enriched_candidate["candidate_snapshot"]["location"],
    "total_experience_years": enriched_candidate["pre_computed_metrics"]["total_experience_years"],
    "is_manager": enriched_candidate["pre_computed_metrics"]["is_manager"],
    "technical_depth_score": enriched_candidate["pre_computed_metrics"]["technical_depth_score"],
    "primary_sector": enriched_candidate["inferred_filters"]["primary_sector"],
    "environment_fit": enriched_candidate["inferred_filters"]["environment_fit"],
    "languages": enriched_candidate["inferred_filters"]["languages"],
    "seniority_level": enriched_candidate["agent_decision_support"]["seniority_level"],
    "ideal_role_match": enriched_candidate["agent_decision_support"]["ideal_role_match"],
    "technical_hard_skills": enriched_candidate["competency_profile"]["technical_hard_skills"],
    "functional_skills": enriched_candidate["competency_profile"]["functional_skills"],
    "soft_skills_and_leadership": enriched_candidate["competency_profile"]["soft_skills_and_leadership"],
    "work_history": enriched_candidate["work_history_timeline"],
    "trajectory_trend": enriched_candidate["stability_analysis"]["trajectory_trend"],
    "job_hopping_risk": enriched_candidate["stability_analysis"]["job_hopping_risk"]
}

def run_real_test():
    print("=== Testing Real Enriched Schemas ===")
    print(f"\nOffer: {offer['job_title']} at {offer['company_name']}")
    print(f"Candidate: {candidate['full_name']} - {candidate['headline']}")
    print(f"\nRequired Experience: {offer['years_experience_required']} years")
    print(f"Candidate Experience: {candidate['total_experience_years']} years")
    print(f"\nRequired Seniority: {offer['required_seniority']}")
    print(f"Candidate Seniority: {candidate['seniority_level']}")
    print(f"\nRequired Sector: {offer['primary_sector']}")
    print(f"Candidate Sector: {candidate['primary_sector']}")
    
    print("\n" + "="*60)
    print("Running AI Evaluation...")
    print("="*60 + "\n")
    
    result = evaluate_candidate(candidate, offer)
    
    print("=== EVALUATION RESULT ===\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print("\n=== SUMMARY ===")
    print(f"Decision: {'✅ LIKED' if result['liked'] else '❌ NOT LIKED'}")
    print(f"Models Agreement: {result['models_liked']}/{result['models_evaluated']}")
    print(f"Compatibility Score: {result['compatibility']}/100")
    print(f"\nFinal Reason: {result['reason']}")

if __name__ == "__main__":
    run_real_test()
