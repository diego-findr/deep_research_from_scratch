"""
Main entry point for the candidate-job matching evaluation system.

This module provides a simple interface to evaluate candidates against job offers
using the multi-agent LangGraph system.
"""

import json
from typing import Any, Dict
from pathlib import Path

from src.graph.graph_builder import build_evaluation_graph
from src.graph.state import create_initial_state
from src.config import config


class EvaluationSystem:
    """
    Main evaluation system for candidate-job matching.
    
    This class encapsulates the LangGraph multi-agent system and provides
    a clean interface for running evaluations.
    
    Example:
        >>> system = EvaluationSystem()
        >>> candidate = load_json("candidate.json")
        >>> job = load_json("job.json")
        >>> result = system.evaluate(candidate, job)
        >>> print(result["final_evaluation"]["overall_score"])
        82
    """
    
    def __init__(self):
        """Initialize the evaluation system by building the graph."""
        # Validate configuration
        config.validate_weights()
        
        # Build the graph
        self.graph = build_evaluation_graph()
    
    def evaluate(
        self,
        candidate: Dict[str, Any],
        job_offer: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate a candidate against a job offer.
        
        Args:
            candidate: Enriched candidate profile (JSON dict)
            job_offer: Enriched job offer (JSON dict)
            
        Returns:
            Complete evaluation result with final score, recommendation,
            all agent evaluations, and explainability information
            
        Raises:
            ValueError: If inputs are invalid
            
        Example:
            >>> result = system.evaluate(candidate_data, job_data)
            >>> result["final_evaluation"]["recommendation"]
            'recommend'
        """
        # Create initial state
        initial_state = create_initial_state(candidate, job_offer)
        
        # Run the graph
        final_state = self.graph.invoke(initial_state)
        
        # Extract final evaluation
        return final_state.get("final_evaluation", {})
    
    def evaluate_from_files(
        self,
        candidate_path: str,
        job_offer_path: str,
        output_path: str = None
    ) -> Dict[str, Any]:
        """
        Evaluate candidate and job from JSON files.
        
        Args:
            candidate_path: Path to candidate JSON file
            job_offer_path: Path to job offer JSON file
            output_path: Optional path to save evaluation result
            
        Returns:
            Complete evaluation result
            
        Example:
            >>> result = system.evaluate_from_files(
            ...     "data/candidate.json",
            ...     "data/job.json",
            ...     "output/evaluation.json"
            ... )
        """
        # Load inputs
        with open(candidate_path, 'r', encoding='utf-8') as f:
            candidate = json.load(f)
        
        with open(job_offer_path, 'r', encoding='utf-8') as f:
            job_offer = json.load(f)
        
        # Run evaluation
        result = self.evaluate(candidate, job_offer)
        
        # Save output if path provided
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"Evaluation result saved to: {output_path}")
        
        return result


def main() -> None:
    """
    CLI entry point for running evaluations.
    
    Example usage:
        python -m src.main
    """
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python -m src.main <candidate_json> <job_json> [output_json]")
        print("\nExample:")
        print("  python -m src.main data/candidate.json data/job.json output/result.json")
        sys.exit(1)
    
    candidate_path = sys.argv[1]
    job_path = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else None
    
    print("Initializing evaluation system...")
    system = EvaluationSystem()
    
    print(f"Loading candidate from: {candidate_path}")
    print(f"Loading job offer from: {job_path}")
    
    print("\nRunning evaluation...")
    result = system.evaluate_from_files(candidate_path, job_path, output_path)
    
    # Print summary
    print("\n" + "="*60)
    print("EVALUATION SUMMARY")
    print("="*60)
    
    final_eval = result.get("final_evaluation", {})
    print(f"Overall Score: {final_eval.get('overall_score', 0)}/100")
    print(f"Fit Classification: {final_eval.get('fit_classification', 'unknown')}")
    print(f"Recommendation: {final_eval.get('recommendation', 'unknown')}")
    print(f"Confidence: {final_eval.get('confidence', 0.0):.2f}")
    
    print("\n" + "-"*60)
    
    # Print explainability summary
    explainability = result.get("explainability", {})
    print("\nExecutive Summary:")
    print(explainability.get("executive_summary", "N/A"))
    
    print("\nKey Decision Factors:")
    for factor in explainability.get("key_decision_factors", [])[:4]:
        print(f"  • {factor}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()

