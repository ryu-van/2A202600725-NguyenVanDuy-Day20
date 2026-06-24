"""Supervisor / router implementation."""

import logging

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient

logger = logging.getLogger(__name__)


class SupervisorAgent(BaseAgent):
    """Decides which worker should run next and when to stop."""

    name = "supervisor"

    def __init__(self) -> None:
        self.settings = get_settings()
        self.llm_client = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Update `state.route_history` with the next route."""
        # Enforce max iterations
        if state.iteration >= self.settings.max_iterations:
            logger.warning(
                f"Max iterations reached ({state.iteration}/{self.settings.max_iterations}). "
                "Forcing routing to done."
            )
            state.record_route("done")
            state.add_trace_event("supervisor_routing", {"route": "done", "reason": "max_iterations"})
            return state

        # Prepare context for the routing decision
        sources_summary = "\n".join(
            f"- [{doc.title}]({doc.url or 'N/A'}): {doc.snippet[:150]}..."
            for doc in state.sources
        ) if state.sources else "None"

        system_prompt = (
            "You are the Supervisor of a Multi-Agent Research System. Your goal is to orchestrate a team of "
            "specialized agents (Researcher, Analyst, Writer, Critic) to answer a research query.\n\n"
            "Your routing choices are:\n"
            "1. 'researcher': Choose this if more research sources or specific facts/snippets need to be gathered, "
            "or if the critic flagged research gaps.\n"
            "2. 'analyst': Choose this if research notes have been updated/gathered, but need to be synthesized, "
            "compared for viewpoints, and evaluated for evidence strength.\n"
            "3. 'writer': Choose this if both research and analysis notes are ready, and a final report needs to be written "
            "or revised based on feedback.\n"
            "4. 'critic': Choose this if a draft of the final answer has been written, but needs validation/fact-checking.\n"
            "5. 'done': Choose this only if the final answer is complete, accurate, addresses the query fully, "
            "has been critiqued, and requires no further edits.\n\n"
            "Rules:\n"
            "- If no research notes exist, do NOT route directly to analyst or writer. Route to researcher first.\n"
            "- If research notes exist but no analysis notes exist, route to analyst next.\n"
            "- If research notes and analysis notes exist but final answer does not, route to writer.\n"
            "- If a final answer exists but has not been checked, route to critic.\n"
            "- If the critic flags errors, route back to researcher, analyst, or writer depending on the errors.\n"
            "- You must reply with ONLY the next routing target string (lowercase, exact match: 'researcher', 'analyst', 'writer', 'critic', or 'done'). "
            "Do not include any formatting, markdown, punctuation, or other text."
        )

        user_prompt = f"""User Query: {state.request.query}
Audience: {state.request.audience}
Current Iteration: {state.iteration}
Route History: {state.route_history}

Current State:
- Gathered Sources Count: {len(state.sources)}
- Sources Summary: {sources_summary}
- Research Notes: {state.research_notes or 'Not started'}
- Analysis Notes: {state.analysis_notes or 'Not started'}
- Critic Errors/Warnings: {state.errors or 'None'}
- Final Answer Draft: {state.final_answer or 'Not started'}

What is the next agent to call? Output only one word ('researcher', 'analyst', 'writer', 'critic', or 'done')."""

        try:
            response = self.llm_client.complete(system_prompt, user_prompt)
            route = response.content.strip().lower()
            
            # Clean up response (in case of model formatting)
            for possible_route in ["researcher", "analyst", "writer", "critic", "done"]:
                if possible_route in route:
                    route = possible_route
                    break

            if route not in ["researcher", "analyst", "writer", "critic", "done"]:
                logger.warning(f"Invalid route received: '{route}'. Defaulting to 'done'.")
                route = "done"

            logger.info(f"Supervisor decided to route to: {route} (Iteration {state.iteration})")
            state.record_route(route)
            state.add_trace_event(
                "supervisor_routing",
                {
                    "route": route,
                    "iteration": state.iteration,
                    "input_tokens": response.input_tokens,
                    "output_tokens": response.output_tokens,
                    "cost_usd": response.cost_usd,
                },
            )
            return state
        except Exception as e:
            logger.error(f"Supervisor failed to route: {e}")
            state.record_route("done")
            state.add_trace_event("supervisor_routing_error", {"error": str(e), "route": "done"})
            return state
