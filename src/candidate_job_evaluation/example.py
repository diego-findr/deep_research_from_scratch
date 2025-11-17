"""Example usage of candidate-job evaluation system."""

import json
from pathlib import Path

from src.candidate_job_evaluation import EvaluationConfig, evaluate_candidate_for_job


def main():
    """Run example evaluation."""
    # Load test data
    tests_dir = Path(__file__).parent.parent.parent / "tests"

    # Load enriched candidate
    with open(tests_dir / "candidates" / "outputs" / "enriched_natalia.json") as f:
        candidate = json.load(f)

    # Load enriched job offer
    with open(tests_dir / "jobs" / "outputs" / "enriched_acciona_job.json") as f:
        job_offer = json.load(f)

    print("=" * 80)
    print("CANDIDATE-JOB FIT EVALUATION")
    print("=" * 80)
    print(f"\nCandidate: {candidate['perfil_raw']['full_name']}")
    print(f"  Sector: {candidate['semantic_enrichment']['key_insights']['primary_sector']}")
    print(f"  Seniority: {candidate['semantic_enrichment']['key_insights']['seniority_level']}")
    print(f"  Experience: {candidate['semantic_enrichment']['key_insights']['years_experience']} years")

    print(f"\nJob: {job_offer['raw_job_posting']['job_title']}")
    print(f"  Company: {job_offer['raw_job_posting']['company_name']}")
    print(f"  Sector: {job_offer['semantic_enrichment']['key_insights']['primary_sector']}")
    print(f"  Required Seniority: {job_offer['semantic_enrichment']['key_insights']['required_seniority']}")
    print(f"  Required Experience: {job_offer['semantic_enrichment']['key_insights']['years_experience_required']} years")

    print("\n" + "-" * 80)
    print("Running multi-agent evaluation...")
    print("-" * 80)

    # Configure evaluation
    config = EvaluationConfig(
        llm_model="gpt-4o",
        llm_temperature=0.1,
    )

    # Run evaluation
    result = evaluate_candidate_for_job(
        candidate=candidate,
        job_offer=job_offer,
        config=config,
    )

    # Display results
    final_eval = result["final_evaluation"]

    print("\n" + "=" * 80)
    print("EVALUATION RESULTS")
    print("=" * 80)

    print(f"\n{'Overall Score:':<25} {final_eval.overall_score}/100")
    print(f"{'Recommendation:':<25} {final_eval.recommendation.upper().replace('_', ' ')}")

    print(f"\n{'Summary:':<25}")
    print(f"{final_eval.summary}")

    print("\nIndividual Agent Scores:")
    print("-" * 40)
    for agent, score in final_eval.agent_scores.items():
        bar_length = int(score / 2)  # Scale to 50 chars max
        bar = "█" * bar_length + "░" * (50 - bar_length)
        print(f"  {agent.replace('_', ' ').title():<20} {bar} {score}/100")

    print("\nKey Strengths:")
    print("-" * 40)
    for i, strength in enumerate(final_eval.strengths, 1):
        print(f"  {i}. {strength}")

    print("\nKey Concerns:")
    print("-" * 40)
    for i, concern in enumerate(final_eval.concerns, 1):
        print(f"  {i}. {concern}")

    if final_eval.missing_skills:
        print("\nMissing Critical Skills:")
        print("-" * 40)
        for i, skill in enumerate(final_eval.missing_skills, 1):
            print(f"  {i}. {skill}")

    if final_eval.all_red_flags:
        print("\nRed Flags Identified:")
        print("-" * 40)
        for i, flag in enumerate(final_eval.all_red_flags, 1):
            print(f"  {i}. {flag}")

    print("\nDecision Reasoning:")
    print("-" * 40)
    print(final_eval.decision_tree)

    print("\n" + "=" * 80)

    # Save results
    output_dir = tests_dir / "evaluations" / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "evaluation_natalia_acciona.json"

    result_serializable = {
        "evaluation_id": result["evaluation_id"],
        "timestamp": result["timestamp"],
        "candidate_id": candidate["candidato_id"],
        "job_id": job_offer["job_id"],
        "sector_evaluation": result["sector_evaluation"].model_dump() if result.get("sector_evaluation") else None,
        "skills_evaluation": result["skills_evaluation"].model_dump() if result.get("skills_evaluation") else None,
        "seniority_evaluation": result["seniority_evaluation"].model_dump() if result.get("seniority_evaluation") else None,
        "competencies_evaluation": result["competencies_evaluation"].model_dump() if result.get("competencies_evaluation") else None,
        "red_flags_evaluation": result["red_flags_evaluation"].model_dump() if result.get("red_flags_evaluation") else None,
        "domain_expert_evaluation": result["domain_expert_evaluation"].model_dump() if result.get("domain_expert_evaluation") else None,
        "final_evaluation": result["final_evaluation"].model_dump() if result.get("final_evaluation") else None,
    }

    with open(output_file, "w") as f:
        json.dump(result_serializable, f, indent=2)

    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
