"""
Email Classifier tool — classifies emails as academic or not.

Milestone: M2 (Router + Orchestrator Skeleton)

Called by the orchestrator. Takes a batch of email IDs, reads the
email subject and body, and returns an EmailVerdict for each:
    - is_academic: True if the email contains academic tasks/deadlines/exams
    - reason: one-line explanation

Examples:
    "Club pizza night" → is_academic=False, reason="social event, not academic"
    "OS mid-term exam schedule" → is_academic=True, reason="exam schedule with date"

Uses the small LLM (TOOL_MODEL) with structured output.
Batches ~10 emails per LLM call to reduce API usage.
"""
