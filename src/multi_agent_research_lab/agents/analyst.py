"""Analyst agent implementation."""

import logging

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient

logger = logging.getLogger(__name__)


class AnalystAgent(BaseAgent):
    """Turns research notes into structured insights."""

    name = "analyst"

    def __init__(self) -> None:
        self.llm_client = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.analysis_notes`."""
        logger.info("AnalystAgent executing...")

        if not state.research_notes:
            logger.warning("AnalystAgent run without research notes. Routing back.")
            state.errors.append("AnalystAgent: Missing research notes to analyze.")
            return state

        system_prompt = (
            "You are a Senior Systems Analyst. Your job is to take raw research notes and analyze them. "
            "You should:\n"
            "1. Extract key claims, technologies, or architectures mentioned in the research.\n"
            "2. Compare and contrast different perspectives, vendors, or approaches.\n"
            "3. Identify any logical gaps, weak evidence, or areas where additional research is needed.\n"
            "4. Organize these findings into a structured analysis report with clear headers (e.g. Key Claims, "
            "Comparative Analysis, Evidence Quality & Gaps, Strategic Recommendations).\n"
            "Ensure you maintain citations referring to the original sources of research notes."
        )

        user_prompt = f"""Primary Query: {state.request.query}
Target Audience: {state.request.audience}
Research Notes:\n{state.research_notes}

Analyze the research notes and produce structured insights:"""

        try:
            response = self.llm_client.complete(system_prompt, user_prompt)
            state.analysis_notes = response.content.strip()

            result = AgentResult(
                agent=AgentName.ANALYST,
                content=state.analysis_notes,
                metadata={
                    "input_tokens": response.input_tokens,
                    "output_tokens": response.output_tokens,
                    "cost_usd": response.cost_usd,
                }
            )
            state.agent_results.append(result)
            state.add_trace_event(
                "analyst_run",
                {
                    "input_tokens": response.input_tokens,
                    "output_tokens": response.output_tokens,
                    "cost_usd": response.cost_usd,
                }
            )
            return state
        except Exception as e:
            logger.error(f"AnalystAgent execution failed: {e}")
            state.errors.append(f"AnalystAgent error: {str(e)}")
            return state
