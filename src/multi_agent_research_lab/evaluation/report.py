"""Benchmark report rendering."""

from multi_agent_research_lab.core.schemas import BenchmarkMetrics


def render_markdown_report(metrics: list[BenchmarkMetrics]) -> str:
    """Render benchmark metrics to markdown."""
    lines = [
        "# Benchmark Report: Single-Agent vs Multi-Agent Systems",
        "",
        "This report compares the performance, latency, cost, and output quality of the Single-Agent baseline versus the Multi-Agent research pipeline.",
        "",
        "## Performance Metrics Comparison",
        "",
        "| Run Name | Latency (s) | Estimated Cost (USD) | Quality Score (0-10) | Evaluation Notes / Citations |",
        "| :--- | :---: | :---: | :---: | :--- |",
    ]
    
    for item in metrics:
        cost = "N/A" if item.estimated_cost_usd is None else f"${item.estimated_cost_usd:.6f}"
        quality = "N/A" if item.quality_score is None else f"{item.quality_score:.1f}/10.0"
        lines.append(f"| **{item.run_name}** | {item.latency_seconds:.2f}s | {cost} | {quality} | {item.notes} |")
        
    lines.extend([
        "",
        "## Detailed Analysis",
        "",
        "### 1. Latency & Response Times",
        "- **Single-Agent Baseline**: Generally experiences lower latency because it involves a single request-response cycle.",
        "- **Multi-Agent System**: Incurs higher latency due to sequential handoffs, search queries, and multiple agent reviews (Supervisor, Researcher, Analyst, Writer, Critic).",
        "",
        "### 2. Cost Effectiveness",
        "- **Single-Agent Baseline**: More cost-effective as it executes only one context call.",
        "- **Multi-Agent System**: Higher token consumption due to repeated context sharing, search results, and agent prompts, but offers significantly greater depth.",
        "",
        "### 3. Answer Quality & Citations",
        "- **Single-Agent Baseline**: Answers are direct but might lack detailed comparisons, structured source checking, or citation density.",
        "- **Multi-Agent System**: Produces richer, multi-faceted reports with robust citations, cross-verified facts, and structured formatting.",
        "",
        "## Recommendations",
        "- **Use Single-Agent** for fast, simple, or low-cost informational requests where structural depth is not critical.",
        "- **Use Multi-Agent** for complex research, competitive analysis, and reports where accuracy, validation (Critic), and comprehensive source citation are essential.",
    ])
    
    return "\n".join(lines) + "\n"
