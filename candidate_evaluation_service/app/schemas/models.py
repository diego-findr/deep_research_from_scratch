from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class AgentEvaluation(BaseModel):
    """Schema for an individual agent's evaluation of the candidate."""
    
    agent_name: str = Field(
        description="Name of the evaluating agent (e.g., 'technical_skills_evaluator')",
    )
    
    agent_sector_expertise: str = Field(
        description="The sector this agent specialized in for this evaluation",
    )
    
    evaluation_focus: str = Field(
        description="What aspect this agent is evaluating (skills, experience, cultural fit)",
    )
    
    score: float = Field(
        description="Numerical score from 0.0 (poor fit) to 1.0 (excellent fit)",
        ge=0.0,
        le=1.0,
    )
    
    strengths: List[str] = Field(
        description="Key strengths of the candidate for this role",
    )
    
    weaknesses: List[str] = Field(
        description="Key weaknesses or gaps of the candidate for this role",
    )
    
    detailed_reasoning: str = Field(
        description="Detailed explanation of the evaluation with specific evidence from enriched data",
    )
    
    recommendation: str = Field(
        description="Agent's recommendation: 'strong_yes', 'yes', 'maybe', 'no', 'strong_no'",
    )
    
    concerns: List[str] = Field(
        description="Specific concerns to discuss in the debate phase",
        default_factory=list,
    )
    
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
    )


class DebateMessage(BaseModel):
    """Schema for a message in the agent debate."""
    
    from_agent: str = Field(
        description="Agent sending the message",
    )
    
    to_agent: Optional[str] = Field(
        description="Target agent (None means all agents)",
        default=None,
    )
    
    message_type: str = Field(
        description="Type: 'argument', 'question', 'response', 'agreement', 'disagreement'",
    )
    
    content: str = Field(
        description="The actual message content",
    )
    
    references: List[str] = Field(
        description="References to specific data points from enriched candidate/job",
        default_factory=list,
    )
    
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
    )


class Question(BaseModel):
    """Schema for a specialized question about the candidate."""
    
    agent_name: str = Field(
        description="Agent generating the question",
    )
    
    question_text: str = Field(
        description="The question text",
    )
    
    question_purpose: str = Field(
        description="Why this question is important for the evaluation",
    )
    
    data_gap: str = Field(
        description="What information gap this question addresses",
    )
    
    priority: str = Field(
        description="Priority level: 'critical', 'important', 'nice_to_have'",
    )
    
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
    )


class AgentAgreement(BaseModel):
    """Schema for an agent's final stance."""
    agent_name: str = Field(description="Name of the agent")
    recommendation: str = Field(description="Agent's final recommendation")


class CompatibilityScore(BaseModel):
    """Schema for compatibility score by dimension."""
    dimension: str = Field(description="Dimension name (technical, experience, cultural)")
    score: float = Field(description="Score for this dimension (0.0-1.0)", ge=0.0, le=1.0)


class ConsensusDecision(BaseModel):
    """Schema for the final consensus decision."""
    
    liked: bool = Field(
        description="Final decision: True if candidate should proceed, False otherwise",
    )
    
    overall_score: float = Field(
        description="Aggregated score from all agents (0.0-1.0)",
        ge=0.0,
        le=1.0,
    )
    
    decision_confidence: float = Field(
        description="Confidence in this decision (0.0-1.0)",
        ge=0.0,
        le=1.0,
    )
    
    primary_reasons: List[str] = Field(
        description="Top 3-5 reasons for the decision",
    )
    
    consensus_summary: str = Field(
        description="Overall summary of the consensus reached by agents",
    )
    
    agent_agreements: List[AgentAgreement] = Field(
        description="Each agent's final stance",
    )
    
    key_strengths: List[str] = Field(
        description="Agreed-upon key strengths",
    )
    
    key_concerns: List[str] = Field(
        description="Agreed-upon key concerns or gaps",
    )
    
    suggested_next_steps: List[str] = Field(
        description="Recommended next steps (e.g., specific interview questions, assessments)",
    )
    
    compatibility_breakdown: List[CompatibilityScore] = Field(
        description="Compatibility scores by dimension",
    )
    
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
    )


class GatekeeperDecision(BaseModel):
    """Schema for the initial gatekeeper decision."""
    
    proceed: bool = Field(
        description="Whether to proceed with full evaluation (True) or fast reject (False)",
    )
    
    confidence: float = Field(
        description="Confidence in the decision (0.0-1.0)",
        ge=0.0,
        le=1.0,
    )
    
    reasoning: str = Field(
        description="Reasoning for the decision, highlighting key knockout factors if rejected",
    )
    
    knockout_reasons: List[str] = Field(
        description="List of knockout criteria met (if any), e.g., 'Sector Mismatch', 'Seniority Gap'",
        default_factory=list,
    )
    
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
    )


class ReasoningLogEntry(BaseModel):
    """Schema for a single entry in the reasoning log."""
    
    step: str = Field(
        description="Step name (e.g., 'technical_evaluation', 'debate_round_1')",
    )
    
    agent: Optional[str] = Field(
        description="Agent responsible for this step (if applicable)",
        default=None,
    )
    
    action: str = Field(
        description="What action was taken",
    )
    
    input_summary: str = Field(
        description="Summary of inputs to this step",
    )
    
    output_summary: str = Field(
        description="Summary of outputs from this step",
    )
    
    key_insights: List[str] = Field(
        description="Key insights or findings from this step",
        default_factory=list,
    )
    
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
    )
