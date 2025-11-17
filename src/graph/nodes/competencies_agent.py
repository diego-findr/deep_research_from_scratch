"""Competencies Evaluator Agent node."""

from typing import Any, Dict
from src.graph.state import EvaluationState
from src.agents.base_agent import BaseEvaluationAgent
from src.agents.prompts.competencies_prompt import format_competencies_prompt


class CompetenciesEvaluatorAgent(BaseEvaluationAgent):
    """Agent for evaluating competencies."""
    
    def get_prompt(self, candidate: Dict[str, Any], job_offer: Dict[str, Any]) -> str:
        """Generate competencies evaluator prompt."""
        return format_competencies_prompt(candidate, job_offer)
    
    def parse_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response."""
        return self.extract_json_from_response(response)


def evaluate_competencies(state: EvaluationState) -> Dict[str, Any]:
    """Node function for competencies evaluation."""
    agent = CompetenciesEvaluatorAgent()
    evaluation = agent.evaluate(state["candidate"], state["job_offer"])
    return {"competencies_eval": evaluation}

