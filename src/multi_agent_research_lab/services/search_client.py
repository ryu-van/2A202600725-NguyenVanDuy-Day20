"""Search client abstraction for ResearcherAgent."""

import json
import logging
import requests

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.schemas import SourceDocument
from multi_agent_research_lab.services.llm_client import LLMClient

logger = logging.getLogger(__name__)


class SearchClient:
    """Provider-agnostic search client with Tavily and LLM-fallback."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._llm_client = None

    def _get_llm_client(self) -> LLMClient:
        if self._llm_client is None:
            self._llm_client = LLMClient()
        return self._llm_client

    def search(self, query: str, max_results: int = 5) -> list[SourceDocument]:
        """Search for documents relevant to a query.

        If TAVILY_API_KEY is available, executes a real Tavily search.
        Otherwise, falls back to generating simulated search results via LLM.
        """
        api_key = self.settings.tavily_api_key

        if api_key:
            logger.info("Tavily API key found. Executing live search.")
            try:
                response = requests.post(
                    "https://api.tavily.com/search",
                    json={
                        "api_key": api_key,
                        "query": query,
                        "search_depth": "basic",
                        "max_results": max_results,
                    },
                    timeout=10,
                )
                response.raise_for_status()
                data = response.json()
                results = data.get("results", [])
                
                documents = []
                for res in results[:max_results]:
                    documents.append(
                        SourceDocument(
                            title=res.get("title", "Untitled Document"),
                            url=res.get("url"),
                            snippet=res.get("content", ""),
                            metadata={"score": res.get("score")},
                        )
                    )
                return documents
            except Exception as e:
                logger.error(f"Error querying Tavily API: {e}. Falling back to LLM simulation.")
                # Fallback to LLM simulation in case API call fails

        logger.info(f"No Tavily API key or query failed. Simulating search results via LLM for: '{query}'")
        try:
            llm = self._get_llm_client()
            system_prompt = (
                "You are simulating a search engine index server. Your task is to generate realistic "
                "search results in response to the user's search query.\n"
                "Return the results STRICTLY as a JSON list of objects. Do not include markdown codeblocks (e.g. ```json), "
                "do not write explanations. Return ONLY the raw JSON array string.\n"
                "Each object in the array must contain:\n"
                "- 'title': The title of the webpage / article (realistic and professional)\n"
                "- 'url': A realistic URL where this information would be hosted\n"
                "- 'snippet': A paragraph containing factual details, numbers, dates, or technical descriptions related to the query."
            )
            user_prompt = f"Query: {query}\nGenerate {max_results} search results."
            
            response = llm.complete(system_prompt, user_prompt)
            raw_content = response.content.strip()
            
            # Strip markdown formatting block wrapper if the LLM output contains it
            if raw_content.startswith("```"):
                # strip opening
                if raw_content.startswith("```json"):
                    raw_content = raw_content[7:]
                else:
                    raw_content = raw_content[3:]
                # strip closing
                if raw_content.endswith("```"):
                    raw_content = raw_content[:-3]
                raw_content = raw_content.strip()
                
            results = json.loads(raw_content)
            
            documents = []
            for item in results[:max_results]:
                documents.append(
                    SourceDocument(
                        title=item.get("title", "Simulated Web Result"),
                        url=item.get("url", "https://example.com/simulated-result"),
                        snippet=item.get("snippet", ""),
                        metadata={"simulated": True},
                    )
                )
            return documents
        except Exception as e:
            logger.error(f"Failed to generate simulated search results: {e}")
            # Absolute fallback to hardcoded mock result to ensure execution never fails
            return [
                SourceDocument(
                    title=f"Mock Results for {query}",
                    url="https://example.com/mock-search",
                    snippet=f"This is a backup search result about '{query}' since both search API and LLM generation failed.",
                    metadata={"fallback": True},
                )
            ]
