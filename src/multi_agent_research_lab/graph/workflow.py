"""LangGraph workflow implementation."""

import logging
from langgraph.graph import END, StateGraph
try:
    from langfuse.decorators import observe
except ImportError:
    def observe(*args, **kwargs):
        return lambda f: f

from multi_agent_research_lab.agents import (
    AnalystAgent,
    CriticAgent,
    ResearcherAgent,
    SupervisorAgent,
    WriterAgent,
)
from multi_agent_research_lab.core.state import ResearchState

logger = logging.getLogger(__name__)


class MultiAgentWorkflow:
    """Builds and runs the multi-agent graph.

    Keep orchestration here; keep agent internals in `agents/`.
    """

    def __init__(self) -> None:
        self.graph = self.build()

    def build(self) -> object:
        """Create a LangGraph graph."""
        workflow = StateGraph(ResearchState)

        # Define node functions
        def supervisor_node(state: ResearchState) -> ResearchState:
            logger.info("Executing node: supervisor")
            return SupervisorAgent().run(state)

        def researcher_node(state: ResearchState) -> ResearchState:
            logger.info("Executing node: researcher")
            return ResearcherAgent().run(state)

        def analyst_node(state: ResearchState) -> ResearchState:
            logger.info("Executing node: analyst")
            return AnalystAgent().run(state)

        def writer_node(state: ResearchState) -> ResearchState:
            logger.info("Executing node: writer")
            return WriterAgent().run(state)

        def critic_node(state: ResearchState) -> ResearchState:
            logger.info("Executing node: critic")
            return CriticAgent().run(state)

        # Add nodes to graph
        workflow.add_node("supervisor", supervisor_node)
        workflow.add_node("researcher", researcher_node)
        workflow.add_node("analyst", analyst_node)
        workflow.add_node("writer", writer_node)
        workflow.add_node("critic", critic_node)

        # Set entry point
        workflow.set_entry_point("supervisor")

        # Routing decision logic
        def router(state: ResearchState) -> str:
            if not state.route_history:
                logger.warning("No route history found in router. Routing to END.")
                return END
            
            next_agent = state.route_history[-1]
            if next_agent == "done":
                return END
            return next_agent

        # Add conditional edges from supervisor
        workflow.add_conditional_edges(
            "supervisor",
            router,
            {
                "researcher": "researcher",
                "analyst": "analyst",
                "writer": "writer",
                "critic": "critic",
                END: END,
            },
        )

        # Add static transitions back to supervisor from workers
        workflow.add_edge("researcher", "supervisor")
        workflow.add_edge("analyst", "supervisor")
        workflow.add_edge("writer", "supervisor")
        workflow.add_edge("critic", "supervisor")

        # Compile graph
        return workflow.compile()

    @observe(name="multi_agent_workflow")
    def run(self, state: ResearchState) -> ResearchState:
        """Execute the graph and return final state."""
        logger.info("Starting MultiAgentWorkflow.run...")
        
        try:
            result = self.graph.invoke(state)
            
            # Ensure the output is converted back/returned as ResearchState
            if isinstance(result, ResearchState):
                return result
            elif isinstance(result, dict):
                # If langgraph returned a dict, reconstruct the state
                return ResearchState(**result)
            else:
                logger.warning(f"Unexpected run result type: {type(result)}. Returning original state.")
                return state
        except Exception as e:
            logger.error(f"Error executing LangGraph workflow: {e}")
            state.errors.append(f"Workflow execution error: {str(e)}")
            return state
