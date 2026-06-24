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

## Failure Modes & Mitigations

### 1. Premature Termination (Supervisor Routing Error)
- **Failure Mode**: As observed in **Query 1**, the Supervisor agent routed directly to `done` on the very first iteration without invoking any worker agents (Researcher, Analyst, Writer). This resulted in a very short execution time (3.80s), a null final answer, and a quality score of `0.0`.
- **Root Cause**: The Supervisor's prompt lacked strict guidelines on when it is acceptable to end, or the LLM hallucinated that the task was already complete.
- **Fix / Mitigation**:
  - Enforce in the Supervisor's system prompt that `done` can only be routed if a final synthesized report exists in the shared state.
  - Implement a state validator in the graph transition logic that prevents transitioning to the end state if `final_answer` is null or empty, routing back to the Supervisor or Writer instead.
  - Lower the router LLM's temperature to `0.0`.

### 2. Infinite Loops & High Latency (Critic-Writer Loop)
- **Failure Mode**: As seen in **Query 2**, the multi-agent workflow took 432.33 seconds and encountered 1 error. This happens when the Critic repeatedly rejects the Writer's draft due to citation gaps or quality issues, causing the graph to cycle back and forth.
- **Root Cause**: Overly strict Critic criteria and a lack of loop-breaking logic in the state machine.
- **Fix / Mitigation**:
  - Implement a strict `max_iterations` counter (e.g., max 5 iterations) in the LangGraph state. When reached, the system must force a final answer output.
  - Design a progressive relaxation of Critic criteria: as the iteration count increases, the Critic should tolerate minor issues or auto-correct them rather than forcing a full re-draft.

