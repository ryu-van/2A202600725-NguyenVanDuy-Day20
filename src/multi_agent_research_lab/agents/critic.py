"""Critic agent implementation."""

import logging

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient

logger = logging.getLogger(__name__)


class CriticAgent(BaseAgent):
    """Optional fact-checking and safety-review agent."""

    name = "critic"

    def __init__(self) -> None:
        self.llm_client = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Validate final answer and append findings."""
        logger.info("CriticAgent executing...")

        if not state.final_answer:
            logger.warning("CriticAgent run without a final answer.")
            state.errors.append("CriticAgent: Missing final answer to critique.")
            return state

        sources_summary = "\n".join(
            f"- [{doc.title}]({doc.url or 'N/A'}): {doc.snippet}"
            for doc in state.sources
        ) if state.sources else "None"

        system_prompt = (
            "You are a Critical Fact-Checker and Editor. Your job is to verify the draft final report "
            "against the original search sources and research requirements.\n"
            "Analyze the draft report for:\n"
            "1. Factuality: Are any claims hallucinated or not supported by the sources?\n"
            "2. Citation Coverage: Are statements and figures properly cited using the source names/URLs?\n"
            "3. Formatting/Tone: Is it appropriate for the target audience?\n"
            "4. Completeness: Does it address the primary query completely?\n\n"
            "Respond strictly in one of two formats:\n"
            "Format A (If errors or gaps exist):\n"
            "CRITIQUE_FAILED\n"
            "- [List of issues, missing citations, or unsupported claims]\n"
            "\n"
            "Format B (If everything is correct and no edits are needed):\n"
            "CRITIQUE_PASSED"
        )

        user_prompt = f"""Primary Query: {state.request.query}
Target Audience: {state.request.audience}
Draft Final Answer:\n{state.final_answer}
Available Sources:\n{sources_summary}

Critique the draft report and verify accuracy:"""

        try:
            response = self.llm_client.complete(system_prompt, user_prompt)
            critique = response.content.strip()

            # Record agent results
            result = AgentResult(
                agent=AgentName.CRITIC,
                content=critique,
                metadata={
                    "input_tokens": response.input_tokens,
                    "output_tokens": response.output_tokens,
                    "cost_usd": response.cost_usd,
                }
            )
            state.agent_results.append(result)
            state.add_trace_event(
                "critic_run",
                {
                    "input_tokens": response.input_tokens,
                    "output_tokens": response.output_tokens,
                    "cost_usd": response.cost_usd,
                }
            )

            if "CRITIQUE_PASSED" in critique:
                logger.info("CriticAgent approved the report (CRITIQUE_PASSED).")
                # Clear errors so supervisor knows we passed
                state.errors = []
            else:
                logger.warning("CriticAgent found issues with the report.")
                # Save the criticism details to state.errors
                state.errors = [critique]

            return state
        except Exception as e:
            logger.error(f"CriticAgent execution failed: {e}")
            state.errors.append(f"CriticAgent error: {str(e)}")
            return state
