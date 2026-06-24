import os
import sys

# Ensure project root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.evaluation.benchmark import run_benchmark
from multi_agent_research_lab.evaluation.report import render_markdown_report
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow


def run_baseline_agent(query: str) -> ResearchState:
    state = ResearchState(request=ResearchQuery(query=query))
    llm_client = LLMClient()
    system_prompt = (
        "You are an expert research assistant. Answer the user's research query comprehensively, "
        "writing a clear, structured report with markdown sections, details, and proper explanations."
    )
    user_prompt = f"Query: {query}\nAudience: {state.request.audience}"
    try:
        response = llm_client.complete(system_prompt, user_prompt)
        state.final_answer = response.content
        
        # Record a dummy result to capture tokens in benchmark
        from multi_agent_research_lab.core.schemas import AgentName, AgentResult
        result = AgentResult(
            agent=AgentName.WRITER,
            content=response.content,
            metadata={
                "cost_usd": response.cost_usd,
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens
            }
        )
        state.agent_results.append(result)
    except Exception as e:
        state.errors.append(str(e))
    return state


def run_multi_agent(query: str) -> ResearchState:
    state = ResearchState(request=ResearchQuery(query=query))
    workflow = MultiAgentWorkflow()
    return workflow.run(state)


def main():
    from multi_agent_research_lab.evaluation.html_report import render_html_report
    queries = [
        "Research GraphRAG state-of-the-art and write a 500-word summary",
        "Analyze the security vulnerabilities of Web3 smart contracts",
    ]
    
    all_metrics = []
    runs_data = []
    
    for idx, query in enumerate(queries):
        print(f"\n=====================================")
        print(f"Benchmarking Query {idx+1}: {query}")
        print(f"=====================================")
        
        # Run baseline
        baseline_state, baseline_metrics = run_benchmark(
            f"Single-Agent Baseline (Query {idx+1})", query, run_baseline_agent
        )
        all_metrics.append(baseline_metrics)
        print(
            f"Baseline Latency: {baseline_metrics.latency_seconds:.2f}s | "
            f"Cost: ${baseline_metrics.estimated_cost_usd:.6f}"
        )
        
        runs_data.append({
            "run_name": baseline_metrics.run_name,
            "query": query,
            "latency_seconds": baseline_metrics.latency_seconds,
            "estimated_cost_usd": baseline_metrics.estimated_cost_usd,
            "quality_score": baseline_metrics.quality_score,
            "notes": baseline_metrics.notes,
            "route_history": baseline_state.route_history,
            "sources": [s.model_dump() for s in baseline_state.sources],
            "trace": baseline_state.trace,
            "final_answer": baseline_state.final_answer,
            "research_notes": baseline_state.research_notes,
            "analysis_notes": baseline_state.analysis_notes,
            "errors": baseline_state.errors,
        })
        
        # Run multi-agent
        multi_state, multi_metrics = run_benchmark(
            f"Multi-Agent Workflow (Query {idx+1})", query, run_multi_agent
        )
        all_metrics.append(multi_metrics)
        print(
            f"Multi-Agent Latency: {multi_metrics.latency_seconds:.2f}s | "
            f"Cost: ${multi_metrics.estimated_cost_usd:.6f}"
        )
        
        runs_data.append({
            "run_name": multi_metrics.run_name,
            "query": query,
            "latency_seconds": multi_metrics.latency_seconds,
            "estimated_cost_usd": multi_metrics.estimated_cost_usd,
            "quality_score": multi_metrics.quality_score,
            "notes": multi_metrics.notes,
            "route_history": multi_state.route_history,
            "sources": [s.model_dump() for s in multi_state.sources],
            "trace": multi_state.trace,
            "final_answer": multi_state.final_answer,
            "research_notes": multi_state.research_notes,
            "analysis_notes": multi_state.analysis_notes,
            "errors": multi_state.errors,
        })
        
    report_md = render_markdown_report(all_metrics)
    report_html = render_html_report(runs_data)
    
    os.makedirs("reports", exist_ok=True)
    with open("reports/benchmark_report.md", "w", encoding="utf-8") as f:
        f.write(report_md)
        
    with open("reports/benchmark_report.html", "w", encoding="utf-8") as f:
        f.write(report_html)
        
    print("\nBenchmark completed successfully!")
    print("Report written to reports/benchmark_report.md")
    print("Interactive HTML report written to reports/benchmark_report.html")


if __name__ == "__main__":
    main()
