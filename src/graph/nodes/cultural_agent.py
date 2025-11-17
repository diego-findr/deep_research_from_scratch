"""Cultural & Soft Fit Agent node."""

from typing import Any, Dict
from src.graph.state import EvaluationState
from src.agents.base_agent import BaseEvaluationAgent
from src.agents.prompts.cultural_prompt import format_cultural_prompt


class CulturalSoftFitAgent(BaseEvaluationAgent):
    """Agent for evaluating cultural and soft skills fit."""
    
    def get_prompt(self, candidate: Dict[str, Any], job_offer: Dict[str, Any]) -> str:
        """Generate cultural soft fit prompt."""
        return format_cultural_prompt(candidate, job_offer)
    
    def parse_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response."""
        return self.extract_json_from_response(response)


def evaluate_cultural_fit(state: EvaluationState) -> Dict[str, Any]:
    """Node function for cultural fit evaluation."""
    agent = CulturalSoftFitAgent()
    evaluation = agent.evaluate(state["candidate"], state["job_offer"])
    return {"cultural_eval": evaluation}

