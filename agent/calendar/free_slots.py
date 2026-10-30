"""
Free-slot calculation — determines available study time per day.

Milestone: M1 (Calendar-Aware Planning)

Algorithm:
    for each date from today to min(max deadline, today + PLANNING_HORIZON_DAYS):
        window = [STUDY_DAY_START, STUDY_DAY_END]
        busy   = busy_events on that date (from calendar)
        busy   = busy minus events marked cancelled in exceptions_store
        free   = window minus busy
        split into SLOT_MINUTES slots, drop anything shorter than 30 minutes

Input:
    - busy_events: list of CalendarEvent from the provider
    - exceptions: list of cancelled/moved events from exceptions_store
    - config: study window, slot size, planning horizon

Output:
    - list[Slot]: available time blocks for scheduling

This is pure Python — no LLM. Math and time calculations must be exact.
"""
