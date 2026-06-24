"""Writer agent implementation."""

import logging

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient

logger = logging.getLogger(__name__)


class WriterAgent(BaseAgent):
    """Produces final answer from research and analysis notes."""

    name = "writer"

    def __init__(self) -> None:
        self.llm_client = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.final_answer`."""
        logger.info("WriterAgent executing...")

        if not state.research_notes:
            logger.warning("WriterAgent run without research notes.")
            state.errors.append("WriterAgent: Missing research notes.")
            return state

        # Collect sources list for referencing
        sources_list = "\n".join(
            f"- [{doc.title}]({doc.url or 'N/A'})"
            for doc in state.sources
        ) if state.sources else "None"

        system_prompt = (
            "You are a Technical Writer. Your goal is to draft a comprehensive, clean, and publication-ready "
            "report answering the user's primary query.\n"
            "You must:\n"
            "1. Tailor the tone, depth, and vocabulary to the target audience.\n"
            "2. Combine research notes and analysis notes into a cohesive, professional narrative.\n"
            "3. Format with clean markdown headings, bullet points, and bold text for key terms.\n"
            "4. Include inline citations to the sources (e.g. [Title of Source](URL) or simply referencing the source title).\n"
            "5. Append a 'References' section at the end of the report listing all sources used."
        )

        user_prompt = f"""Primary Query: {state.request.query}
Target Audience: {state.request.audience}
Research Notes:\n{state.research_notes}
Analysis Notes:\n{state.analysis_notes or 'None'}
Sources:\n{sources_list}

Draft the final report:"""

        try:
            response = self.llm_client.complete(system_prompt, user_prompt)
            state.final_answer = response.content.strip()

            result = AgentResult(
                agent=AgentName.WRITER,
                content=state.final_answer,
                metadata={
                    "input_tokens": response.input_tokens,
                    "output_tokens": response.output_tokens,
                    "cost_usd": response.cost_usd,
                }
            )
            state.agent_results.append(result)
            state.add_trace_event(
                "writer_run",
                {
                    "input_tokens": response.input_tokens,
                    "output_tokens": response.output_tokens,
                    "cost_usd": response.cost_usd,
                }
            )
            return state
        except Exception as e:
            logger.error(f"WriterAgent execution failed: {e}")
            state.errors.append(f"WriterAgent error: {str(e)}")
            return state
