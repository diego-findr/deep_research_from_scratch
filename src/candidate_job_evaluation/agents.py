"""Specialized evaluation agents."""

import json
from typing import Any, Dict, Optional

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from .config import EvaluationConfig
from .prompts import (
    COMPETENCIES_AGENT_PROMPT,
    DOMAIN_EXPERT_PROMPT,
    ORCHESTRATOR_PROMPT,
    RED_FLAGS_AGENT_PROMPT,
    SECTOR_AGENT_PROMPT,
    SECTOR_CONSIDERATIONS,
    SENIORITY_AGENT_PROMPT,
    SKILLS_AGENT_PROMPT,
)
from .state import AgentEvaluation, EvaluationState, FinalEvaluation


class EvaluationAgents:
    """Container for all specialized evaluation agents."""

    def __init__(self, config: EvaluationConfig):
        """Initialize agents with configuration.

        Args:
            config: Evaluation configuration
        """
        self.config = config
        self.llm = ChatOpenAI(
            model=config.llm_model,
            temperature=config.llm_temperature,
        )

    def _safe_agent_call(
        self, prompt: str, agent_name: str, state: EvaluationState
    ) -> AgentEvaluation:
        """Safely call an agent with error handling.

        Args:
            prompt: Formatted prompt for the agent
            agent_name: Name of the agent
            state: Current evaluation state

        Returns:
            AgentEvaluation with results or fallback
        """
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            result = json.loads(response.content)
            return AgentEvaluation(**result)
        except Exception as e:
            print(f"Error in {agent_name}: {e}")
            # Fallback evaluation
            return AgentEvaluation(
                agent_name=agent_name,
                score=self.config.agent_failure_default_score,
                alignment_level="partial_match",
                reasoning=f"Agent failed with error: {str(e)}. Using default score.",
                evidence=[],
                red_flags=[f"agent_error: {agent_name}"],
                confidence=0.3,
            )

    def sector_alignment_agent(self, state: EvaluationState) -> Dict[str, Any]:
        """Evaluate sector alignment between candidate and job.

        Args:
            state: Current evaluation state

        Returns:
            Updated state with sector evaluation
        """
        candidate = state["candidate"]
        job = state["job_offer"]

        prompt = SECTOR_AGENT_PROMPT.format(
            candidate_sector=json.dumps(
                candidate["semantic_enrichment"]["analysis_components"][
                    "sector_inference"
                ],
                indent=2,
            ),
            job_sector=json.dumps(
                job["semantic_enrichment"]["analysis_components"]["sector_inference"],
                indent=2,
            ),
            candidate_disambiguation=json.dumps(
                candidate["semantic_enrichment"]["disambiguation_map"], indent=2
            ),
            job_red_flags=json.dumps(
                job["semantic_enrichment"]["ideal_candidate"].get(
                    "potential_red_flags", []
                ),
                indent=2,
            ),
        )

        evaluation = self._safe_agent_call(prompt, "sector_alignment", state)

        return {
            "sector_evaluation": evaluation,
            "messages": [
                HumanMessage(content=f"Sector alignment evaluated: {evaluation.score}/100")
            ],
        }

    def skills_matching_agent(self, state: EvaluationState) -> Dict[str, Any]:
        """Evaluate skills match between candidate and job.

        Args:
            state: Current evaluation state

        Returns:
            Updated state with skills evaluation
        """
        candidate = state["candidate"]
        job = state["job_offer"]

        prompt = SKILLS_AGENT_PROMPT.format(
            candidate_skills_explicit=json.dumps(
                candidate["semantic_enrichment"]["structured_skills"]["explicit"],
                indent=2,
            ),
            candidate_skills_implicit=json.dumps(
                candidate["semantic_enrichment"]["structured_skills"]["implicit"],
                indent=2,
            ),
            job_required_skills=json.dumps(
                [
                    s
                    for s in job["semantic_enrichment"]["structured_skills"].get(
                        "explicit", []
                    )
                    + job["semantic_enrichment"]["structured_skills"].get(
                        "implicit", []
                    )
                    if s.get("importance") == "required"
                ],
                indent=2,
            ),
            job_preferred_skills=json.dumps(
                [
                    s
                    for s in job["semantic_enrichment"]["structured_skills"].get(
                        "explicit", []
                    )
                    + job["semantic_enrichment"]["structured_skills"].get(
                        "implicit", []
                    )
                    if s.get("importance") == "preferred"
                ],
                indent=2,
            ),
            candidate_synonyms=json.dumps(
                candidate["semantic_enrichment"]["synonym_map"], indent=2
            ),
            job_must_have=json.dumps(
                job["semantic_enrichment"]["ideal_candidate"].get(
                    "must_have_experience", []
                ),
                indent=2,
            ),
        )

        evaluation = self._safe_agent_call(prompt, "skills_matching", state)

        return {
            "skills_evaluation": evaluation,
            "messages": [
                HumanMessage(content=f"Skills matching evaluated: {evaluation.score}/100")
            ],
        }

    def seniority_alignment_agent(self, state: EvaluationState) -> Dict[str, Any]:
        """Evaluate seniority alignment between candidate and job.

        Args:
            state: Current evaluation state

        Returns:
            Updated state with seniority evaluation
        """
        candidate = state["candidate"]
        job = state["job_offer"]

        prompt = SENIORITY_AGENT_PROMPT.format(
            candidate_seniority=candidate["semantic_enrichment"][
                "analysis_components"
            ]["seniority_inference"]["seniority_level"],
            candidate_years=candidate["semantic_enrichment"]["analysis_components"][
                "seniority_inference"
            ]["years_experience_estimate"],
            job_seniority=job["semantic_enrichment"]["analysis_components"][
                "seniority_inference"
            ]["required_seniority"],
            job_years=job["semantic_enrichment"]["analysis_components"][
                "seniority_inference"
            ]["years_experience_required"],
            candidate_seniority_evidence=json.dumps(
                candidate["semantic_enrichment"]["analysis_components"][
                    "seniority_inference"
                ]["evidence"],
                indent=2,
            ),
            job_red_flags=json.dumps(
                job["semantic_enrichment"]["ideal_candidate"].get(
                    "potential_red_flags", []
                ),
                indent=2,
            ),
        )

        evaluation = self._safe_agent_call(prompt, "seniority_alignment", state)

        return {
            "seniority_evaluation": evaluation,
            "messages": [
                HumanMessage(
                    content=f"Seniority alignment evaluated: {evaluation.score}/100"
                )
            ],
        }

    def competencies_matching_agent(self, state: EvaluationState) -> Dict[str, Any]:
        """Evaluate competencies match between candidate and job.

        Args:
            state: Current evaluation state

        Returns:
            Updated state with competencies evaluation
        """
        candidate = state["candidate"]
        job = state["job_offer"]

        prompt = COMPETENCIES_AGENT_PROMPT.format(
            candidate_competencies=json.dumps(
                candidate["semantic_enrichment"]["structured_competencies"], indent=2
            ),
            job_competencies=json.dumps(
                job["semantic_enrichment"]["structured_competencies"], indent=2
            ),
            candidate_leadership=json.dumps(
                candidate["semantic_enrichment"]["analysis_components"][
                    "competencies_analysis"
                ].get("leadership_indicators", []),
                indent=2,
            ),
            job_leadership_level=job["semantic_enrichment"]["analysis_components"][
                "competencies_analysis"
            ].get("leadership_level", "individual_contributor"),
        )

        evaluation = self._safe_agent_call(prompt, "competencies_matching", state)

        return {
            "competencies_evaluation": evaluation,
            "messages": [
                HumanMessage(
                    content=f"Competencies matching evaluated: {evaluation.score}/100"
                )
            ],
        }

    def red_flags_detector_agent(self, state: EvaluationState) -> Dict[str, Any]:
        """Detect red flags in candidate-job match.

        Args:
            state: Current evaluation state

        Returns:
            Updated state with red flags evaluation
        """
        candidate = state["candidate"]
        job = state["job_offer"]

        prompt = RED_FLAGS_AGENT_PROMPT.format(
            candidate=json.dumps(candidate, indent=2),
            job=json.dumps(job, indent=2),
            job_red_flags=json.dumps(
                job["semantic_enrichment"]["ideal_candidate"].get(
                    "potential_red_flags", []
                ),
                indent=2,
            ),
        )

        evaluation = self._safe_agent_call(prompt, "red_flags_detector", state)

        # Check for critical red flags
        critical_flags = [
            flag
            for flag in evaluation.red_flags
            if any(
                critical_type in flag.lower()
                for critical_type in self.config.critical_red_flag_types
            )
        ]

        critical_red_flags_found = len(critical_flags) > 0

        return {
            "red_flags_evaluation": evaluation,
            "critical_red_flags_found": critical_red_flags_found,
            "early_termination": critical_red_flags_found,
            "messages": [
                HumanMessage(
                    content=f"Red flags detection: {len(evaluation.red_flags)} flags found ({'CRITICAL' if critical_red_flags_found else 'MINOR'})"
                )
            ],
        }

    def domain_expert_agent(self, state: EvaluationState) -> Dict[str, Any]:
        """Provide domain-specific expert evaluation.

        Args:
            state: Current evaluation state

        Returns:
            Updated state with domain expert evaluation
        """
        job = state["job_offer"]
        sector = job["semantic_enrichment"]["analysis_components"]["sector_inference"][
            "primary_sector"
        ]

        sector_considerations = SECTOR_CONSIDERATIONS.get(
            sector, "No specific considerations for this sector."
        )

        previous_evaluations = {
            "sector": state.get("sector_evaluation"),
            "skills": state.get("skills_evaluation"),
            "seniority": state.get("seniority_evaluation"),
            "competencies": state.get("competencies_evaluation"),
            "red_flags": state.get("red_flags_evaluation"),
        }

        prompt = DOMAIN_EXPERT_PROMPT.format(
            sector=sector,
            candidate=json.dumps(state["candidate"], indent=2),
            job=json.dumps(job, indent=2),
            previous_evaluations=json.dumps(
                {
                    k: v.model_dump() if v else None
                    for k, v in previous_evaluations.items()
                },
                indent=2,
            ),
            sector_considerations=sector_considerations,
        )

        evaluation = self._safe_agent_call(prompt, f"domain_expert_{sector}", state)

        return {
            "domain_expert_evaluation": evaluation,
            "messages": [
                HumanMessage(
                    content=f"Domain expert ({sector}) evaluated: {evaluation.score}/100"
                )
            ],
        }

    def orchestrator_agent(self, state: EvaluationState) -> Dict[str, Any]:
        """Synthesize all evaluations into final verdict.

        Args:
            state: Current evaluation state

        Returns:
            Updated state with final evaluation
        """
        job = state["job_offer"]
        sector = job["semantic_enrichment"]["analysis_components"]["sector_inference"][
            "primary_sector"
        ]

        # Get weights (apply sector-specific adjustments)
        weights = self.config.default_weights.copy()
        if sector in self.config.sector_weight_adjustments:
            weights.update(self.config.sector_weight_adjustments[sector])

        # Normalize weights to sum to 1
        total_weight = sum(weights.values())
        weights = {k: v / total_weight for k, v in weights.items()}

        prompt = ORCHESTRATOR_PROMPT.format(
            sector_eval=json.dumps(
                state["sector_evaluation"].model_dump()
                if state.get("sector_evaluation")
                else None,
                indent=2,
            ),
            skills_eval=json.dumps(
                state["skills_evaluation"].model_dump()
                if state.get("skills_evaluation")
                else None,
                indent=2,
            ),
            seniority_eval=json.dumps(
                state["seniority_evaluation"].model_dump()
                if state.get("seniority_evaluation")
                else None,
                indent=2,
            ),
            competencies_eval=json.dumps(
                state["competencies_evaluation"].model_dump()
                if state.get("competencies_evaluation")
                else None,
                indent=2,
            ),
            red_flags_eval=json.dumps(
                state["red_flags_evaluation"].model_dump()
                if state.get("red_flags_evaluation")
                else None,
                indent=2,
            ),
            domain_expert_eval=json.dumps(
                state["domain_expert_evaluation"].model_dump()
                if state.get("domain_expert_evaluation")
                else None,
                indent=2,
            ),
            weights=json.dumps(weights, indent=2),
        )

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            result = json.loads(response.content)
            final_evaluation = FinalEvaluation(**result)
        except Exception as e:
            print(f"Error in orchestrator: {e}")
            # Fallback: calculate simple weighted average
            scores = {
                "sector": state.get("sector_evaluation").score
                if state.get("sector_evaluation")
                else 50,
                "skills": state.get("skills_evaluation").score
                if state.get("skills_evaluation")
                else 50,
                "seniority": state.get("seniority_evaluation").score
                if state.get("seniority_evaluation")
                else 50,
                "competencies": state.get("competencies_evaluation").score
                if state.get("competencies_evaluation")
                else 50,
                "domain_expert": state.get("domain_expert_evaluation").score
                if state.get("domain_expert_evaluation")
                else 50,
            }

            overall_score = int(
                sum(scores.get(k, 50) * weights.get(k, 0.2) for k in weights.keys())
            )

            if state.get("critical_red_flags_found"):
                overall_score = min(overall_score, 40)

            if overall_score >= self.config.highly_recommend_threshold:
                recommendation = "highly_recommend"
            elif overall_score >= self.config.recommend_threshold:
                recommendation = "recommend"
            elif overall_score >= self.config.acceptable_threshold:
                recommendation = "acceptable"
            else:
                recommendation = "not_recommend"

            final_evaluation = FinalEvaluation(
                overall_score=overall_score,
                recommendation=recommendation,
                summary=f"Orchestrator failed. Fallback score: {overall_score}/100. Error: {str(e)}",
                strengths=[],
                concerns=["Orchestrator agent failed"],
                missing_skills=[],
                all_red_flags=[],
                agent_scores=scores,
                decision_tree="Fallback evaluation due to orchestrator failure.",
            )

        return {
            "final_evaluation": final_evaluation,
            "messages": [
                HumanMessage(
                    content=f"Final evaluation: {final_evaluation.overall_score}/100 - {final_evaluation.recommendation}"
                )
            ],
        }
