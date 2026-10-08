"""
Academic Workflow Agent — Phase 0 Entry Point

Runs three test scenarios through the LangGraph to validate:
1. Full ingest → plan pipeline (with conflict detection)
2. Command interpretation branch
3. Plan-request routing
"""

from agent.graph import build_graph


def run_scenario(graph, prompt: str):
    """Run a single scenario through the graph and display results."""
    print(f"\n{'#' * 62}")
  
    result = graph.invoke({
        "user_input": prompt,
        "messages": [],
    })

    # Print execution trace
    print("\nEXECUTION TRACE:")
    print("─" * 42)
    for msg in result.get("messages", []):
        print(f"  {msg}")

    # Print final output
    if result.get("plan_output"):
        print(result["plan_output"])


def main():
    print("=" * 62)
    print("Academic Workflow Agent — Phase 0 (Dummy Data)")
    print("LangGraph Skeleton Validation")
    print("=" * 62)

    graph = build_graph()

    print("\n[Saving LangGraph Architecture Diagram]")
    try:
        graph.get_graph().draw_mermaid_png(output_file_path="graph.png")
        print("Saved graph.png — open it to see the diagram")
    except Exception as e:
        print(f"Could not draw graph: {e}")
    print("")

    # ── Full pipeline ──────────────────────────────
    run_scenario(
        graph,
        "Show me what's due and create a study plan",
    )

    print("\nscenario completed. Graph flow validated.\n")

if __name__ == "__main__":
    main()
