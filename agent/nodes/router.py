"""
Router node — decides whether the user wants a plan or a command.

Milestone: M2 (Router + Orchestrator Skeleton)

Uses a small LLM with structured output (RouterDecision) to classify:
    - "plan": user wants to see what's due or get a study plan
    - "command": user wants to change something (cancel, move, reschedule)
    - "unclear": can't tell — asks a clarifying question

The router only chooses a route. It never changes anything itself.

If confidence is below ROUTER_MIN_CONFIDENCE, it routes to "unclear"
and the graph goes to ask_clarification → END.

Input:  state["user_input"]
Output: state["route"], state["route_confidence"]
"""
