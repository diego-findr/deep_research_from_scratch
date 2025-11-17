"""Experience Relevance Agent node."""

from typing import Any, Dict
from src.graph.state import EvaluationState
from src.agents.base_agent import BaseEvaluationAgent
from src.agents.prompts.experience_prompt import format_experience_prompt


class ExperienceRelevanceAgent(BaseEvaluationAgent):
    """Agent for evaluating experience relevance."""
    
    def get_prompt(self, candidate: Dict[str, Any], job_offer: Dict[str, Any]) -> str:
        """Generate experience relevance prompt."""
        return format_experience_prompt(candidate, job_offer)
    
    def parse_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response."""
        return self.extract_json_from_response(response)


def evaluate_experience_relevance(state: EvaluationState) -> Dict[str, Any]:
    """Node function for experience relevance evaluation."""
    agent = ExperienceRelevanceAgent()
    evaluation = agent.evaluate(state["candidate"], state["job_offer"])
    return {"experience_eval": evaluation}

