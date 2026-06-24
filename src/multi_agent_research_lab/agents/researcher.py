"""Researcher agent implementation."""

import logging

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.services.search_client import SearchClient

logger = logging.getLogger(__name__)


class ResearcherAgent(BaseAgent):
    """Collects sources and creates concise research notes."""

    name = "researcher"

    def __init__(self) -> None:
        self.llm_client = LLMClient()
        self.search_client = SearchClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.sources` and `state.research_notes`."""
        logger.info("ResearcherAgent executing...")

        # Step 1: Generate search query keywords
        system_query_prompt = (
            "You are a search query optimizer. Given the user's primary query, current state, "
            "and any feedback/errors from the critic, generate a single, highly effective search query "
            "string for a search engine to find relevant information.\n"
            "Respond with ONLY the search query string, no quotes, no markdown, no introduction."
        )
        user_query_prompt = f"""Primary Query: {state.request.query}
Current Research Notes: {state.research_notes or 'None'}
Critic Feedback: {state.errors or 'None'}

Generate a specific search query to gather new details or address gaps:"""

        try:
            query_response = self.llm_client.complete(system_query_prompt, user_query_prompt)
            search_query = query_response.content.strip()
            logger.info(f"Generated search query: '{search_query}'")

            # Step 2: Execute search
            new_sources = self.search_client.search(
                query=search_query,
                max_results=state.request.max_sources,
            )

            # De-duplicate and add to state sources
            existing_urls = {doc.url for doc in state.sources if doc.url}
            added_count = 0
            for doc in new_sources:
                if doc.url not in existing_urls:
                    state.sources.append(doc)
                    if doc.url:
                        existing_urls.add(doc.url)
                    added_count += 1

            logger.info(f"Added {added_count} new unique sources. Total sources: {len(state.sources)}")

            # Step 3: Synthesize research notes
            sources_content = "\n\n".join(
                f"Source: {doc.title} ({doc.url or 'N/A'})\nSnippet: {doc.snippet}"
                for doc in state.sources
            )

            system_synthesis_prompt = (
                "You are an expert researcher. Synthesize all provided search source snippets into comprehensive, "
                "well-structured research notes. Highlight key facts, figures, timelines, and technical details.\n"
                "Do not write the final report, write raw, informative research notes categorized by topics. "
                "Ensure every key point includes clear inline citations referring to the source titles."
            )
            user_synthesis_prompt = f"""Primary Query: {state.request.query}
Audience: {state.request.audience}
Existing Research Notes: {state.research_notes or 'None'}
Available Sources:\n{sources_content}

Synthesize and write updated research notes:"""

            synthesis_response = self.llm_client.complete(system_synthesis_prompt, user_synthesis_prompt)
            state.research_notes = synthesis_response.content.strip()

            # Record agent results
            result = AgentResult(
                agent=AgentName.RESEARCHER,
                content=state.research_notes,
                metadata={
                    "search_query": search_query,
                    "sources_added": added_count,
                    "query_cost": query_response.cost_usd or 0.0,
                    "synthesis_cost": synthesis_response.cost_usd or 0.0,
                }
            )
            state.agent_results.append(result)
            state.add_trace_event(
                "researcher_run",
                {
                    "search_query": search_query,
                    "sources_added": added_count,
                    "input_tokens": (query_response.input_tokens or 0) + (synthesis_response.input_tokens or 0),
                    "output_tokens": (query_response.output_tokens or 0) + (synthesis_response.output_tokens or 0),
                    "cost_usd": (query_response.cost_usd or 0.0) + (synthesis_response.cost_usd or 0.0),
                }
            )
            return state

        except Exception as e:
            logger.error(f"ResearcherAgent execution failed: {e}")
            state.errors.append(f"ResearcherAgent error: {str(e)}")
            return state
