"""
Orchestrator — the LLM that calls small LLM tools to process raw data.

Milestone: M2 (Router + Orchestrator Skeleton)

Contains three sub-nodes that loop together:

    orchestrator_llm → policy_gate → dispatch → orchestrator_llm ...

orchestrator_llm:
    - Large model with bind_tools(ORCH_TOOLS)
    - Does NOT see raw email text — sees a workspace status summary
    - Each turn: states why it picks the next tool, then calls one tool, or calls finish
    - System prompt tells it the typical order: classify emails → extract tasks →
      check duplicates → resolve conflicts → estimate effort → finish

policy_gate (deterministic, safety/policy.py):
    - Checks: tool in allowlist? budget not exceeded? not a repeated call?
    - A blocked call returns a tool message explaining why

dispatch (custom node):
    - Runs the tool function with the current state
    - Returns a compact summary to the LLM (large payloads stay in state)

The orchestrator stops when all processing is done or MAX_TOOL_CALLS is reached.
"""
