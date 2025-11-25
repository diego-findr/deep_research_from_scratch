"""
Multi-Agent Candidate Evaluation System Implementation.

This module implements the collaborative evaluation graph with three specialized
recruiter agents that evaluate candidates, debate findings, and reach consensus.
"""

import json
from typing import Any, Dict, List, Literal
from langchain_core.messages import HumanMessage
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, END

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from .state import (
    CandidateEvaluationState,
    AgentEvaluation,
    DebateMessage,
    Question,
    ConsensusDecision,
    ReasoningLogEntry,
)
from .prompts import (
    TECHNICAL_SKILLS_EVALUATOR_PROMPT,
    EXPERIENCE_TRAJECTORY_EVALUATOR_PROMPT,
    CULTURAL_FIT_EVALUATOR_PROMPT,
    AGENT_DEBATE_PROMPT,
    CONSENSUS_BUILDING_PROMPT,
    QUESTION_GENERATION_PROMPT,
    format_agent_evaluations,
    format_debate_messages,
    format_enriched_data,
)


# ===== CONFIGURATION =====

# Initialize model for all operations
model = init_chat_model(model="openai:gpt-4.1")


# ===== UTILITY FUNCTIONS =====

def get_sector_from_job(enriched_job: Dict[str, Any]) -> str:
    """Extract the primary sector from enriched job data (handles both old and new formats)."""
    # New format - check identity field first
    if 'identity' in enriched_job:
        sector = enriched_job['identity'].get('sector')
        if sector:
            return sector
    
    # Old format - semantic_enrichment
    semantic = enriched_job.get("semantic_enrichment", {})
    analysis = semantic.get("analysis_components", {})
    sector_info = analysis.get("sector_inference", {})
    return sector_info.get("primary_sector", "unknown")


def get_candidate_name(enriched_candidate: Dict[str, Any]) -> str:
    """Extract candidate name from enriched data."""
    identity = enriched_candidate.get("identity", {})
    return identity.get("full_name", "Unknown Candidate")


def get_job_title(enriched_job: Dict[str, Any]) -> str:
    """Extract job title from enriched data (handles both old and new formats)."""
    # New format - check identity field first
    if 'identity' in enriched_job:
        title = enriched_job['identity'].get('title')
        if title:
            return title
    
    # Old format - raw_job_posting
    raw_job = enriched_job.get("raw_job_posting", {})
    return raw_job.get("job_title", "Unknown Role")


def safe_parse_json_response(response_content: str, pydantic_model: type):
    """Safely parse JSON response from LLM into Pydantic model."""
    import re
    
    # Try to extract JSON from markdown code blocks
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_content, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        json_str = response_content.strip()
    
    try:
        data = json.loads(json_str)
        return pydantic_model(**data)
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        print(f"Response content: {response_content[:500]}")
        raise


def add_reasoning_log(
    state: CandidateEvaluationState,
    step: str,
    agent: str | None,
    action: str,
    input_summary: str,
    output_summary: str,
    key_insights: List[str] = None,
) -> Dict[str, Any]:
    """Add an entry to the reasoning log."""
    entry = ReasoningLogEntry(
        step=step,
        agent=agent,
        action=action,
        input_summary=input_summary,
        output_summary=output_summary,
        key_insights=key_insights or [],
    )
    return {"reasoning_log": [entry.model_dump()]}


# ===== AGENT NODES =====

def evaluate_technical_skills(state: CandidateEvaluationState) -> Dict[str, Any]:
    """
    Technical Skills Evaluator Agent.
    
    Evaluates the candidate's technical skills, domain knowledge, and
    technical competencies specific to the job's sector.
    """
    print("🔧 Technical Skills Evaluator analyzing candidate...")
    
    sector = get_sector_from_job(state["enriched_job"])
    
    # Prepare prompt
    prompt = TECHNICAL_SKILLS_EVALUATOR_PROMPT.format(
        sector=sector,
        enriched_candidate=format_enriched_data(state["enriched_candidate"]),
        enriched_job=format_enriched_data(state["enriched_job"]),
    )
    
    # Get structured evaluation
    structured_llm = model.with_structured_output(AgentEvaluation)
    response = structured_llm.invoke([HumanMessage(content=prompt)])
    
    evaluation = response.model_dump()
    evaluation["agent_name"] = "technical_skills_evaluator"
    evaluation["agent_sector_expertise"] = sector
    evaluation["evaluation_focus"] = "technical_skills"
    
    print(f"   Score: {evaluation['score']:.2f} | Recommendation: {evaluation['recommendation']}")
    
    # Add to reasoning log
    log_entry = add_reasoning_log(
        state,
        step="technical_evaluation",
        agent="technical_skills_evaluator",
        action="Evaluated candidate's technical skills and domain knowledge",
        input_summary=f"Candidate: {get_candidate_name(state['enriched_candidate'])}, Sector: {sector}",
        output_summary=f"Score: {evaluation['score']:.2f}, Recommendation: {evaluation['recommendation']}",
        key_insights=evaluation["strengths"][:3],
    )
    
    return {
        "agent_evaluations": [evaluation],
        **log_entry,
    }


def evaluate_experience_trajectory(state: CandidateEvaluationState) -> Dict[str, Any]:
    """
    Experience & Trajectory Evaluator Agent.
    
    Evaluates the candidate's experience, career progression, and
    alignment with the role's seniority requirements.
    """
    print("📊 Experience & Trajectory Evaluator analyzing candidate...")
    
    sector = get_sector_from_job(state["enriched_job"])
    
    # Prepare prompt
    prompt = EXPERIENCE_TRAJECTORY_EVALUATOR_PROMPT.format(
        sector=sector,
        enriched_candidate=format_enriched_data(state["enriched_candidate"]),
        enriched_job=format_enriched_data(state["enriched_job"]),
    )
    
    # Get structured evaluation
    structured_llm = model.with_structured_output(AgentEvaluation)
    response = structured_llm.invoke([HumanMessage(content=prompt)])
    
    evaluation = response.model_dump()
    evaluation["agent_name"] = "experience_trajectory_evaluator"
    evaluation["agent_sector_expertise"] = sector
    evaluation["evaluation_focus"] = "experience_and_trajectory"
    
    print(f"   Score: {evaluation['score']:.2f} | Recommendation: {evaluation['recommendation']}")
    
    # Add to reasoning log
    log_entry = add_reasoning_log(
        state,
        step="experience_evaluation",
        agent="experience_trajectory_evaluator",
        action="Evaluated candidate's experience and career trajectory",
        input_summary=f"Candidate experience: {state['enriched_candidate'].get('identity', {}).get('years_experience', 'N/A')} years",
        output_summary=f"Score: {evaluation['score']:.2f}, Recommendation: {evaluation['recommendation']}",
        key_insights=evaluation["strengths"][:3],
    )
    
    return {
        "agent_evaluations": [evaluation],
        **log_entry,
    }


def evaluate_cultural_fit(state: CandidateEvaluationState) -> Dict[str, Any]:
    """
    Cultural Fit & Soft Skills Evaluator Agent.
    
    Evaluates the candidate's soft skills, competencies, cultural fit,
    and potential for success in the role.
    """
    print("🤝 Cultural Fit Evaluator analyzing candidate...")
    
    sector = get_sector_from_job(state["enriched_job"])
    
    # Prepare prompt
    prompt = CULTURAL_FIT_EVALUATOR_PROMPT.format(
        sector=sector,
        enriched_candidate=format_enriched_data(state["enriched_candidate"]),
        enriched_job=format_enriched_data(state["enriched_job"]),
    )
    
    # Get structured evaluation
    structured_llm = model.with_structured_output(AgentEvaluation)
    response = structured_llm.invoke([HumanMessage(content=prompt)])
    
    evaluation = response.model_dump()
    evaluation["agent_name"] = "cultural_fit_evaluator"
    evaluation["agent_sector_expertise"] = sector
    evaluation["evaluation_focus"] = "cultural_fit_and_soft_skills"
    
    print(f"   Score: {evaluation['score']:.2f} | Recommendation: {evaluation['recommendation']}")
    
    # Add to reasoning log
    log_entry = add_reasoning_log(
        state,
        step="cultural_evaluation",
        agent="cultural_fit_evaluator",
        action="Evaluated candidate's cultural fit and soft skills",
        input_summary=f"Evaluating soft skills and cultural alignment for {sector} sector",
        output_summary=f"Score: {evaluation['score']:.2f}, Recommendation: {evaluation['recommendation']}",
        key_insights=evaluation["strengths"][:3],
    )
    
    return {
        "agent_evaluations": [evaluation],
        **log_entry,
    }


def agent_debate_round(state: CandidateEvaluationState) -> Dict[str, Any]:
    """
    Facilitate one round of debate between agents.
    
    Each agent reviews others' evaluations and the debate history,
    then contributes messages (arguments, questions, agreements).
    """
    current_round = state["debate_round"]
    max_rounds = state["max_debate_rounds"]
    
    print(f"💬 Debate Round {current_round}/{max_rounds}...")
    
    agent_evaluations = state["agent_evaluations"]
    debate_history = state.get("debate_messages", [])
    
    new_messages = []
    
    # Each agent participates in the debate
    for agent_eval in agent_evaluations:
        agent_name = agent_eval["agent_name"]
        
        # Get other agents' evaluations
        other_evals = [e for e in agent_evaluations if e["agent_name"] != agent_name]
        
        # Prepare prompt
        prompt = AGENT_DEBATE_PROMPT.format(
            agent_name=agent_name,
            your_evaluation=json.dumps(agent_eval, indent=2),
            other_evaluations=json.dumps(other_evals, indent=2),
            debate_history=format_debate_messages(debate_history),
            round_number=current_round,
            max_rounds=max_rounds,
        )
        
        # Get debate messages from this agent
        # For simplicity, we'll get 1-2 messages per agent
        response = model.invoke([HumanMessage(content=prompt)])
        
        # Parse response to extract debate messages
        # In a production system, use structured output
        # For now, create a simple message
        message = DebateMessage(
            from_agent=agent_name,
            to_agent=None,
            message_type="argument",
            content=response.content,
            references=[],
        )
        
        new_messages.append(message.model_dump())
    
    # Increment debate round
    new_round = current_round + 1
    
    # Add to reasoning log
    log_entry = add_reasoning_log(
        state,
        step=f"debate_round_{current_round}",
        agent=None,
        action=f"Agents exchanged {len(new_messages)} debate messages",
        input_summary=f"Round {current_round} with {len(agent_evaluations)} agents",
        output_summary=f"Generated {len(new_messages)} debate messages",
        key_insights=[f"Agent {m['from_agent']} contributed" for m in new_messages[:3]],
    )
    
    return {
        "debate_messages": new_messages,
        "debate_round": new_round,
        **log_entry,
    }


def should_continue_debate(state: CandidateEvaluationState) -> Literal["continue", "consensus"]:
    """
    Decide whether to continue debate or move to consensus.
    
    Continue if:
    - Haven't reached max rounds
    - Agents have significant disagreement in scores
    
    Otherwise, move to consensus.
    """
    current_round = state["debate_round"]
    max_rounds = state["max_debate_rounds"]
    
    # If we've reached max rounds, go to consensus
    if current_round > max_rounds:
        return "consensus"
    
    # Check if there's significant disagreement
    evaluations = state["agent_evaluations"]
    scores = [e["score"] for e in evaluations]
    
    if len(scores) >= 2:
        score_range = max(scores) - min(scores)
        # If scores differ by more than 0.3, continue debate (if rounds remain)
        if score_range > 0.3 and current_round <= max_rounds:
            return "continue"
    
    # Otherwise, move to consensus
    return "consensus"


def generate_questions(state: CandidateEvaluationState) -> Dict[str, Any]:
    """
    Generate specialized questions that agents want to ask about the candidate.
    
    Each agent generates questions based on their evaluation and identified gaps.
    """
    print("❓ Generating specialized questions...")
    
    sector = get_sector_from_job(state["enriched_job"])
    candidate_name = get_candidate_name(state["enriched_candidate"])
    job_title = get_job_title(state["enriched_job"])
    
    all_questions = []
    
    for agent_eval in state["agent_evaluations"]:
        agent_name = agent_eval["agent_name"]
        
        prompt = QUESTION_GENERATION_PROMPT.format(
            agent_name=agent_name,
            sector=sector,
            your_evaluation=json.dumps(agent_eval, indent=2),
            candidate_name=candidate_name,
            job_title=job_title,
        )
        
        # For simplicity, get questions as text response
        # In production, use structured output for a list of Question objects
        response = model.invoke([HumanMessage(content=prompt)])
        
        # Create a sample question (in production, parse multiple structured questions)
        question = Question(
            agent_name=agent_name,
            question_text=response.content[:500],  # Truncate for demo
            question_purpose=f"Clarify uncertainties from {agent_eval['evaluation_focus']} evaluation",
            data_gap="Various gaps identified in evaluation",
            priority="important",
        )
        
        all_questions.append(question.model_dump())
    
    print(f"   Generated {len(all_questions)} specialized questions")
    
    # Add to reasoning log
    log_entry = add_reasoning_log(
        state,
        step="question_generation",
        agent=None,
        action="Generated specialized questions about candidate",
        input_summary=f"Based on {len(state['agent_evaluations'])} agent evaluations",
        output_summary=f"Generated {len(all_questions)} questions",
        key_insights=[f"Questions from {q['agent_name']}" for q in all_questions],
    )
    
    return {
        "questions_asked": all_questions,
        **log_entry,
    }


def build_consensus(state: CandidateEvaluationState) -> Dict[str, Any]:
    """
    Build final consensus decision from all agent evaluations and debate.
    
    Synthesizes individual evaluations, debate findings, and creates
    a final recommendation with detailed reasoning.
    """
    print("🎯 Building consensus decision...")
    
    sector = get_sector_from_job(state["enriched_job"])
    candidate_name = get_candidate_name(state["enriched_candidate"])
    job_title = get_job_title(state["enriched_job"])
    
    prompt = CONSENSUS_BUILDING_PROMPT.format(
        candidate_name=candidate_name,
        job_title=job_title,
        sector=sector,
        agent_evaluations=format_agent_evaluations(state["agent_evaluations"]),
        debate_messages=format_debate_messages(state.get("debate_messages", [])),
    )
    
    # Get structured consensus decision
    structured_llm = model.with_structured_output(ConsensusDecision)
    response = structured_llm.invoke([HumanMessage(content=prompt)])
    
    decision = response.model_dump()
    
    print(f"   Decision: {'✅ LIKED' if decision['liked'] else '❌ NOT LIKED'}")
    print(f"   Overall Score: {decision['overall_score']:.2f}")
    print(f"   Confidence: {decision['decision_confidence']:.2f}")
    
    # Add to reasoning log
    log_entry = add_reasoning_log(
        state,
        step="consensus_building",
        agent=None,
        action="Built final consensus decision from all agents",
        input_summary=f"{len(state['agent_evaluations'])} evaluations, {len(state.get('debate_messages', []))} debate messages",
        output_summary=f"Decision: {decision['liked']}, Score: {decision['overall_score']:.2f}",
        key_insights=decision["primary_reasons"][:3],
    )
    
    return {
        "consensus_decision": decision,
        **log_entry,
    }


# ===== GRAPH CONSTRUCTION =====

def create_evaluation_graph() -> StateGraph:
    """
    Create the multi-agent evaluation graph.
    
    Graph flow:
    1. Three agents evaluate in parallel (technical, experience, cultural)
    2. Agents debate their findings (iterative, conditional)
    3. Questions are generated
    4. Final consensus is built
    
    Returns compiled graph.
    """
    # Create graph
    workflow = StateGraph(CandidateEvaluationState)
    
    # Add evaluation nodes (will execute in parallel)
    workflow.add_node("technical_evaluation", evaluate_technical_skills)
    workflow.add_node("experience_evaluation", evaluate_experience_trajectory)
    workflow.add_node("cultural_evaluation", evaluate_cultural_fit)
    
    # Add debate node (conditional iteration)
    workflow.add_node("debate", agent_debate_round)
    
    # Add question generation node
    workflow.add_node("questions", generate_questions)
    
    # Add consensus building node
    workflow.add_node("consensus", build_consensus)
    
    # Set entry point - all three evaluations start in parallel
    workflow.set_entry_point("technical_evaluation")
    workflow.set_entry_point("experience_evaluation")
    workflow.set_entry_point("cultural_evaluation")
    
    # After evaluations, go to debate
    workflow.add_edge("technical_evaluation", "debate")
    workflow.add_edge("experience_evaluation", "debate")
    workflow.add_edge("cultural_evaluation", "debate")
    
    # Conditional edge: continue debate or move to questions
    workflow.add_conditional_edges(
        "debate",
        should_continue_debate,
        {
            "continue": "debate",
            "consensus": "questions",
        },
    )
    
    # After questions, build consensus
    workflow.add_edge("questions", "consensus")
    
    # After consensus, end
    workflow.add_edge("consensus", END)
    
    return workflow.compile()


# ===== MAIN EVALUATION FUNCTION =====

def evaluate_candidate(
    enriched_candidate: Dict[str, Any],
    enriched_job: Dict[str, Any],
    max_debate_rounds: int = 2,
) -> Dict[str, Any]:
    """
    Evaluate a candidate for a job using multi-agent collaborative system.
    
    Args:
        enriched_candidate: Enriched candidate profile from profile_enrichment
        enriched_job: Enriched job offer from job_enrichment
        max_debate_rounds: Maximum number of debate rounds (default: 2)
    
    Returns:
        Complete evaluation result with all agent evaluations, debate transcript,
        questions, consensus decision, and reasoning log.
    """
    print(f"\n{'='*60}")
    print(f"MULTI-AGENT CANDIDATE EVALUATION")
    print(f"{'='*60}")
    print(f"Candidate: {get_candidate_name(enriched_candidate)}")
    print(f"Job: {get_job_title(enriched_job)}")
    print(f"Sector: {get_sector_from_job(enriched_job)}")
    print(f"{'='*60}\n")
    
    # Initialize state
    initial_state: CandidateEvaluationState = {
        "enriched_candidate": enriched_candidate,
        "enriched_job": enriched_job,
        "agent_evaluations": [],
        "debate_messages": [],
        "questions_asked": [],
        "consensus_decision": None,
        "reasoning_log": [],
        "debate_round": 1,
        "max_debate_rounds": max_debate_rounds,
    }
    
    # Create and run graph
    graph = create_evaluation_graph()
    result = graph.invoke(initial_state)
    
    print(f"\n{'='*60}")
    print("EVALUATION COMPLETE")
    print(f"{'='*60}\n")
    
    return result
