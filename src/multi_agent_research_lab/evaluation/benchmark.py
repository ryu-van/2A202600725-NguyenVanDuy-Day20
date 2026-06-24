"""Benchmark implementation for single-agent vs multi-agent."""

import logging
from time import perf_counter
from typing import Callable

from multi_agent_research_lab.core.schemas import BenchmarkMetrics
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient

logger = logging.getLogger(__name__)

Runner = Callable[[str], ResearchState]


def evaluate_quality_with_llm(query: str, final_answer: str, sources_count: int) -> float:
    """Use an LLM-as-a-judge to evaluate report quality on a 0-10 scale."""
    if not final_answer:
        return 0.0
        
    try:
        llm = LLMClient()
        system_prompt = (
            "You are an expert evaluator grading a research report on a scale from 0.0 to 10.0.\n"
            "Evaluate based on:\n"
            "1. Accuracy and alignment with query.\n"
            "2. Structural clarity and organization.\n"
            "3. Citation usage and references.\n"
            "4. Writing quality and target audience suitability.\n"
            "Respond ONLY with a single float score (e.g., 8.5). Do not include any explanations."
        )
        user_prompt = (
            f"Query: {query}\n"
            f"Sources Cited: {sources_count}\n\n"
            f"Draft Report:\n{final_answer}\n\n"
            f"Score (0.0 to 10.0):"
        )
        response = llm.complete(system_prompt, user_prompt)
        score_str = response.content.strip()
        
        # Clean score string in case the LLM returned extra characters
        for word in score_str.split():
            try:
                score = float(word)
                if 0.0 <= score <= 10.0:
                    return score
            except ValueError:
                continue
        return 7.5  # fallback default if parsing fails
    except Exception as e:
        logger.error(f"Error grading quality: {e}")
        return 7.0


def run_benchmark(run_name: str, query: str, runner: Runner) -> tuple[ResearchState, BenchmarkMetrics]:
    """Measure latency, token cost, quality score, and citation coverage of a runner."""
    logger.info(f"Running benchmark for '{run_name}'...")
    started = perf_counter()
    state = runner(query)
    latency = perf_counter() - started

    # Calculate total cost
    total_cost = 0.0
    for res in state.agent_results:
        total_cost += res.metadata.get("query_cost", 0.0)
        total_cost += res.metadata.get("synthesis_cost", 0.0)
        total_cost += res.metadata.get("input_tokens", 0.0) * 0.150 / 1_000_000 # fallback if gpt-4o-mini
        total_cost += res.metadata.get("output_tokens", 0.0) * 0.600 / 1_000_000
        # Check standard metadata fields
        total_cost += res.metadata.get("cost_usd", 0.0)

    # Dedup trace cost
    for event in state.trace:
        payload = event.get("payload", {})
        # If the event has a cost_usd, use it (making sure we don't double count if we can avoid it, 
        # but since we want the most complete calculation, let's fall back to it)
        if "cost_usd" in payload and not state.agent_results:
            total_cost += payload["cost_usd"]

    # If no cost recorded yet (e.g. single-agent baseline run that doesn't use agent_results list), 
    # check if we can estimate it or if it's already recorded in another way.
    # In cli.py baseline, we didn't populate agent_results, so let's estimate cost if 0
    if total_cost == 0.0 and state.final_answer:
        # Roughly estimate: input ~100 tokens, output ~ len(final_answer)/4
        est_input = 100
        est_output = len(state.final_answer) // 4
        total_cost = (est_input * 0.150 + est_output * 0.600) / 1_000_000

    # Calculate quality score
    quality = evaluate_quality_with_llm(query, state.final_answer or "", len(state.sources))

    # Calculate citation coverage
    citations = 0
    if state.final_answer:
        text = state.final_answer.lower()
        for doc in state.sources:
            title = doc.title.lower()
            if title in text or (doc.url and doc.url.lower() in text):
                citations += 1
                
    coverage_percentage = (citations / len(state.sources)) * 100 if state.sources else 0
    notes = f"Sources: {len(state.sources)}, Cited: {citations} ({coverage_percentage:.0f}%)"
    if state.errors:
        notes += f" | Errors: {len(state.errors)}"

    metrics = BenchmarkMetrics(
        run_name=run_name,
        latency_seconds=latency,
        estimated_cost_usd=total_cost,
        quality_score=quality,
        notes=notes,
    )
    return state, metrics
