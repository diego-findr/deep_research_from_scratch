"""
Example script demonstrating the evaluation system.

Run this script to see the multi-agent system in action.
"""

import sys
sys.path.append('..')

import json
from pathlib import Path
from src.main import EvaluationSystem


def main():
    """Run example evaluation."""
    print("="*70)
    print("CANDIDATE-JOB MATCHING SYSTEM - EXAMPLE EVALUATION")
    print("="*70)
    
    # Load sample data
    print("\n1. Loading sample data...")
    with open('../tests/fixtures/sample_candidate.json', 'r', encoding='utf-8') as f:
        candidate = json.load(f)
    
    with open('../tests/fixtures/sample_job_offer.json', 'r', encoding='utf-8') as f:
        job_offer = json.load(f)
    
    print(f"   Candidate: {candidate['perfil_raw']['name']}")
    print(f"   Job: {job_offer['raw_job_posting']['title']}")
    print(f"   Company: {job_offer['raw_job_posting']['company']}")
    
    # Initialize system
    print("\n2. Initializing evaluation system...")
    system = EvaluationSystem()
    print("   ✓ System initialized")
    
    # Run evaluation
    print("\n3. Running multi-agent evaluation...")
    print("   This may take 30-60 seconds as agents analyze the data...")
    result = system.evaluate(candidate, job_offer)
    print("   ✓ Evaluation complete")
    
    # Display results
    print("\n" + "="*70)
    print("EVALUATION RESULTS")
    print("="*70)
    
    final_eval = result['final_evaluation']
    print(f"\nOverall Score: {final_eval['overall_score']}/100")
    print(f"Fit Classification: {final_eval['fit_classification'].upper()}")
    print(f"Recommendation: {final_eval['recommendation'].upper()}")
    print(f"Confidence: {final_eval['confidence']:.1%}")
    
    # Agent scores
    print("\n" + "-"*70)
    print("INDIVIDUAL AGENT SCORES")
    print("-"*70)
    
    for agent_eval in result['agents_evaluations']:
        agent = agent_eval['agent'].replace('_', ' ').title()
        score = agent_eval['score']
        indicator = "✓" if score >= 70 else "⚠" if score >= 50 else "✗"
        print(f"{indicator} {agent:35s} {score:3d}/100")
    
    # Key insights
    orchestrator = result['orchestrator_synthesis']
    
    print("\n" + "-"*70)
    print("KEY STRENGTHS")
    print("-"*70)
    for strength in orchestrator['key_strengths'][:3]:
        print(f"  ✓ {strength}")
    
    print("\n" + "-"*70)
    print("KEY WEAKNESSES")
    print("-"*70)
    for weakness in orchestrator['key_weaknesses'][:3]:
        print(f"  ✗ {weakness}")
    
    print("\n" + "-"*70)
    print("DECISION RATIONALE")
    print("-"*70)
    print(f"\n{orchestrator['decision_rationale']}\n")
    
    print("-"*70)
    print("RECOMMENDED NEXT STEPS")
    print("-"*70)
    for i, step in enumerate(orchestrator['next_steps_recommendation'], 1):
        print(f"  {i}. {step}")
    
    # Save results
    print("\n" + "="*70)
    output_path = Path('../output/example_evaluation.json')
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"Full results saved to: {output_path}")
    print("="*70)


if __name__ == "__main__":
    main()

