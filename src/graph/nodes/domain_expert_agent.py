"""Domain Expert Agent node (dynamic based on sector)."""

from typing import Any, Dict
from src.graph.state import EvaluationState
from src.agents.base_agent import BaseEvaluationAgent
from src.agents.prompts.domain_expert_prompt import format_domain_expert_prompt


class DomainExpertAgent(BaseEvaluationAgent):
    """Agent for domain-specific evaluation."""
    
    def __init__(self, sector: str, **kwargs: Any):
        """Initialize with specific sector."""
        super().__init__(**kwargs)
        self.sector = sector
        self.agent_name = f"domain_expert_{sector}"
    
    def get_prompt(self, candidate: Dict[str, Any], job_offer: Dict[str, Any]) -> str:
        """Generate domain expert prompt."""
        return format_domain_expert_prompt(candidate, job_offer, self.sector)
    
    def parse_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response."""
        return self.extract_json_from_response(response)


def evaluate_domain_expertise(state: EvaluationState) -> Dict[str, Any]:
    """Node function for domain expert evaluation."""
    # Determine sector from job offer
    job_sector_info = state["job_offer"].get("semantic_enrichment", {}).get("sector_inference", {})
    sector = job_sector_info.get("primary_sector", "general")
    
    agent = DomainExpertAgent(sector=sector)
    evaluation = agent.evaluate(state["candidate"], state["job_offer"])
    return {"domain_expert_eval": evaluation}

