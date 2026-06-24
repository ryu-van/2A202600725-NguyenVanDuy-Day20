"""Command-line entrypoint for the lab starter."""

from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow
from multi_agent_research_lab.observability.logging import configure_logging
from multi_agent_research_lab.services.llm_client import LLMClient

app = typer.Typer(help="Multi-Agent Research Lab starter CLI")
console = Console()


def _init() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)


@app.command()
def baseline(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run a real single-agent baseline call."""
    _init()
    request = ResearchQuery(query=query)
    state = ResearchState(request=request)
    
    console.print(f"[bold blue]Running Single-Agent Baseline for query:[/bold blue] {query}")
    
    llm_client = LLMClient()
    system_prompt = (
        "You are an expert research assistant. Answer the user's research query comprehensively, "
        "writing a clear, structured report with markdown sections, details, and proper explanations."
    )
    user_prompt = f"Query: {query}\nAudience: {state.request.audience}"
    
    try:
        response = llm_client.complete(system_prompt, user_prompt)
        state.final_answer = response.content
        console.print(Panel(state.final_answer, title="Single-Agent Baseline Result", border_style="green"))
        console.print(
            f"[dim]Metrics: Input Tokens: {response.input_tokens} | "
            f"Output Tokens: {response.output_tokens} | "
            f"Estimated Cost: ${response.cost_usd:.5f}[/dim]"
        )
    except Exception as e:
        console.print(f"[bold red]Error executing single-agent baseline: {e}[/bold red]")
        raise typer.Exit(code=1)


@app.command("multi-agent")
def multi_agent(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run the multi-agent workflow."""
    _init()
    state = ResearchState(request=ResearchQuery(query=query))
    workflow = MultiAgentWorkflow()
    
    console.print(f"[bold purple]Running Multi-Agent Workflow for query:[/bold purple] {query}")
    
    try:
        result = workflow.run(state)
        
        if result.final_answer:
            console.print(Panel(result.final_answer, title="Multi-Agent Workflow Final Answer", border_style="purple"))
        else:
            console.print("[bold red]Multi-agent workflow completed without a final answer.[/bold red]")
            
        console.print("[bold]Route History:[/bold]")
        for idx, route in enumerate(result.route_history):
            console.print(f"  {idx + 1}. {route}")
            
        # Calculate total cost from trace events
        total_cost = 0.0
        for event in result.trace:
            payload = event.get("payload", {})
            total_cost += payload.get("cost_usd") or 0.0
            
        console.print(f"[dim]Total Iterations: {result.iteration} | Total Estimated Cost: ${total_cost:.5f}[/dim]")
        if result.errors:
            console.print(f"[bold red]Errors occurred during execution: {result.errors}[/bold red]")
    except StudentTodoError as exc:
        console.print(Panel.fit(str(exc), title="Expected TODO", style="yellow"))
        raise typer.Exit(code=2) from exc
    except Exception as exc:
        console.print(f"[bold red]Workflow execution failed: {exc}[/bold red]")
        raise typer.Exit(code=1) from exc


if __name__ == "__main__":
    app()
