"""
Tool Registry — allowlist of tools the orchestrator can call.

Milestone: M2 (Router + Orchestrator Skeleton)

Maps tool names to their functions and metadata.
The policy_gate checks this registry before allowing any tool call.

Registry entries:
    - classify_emails:    EmailClassifier   (small model)
    - extract_tasks:      TaskExtractor     (small model)
    - check_duplicates:   DuplicateChecker  (large model)
    - resolve_conflicts:  ConflictResolver  (small/large model)
    - estimate_effort:    EffortEstimator   (small model + RAG)
    - read_document:      DocumentReader    (small model, added in M7)
    - finish:             no model          (ends the orchestrator loop)

Security:
    Only tools in this allowlist can be called.
    The orchestrator LLM cannot invent new tool names.
    Each tool entry specifies its prerequisites (e.g., cannot estimate
    effort if zero tasks have been extracted).
"""
