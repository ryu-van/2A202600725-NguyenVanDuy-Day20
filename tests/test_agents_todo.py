from multi_agent_research_lab.agents import (
    AnalystAgent,
    CriticAgent,
    ResearcherAgent,
    SupervisorAgent,
    WriterAgent,
)
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState


def test_supervisor_routing() -> None:
    state = ResearchState(request=ResearchQuery(query="Explain multi-agent systems"))
    
    # First route should be researcher since there are no research notes
    new_state = SupervisorAgent().run(state)
    assert new_state.iteration == 1
    assert new_state.route_history == ["researcher"]


def test_agents_execution_simulated() -> None:
    state = ResearchState(request=ResearchQuery(query="Explain multi-agent systems"))
    
    # Researcher should populate notes and sources
    state = ResearcherAgent().run(state)
    assert state.research_notes is not None
    assert len(state.sources) > 0
    
    # Analyst should produce analysis notes
    state = AnalystAgent().run(state)
    assert state.analysis_notes is not None
    
    # Writer should produce final report draft
    state = WriterAgent().run(state)
    assert state.final_answer is not None
    
    # Critic should validate final answer (simulation passes critique)
    state = CriticAgent().run(state)
    assert len(state.errors) == 0
