"""
LangGraph graph definition — wires all nodes together.

Graph structure:
Graph structure:
    START → ingest → task_extractor → planner → validator → (conditional)
        "valid"   → output → END
        "invalid" → planner (re-plan, max 2 retries)
"""

from langgraph.graph import StateGraph, START, END

from agent.state import AgentState
from agent.nodes.ingest import ingest
from agent.nodes.task_extractor import task_extractor
from agent.nodes.planner import planner
from agent.nodes.validator import validator
from agent.nodes.output_formatter import output_formatter


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------

def build_graph():
    """Build and compile the LangGraph agent graph."""

    graph = StateGraph(AgentState)

    # ── Register all nodes ─────────────────────────────────────
    graph.add_node("ingest", ingest)
    graph.add_node("task_extractor", task_extractor)
    graph.add_node("planner", planner)
    graph.add_node("validator", validator)
    graph.add_node("output", output_formatter)

    # ── Wire edges ─────────────────────────────────────────────
    # Entry point
    graph.add_edge(START, "ingest")

    # Ingest pipeline: ingest → extract → dedup/conflict → plan → validate
    graph.add_edge("ingest", "task_extractor")
    graph.add_edge("task_extractor", "planner")
    graph.add_edge("planner", "validator")
    graph.add_edge("validator", "output")

    # Output is the terminal node
    graph.add_edge("output", END)

    return graph.compile()
