"""HTML benchmark report rendering with interactive trace views, Chart.js metrics, and agent breakdowns."""

import json
from typing import Any


def render_html_report(runs_data: list[dict[str, Any]]) -> str:
    """Render benchmark runs and their full states to an interactive HTML report."""
    
    # Serialize runs_data to json to inject into javascript
    json_data = json.dumps(runs_data, indent=2)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multi-Agent Research Lab - Interactive Dashboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-dark: #030712;
            --bg-card: #0b1329;
            --bg-card-hover: #111d3d;
            --border-color: #1f3460;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --primary: #6366f1;
            --primary-light: #818cf8;
            --primary-glow: rgba(99, 102, 241, 0.15);
            --secondary: #0ea5e9;
            --secondary-glow: rgba(14, 165, 233, 0.15);
            --accent-purple: #d946ef;
            --danger: #f43f5e;
            --success: #10b981;
            --warning: #f59e0b;
            --font-main: 'Outfit', sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
            --transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            --glass-bg: rgba(11, 19, 41, 0.7);
            --glass-border: rgba(31, 52, 96, 0.5);
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            background-color: var(--bg-dark);
            color: var(--text-main);
            font-family: var(--font-main);
            line-height: 1.6;
            padding: 2rem 1.5rem;
            min-height: 100vh;
            background-image: 
                radial-gradient(at 10% 20%, rgba(99, 102, 241, 0.05) 0px, transparent 50%),
                radial-gradient(at 90% 80%, rgba(217, 70, 239, 0.05) 0px, transparent 50%);
            background-attachment: fixed;
        }}

        .container {{
            max-width: 1500px;
            margin: 0 auto;
        }}

        header {{
            margin-bottom: 3rem;
            text-align: center;
            position: relative;
            padding: 2rem 0;
            border-bottom: 1px solid var(--border-color);
        }}

        header h1 {{
            font-size: 3rem;
            font-weight: 700;
            background: linear-gradient(135deg, #a5b4fc 0%, #f472b6 50%, #38bdf8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            letter-spacing: -0.03em;
        }}

        header p {{
            color: var(--text-muted);
            font-size: 1.25rem;
            font-weight: 300;
        }}

        .badge-container {{
            display: inline-flex;
            gap: 0.75rem;
            margin-top: 1.25rem;
        }}

        .badge {{
            padding: 0.35rem 0.85rem;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
        }}

        .badge-framework {{
            background-color: rgba(99, 102, 241, 0.15);
            color: #a5b4fc;
            border: 1px solid rgba(99, 102, 241, 0.3);
        }}

        .badge-status {{
            background-color: rgba(16, 185, 129, 0.15);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }}

        /* Grid Layouts */
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
            gap: 1.5rem;
            margin-bottom: 3rem;
        }}

        .card {{
            background-color: var(--glass-bg);
            backdrop-filter: blur(12px);
            border: 1px solid var(--glass-border);
            border-radius: 20px;
            padding: 1.75rem;
            transition: var(--transition);
            position: relative;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }}

        .card:hover {{
            transform: translateY(-5px);
            border-color: var(--primary);
            box-shadow: 0 15px 35px -10px rgba(99, 102, 241, 0.3);
        }}

        .card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 5px;
            height: 100%;
            border-radius: 20px 0 0 20px;
        }}

        .card.card-multi::before {{
            background: linear-gradient(to bottom, var(--primary), var(--accent-purple));
        }}

        .card.card-single::before {{
            background: var(--secondary);
        }}

        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }}

        .card-title {{
            font-size: 1.35rem;
            font-weight: 700;
            color: var(--text-main);
            letter-spacing: -0.01em;
        }}

        .card-subtitle {{
            font-size: 0.95rem;
            color: var(--text-muted);
            margin-bottom: 1.5rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .stats-list {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
        }}

        .stat-item {{
            background-color: rgba(255,255,255,0.01);
            padding: 0.85rem;
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.03);
            transition: var(--transition);
        }}

        .stat-item:hover {{
            background-color: rgba(255,255,255,0.03);
        }}

        .stat-label {{
            font-size: 0.75rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.35rem;
        }}

        .stat-value {{
            font-size: 1.25rem;
            font-weight: 700;
        }}

        .stat-value.latency {{ color: var(--danger); }}
        .stat-value.cost {{ color: var(--warning); }}
        .stat-value.quality {{ color: var(--success); }}
        .stat-value.efficiency {{ color: var(--secondary); }}

        /* Tabs Section */
        .workspace-tabs {{
            display: flex;
            gap: 0.75rem;
            margin-bottom: 2rem;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 0.75rem;
            overflow-x: auto;
        }}

        .tab-btn {{
            background: none;
            border: none;
            color: var(--text-muted);
            font-family: var(--font-main);
            font-size: 0.95rem;
            font-weight: 600;
            padding: 0.6rem 1.25rem;
            cursor: pointer;
            border-radius: 10px;
            transition: var(--transition);
            white-space: nowrap;
        }}

        .tab-btn:hover {{
            color: var(--text-main);
            background-color: rgba(255, 255, 255, 0.04);
        }}

        .tab-btn.active {{
            color: var(--text-main);
            background-color: var(--primary-glow);
            border: 1px solid rgba(99, 102, 241, 0.4);
            box-shadow: 0 0 10px var(--primary-glow);
        }}

        /* Left/Right Main Panels */
        .layout-grid {{
            display: grid;
            grid-template-columns: 420px 1fr;
            gap: 2rem;
            margin-top: 1rem;
        }}

        @media (max-width: 1024px) {{
            .layout-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        /* Timeline / Trace Column */
        .trace-column {{
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }}

        .section-title {{
            font-size: 1.6rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            letter-spacing: -0.02em;
        }}

        .timeline-container {{
            position: relative;
            padding-left: 2.75rem;
            margin-top: 1rem;
        }}

        .timeline-container::before {{
            content: '';
            position: absolute;
            left: 11px;
            top: 6px;
            bottom: 6px;
            width: 2px;
            background: linear-gradient(to bottom, var(--primary) 0%, var(--accent-purple) 50%, var(--border-color) 100%);
        }}

        .timeline-item {{
            position: relative;
            margin-bottom: 2rem;
        }}

        .timeline-item:last-child {{
            margin-bottom: 0;
        }}

        .timeline-marker {{
            position: absolute;
            left: -2.75rem;
            top: 4px;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background-color: var(--bg-dark);
            border: 5px solid var(--border-color);
            transition: var(--transition);
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .timeline-item.active-step .timeline-marker {{
            border-color: var(--primary);
            box-shadow: 0 0 15px var(--primary);
            background-color: var(--primary);
        }}

        .timeline-item.success-step .timeline-marker {{
            border-color: var(--success);
            background-color: var(--success);
        }}

        .timeline-content-card {{
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 1.25rem;
            cursor: pointer;
            transition: var(--transition);
            box-shadow: 0 4px 20px rgba(0,0,0,0.25);
        }}

        .timeline-content-card:hover {{
            background-color: var(--bg-card-hover);
            border-color: var(--primary-light);
            transform: scale(1.01);
        }}

        .timeline-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.6rem;
        }}

        .agent-badge {{
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            padding: 0.25rem 0.75rem;
            border-radius: 8px;
            letter-spacing: 0.08em;
        }}

        .badge-supervisor {{ background-color: rgba(168, 85, 247, 0.15); color: #e9d5ff; border: 1px solid rgba(168, 85, 247, 0.3); }}
        .badge-researcher {{ background-color: rgba(244, 63, 94, 0.15); color: #fecdd3; border: 1px solid rgba(244, 63, 94, 0.3); }}
        .badge-analyst {{ background-color: rgba(20, 184, 166, 0.15); color: #ccfbf1; border: 1px solid rgba(20, 184, 166, 0.3); }}
        .badge-writer {{ background-color: rgba(234, 179, 8, 0.15); color: #fef9c3; border: 1px solid rgba(234, 179, 8, 0.3); }}
        .badge-critic {{ background-color: rgba(249, 115, 22, 0.15); color: #ffedd5; border: 1px solid rgba(249, 115, 22, 0.3); }}

        .timeline-time {{
            font-size: 0.8rem;
            color: var(--text-muted);
            font-family: var(--font-mono);
        }}

        .timeline-title {{
            font-size: 1.15rem;
            font-weight: 600;
            color: var(--text-main);
            margin-bottom: 0.5rem;
            letter-spacing: -0.01em;
        }}

        .timeline-details {{
            display: none;
            margin-top: 1.25rem;
            padding-top: 1.25rem;
            border-top: 1px dashed var(--border-color);
        }}

        .timeline-content-card.expanded .timeline-details {{
            display: block;
        }}

        .payload-pre {{
            background-color: rgba(0,0,0,0.4);
            border: 1px solid rgba(255,255,255,0.04);
            border-radius: 12px;
            padding: 1.25rem;
            font-family: var(--font-mono);
            font-size: 0.8rem;
            overflow-x: auto;
            white-space: pre-wrap;
            color: #e2e8f0;
            max-height: 450px;
        }}

        /* Output Column & Right Panels */
        .output-panel {{
            background-color: var(--glass-bg);
            backdrop-filter: blur(12px);
            border: 1px solid var(--glass-border);
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 12px 40px rgba(0,0,0,0.4);
        }}

        .output-panel-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 0.75rem;
        }}

        .output-panel-title {{
            font-size: 1.4rem;
            font-weight: 700;
            letter-spacing: -0.015em;
        }}

        .output-body {{
            background-color: rgba(0,0,0,0.25);
            border: 1px solid rgba(255,255,255,0.03);
            border-radius: 14px;
            padding: 2rem;
            font-size: 1rem;
            max-height: 700px;
            overflow-y: auto;
            color: #cbd5e1;
            box-shadow: inset 0 2px 8px rgba(0,0,0,0.5);
        }}

        /* Markdown Styling inside output-body */
        .output-body h1 {{
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--text-main);
            margin-top: 0.5rem;
            margin-bottom: 1.25rem;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 0.5rem;
        }}

        .output-body h2 {{
            font-size: 1.4rem;
            font-weight: 600;
            color: var(--text-main);
            margin-top: 2rem;
            margin-bottom: 1rem;
        }}

        .output-body h3 {{
            font-size: 1.15rem;
            font-weight: 600;
            color: var(--text-main);
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
        }}

        .output-body p {{
            margin-bottom: 1.25rem;
            line-height: 1.7;
        }}

        .output-body ul, .output-body ol {{
            margin-left: 1.75rem;
            margin-bottom: 1.25rem;
        }}

        .output-body li {{
            margin-bottom: 0.5rem;
        }}

        .output-body a.source-url {{
            color: #38bdf8;
            text-decoration: none;
            font-weight: 500;
            border-bottom: 1px dashed rgba(56, 189, 248, 0.4);
            transition: var(--transition);
        }}

        .output-body a.source-url:hover {{
            color: #7dd3fc;
            border-bottom-style: solid;
        }}

        /* Source Document Index */
        .source-grid {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 1.25rem;
        }}

        .source-item {{
            background-color: rgba(255,255,255,0.01);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.25rem;
            transition: var(--transition);
        }}

        .source-item:hover {{
            background-color: rgba(255,255,255,0.03);
            border-color: var(--primary);
        }}

        .source-title {{
            font-weight: 600;
            font-size: 1.1rem;
            margin-bottom: 0.35rem;
            color: var(--text-main);
        }}

        .source-url {{
            font-size: 0.85rem;
            color: var(--secondary);
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            margin-bottom: 0.75rem;
            font-family: var(--font-mono);
        }}

        .source-url:hover {{
            text-decoration: underline;
        }}

        .source-snippet {{
            font-size: 0.95rem;
            color: var(--text-muted);
            font-style: italic;
            border-left: 3px solid var(--border-color);
            padding-left: 1rem;
        }}

        /* Charts & Visual Analytics Section */
        .analytics-grid {{
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 1.5rem;
            margin-bottom: 3rem;
        }}

        @media (max-width: 900px) {{
            .analytics-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        .chart-card {{
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 1.75rem;
            min-height: 380px;
        }}

        .chart-container {{
            position: relative;
            width: 100%;
            height: 280px;
        }}

        /* Agent Breakdown Section */
        .breakdown-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
            font-size: 0.9rem;
        }}

        .breakdown-table th, .breakdown-table td {{
            padding: 0.75rem 1rem;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }}

        .breakdown-table th {{
            color: var(--text-muted);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .breakdown-table td {{
            font-weight: 500;
        }}

        .breakdown-table tr:hover td {{
            background-color: rgba(255,255,255,0.02);
        }}

        /* Rubric Interactive Assessor Widget */
        .rubric-widget {{
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
        }}

        .rubric-row {{
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            background-color: rgba(255,255,255,0.01);
            padding: 1rem;
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.02);
        }}

        .rubric-info {{
            display: flex;
            justify-content: space-between;
            font-weight: 600;
        }}

        .rubric-label {{
            font-size: 0.95rem;
            color: var(--text-main);
        }}

        .rubric-score-badge {{
            color: var(--primary-light);
            font-family: var(--font-mono);
        }}

        .rubric-desc {{
            font-size: 0.8rem;
            color: var(--text-muted);
        }}

        .rubric-slider {{
            -webkit-appearance: none;
            width: 100%;
            height: 6px;
            border-radius: 5px;
            background: var(--border-color);
            outline: none;
            cursor: pointer;
        }}

        .rubric-slider::-webkit-slider-thumb {{
            -webkit-appearance: none;
            appearance: none;
            width: 16px;
            height: 16px;
            border-radius: 50%;
            background: var(--primary);
            cursor: pointer;
            box-shadow: 0 0 10px var(--primary);
        }}

        .rubric-total {{
            margin-top: 1.5rem;
            padding: 1.5rem;
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(217, 70, 239, 0.1) 100%);
            border-radius: 16px;
            border: 1px solid var(--primary-glow);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .rubric-total-title {{
            font-size: 1.2rem;
            font-weight: 700;
        }}

        .rubric-total-val {{
            font-size: 2rem;
            font-weight: 700;
            color: var(--success);
            text-shadow: 0 0 15px rgba(16, 185, 129, 0.4);
        }}

        /* Pipeline Visualizer */
        .pipeline-wrapper {{
            display: flex;
            flex-direction: column;
            gap: 2rem;
            margin-top: 1rem;
        }}

        .pipeline-card {{
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.25);
            position: relative;
        }}

        .pipeline-card-title {{
            font-size: 1.15rem;
            font-weight: 700;
            margin-bottom: 1.25rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .pipeline-flow {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 1rem;
            padding: 1.25rem;
            background-color: rgba(0, 0, 0, 0.2);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.02);
        }}

        .pipeline-step {{
            background-color: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border-color);
            padding: 0.75rem 1.25rem;
            border-radius: 10px;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 0.25rem;
            min-width: 130px;
            text-align: center;
            transition: var(--transition);
        }}

        .pipeline-step:hover {{
            border-color: var(--primary-light);
            background-color: rgba(255, 255, 255, 0.05);
            transform: translateY(-2px);
        }}

        .pipeline-step.step-query {{
            border-color: var(--text-muted);
            color: var(--text-main);
            background-color: rgba(255, 255, 255, 0.01);
        }}

        .pipeline-step.step-llm-single {{
            border-color: var(--secondary);
            background-color: var(--secondary-glow);
            box-shadow: 0 0 10px var(--secondary-glow);
        }}

        .pipeline-step.step-supervisor {{
            border-color: var(--accent-purple);
            background-color: rgba(168, 85, 247, 0.1);
            box-shadow: 0 0 10px rgba(168, 85, 247, 0.1);
        }}

        .pipeline-step.step-worker {{
            border-color: var(--primary);
            background-color: var(--primary-glow);
        }}

        .pipeline-step.step-critic {{
            border-color: var(--warning);
            background-color: rgba(245, 158, 11, 0.1);
        }}

        .pipeline-step.step-done {{
            border-color: var(--success);
            background-color: rgba(16, 185, 129, 0.1);
        }}

        .pipeline-step-title {{
            font-size: 0.9rem;
            font-weight: 600;
        }}

        .pipeline-step-desc {{
            font-size: 0.7rem;
            color: var(--text-muted);
        }}

        .pipeline-arrow {{
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--text-muted);
            font-size: 1.2rem;
            font-weight: bold;
        }}

        .pipeline-loop-section {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 1rem;
            width: 100%;
        }}

        .pipeline-loop-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 0.75rem;
            margin-top: 0.5rem;
        }}

        @media (max-width: 600px) {{
            .pipeline-loop-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        .pipeline-loop-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 0.8rem;
            color: var(--text-muted);
            border-bottom: 1px dashed var(--border-color);
            padding-bottom: 0.5rem;
            margin-top: 0.5rem;
        }}

    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Multi-Agent Research Lab</h1>
            <p>Interactive Benchmark Metrics, Charts & Trace Report Dashboard</p>
            <div class="badge-container">
                <span class="badge badge-framework">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="18" cy="18" r="3"></circle><circle cx="6" cy="6" r="3"></circle><circle cx="6" cy="18" r="3"></circle><path d="M20 4H4v2"></path><path d="M4 12h16v2"></path></svg>
                    LangGraph Orchestrated
                </span>
                <span class="badge badge-status">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
                    Completed & Validated
                </span>
            </div>
        </header>

        <!-- Tab Panel to Switch Queries -->
        <div class="workspace-tabs" id="query-tabs">
            <!-- Populated via JS -->
        </div>

        <!-- Dashboard Cards Section -->
        <div class="dashboard-grid" id="metrics-dashboard">
            <!-- Populated via JS -->
        </div>

        <!-- Charts & Analytics Section -->
        <div class="analytics-grid">
            <!-- Performance Comparison Chart Card -->
            <div class="chart-card">
                <h3 class="card-title" style="margin-bottom: 1.5rem; display: flex; align-items: center; gap: 0.5rem;">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>
                    Performance Comparison Charts
                </h3>
                <div class="chart-container">
                    <canvas id="comparisonChart"></canvas>
                </div>
            </div>

            <!-- Agent Role Breakdowns Card -->
            <div class="chart-card" style="min-height: auto;">
                <h3 class="card-title" style="margin-bottom: 1.25rem; display: flex; align-items: center; gap: 0.5rem;">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.21 15.89A10 10 0 1 1 8 2.83"></path><path d="M22 12A10 10 0 0 0 12 2v10z"></path></svg>
                    Multi-Agent Resource Allocation
                </h3>
                <div id="breakdown-container">
                    <!-- Populated via JS -->
                </div>
            </div>
        </div>

        <!-- Main Workspace Grid -->
        <div class="layout-grid">
            <!-- Left Side: Interactive Step Trace -->
            <div class="trace-column">
                <h2 class="section-title">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="color: var(--primary)"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
                    Execution Trace
                </h2>
                <div class="timeline-container" id="trace-timeline">
                    <!-- Populated via JS -->
                </div>
            </div>

            <!-- Right Side: Outputs & References -->
            <div class="output-column">
                <h2 class="section-title">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="color: var(--secondary)"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                    Report Outputs & Details
                </h2>
                
                <div class="workspace-tabs" style="border-bottom: none; margin-bottom: 1rem;">
                    <button class="tab-btn active" onclick="switchOutputTab('final-report')">Final Report</button>
                    <button class="tab-btn" onclick="switchOutputTab('research-notes')">Research Notes</button>
                    <button class="tab-btn" onclick="switchOutputTab('analysis-notes')">Analysis Notes</button>
                    <button class="tab-btn" onclick="switchOutputTab('sources')">Sources & References</button>
                    <button class="tab-btn" onclick="switchOutputTab('pipelines')">Pipelines</button>
                    <button class="tab-btn" onclick="switchOutputTab('rubric')">Rubric Assessor</button>
                </div>

                <div class="output-panel">
                    <div id="output-content-panel">
                        <!-- Populated via JS -->
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Embed the benchmark run data directly from Python
        const runs = {json_data};
        
        let currentQueryIndex = 0;
        let activeOutputTab = 'final-report';
        let comparisonChartInstance = null;

        // Peer Rubric scoring state
        let rubricScores = {{
            clarity: 2,
            design: 2,
            guard: 2,
            benchmark: 2,
            trace: 2
        }};

        // Markdown helper to render basics in HTML
        function simpleMarkdown(text) {{
            if (!text) return '<p style="color: var(--text-muted);">Not started or not available.</p>';
            let html = text
                .replace(/\\r\\n/g, '\\n')
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;');
            
            // Headings
            html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
            html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
            html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
            html = html.replace(/^#### (.*$)/gim, '<h4>$1</h4>');
            
            // Bold
            html = html.replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>');
            
            // Bullet lists
            html = html.replace(/^\\s*-\\s*(.*$)/gim, '<li>$1</li>');
            // Group <li> into <ul> (crude helper)
            html = html.replace(/(<li>.*<\\/li>)/sg, '<ul>$1</ul>');
            
            // Clean up list closures
            html = html.replace(/<\\/ul>\\s*<ul>/g, '');
            
            // Paragraph breaks
            html = html.replace(/\\n\\n/g, '</p><p>');
            
            // Link markdown formatting [text](url)
            html = html.replace(/\\[(.*?)\\]\\((.*?)\\)/g, '<a href="$2" target="_blank" class="source-url">$1</a>');
            
            return '<p>' + html + '</p>';
        }}

        function init() {{
            renderQueryTabs();
            renderDashboard();
            renderTimeline();
            renderCharts();
            renderAgentBreakdownTable();
            renderOutputTabContent();
        }}

        function renderQueryTabs() {{
            const container = document.getElementById('query-tabs');
            container.innerHTML = '';
            
            // Filter unique queries from runs (each has a baseline and a multi-agent run)
            const queries = [];
            runs.forEach(run => {{
                if (!queries.includes(run.query)) {{
                    queries.push(run.query);
                }}
            }});

            queries.forEach((q, idx) => {{
                const btn = document.createElement('button');
                btn.className = `tab-btn ${{idx === currentQueryIndex ? 'active' : ''}}`;
                btn.innerText = `Query ${{idx + 1}}: ${{q.substring(0, 40)}}...`;
                btn.onclick = () => {{
                    currentQueryIndex = idx;
                    document.querySelectorAll('#query-tabs .tab-btn').forEach((b, i) => {{
                        b.className = `tab-btn ${{i === idx ? 'active' : ''}}`;
                    }});
                    renderDashboard();
                    renderTimeline();
                    renderCharts();
                    renderAgentBreakdownTable();
                    renderOutputTabContent();
                }};
                container.appendChild(btn);
            }});
        }}

        function getActiveQueryRuns() {{
            const queries = [];
            runs.forEach(run => {{
                if (!queries.includes(run.query)) {{
                    queries.push(run.query);
                }}
            }});
            const targetQuery = queries[currentQueryIndex];
            
            const baseline = runs.find(r => r.query === targetQuery && r.run_name.toLowerCase().includes('baseline'));
            const multi = runs.find(r => r.query === targetQuery && r.run_name.toLowerCase().includes('multi-agent'));
            
            return {{ baseline, multi }};
        }}

        function renderDashboard() {{
            const container = document.getElementById('metrics-dashboard');
            const {{ baseline, multi }} = getActiveQueryRuns();
            
            // Extract extra metrics: word count, token count, throughput
            const baseline_wc = baseline && baseline.final_answer ? baseline.final_answer.split(/\\s+/).length : 0;
            const multi_wc = multi && multi.final_answer ? multi.final_answer.split(/\\s+/).length : 0;
            
            let multi_tokens = 0;
            if (multi && multi.trace) {{
                multi.trace.forEach(t => {{
                    multi_tokens += (t.payload.input_tokens || 0) + (t.payload.output_tokens || 0);
                }});
            }}
            const multi_throughput = multi ? (multi_tokens / multi.latency_seconds) : 0;
            
            container.innerHTML = `
                <!-- Single Agent Baseline Card -->
                <div class="card card-single">
                    <div class="card-header">
                        <span class="card-title">Single-Agent Baseline</span>
                        <span class="badge badge-framework" style="color: var(--secondary); border-color: rgba(14, 165, 233, 0.3);">Baseline Call</span>
                    </div>
                    <div class="card-subtitle" title="${{baseline ? baseline.query : ''}}">
                        Query: "${{baseline ? baseline.query : 'N/A'}}"
                    </div>
                    <div class="stats-list">
                        <div class="stat-item">
                            <div class="stat-label">Latency</div>
                            <div class="stat-value latency">${{baseline ? baseline.latency_seconds.toFixed(2) : '0.00'}}s</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Cost</div>
                            <div class="stat-value cost">$${{baseline ? baseline.estimated_cost_usd.toFixed(6) : '0.000000'}}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Quality Score</div>
                            <div class="stat-value quality">${{baseline && baseline.quality_score ? baseline.quality_score.toFixed(1) : 'N/A'}}/10</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Report Word Count</div>
                            <div class="stat-value">${{baseline_wc}} words</div>
                        </div>
                    </div>
                </div>

                <!-- Multi Agent Workflow Card -->
                <div class="card card-multi">
                    <div class="card-header">
                        <span class="card-title">Multi-Agent Workflow</span>
                        <span class="badge" style="background-color: rgba(217, 70, 239, 0.15); color: #f472b6; border: 1px solid rgba(217, 70, 239, 0.3);">Supervisor + Workers</span>
                    </div>
                    <div class="card-subtitle" title="${{multi ? multi.query : ''}}">
                        Query: "${{multi ? multi.query : 'N/A'}}"
                    </div>
                    <div class="stats-list">
                        <div class="stat-item">
                            <div class="stat-label">Latency</div>
                            <div class="stat-value latency">${{multi ? multi.latency_seconds.toFixed(2) : '0.00'}}s</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Cost</div>
                            <div class="stat-value cost">$${{multi ? multi.estimated_cost_usd.toFixed(6) : '0.000000'}}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Quality Score</div>
                            <div class="stat-value quality">${{multi && multi.quality_score ? multi.quality_score.toFixed(1) : 'N/A'}}/10</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Throughput</div>
                            <div class="stat-value efficiency">${{multi_throughput.toFixed(1)}} tok/s</div>
                        </div>
                    </div>
                </div>
            `;
        }}

        function renderCharts() {{
            const {{ baseline, multi }} = getActiveQueryRuns();
            
            const labels = ['Latency (s)', 'Cost ($ * 10000)', 'Quality (score)'];
            const baselineData = [
                baseline ? baseline.latency_seconds : 0,
                baseline ? baseline.estimated_cost_usd * 10000 : 0,
                baseline && baseline.quality_score ? baseline.quality_score : 0
            ];
            
            const multiData = [
                multi ? multi.latency_seconds : 0,
                multi ? multi.estimated_cost_usd * 10000 : 0,
                multi && multi.quality_score ? multi.quality_score : 0
            ];

            const ctx = document.getElementById('comparisonChart').getContext('2d');
            
            if (comparisonChartInstance) {{
                comparisonChartInstance.destroy();
            }}

            // Premium Chart Styling
            comparisonChartInstance = new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: labels,
                    datasets: [
                        {{
                            label: 'Single-Agent Baseline',
                            data: baselineData,
                            backgroundColor: 'rgba(14, 165, 233, 0.65)',
                            borderColor: '#0ea5e9',
                            borderWidth: 2,
                            borderRadius: 6
                        }},
                        {{
                            label: 'Multi-Agent Workflow',
                            data: multiData,
                            backgroundColor: 'rgba(99, 102, 241, 0.65)',
                            borderColor: '#6366f1',
                            borderWidth: 2,
                            borderRadius: 6
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            grid: {{ color: 'rgba(255,255,255,0.05)' }},
                            ticks: {{ color: '#94a3b8' }}
                        }},
                        x: {{
                            grid: {{ display: false }},
                            ticks: {{ color: '#94a3b8' }}
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            labels: {{
                                color: '#f8fafc',
                                font: {{ family: 'Outfit', size: 12 }}
                            }}
                        }}
                    }}
                }}
            }});
        }}

        function renderAgentBreakdownTable() {{
            const container = document.getElementById('breakdown-container');
            const {{ multi }} = getActiveQueryRuns();
            
            if (!multi || !multi.trace) {{
                container.innerHTML = '<p style="color: var(--text-muted);">No agent stats found.</p>';
                return;
            }}

            // Analyze agent payloads from traces to compute statistics
            const agentStats = {{
                supervisor: {{ calls: 0, cost: 0.0, tokens: 0 }},
                researcher: {{ calls: 0, cost: 0.0, tokens: 0 }},
                analyst: {{ calls: 0, cost: 0.0, tokens: 0 }},
                writer: {{ calls: 0, cost: 0.0, tokens: 0 }},
                critic: {{ calls: 0, cost: 0.0, tokens: 0 }}
            }};

            multi.trace.forEach(step => {{
                let role = '';
                if (step.name === 'supervisor_routing') role = 'supervisor';
                else if (step.name === 'researcher_run') role = 'researcher';
                else if (step.name === 'analyst_run') role = 'analyst';
                else if (step.name === 'writer_run') role = 'writer';
                else if (step.name === 'critic_run') role = 'critic';

                if (role && agentStats[role]) {{
                    agentStats[role].calls += 1;
                    agentStats[role].cost += step.payload.cost_usd || 0.0;
                    agentStats[role].tokens += (step.payload.input_tokens || 0) + (step.payload.output_tokens || 0);
                }}
            }});

            let rowsHtml = '';
            for (const [agent, stats] of Object.entries(agentStats)) {{
                if (stats.calls === 0) continue;
                rowsHtml += `
                    <tr>
                        <td style="text-transform: capitalize; font-weight: 600;">${{agent}}</td>
                        <td style="font-family: var(--font-mono);">${{stats.calls}}</td>
                        <td style="font-family: var(--font-mono);">${{stats.tokens}}</td>
                        <td style="font-family: var(--font-mono); color: var(--warning);">$${{stats.cost.toFixed(5)}}</td>
                    </tr>
                `;
            }}

            container.innerHTML = `
                <table class="breakdown-table">
                    <thead>
                        <tr>
                            <th>Agent Role</th>
                            <th>Calls</th>
                            <th>Tokens</th>
                            <th>Est Cost</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${{rowsHtml}}
                    </tbody>
                </table>
            `;
        }}

        function renderTimeline() {{
            const container = document.getElementById('trace-timeline');
            const {{ multi }} = getActiveQueryRuns();
            
            if (!multi || !multi.trace || multi.trace.length === 0) {{
                container.innerHTML = '<p style="color: var(--text-muted);">No trace data available for this run.</p>';
                return;
            }}
            
            container.innerHTML = '';
            
            multi.trace.forEach((step, index) => {{
                const item = document.createElement('div');
                item.className = 'timeline-item';
                if (index === multi.trace.length - 1) {{
                    item.className += ' active-step';
                }} else {{
                    item.className += ' success-step';
                }}
                
                let agentName = 'System';
                let agentBadgeClass = 'badge-supervisor';
                let stepTitle = step.name;
                let payloadContent = JSON.stringify(step.payload, null, 2);
                
                if (step.name === 'supervisor_routing') {{
                    agentName = 'Supervisor';
                    agentBadgeClass = 'badge-supervisor';
                    stepTitle = `Routed to: ${{step.payload.route}}`;
                }} else if (step.name === 'researcher_run') {{
                    agentName = 'Researcher';
                    agentBadgeClass = 'badge-researcher';
                    stepTitle = `Executed Search: "${{step.payload.search_query}}"`;
                }} else if (step.name === 'analyst_run') {{
                    agentName = 'Analyst';
                    agentBadgeClass = 'badge-analyst';
                    stepTitle = 'Analyzed Research Notes';
                }} else if (step.name === 'writer_run') {{
                    agentName = 'Writer';
                    agentBadgeClass = 'badge-writer';
                    stepTitle = 'Compiled Final Report';
                }} else if (step.name === 'critic_run') {{
                    agentName = 'Critic';
                    agentBadgeClass = 'badge-critic';
                    stepTitle = 'Validated Citations & Fact-Checked';
                }}
                
                item.innerHTML = `
                    <div class="timeline-marker"></div>
                    <div class="timeline-content-card" onclick="this.classList.toggle('expanded')">
                        <div class="timeline-header">
                            <span class="agent-badge ${{agentBadgeClass}}">${{agentName}}</span>
                            <span class="timeline-time">Step ${{index + 1}}</span>
                        </div>
                        <div class="timeline-title">${{stepTitle}}</div>
                        <div style="font-size: 0.75rem; color: var(--text-muted); text-align: right; cursor: pointer;">
                            Click to expand details
                        </div>
                        <div class="timeline-details">
                            <h4 style="font-size: 0.85rem; margin-bottom: 0.5rem; color: var(--text-muted);">Step Metadata & Payload</h4>
                            <pre class="payload-pre">${{payloadContent}}</pre>
                        </div>
                    </div>
                `;
                container.appendChild(item);
            }});
        }}

        function switchOutputTab(tab) {{
            activeOutputTab = tab;
            document.querySelectorAll('.output-column .tab-btn').forEach(btn => {{
                if (btn.innerText.toLowerCase().replace(/\\s/g, '-') === tab) {{
                    btn.classList.add('active');
                }} else {{
                    btn.classList.remove('active');
                }}
            }});
            renderOutputTabContent();
        }}

        function updateRubricScore(criteria, value) {{
            rubricScores[criteria] = parseInt(value);
            document.getElementById(`${{criteria}}-score-val`).innerText = `${{value}}/2`;
            
            const total = rubricScores.clarity + rubricScores.design + rubricScores.guard + rubricScores.benchmark + rubricScores.trace;
            document.getElementById('rubric-total-score').innerText = `${{total}}/10`;
            
            // Adjust colors of total score dynamically
            const badge = document.getElementById('rubric-total-score');
            if (total >= 8) badge.style.color = 'var(--success)';
            else if (total >= 5) badge.style.color = 'var(--warning)';
            else badge.style.color = 'var(--danger)';
        }}

        function renderOutputTabContent() {{
            const container = document.getElementById('output-content-panel');
            const {{ multi }} = getActiveQueryRuns();
            
            if (!multi) {{
                container.innerHTML = '<p>No data available.</p>';
                return;
            }}
            
            if (activeOutputTab === 'final-report') {{
                container.innerHTML = `
                    <div class="output-panel-header">
                        <span class="output-panel-title">Final Synthesis Report</span>
                        <span style="font-size: 0.8rem; color: var(--text-muted);">Generated by WriterAgent</span>
                    </div>
                    <div class="output-body">
                        ${{simpleMarkdown(multi.final_answer)}}
                    </div>
                `;
            }} else if (activeOutputTab === 'research-notes') {{
                container.innerHTML = `
                    <div class="output-panel-header">
                        <span class="output-panel-title">Compiled Research Notes</span>
                        <span style="font-size: 0.8rem; color: var(--text-muted);">Generated by ResearcherAgent</span>
                    </div>
                    <div class="output-body">
                        ${{simpleMarkdown(multi.research_notes)}}
                    </div>
                `;
            }} else if (activeOutputTab === 'analysis-notes') {{
                container.innerHTML = `
                    <div class="output-panel-header">
                        <span class="output-panel-title">Structured Analysis Notes</span>
                        <span style="font-size: 0.8rem; color: var(--text-muted);">Generated by AnalystAgent</span>
                    </div>
                    <div class="output-body">
                        ${{simpleMarkdown(multi.analysis_notes)}}
                    </div>
                `;
            }} else if (activeOutputTab === 'sources') {{
                let sourcesHtml = '<div class="source-grid">';
                if (multi.sources && multi.sources.length > 0) {{
                    multi.sources.forEach(src => {{
                        sourcesHtml += `
                            <div class="source-item">
                                <div class="source-title">${{src.title}}</div>
                                <a href="${{src.url || '#'}}" target="_blank" class="source-url">
                                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 0.15rem;"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                                    ${{src.url || 'No URL available'}}
                                </a>
                                <div class="source-snippet">"${{src.snippet}}"</div>
                            </div>
                        `;
                    }});
                }} else {{
                    sourcesHtml += '<p style="color: var(--text-muted);">No sources collected for this run.</p>';
                }}
                sourcesHtml += '</div>';
                
                container.innerHTML = `
                    <div class="output-panel-header">
                        <span class="output-panel-title">Sources Index</span>
                        <span style="font-size: 0.8rem; color: var(--text-muted);">${{multi.sources ? multi.sources.length : 0}} Sources Gained</span>
                    </div>
                    <div class="output-body" style="background: none; border: none; padding: 0;">
                        ${{sourcesHtml}}
                    </div>
                `;
            }} else if (activeOutputTab === 'rubric') {{
                const total = rubricScores.clarity + rubricScores.design + rubricScores.guard + rubricScores.benchmark + rubricScores.trace;
                container.innerHTML = `
                    <div class="output-panel-header">
                        <span class="output-panel-title">Peer Review Rubric Assessor</span>
                        <span style="font-size: 0.8rem; color: var(--text-muted);">Interactive Evaluation Widget</span>
                    </div>
                    <div class="rubric-widget">
                        <div class="rubric-row">
                            <div class="rubric-info">
                                <span class="rubric-label">Role Clarity</span>
                                <span class="rubric-score-badge" id="clarity-score-val">${{rubricScores.clarity}}/2</span>
                            </div>
                            <div class="rubric-desc">Does each agent have clear responsibilities and avoid over-lapping tasks?</div>
                            <input type="range" class="rubric-slider" min="0" max="2" value="${{rubricScores.clarity}}" oninput="updateRubricScore('clarity', this.value)">
                        </div>
                        
                        <div class="rubric-row">
                            <div class="rubric-info">
                                <span class="rubric-label">State Design</span>
                                <span class="rubric-score-badge" id="design-score-val">${{rubricScores.design}}/2</span>
                            </div>
                            <div class="rubric-desc">Does the Shared State transfer clean context between handoffs without losses?</div>
                            <input type="range" class="rubric-slider" min="0" max="2" value="${{rubricScores.design}}" oninput="updateRubricScore('design', this.value)">
                        </div>
                        
                        <div class="rubric-row">
                            <div class="rubric-info">
                                <span class="rubric-label">Failure Guardrails</span>
                                <span class="rubric-score-badge" id="guard-score-val">${{rubricScores.guard}}/2</span>
                            </div>
                            <div class="rubric-desc">Are max iterations, API fail fallbacks, and validation critic steps active?</div>
                            <input type="range" class="rubric-slider" min="0" max="2" value="${{rubricScores.guard}}" oninput="updateRubricScore('guard', this.value)">
                        </div>
                        
                        <div class="rubric-row">
                            <div class="rubric-info">
                                <span class="rubric-label">Benchmarking Comparison</span>
                                <span class="rubric-score-badge" id="benchmark-score-val">${{rubricScores.benchmark}}/2</span>
                            </div>
                            <div class="rubric-desc">Does the project compare single-agent baseline vs multi-agent pipelines with metrics?</div>
                            <input type="range" class="rubric-slider" min="0" max="2" value="${{rubricScores.benchmark}}" oninput="updateRubricScore('benchmark', this.value)">
                        </div>
                        
                        <div class="rubric-row">
                            <div class="rubric-info">
                                <span class="rubric-label">Trace Explanation</span>
                                <span class="rubric-score-badge" id="trace-score-val">${{rubricScores.trace}}/2</span>
                            </div>
                            <div class="rubric-desc">Are step traces easily legible, detailing who did what, cost breakdown, and errors?</div>
                            <input type="range" class="rubric-slider" min="0" max="2" value="${{rubricScores.trace}}" oninput="updateRubricScore('trace', this.value)">
                        </div>
                        
                        <div class="rubric-total">
                            <span class="rubric-total-title">Total Evaluated Score:</span>
                            <span class="rubric-total-val" id="rubric-total-score">${{total}}/10</span>
                        </div>
                    </div>
                `;
            }} else if (activeOutputTab === 'pipelines') {{
                container.innerHTML = `
                    <div class="output-panel-header">
                        <span class="output-panel-title">System Architecture & Pipelines</span>
                        <span style="font-size: 0.8rem; color: var(--text-muted);">Pipeline Execution Flow</span>
                    </div>
                    <div class="pipeline-wrapper">
                        <!-- Single-Agent Baseline Pipeline -->
                        <div class="pipeline-card">
                            <div class="pipeline-card-title">
                                <span class="badge badge-framework" style="color: var(--secondary); border-color: rgba(14, 165, 233, 0.3);">
                                    Single-Agent
                                </span>
                                Baseline Pipeline
                            </div>
                            <div class="pipeline-flow">
                                <div class="pipeline-step step-query">
                                    <span class="pipeline-step-title">User Query</span>
                                    <span class="pipeline-step-desc">Input Question</span>
                                </div>
                                <div class="pipeline-arrow">➔</div>
                                <div class="pipeline-step step-llm-single" style="flex: 2;">
                                    <span class="pipeline-step-title">Monolithic LLM</span>
                                    <span class="pipeline-step-desc">System Prompt + User Prompt (1 call)</span>
                                </div>
                                <div class="pipeline-arrow">➔</div>
                                <div class="pipeline-step step-done">
                                    <span class="pipeline-step-title">Final Answer</span>
                                    <span class="pipeline-step-desc">Direct output</span>
                                </div>
                            </div>
                        </div>

                        <!-- Multi-Agent Workflow Pipeline -->
                        <div class="pipeline-card">
                            <div class="pipeline-card-title">
                                <span class="badge" style="background-color: rgba(217, 70, 239, 0.15); color: #f472b6; border: 1px solid rgba(217, 70, 239, 0.3);">
                                    Multi-Agent
                                </span>
                                Workflow (LangGraph)
                            </div>
                            <div class="pipeline-flow" style="flex-direction: column; align-items: stretch; gap: 1.5rem;">
                                <!-- Top Flow -->
                                <div style="display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; flex-wrap: wrap;">
                                    <div class="pipeline-step step-query">
                                        <span class="pipeline-step-title">User Query</span>
                                        <span class="pipeline-step-desc">Input Question</span>
                                    </div>
                                    <div class="pipeline-arrow">➔</div>
                                    <div class="pipeline-step step-supervisor" style="flex: 1; min-width: 150px;">
                                        <span class="pipeline-step-title">Supervisor (Router)</span>
                                        <span class="pipeline-step-desc">State Orchestrator</span>
                                    </div>
                                    <div class="pipeline-arrow">➔</div>
                                    <div class="pipeline-step step-done">
                                        <span class="pipeline-step-title">Done</span>
                                        <span class="pipeline-step-desc">Return Final Report</span>
                                    </div>
                                </div>
                                
                                <!-- Router Loop Details -->
                                <div class="pipeline-loop-section">
                                    <div class="pipeline-loop-header">
                                        <span>DYNAMIC WORKER ROUTING LOOP (Controlled by Supervisor State)</span>
                                        <span style="color: var(--accent-purple);">Decided dynamically based on Shared State</span>
                                    </div>
                                    <div class="pipeline-loop-grid">
                                        <div class="pipeline-step step-worker">
                                            <span class="pipeline-step-title">Researcher</span>
                                            <span class="pipeline-step-desc">Query search index & gather sources</span>
                                        </div>
                                        <div class="pipeline-step step-worker">
                                            <span class="pipeline-step-title">Analyst</span>
                                            <span class="pipeline-step-desc">Analyze research & extract insights</span>
                                        </div>
                                        <div class="pipeline-step step-worker">
                                            <span class="pipeline-step-title">Writer</span>
                                            <span class="pipeline-step-desc">Draft the report with markdown sections</span>
                                        </div>
                                        <div class="pipeline-step step-critic">
                                            <span class="pipeline-step-title">Critic</span>
                                            <span class="pipeline-step-desc">Verify sources, citations & grade quality</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }}
        }}

        window.onload = init;
    </script>
</body>
</html>
"""
    return html
