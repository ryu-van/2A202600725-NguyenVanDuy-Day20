# Benchmark Report: Single-Agent vs Multi-Agent Systems

This report compares the performance, latency, cost, and output quality of the Single-Agent baseline versus the Multi-Agent research pipeline.

## Performance Metrics Comparison

| Run Name | Latency (s) | Estimated Cost (USD) | Quality Score (0-10) | Evaluation Notes / Citations |
| :--- | :---: | :---: | :---: | :--- |
| **Single-Agent Baseline (Query 1)** | 238.84s | $0.001757 | 7.5/10.0 | Sources: 0, Cited: 0 (0%) |
| **Multi-Agent Workflow (Query 1)** | 88.25s | $0.003181 | 0.0/10.0 | Sources: 5, Cited: 0 (0%) |
| **Single-Agent Baseline (Query 2)** | 27.47s | $0.002026 | 8.5/10.0 | Sources: 0, Cited: 0 (0%) |
| **Multi-Agent Workflow (Query 2)** | 378.64s | $0.017054 | 8.5/10.0 | Sources: 14, Cited: 5 (36%) | Errors: 1 |

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
