"""
Duplicate Checker tool — finds tasks that are the same deliverable.

Milestone: M2 stub, M4 implementation

Called by the orchestrator after task extraction.
The same task often appears in both email and LMS with different wording.

The LLM does the duplicate checking — it reads the whole task list and
decides which tasks are the same deliverable. Python only validates the
answer and does the mechanical merge.

Input:  compact task list (task_id, title, course, deadline, source, snippet)
Output: DuplicateResult — groups of task IDs that are the same deliverable

Merge rules:
    - Use the LLM's merged_title
    - Union of sources (e.g., ["email", "lms"])
    - Union of deadline_claims
    - Only merge if confidence >= 0.7
    - Groups below 0.7 add a warning instead

Uses the large model (DEDUP_MODEL) because dedup needs broad context.
"""
