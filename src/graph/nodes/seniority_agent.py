"""Seniority Calibration Agent node."""

from typing import Any, Dict
from src.graph.state import EvaluationState
from src.agents.base_agent import BaseEvaluationAgent
from src.agents.prompts.seniority_prompt import format_seniority_prompt


class SeniorityCalibrationAgent(BaseEvaluationAgent):
    """Agent for evaluating seniority calibration."""
    
    def get_prompt(self, candidate: Dict[str, Any], job_offer: Dict[str, Any]) -> str:
        """Generate seniority calibration prompt."""
        return format_seniority_prompt(candidate, job_offer)
    
    def parse_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response."""
        return self.extract_json_from_response(response)


def evaluate_seniority_calibration(state: EvaluationState) -> Dict[str, Any]:
    """Node function for seniority calibration evaluation."""
    agent = SeniorityCalibrationAgent()
    evaluation = agent.evaluate(state["candidate"], state["job_offer"])
    return {"seniority_eval": evaluation}

