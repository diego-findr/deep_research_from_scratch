"""Skills Matching Agent node."""

from typing import Any, Dict
from src.graph.state import EvaluationState
from src.agents.base_agent import BaseEvaluationAgent
from src.agents.prompts.skills_prompt import format_skills_prompt


class SkillsMatchingAgent(BaseEvaluationAgent):
    """Agent for evaluating skills matching."""
    
    def get_prompt(self, candidate: Dict[str, Any], job_offer: Dict[str, Any]) -> str:
        """Generate skills matching prompt."""
        return format_skills_prompt(candidate, job_offer)
    
    def parse_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response."""
        return self.extract_json_from_response(response)


def evaluate_skills_matching(state: EvaluationState) -> Dict[str, Any]:
    """Node function for skills matching evaluation."""
    agent = SkillsMatchingAgent()
    evaluation = agent.evaluate(state["candidate"], state["job_offer"])
    return {"skills_eval": evaluation}

