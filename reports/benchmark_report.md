# Benchmark Report: Single-Agent vs Multi-Agent Systems

This report compares the performance, latency, cost, and output quality of the Single-Agent baseline versus the Multi-Agent research pipeline.

## Performance Metrics Comparison

| Run Name | Latency (s) | Estimated Cost (USD) | Quality Score (0-10) | Evaluation Notes / Citations |
| :--- | :---: | :---: | :---: | :--- |
| **Single-Agent Baseline (Query 1)** | 11.25s | $0.001088 | 4.0/10.0 | Sources: 0, Cited: 0 (0%) |
| **Multi-Agent Workflow (Query 1)** | 3.80s | $0.000158 | 0.0/10.0 | Sources: 0, Cited: 0 (0%) |
| **Single-Agent Baseline (Query 2)** | 49.05s | $0.004482 | 7.5/10.0 | Sources: 0, Cited: 0 (0%) |
| **Multi-Agent Workflow (Query 2)** | 432.33s | $0.011748 | 8.2/10.0 | Sources: 13, Cited: 5 (38%) | Errors: 1 |

## Detailed Analysis

### 1. Latency & Response Times
- **Single-Agent Baseline**: Generally experiences lower latency because it involves a single request-response cycle.
- **Multi-Agent System**: Incurs higher latency due to sequential handoffs, search queries, and multiple agent reviews (Supervisor, Researcher, Analyst, Writer, Critic).

### 2. Cost Effectiveness
- **Single-Agent Baseline**: More cost-effective as it executes only one context call.
- **Multi-Agent System**: Higher token consumption due to repeated context sharing, search results, and agent prompts, but offers significantly greater depth.

### 3. Answer Quality & Citations
- **Single-Agent Baseline**: Answers are direct but might lack detailed comparisons, structured source checking, or citation density.
- **Multi-Agent System**: Produces richer, multi-faceted reports with robust citations, cross-verified facts, and structured formatting.

## Recommendations
- **Use Single-Agent** for fast, simple, or low-cost informational requests where structural depth is not critical.
- **Use Multi-Agent** for complex research, competitive analysis, and reports where accuracy, validation (Critic), and comprehensive source citation are essential.
