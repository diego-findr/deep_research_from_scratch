"""Red Flags Detector Agent node."""

from typing import Any, Dict
from src.graph.state import EvaluationState
from src.agents.base_agent import BaseEvaluationAgent
from src.agents.prompts.red_flags_prompt import format_red_flags_prompt


class RedFlagsDetectorAgent(BaseEvaluationAgent):
    """Agent for detecting and classifying red flags."""
    
    def get_prompt(self, candidate: Dict[str, Any], job_offer: Dict[str, Any]) -> str:
        """Generate red flags detector prompt - requires all_evaluations from state."""
        # This will be called differently since it needs aggregated evaluations
        return ""
    
    def parse_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response."""
        return self.extract_json_from_response(response)
    
    def evaluate_red_flags(
        self,
        all_evaluations: list,
        job_offer: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate red flags from all agent evaluations.
        
        Args:
            all_evaluations: List of all agent evaluations
            job_offer: Job offer data
            
        Returns:
            Red flags evaluation
        """
        try:
            prompt = format_red_flags_prompt(all_evaluations, job_offer)
            response = self.llm.invoke(prompt)
            
            if hasattr(response, 'content'):
                content = response.content
            else:
                content = str(response)
            
            evaluation = self.parse_response(content)
            evaluation["agent"] = "red_flags_detector"
            
            return evaluation
            
        except Exception as e:
            return self._create_fallback_evaluation(str(e))


def evaluate_red_flags(state: EvaluationState) -> Dict[str, Any]:
    """Node function for red flags detection."""
    agent = RedFlagsDetectorAgent()
    evaluation = agent.evaluate_red_flags(
        state.get("all_evaluations", []),
        state["job_offer"]
    )
    
    # Update aggregated_red_flags with classified flags
    updated_flags = {
        "critical": evaluation.get("critical_flags", []),
        "high": evaluation.get("high_flags", []),
        "medium": evaluation.get("medium_flags", []),
    }
    
    return {
        "red_flags_eval": evaluation,
        "aggregated_red_flags": updated_flags,
    }

