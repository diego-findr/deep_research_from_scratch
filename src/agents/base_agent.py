"""
Base agent class for all evaluation agents.

This module provides the abstract base class that all specialized agents
inherit from, ensuring consistent structure and behavior.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from src.config import config
import json


class BaseEvaluationAgent(ABC):
    """
    Abstract base class for all evaluation agents.
    
    Each specialized agent must inherit from this class and implement
    the evaluate() method with agent-specific logic.
    """
    
    def __init__(self, llm: Optional[BaseChatModel] = None):
        """
        Initialize the agent with an LLM.
        
        Args:
            llm: Optional LLM instance. If None, creates one from config.
        """
        if llm is None:
            llm = self._create_llm_from_config()
        self.llm = llm
        self.agent_name = self.__class__.__name__.replace("Agent", "").lower()
    
    @staticmethod
    def _create_llm_from_config() -> BaseChatModel:
        """
        Create an LLM instance from configuration.
        
        Returns:
            Configured LLM instance (OpenAI or Anthropic)
            
        Raises:
            ValueError: If provider is not supported
        """
        if config.llm_provider == "openai":
            return ChatOpenAI(
                model=config.llm_model,
                temperature=config.llm_temperature,
                api_key=config.openai_api_key or None,
            )
        elif config.llm_provider == "anthropic":
            return ChatAnthropic(
                model=config.llm_model,
                temperature=config.llm_temperature,
                api_key=config.anthropic_api_key or None,
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {config.llm_provider}")
    
    @abstractmethod
    def get_prompt(self, candidate: Dict[str, Any], job_offer: Dict[str, Any]) -> str:
        """
        Generate the prompt for this agent.
        
        Args:
            candidate: Candidate profile data
            job_offer: Job offer data
            
        Returns:
            Formatted prompt string
        """
        pass
    
    @abstractmethod
    def parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse LLM response into structured output.
        
        Args:
            response: Raw LLM response string
            
        Returns:
            Parsed evaluation dict conforming to AgentEvaluation schema
        """
        pass
    
    def evaluate(
        self,
        candidate: Dict[str, Any],
        job_offer: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute evaluation for this agent.
        
        This method orchestrates the evaluation: generates prompt, calls LLM,
        parses response, and returns structured evaluation.
        
        Args:
            candidate: Complete candidate profile
            job_offer: Complete job offer
            
        Returns:
            Structured evaluation dict with keys: agent, score, evidence,
            reasoning, red_flags, confidence, details
            
        Raises:
            Exception: If evaluation fails, returns fallback evaluation
        """
        try:
            # Generate prompt
            prompt = self.get_prompt(candidate, job_offer)
            
            # Call LLM
            response = self.llm.invoke(prompt)
            
            # Extract content
            if hasattr(response, 'content'):
                content = response.content
            else:
                content = str(response)
            
            # Parse response
            evaluation = self.parse_response(content)
            
            # Ensure agent name is set
            evaluation["agent"] = self.agent_name
            
            return evaluation
            
        except Exception as e:
            # Fallback: return conservative evaluation
            return self._create_fallback_evaluation(str(e))
    
    def _create_fallback_evaluation(self, error_msg: str) -> Dict[str, Any]:
        """
        Create a fallback evaluation when agent fails.
        
        Args:
            error_msg: Error message
            
        Returns:
            Conservative evaluation dict with neutral score
        """
        return {
            "agent": self.agent_name,
            "score": 50,  # Neutral score
            "evidence": [f"Agent evaluation failed: {error_msg}"],
            "reasoning": f"Failed to complete evaluation due to error. Returning neutral score.",
            "red_flags": [f"evaluation_error_{self.agent_name}"],
            "confidence": 0.3,
            "details": {"error": error_msg, "fallback": True},
        }
    
    def extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """
        Extract JSON from LLM response that may contain additional text.
        
        Args:
            response: Raw LLM response
            
        Returns:
            Parsed JSON dict
            
        Raises:
            ValueError: If no valid JSON found
        """
        # Try to parse entire response as JSON first
        try:
            return json.loads(response.strip())
        except json.JSONDecodeError:
            pass
        
        # Look for JSON within code blocks
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            json_str = response[start:end].strip()
            return json.loads(json_str)
        
        if "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            json_str = response[start:end].strip()
            return json.loads(json_str)
        
        # Look for JSON between curly braces
        start = response.find("{")
        end = response.rfind("}") + 1
        if start != -1 and end > start:
            json_str = response[start:end]
            return json.loads(json_str)
        
        raise ValueError("No valid JSON found in response")

