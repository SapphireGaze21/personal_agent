"""
Task Extractor tool — extracts structured tasks from academic text.

Milestone: M2 (Router + Orchestrator Skeleton)

Called by the orchestrator after emails are classified.
Takes academic email/LMS text and extracts:
    - title, deadline, task_type, course, effort estimate

This is the existing task_extractor logic moved from agent/nodes/
into a tool that the orchestrator can call.

Uses the small LLM (TOOL_MODEL) with structured output (ExtractedTask).
Only processes items marked as academic by the email_classifier.
"""
