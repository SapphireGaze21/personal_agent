"""
Guard — injection scan and trust tagging.

Milestone: M2 (Router + Orchestrator Skeleton)

A pure function that scans each ingested item for prompt injection patterns.

Scans for patterns like:
    - "ignore previous instructions"
    - "you are now"
    - "system prompt"
    - "delete all"
    - "cancel all"

Flagged items:
    - Are still processed as data (not dropped)
    - Tasks extracted from them get trust="low"
    - The final output shows a warning
    - Flagged items can NEVER produce a command

All ingested text is wrapped in <untrusted_source> tags before
being passed to any LLM prompt. This is a defense-in-depth measure.

Can be disabled with GUARD_ENABLED=false for ablation experiments.
"""
