"""Salary & Compensation Agent node."""

from typing import Any, Dict
from src.graph.state import EvaluationState
from src.agents.base_agent import BaseEvaluationAgent
from src.agents.prompts.salary_prompt import format_salary_prompt


class SalaryCompensationAgent(BaseEvaluationAgent):
    """Agent for evaluating salary compensation alignment."""
    
    def get_prompt(self, candidate: Dict[str, Any], job_offer: Dict[str, Any]) -> str:
        """Generate salary compensation prompt."""
        return format_salary_prompt(candidate, job_offer)
    
    def parse_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response."""
        return self.extract_json_from_response(response)


def evaluate_salary_compensation(state: EvaluationState) -> Dict[str, Any]:
    """Node function for salary compensation evaluation."""
    agent = SalaryCompensationAgent()
    evaluation = agent.evaluate(state["candidate"], state["job_offer"])
    return {"salary_eval": evaluation}

