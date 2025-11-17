"""Sector Alignment Agent node."""

from typing import Any, Dict
from src.graph.state import EvaluationState
from src.agents.base_agent import BaseEvaluationAgent
from src.agents.prompts.sector_prompt import format_sector_prompt


class SectorAlignmentAgent(BaseEvaluationAgent):
    """Agent for evaluating sector alignment between candidate and job."""
    
    def get_prompt(self, candidate: Dict[str, Any], job_offer: Dict[str, Any]) -> str:
        """Generate sector alignment prompt."""
        return format_sector_prompt(candidate, job_offer)
    
    def parse_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response."""
        return self.extract_json_from_response(response)


def evaluate_sector_alignment(state: EvaluationState) -> Dict[str, Any]:
    """
    Node function for sector alignment evaluation.
    
    Args:
        state: Current evaluation state
        
    Returns:
        Updated state with sector evaluation
    """
    agent = SectorAlignmentAgent()
    evaluation = agent.evaluate(state["candidate"], state["job_offer"])
    
    return {"sector_eval": evaluation}

