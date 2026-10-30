"""
Pydantic data contracts — every value that crosses a node boundary.

Milestone: M0 (Foundation)

Contains:
    - SourceRef: identifies where a piece of data came from (email, lms, doc, calendar)
    - DeadlineClaim: a deadline value with its source and timestamp
    - Task: a single academic task with full traceability
    - EmailVerdict: classification result for one email
    - DuplicateGroup / DuplicateResult: output of the duplicate checker LLM
    - ConflictRecord: how a conflict between sources was resolved
    - RouterDecision: output of the router LLM
    - CommandIntent: parsed intent from a natural-language command
    - CalendarEvent: a busy event from the calendar
    - Slot: a free time slot available for study
    - ScheduleBlock: a single block of scheduled study time
    - ValidationIssue / ValidationResult: output of the validator
    - TraceEvent: one entry in the execution trace log

Why Pydantic:
    Invalid data raises an error at the boundary instead of failing
    three nodes later. Every LLM output is validated through these schemas.
"""
