"""
Policy Gate — allowlist, budgets, and loop detection.

Milestone: M2 (Router + Orchestrator Skeleton)

Sits between orchestrator_llm and dispatch. Every tool call passes through here.

Checks:
    1. Tool name is in the registry allowlist → block if not
    2. tool_calls_made < MAX_TOOL_CALLS → stop loop, go to planner with warning
    3. Same tool + same arguments as the last call → block as a loop
    4. Prerequisites exist (e.g., cannot estimate effort with zero tasks) → block

A blocked call returns a tool message explaining why,
so the orchestrator can correct itself.

This is the "where it can break" demo:
    Turn the gate off (POLICY_GATE_ENABLED=false) and compare behavior.

Can be disabled with POLICY_GATE_ENABLED=false for ablation experiments.
"""
